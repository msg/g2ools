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

from nord import printf
from nord.net import NetList
from nord.module import Module
from nord.file import *
from modules import fromname, fromtype

NMORPHS = 4

class NM1Error(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Section(object):
  def __init__(self, patch, lines):
    self.patch = patch
    self.lines = lines
    self.parse()

  def parse(self):
    pass

class HeaderV3(Section):
  def parse(self):
    patch = self.patch
    patch.header = self
    lines = self.lines
    while lines:
      line = lines.pop(0)
      if 'Version=' in line:
        self.version = line
	if self.version.find('patch 3') < 0:
          raise NM1Error('Header: version "%s" invalid' % self.version)
        break
    values = map(int,lines[0].split()) + [1]*23 # make sure we have enough
    (self.keymin,self.keymax, self.velmin,self.velmax,
     self.bend,self.porta,self.portatime,self.voices,self.areasep,
     self.octshift,self.voiceretrig,self.commonretrig,
     self.unk1,self.unk2,self.unk3,self.unk4,
     self.red,self.blue,self.yellow,self.gray,self.green,self.purple,self.white
    ) = values[:23]

class ModuleDumpV3(Section):
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
        module = area.addmodule(fromtype(type).shortnm)
      module.index,module.horiz,module.vert=index,horiz,vert

class CurrentNoteDumpV3(Section):
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

class CableDumpV3(Section):
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
    area.netlist = NetList()
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
      area.netlist.add(source, dest)

class ParameterDumpV3(Section):
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
        continue
      module.index = index
      count = values.pop(0)
      if len(values) < count:
        values.extend(map(int,lines.pop(0).split()))
      for i in range(min(len(values),len(module.params))):
        module.params[i].variations = [ values[i] for variations in range(9) ]

class CustomDumpV3(Section):
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

class MorphMapDumpV3(Section):
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
      if not morph in range(NMORPHS):
        raise NM1Error('MorphMapDump: invalid morph index %d' % morph)
      morphs[morph].maps.append(morphmap)

class KeyboardAssignmentV3(Section):
  def parse(self):
    keyassign = map(int, self.lines[0].split())
    morphs = self.patch.morphs
    for i in range(NMORPHS):
      morphs[i].keyassign = keyassign[i]

class KnobMapDumpV3(Section):
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

class CtrlMapDumpV3(Section):
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

class NameDumpV3(Section):
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
      if module == None:
        printf("[NameDump]: module index %d not found\n", int(vals[0]))
        continue
      module.name = name

class NotesV3(Section):
  def parse(self):
    self.patch.textpad = '\r\n'.join(self.lines)

class V2Define(object):
  def __init__(self, title, lines, **kw):
    self.__dict__ = kw # must be done first
    self.title = title
    self.lines = lines

class V2Section(object):
  def __init__(self, patch, defines, moduledefs):
    self.patch = patch
    self.defines = defines
    self.moduledefs = moduledefs
    self.parse()

  def parse(self):
    pass

def getv2moduledefs(defines):
  def ismodule(define): return define[1].title[:6] == 'Module'
  def bymoduleindex(a, b): return cmp(int(a[1].title[6:]), int(b[1].title[6:]))
  moduledefs = [ (int(define[0][6:]),define[1]) for define in defines.items()
  			if ismodule(define) ]
  moduledefs.sort(bymoduleindex)
  return moduledefs

def findv2moduledef(defines, index):
  for define in defines:
    if define[0] == index:
      return define
  return None
  
def getv2params(define, leader):
  def isparam(leader, key): return key[:len(leader)] == leader
  def byparamindex(a, b, l=len(leader)): return cmp(int(a[l:]),int(b[l:]))
  keys = [ key for key in define.__dict__.keys() if isparam(leader, key) ]
  keys.sort(byparamindex)
  return [ [int(key[len(leader):]),getattr(define,key)] for key in keys ]

MORPH_TYPE = 6
MAX_MODULES = 127
class ModulesV2(V2Section):
  def parse(self):
    # - create modules from modules sections
    #   - module type 6 is morph, must be handled
    #     midicc 126 and 127 are note and vel? (could be reversed)
    #     knobs connect to morphs via module definition
    # - create cables from modules sections
    self.create_modules()
    self.create_cables()

  def update_module_params(self, moduledef, module):
    params = getv2params(moduledef,'p')
    lp, lmp = len(params), len(module.params)
    for i in range(min(lp,lmp)):
      val = int(params[i][1])
      val = max(val,module.params[i].type.type.low)
      val = min(val,module.params[i].type.type.high)
      module.params[i].variations = [ val for variations in range(9) ]

  def create_modules(self):
    area = self.patch.voice
    for i in range(len(self.moduledefs)):
      index, moduledef = self.moduledefs[i]
      if moduledef.type == MORPH_TYPE: # handle this later
        continue

      module = area.addmodule(fromtype(moduledef.type).shortnm)
      module.index,module.name = (index, str(moduledef.name))
      module.horiz,module.vert = (moduledef.col, moduledef.row*2)

      self.update_module_params(moduledef, module)

  def create_cables(self):
    OUTPUT = 0x40
    area = self.patch.voice
    for i in range(len(self.moduledefs)):
      index, moduledef = self.moduledefs[i]
      if moduledef.type == MORPH_TYPE: # handle this later
        continue
      module = area.findmodule(index)
      ims = getv2params(moduledef,'im') # module to connect to
      ihs = getv2params(moduledef,'ih') # port (0x40=output) rest index
      ics = getv2params(moduledef,'ic') # cable color
      for j in range(len(ims)):
        dconn, smod = ims[j]
	sconn, color = ihs[j][1], ics[j][1]
	smoduledef = findv2moduledef(self.moduledefs, smod)
	if not smoduledef or smoduledef[1].type == MORPH_TYPE:
	  continue

	dest = module.inputs[dconn]
	smodule = area.findmodule(smod)
	if sconn & OUTPUT:
	  source = smodule.outputs[sconn & ~OUTPUT]
	else:
	  source = smodule.inputs[sconn]
        
	self.patch.voice.connect(source, dest, color)


class HeaderV2(V2Section):
  def parse(self):
    define = self.defines['Header']
    self.patch.header = self
    self.keymin, self.keymax = define.kbrangemin, define.kbrangemax
    self.velmin, self.velmax = define.velrangemin, define.velrangemax
    self.bend = define.bendrange
    self.porta = define.pmmode
    self.portatime = define.pmtime
    self.voices = define.voices
    self.areasep = 0
    if hasattr(define, 'octshift'):
      self.octshift = define.octshift
    else:
      self.octshift = 0
    self.voiceretrig = define.retrig
    self.commonretrig = 0
    self.red = define.cable0
    self.blue = define.cable1
    self.yellow = define.cable2
    self.gray = define.cable3
    self.green = self.purple = self.white = 1

class VoicesV2(V2Section):
  def parse(self):
    def getnote(value):
      return (value & 0x7f, (value>>8)&0x7f, (value>>16)&0x7f)
    define = self.defines.get('Voices', None)
    if define == None: return
    voices = getv2params(define,'v')
    values = [ getnote(voice[1]) for voice in voices ]
    l = len(values)
    lastnote = self.patch.lastnote = Note()
    lastnote.note,lastnote.attack,lastnote.release = values[0]
    values = values[1:]
    l-=1
    currentnotes = []
    for i in range(l):
      if values[i] in currentnotes:
        continue
      currentnotes.append(values[i])
    l = len(currentnotes)
    notes = self.patch.notes = [ Note() for i in range(l) ]
    for i in range(l):
      notes[i].note,notes[i].attack,notes[i].release = values[i]

class ControllersV2(V2Section):
  def parse(self):
    define = self.defines.get('Controllers', None)
    if define == None: return
    modules = getv2params(define,'m')   # module to connect to
    params = getv2params(define,'p')    # parameters to connecto to
    for i in range(len(modules)):
      midicc, modindex = modules[i]
      midicc, param = params[i]
      moduledef = findv2moduledef(self.moduledefs, modindex)
      if moduledef and moduledef[1].type == MORPH_TYPE:
        continue # add midicc to morph, param is morph group

class MorphsV2(V2Section):
  def parse(self):
    morphs = self.patch.morphs
    morphmod = None
    for i in range(len(self.moduledefs)):
      if self.moduledefs[i][1].type == MORPH_TYPE:
        morphdmod = self.moduledefs[i][1]
    if morphmod:
      for i in range(NMORPHS):
        morphs[i].dial = getattr(morphmod, 'p%d' % i)
    define = self.defines.get('Morphs', None)
    if define == None: return
    modules = getv2params(define,'m') # module to connect to
    params = getv2params(define,'p')  # parameters to connecto to
    dials = getv2params(define,'d')   # morph dial of parameter
    groups = getv2params(define,'g')  # morph groups
    area = self.patch.voice
    for i in range(len(modules)):
      morph, index = modules[i]
      morph, param  = params[i]
      morph, dial   = dials[i]
      morph, group  = groups[i]
      if not morph in range(25): ### HACK
        #raise NM1Error('MorphMapDump: invalid morph index %d' % morph)
	continue
      morphmap = MorphMap()
      morphmap.range = dial
      mod = area.findmodule(index)
      if param > len(mod.params) - 1:
        param = 0
      morphmap.param = mod.params[param]
      morphmap.param.morph = morphs[group]
      morphs[group].maps.append(morphmap)

class KnobsV2(V2Section):
  def parse(self):
    define = self.defines.get('Knobs', None)
    if define == None: return

    modules = getv2params(define,'m') # module to connect to
    params = getv2params(define,'p')  # parameters to connecto to
    knobs = self.patch.knobs = [ Knob() for i in range(len(modules)) ]
    for i in range(len(modules)):
      knob, index = modules[i]
      knob, param = params[i]
      moduledef = findv2moduledef(self.moduledefs, index)
      knobs[i].knob = knob
      if moduledef and moduledef[1].type == MORPH_TYPE:
        if param > 3: #### HACK
	  param &= 3
        knobs[i].param = self.patch.morphs[param]
      else:
	if moduledef and moduledef[1].type == 106 and param > 23: ### HACK
	  param -= 13
	mod = self.patch.voice.findmodule(index)
	if param > len(mod.params) - 1: ### HACK
	  param = 0
        knobs[i].param = mod.params[param]
      knobs[i].param.knob = knobs[i]

class NotesV2(V2Section):
  def parse(self):
    define = self.defines.get('Notes', None)
    if define == None: return
    lines = [ getattr(define, 'l%d' % i) for i in range(define.count) ]
    self.patch.textpad = '\r\n'.join(lines)

class Morph(object):
  def __init__(self,index):
    self.maps = []
    self.index = index
    self.dial = 0
    self.keyassign = 0
    self.knob = None
    self.ctrl = None

class NM1Patch(Patch):
  def __init__(self,fromname):
    super(NM1Patch,self).__init__(fromname)
    self.morphs = [ Morph(i+1) for i in range(NMORPHS) ]
    self.knobs = []
    self.textpad = ''

class PchFile(object):
  v3tags = [
    'Header','ModuleDump','CurrentNoteDump','CableDump','ParameterDump',
    'CustomDump','MorphMapDump','KeyboardAssignment','KnobMapDump',
    'CtrlMapDump','NameDump','Notes'
  ]
  v3counts = [ 1, 2, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1 ]
  v2tags = [
    'Modules', 'Header', 'Voices', 'Controllers', 'Morphs', 'Knobs', 'Notes'
  ]

  def __init__(self, fname=None):
    self.patch = NM1Patch(fromname)
    if fname:
      self.read(fname)

  def read(self, fname):
    self.fname = fname
    data = open(fname).read()
    v2 = data.find('Nord Modular patch 2.10')
    v3 = data.find('Nord Modular patch 3.0')
    if v2 < 0 and v3 < 0:
      raise NM1Error('%s not valid .pch file' % fname)
    lines = filter(lambda s: s!='', map(string.strip, open(fname).readlines()))
    if not len(lines):
      raise NM1Error('%s no valid data: not parsing' % fname)
    if lines[0] != '[Header]':
      printf('added missing [Header]\n')
      lines.insert(0,'[Header]')

    if fname[-4:].lower() != '.pch':
      self.fname += '.pch'

    if v2 > -1:
      self.readv2(data)

    if v3 > -1:
      self.readv3(data)

  def findv3sections(self, data):
    sections = []
    counts = self.v3counts[:]
    for tag in self.v3tags:
      count = counts.pop(0)
      starttag = '[' + tag + ']'
      endtag = '[/' + tag + ']'
      off = start = 0
      while start > -1 and count > 0:
	start = data.find(starttag, off)
	if start < 0:
	  continue
	end = data.find(endtag, start)
	if end > -1:
	  end += len(endtag)
	sections.append([tag, start, end])
	off = start + len(starttag)
	count -= 1
    return sections

  def parsev3data(self, data, sections):
    l = len(sections)
    for i in range(l):
      tag, start, end = sections[i]
      if start < 0:
        printf('no start tag %s\n', tag)
        continue
      if end < 0:
        if i < l-1:
	  ntag, nstart, nend = sections[i+1]
	  end = nstart
	else:
	  end = None
      lines = map(string.strip, data[start:end].split('\n'))
      lines = [ line for line in lines if line ]
      if len(lines) > 2:
        sect = eval('%sV3(self.patch,lines[1:-1])' % tag)

  def readv3(self, data):
    sections = self.findv3sections(data)
    self.parsev3data(data, sections)

  def findv2defines(self, data):
    sections = data.split('\r\n[')
    sections = [ ('[' + section.strip()).split('\r\n') for section in sections ]
    sections[0][0] = sections[0][0][1:] # fix [[Header] to [Header]
    # create dictionary of sections with
    # each line in each section set to a parameter in a class object
    # remove ' ' from sections names before creating
    def fixparam(v):
      name, value = v
      try:
        y = int(name)
	name = 'v'+name
      except:
        pass
      try:
        if name != 'name':
	  value = int(value)
      except:
        pass
      return name.lower(), value

    defines = { }
    for section in sections:
      title = section[0][1:-1].replace(' ', '')  # remove [ ]
      values = [ line.split('=',1) for line in section[1:] if line.strip() ]
      values = [ fixparam(v) for v in values if len(v) > 1 ]
      pairs = dict(values)
      defines[title] = V2Define(title, section, **pairs)
    return defines

  def parsev2defines(self, defines):
    moduledefs = getv2moduledefs(defines)
    for tag in self.v2tags:
      sect = eval('%sV2(self.patch, defines, moduledefs)' % tag)

  def readv2(self, data):
    defines = self.findv2defines(data)
    self.parsev2defines(defines)

if __name__ == '__main__':
  prog = sys.argv.pop(0)
  while sys.argv:
    fname = sys.argv.pop(0)
    printf('"%s"\n', fname)
    try:
      nm1 = PchFile(fname)
    except NM1Error, s:
      printf('%s\n', s)

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
