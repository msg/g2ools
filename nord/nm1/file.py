#!/usr/bin/env python
#
# Copyright (c) 2006,2007 Matt Gerassimoff
#
# This file is part of g2ools.
#
# g2ools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# g2ools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import re, string, sys

from nord.net import addnet
from nord.module import Module
from nord.file import *
from modules import fromname, fromtype

NMORPHS = 4

class NM1Error(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Section:
  def __init__(self, patch, lines):
    self.patch = patch
    self.lines = lines
    self.parse()

  def parse(self):
    pass

class Header(Section):
  def parse(self):
    patch = self.patch
    patch.header = self
    lines = self.lines
    while lines:
      line = lines.pop(0)
      if 'Version=' in line:
        self.version = line
        if float(self.version.split()[-1]) < 3:
          raise NM1Error('Header: Cannot parse .pch with version < 3')
        break
    values = map(int,lines[0].split()) + [1]*23 # make sure we have enough
    (self.keymin,self.keymax, self.velmin,self.velmax,
     self.bend,self.porta,self.portatime,self.voices,self.areasep,
     self.octshift,self.voiceretrig,self.commonretrig,
     self.unk1,self.unk2,self.unk3,self.unk4,
     self.red,self.blue,self.yellow,self.gray,self.green,self.purple,self.white
    ) = values[:23]

class ModuleDump(Section):
  def parse(self):
    for line in self.lines:
      values = map(int, line.split())
      if len(values) == 1 or len(values) > 4:
        sect = values.pop(0)
        if sect:
          area = self.patch.voice
        else:
          area = self.patch.fx
        if not len(values):
          continue
      (index,type,horiz,vert) = values
      module = area.findmodule(index)
      if not module:
        module = area.addmodule(fromtype[type].shortnm)
      module.index,module.horiz,module.vert=index,horiz,vert

class CurrentNoteDump(Section):
  def parse(self):
    # # name              value   bit count remarks
    # 1 note              0..127  7         midi note number: 64~middle E
    # 2 attack velocity   0..127  7
    # 3 release velocity  0..127  7
    values = map(int, self.lines[0].split())
    l = len(values)/3
    lastnote = self.patch.lastnote = Note()
    lastnote.note,lastnote.attack,lastnote.release = values[:3]
    values = values[3:]
    l-=1
    currentnotes = []
    for i in range(0,l,3):
      if values[i] in currentnotes:
        continue
      currentnotes.append(values[i])
    l = len(currentnotes)
    notes = self.patch.notes = [ Note() for i in range(l) ]
    for i in range(l):
      note,attack,release = values[i*3:i*3+3]
      notes[i].note = note
      notes[i].attack = attack
      notes[i].release = release

class CableDump(Section):
  def parse(self):
    lines = self.lines
    line = lines.pop(0)
    if len(line) > 1:
      if len(line.split()) == 8:
        l = line.split()[0]
        line = ' '.join(line.split()[1:])
        lines.insert(0,line)
      sect = int(l)
    else:
      sect = int(line)
    if sect:
      area = self.patch.voice
    else:
      area = self.patch.fx
    area.cables = []
    area.netlist = []
    area.cables = [ None ] * len(self.lines)
    for i in range(len(self.lines)):
      color,dmod,dconn,ddir,smod,sconn,sdir = map(int, lines[i].split())
      dmodule = area.findmodule(dmod)
      smodule = area.findmodule(smod)
      if ddir:
        dest = dmodule.outputs[dconn]
      else:
        dest = dmodule.inputs[dconn]
      if sdir:
        source = smodule.outputs[sconn]
      else:
        source = smodule.inputs[sconn]

      # if dest is an output, make it the source
      if dest.direction:
        dest,source = source,dest

      c = Cable(area)
      area.cables[i] = c
      c.color,c.source,c.dest = color,source,dest

      source.cables.append(c)
      dest.cables.append(c)

      # update netlist with source and dest
      addnet(area.netlist, source, dest)

class ParameterDump(Section):
  def parse(self):
    lines = self.lines[:]
    sect = int(lines.pop(0))
    if sect:
      area = self.patch.voice
    else:
      area = self.patch.fx
    while lines:
      line = lines.pop(0)
      values = map(int, line.split())
      index = values.pop(0)
      typecode = int(values.pop(0))
      module = area.findmodule(index)
      if not module:
        type = fromtype[typecode]
        module = Module(type)
        area.modules.append(module)
      module.index = index
      count = values.pop(0)
      if len(values) < count:
        values.extend(map(int,lines.pop(0).split()))
      for i in range(len(module.params)):
        module.params[i].variations = [ values[i] for variations in range(9) ]

class CustomDump(Section):
  def parse(self):
    sect = int(self.lines[0])
    if sect:
      area = self.patch.voice
    else:
      area = self.patch.fx
    for line in self.lines[1:]:
      values = map(int, line.split())
      index = values.pop(0)
      module = area.findmodule(index)
      if not module:
        raise NM1Error('CustomDump: invalid module index %s' % index)
      modes = values.pop(0)
      for i in range(len(module.modes)):
        module.modes[i].value = values[i]

class Morph:
  def __init__(self,index):
    self.maps = []
    self.index = index
    self.dial = 0
    self.keyassign = 0
    self.knob = None
    self.ctrl = None

class MorphMapDump(Section):
  def parse(self):
    morphs = self.patch.morphs
    dials = map(int, self.lines[0].split())
    for i in range(NMORPHS):
      morphs[i].dial = dials[i]
    values = []
    for line in self.lines[1:]:
      values.extend(map(int, line.split()))
    for i in range(len(values)/5):
      morphmap = MorphMap()
      sect,index,param,morph,morphmap.range = values[i*5:i*5+5]
      if sect:
        area = self.patch.voice
      else:
        area = self.patch.fx
      morphmap.param = area.findmodule(index).params[param]
      morphmap.param.morph = morphs[morph]
      if not morph in range(4):
        raise NM1Error('MorphMapDump: invalid morph index %d' % morph)
      morphs[morph].maps.append(morphmap)

class KeyboardAssignment(Section):
  def parse(self):
    keyassign = map(int, self.lines[0].split())
    morphs = self.patch.morphs
    for i in range(NMORPHS):
      morphs[i].keyassign = keyassign[i]

class KnobMapDump(Section):
  def parse(self):
    knobs = self.patch.knobs = [ Knob() for i in range(len(self.lines)) ]
    for i in range(len(self.lines)):
      vals = map(int, self.lines[i].split())
      sect,index,param,knob = vals
      knobs[i].knob = knob
      if sect == 1:
        knobs[i].param = self.patch.voice.findmodule(index).params[param]
      elif sect == 0:
        knobs[i].param = self.patch.fx.findmodule(index).params[param]
      else:
        knobs[i].param = self.patch.morphs[param]
      knobs[i].param.knob = knobs[i]

class CtrlMapDump(Section):
  def parse(self):
    ctrls = self.patch.ctrls = [ Ctrl() for i in range(len(self.lines)) ]
    for i in range(len(self.lines)):
      sect,index,param,midicc = map(int, self.lines[i].split())
      if sect == 1:
        ctrls[i].param = self.patch.voice.findmodule(index).params[param]
      elif sect == 0:
        ctrls[i].param = self.patch.fx.findmodule(index).params[param]
      else:
        ctrls[i].param = self.patch.morphs[param]
      ctrls[i].midicc = midicc
      ctrls[i].param.ctrl = ctrls[i]

class NameDump(Section):
  def parse(self):
    if not len(self.lines):
      return
    sect = int(self.lines[0])
    if sect:
      area = self.patch.voice
    else:
      area = self.patch.fx
    for line in self.lines[1:]:
      vals = line.split(' ',1)
      if len(vals) > 1:
        name = vals[1]
      else:
        name = ''
      module = area.findmodule(int(vals[0]))
      module.name = name

class Notes(Section):
  def parse(self):
    self.patch.textpad = '\r\n'.join(self.lines)

class NM1Patch(Patch):
  def __init__(self,fromname):
    Patch.__init__(self,fromname)
    self.morphs = [ Morph(i+1) for i in range(NMORPHS) ]
    self.knobs = []
    self.textpad = ''

class PchFile:
  def __init__(self, fname=None):
    self.patch = NM1Patch(fromname)
    if fname:
      self.read(fname)

  def read(self, fname):
    self.fname = fname
    validtags = [
      'Header','ModuleDump','CurrentNoteDump','CableDump','ParameterDump',
      'CustomDump','MorphMapDump','KeyboardAssignment','KnobMapDump',
      'CtrlMapDump','NameDump','Notes'
    ]
    data = open(fname).read(1024)
    if data.find('Nord Modular patch') < 0:
      raise NM1Error('NM1File: %s not valid .pch file' % fname)
    lines = filter(lambda s: s!='', map(string.strip, open(fname).readlines()))
    if not len(lines):
      raise NM1Error('NM1File: no valid data: not parsing')
    if lines[0] != '[Header]':
      print 'added missing [Header]'
      lines.insert(0,'[Header]')

    if fname[-4:].lower() != '.pch':
      self.fname += '.pch'

    starttags = []
    endtags = []
    i=0
    while i < len(lines):
      line = lines[i]
      lb = line.find('[')
      if lb > 0:
        validsection = 0
        for tag in validtags:
          if line.find(tag) > -1:
            validsection = 1
        if validsection:
          lines[i] = line[:lb]
          lines.insert(i+1,line[lb:])
          line = lines[i]
      if len(line) and line[0] == '[':
        rb = line.find(']')
        if rb < 0:
          rb = None
        if line[1] != '/' and line[1:rb] in validtags:
          starttags.append(i)
        elif line[2:rb] in validtags:
          endtags.append(i)
      i += 1

    if len(endtags):
      if len(starttags) != len(endtags):
        lasttag = '[/'+lines[starttags[-1]][1:]
        print 'added missing endtag: %s' % lasttag
        lines.append(lasttag)
        endtags.append(len(lines)-1)
      if len(starttags) != len(endtags):
        raise NM1Error(
            'NM1File: Start/End tag mismatch: Cannot parse\n%s\n%s' %
            (repr(starttags), repr(endtags)))
      sections = map(lambda s,e,l=lines: l[s:e+1], starttags, endtags)
    else:
      sections = map(lambda s,e,l=lines: l[s:e+1], starttags[:-1], starttags[1:])

    for s,e in zip(starttags,endtags):
      if e < s:
        raise NM1Error(
            'NM1File: tags "%s" comes before "%s"' % (lines[e],lines[s]))
    for section in sections:
      section = filter(lambda a: a, section)
      rb = section[0].find(']')
      if rb < 0:
        rb = None
      nm = section[0][1:rb]
      #print nm
      sect = eval('%s(self.patch,section[1:-1])' % nm)

if __name__ == '__main__':
  prog = sys.argv.pop(0)
  while sys.argv:
    fname = sys.argv.pop(0)
    print '"%s"' % fname
    try:
      nm1 = PchFile(fname)
    except NM1Error, s:
      print s

# object ledgend when finished parsing
#   nm1.patch.header
#   patch = nm1.patch
#   area = patch.voice
#   area = patch.fx
#   module = area.modules[i]
#     module.name
#     module.index
#     module.type
#     module.col
#     module.row
#   note = patch.notes[i]
#     note.note
#     note.attack
#     note.release
#   cable = area.cables[i]
#     cable.color
#   src = cable.source
#     src.rate
#     src.cables
#     src.net
#   dest = cable.dest # same as src
#   net = src.net
#     net.output
#     net.inputs[i]
#   param = module.params[i]
#   custom = module.custom
#     custom.parameters
#   morph = patch.morphs[i]
#     morph.knob
#     morph.keyassign
#     map = morph.maps[i]
#       map.param
#       map.range
#   knob = patch.knobs[i]
#     knob.param
#     knob.knob
#   ctrl = patch.ctrls[i]
#     ctrl.param
#     ctrl.cc
#   patch.notes
