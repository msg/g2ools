#!/usr/bin/env python

# Copyright: Matt Gerassimoff 2006
#
# Free to redistribute as long as copyright remains
#

import re, string, sys
import modules

NMORPHS = 4

class ParseNM1Error(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Struct:
  def __init__(self, **kw):
    self.__dict__ = kw

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
          raise ParseNM1Error('Header: Cannot parse .pch with version < 3')
        break
    values = map(int,lines[0].split()) + [1]*23 # make sure we have enough
    (self.keymin,self.keymax, self.velmin,self.velmax,
     self.bend,self.porta,self.portatime,self.voices,self.areasep,
     self.octshift,self.voiceretrig,self.commonretrig,
     self.unk1,self.unk2,self.unk3,self.unk4,
     self.red,self.blue,self.yellow,self.gray,self.green,self.purple,self.white
    ) = values[:23]

class Module:
  pass

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
      (index,type,col,row) = values
      module = area.findmodule(index)
      if not module:
        module = Module()
        area.modules.append(module)
      module.index,module.col,module.row=index,col,row
      module.type = modules.fromtype[type]

class Note:
  pass

class CurrentNoteDump(Section):
  def parse(self):
    # # name              value   bit count remarks
    # 1 note              0..127  7         midi note number: 64~middle E
    # 2 attack velocity   0..127  7
    # 3 release velocity  0..127  7
    values = map(int, self.lines[0].split())
    l = len(values)/3
    notes = self.patch.notes = [ Note() for i in range(l) ]
    for i in range(l):
      note,attack,release = values[i*3:i*3+3]
      notes[i].note = note
      notes[i].attack = attack
      notes[i].release = release

# ---- this needs to be a separate module, duplicated in nord.g2.file
class Node(Struct):
  pass

class Net(Struct):
  # ininputs - check if input is in net's input list
  def ininputs(self, input):
    for i in self.inputs:
      if input.module.index == i.module.index and \
        input.conn == i.conn and input.type == i.type:
        return 1
    return 0

# updatenetlist - update the netlist based on source and dest
def updatenetlist(netlist, source, dest):
  found = 0
  for net in netlist:
    if source == net.output or net.ininputs(source) or net.ininputs(dest):
      found = 1
      if not dest in net.inputs:
        net.inputs.append(dest)
      if source.type:
        if net.output:
          raise \
            'Two outputs connected to net: source=%d:%d net.source=%d:%d' % (
            source.module.index, source.conn,
            net.source.module.index, net.source.conn)
        net.output = source
      elif not source in net.inputs:
        net.inputs.append(source)
      break
  if not found:
    if source.type:
      net = Net(output=source,inputs=[dest])
    else:
      net = Net(output=None,inputs=[dest,source])
    netlist.append(net)
# end ---- this needs to be a separate module, duplicated in nord.g2.file

class Cable:
  pass

class CableDump(Section):
  def parse(self):
    lines = self.lines
    if len(lines[0]) > 1:
      sect = 1
    else:
      sect = int(lines.pop(0))
    if sect:
      area = self.patch.voice
    else:
      area = self.patch.fx
    area.cables = []
    area.netlist = []
    for line in self.lines:
      color,dmod,dconn,dtype,smod,sconn,stype = map(int, line.split())
      dmodule = area.findmodule(dmod)
      smodule = area.findmodule(smod)
      dest = Node(module=dmodule,conn=dconn,type=dtype)
      source = Node(module=smodule,conn=sconn,type=stype)
      # if dest is an output, make it the source
      if dest.type:
        dest,source = source,dest
      c = Cable()
      c.color,c.source,c.dest = color,source,dest
      area.cables.append(c)
      # update netlist with nodes
      updatenetlist(area.netlist, source, dest)

class Parameter:
  pass

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
      module = area.findmodule(index)
      if not module:
        module = Module()
        area.modules.append(module)
      module.index = index
      module.type = modules.fromtype[int(values.pop(0))]
      count = values.pop(0)
      module.params = values
      if len(module.params) < count:
        module.params.extend(map(int,lines.pop(0).split()))

class Custom:
  pass

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
        raise ParseNM1Error('CustomDump: invalid module index %s' % index)
      custom = module.custom = Custom()
      custom.parameters = values

class Morph:
  def __init__(self):
    self.maps = []

class MorphMap:
  pass

class MorphMapDump(Section):
  def parse(self):
    if not hasattr(self.patch, 'morphs'):
      self.patch.morphs = [ Morph() for i in range(NMORPHS) ]
    morphs = self.patch.morphs
    knobs = map(int, self.lines[0].split())
    for i in range(NMORPHS):
      morphs[i].knob = knobs[i]
    values = []
    for line in self.lines[1:]:
      values.extend(map(int, line.split()))
    for i in range(len(values)/5):
      morphmap = MorphMap()
      sect,index,morphmap.param,morph,morphmap.range = values[i*5:i*5+5]
      if sect:
        area = self.patch.voice
      else:
        area = self.patch.fx
      morphmap.module = area.findmodule(index)
      if not morph in range(4):
        raise ParseNM1Error('MorphMapDump: invalid morph index %d' % morph)
      morphs[morph].maps.append(morphmap)

class KeyboardAssignment(Section):
  def parse(self):
    keyassign = map(int, self.lines[0].split())
    if not hasattr(self.patch, 'morphs'):
      morphs = self.patch.morphs = [ Morph() for i in range(NMORPHS) ]
    morphs = self.patch.morphs
    for i in range(NMORPHS):
      morphs[i].keyassign = keyassign[i]

class Knob:
  pass

class KnobMapDump(Section):
  def parse(self):
    knobs = self.patch.knobs = [ Knob() for i in range(len(self.lines)) ]
    for i in range(len(self.lines)):
      sect,index,param,knob = map(int, self.lines[i].split())
      if sect:
        area = self.patch.voice
      else:
        area = self.patch.fx
      knobs[i].module = area.findmodule(index)
      knobs[i].param = param
      knobs[i].knob = knob

class Ctrl:
  pass

class CtrlMapDump(Section):
  def parse(self):
    ctrls = self.patch.ctrls = [ Ctrl() for i in range(len(self.lines)) ]
    for i in range(len(self.lines)):
      sect,index,param,cc = map(int, self.lines[i].split())
      if sect:
        area = self.patch.voice
      else:
        area = self.patch.fx
      ctrls[i].module = area.findmodule(index)
      ctrls[i].param = param
      ctrls[i].cc = cc

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
    self.patch.notes = self.lines

class Area:
  def __init__(self):
    self.modules = []

  def findmodule(self, index):
    for m in self.modules:
      if m.index == index:
        return m
    return None

class Patch:
  def __init__(self):
    self.voice = Area()
    self.fx = Area()

class PchFile:
  def __init__(self, fname=None):
    self.patch = Patch()
    if fname:
      self.read(fname)

  def read(self, fname):
    validtags = [
      'Header','ModuleDump','CurrentNoteDump','CableDump','ParameterDump',
      'CustomDump','MorphMapDump','KeyboardAssignment','KnobMapDump',
      'CtrlMapDump','NameDump','Notes'
    ]
    lines = map(string.strip, open(fname).readlines())
    if not len(lines):
      raise ParseNM1Error('NM1File: no valid data: not parsing')
    if lines[0] != '[Header]':
      print 'added missing [Header]'
      lines.insert(0,'[Header]')

    starttags = []
    endtags = []
    for i in range(len(lines)):
      line = lines[i]
      if not len(line):  continue
      if line[0] != '[': continue
      rb = line.find(']')
      if rb < 0:
        rb = None
      if line[1] != '/' and line[1:rb] in validtags:
        starttags.append(i)
      elif line[2:rb] in validtags:
        endtags.append(i)

    if len(endtags):
      if len(starttags) != len(endtags):
        lasttag = '[/'+lines[starttags[-1]][1:]
        print 'added missing endtag: %s' % lasttag
        lines.append(lasttag)
        endtags.append(len(lines)-1)
      if len(starttags) != len(endtags):
        raise ParseNM1Error(
            'NM1File: Start/End tag mismatch: Cannot parse\n%s\n%s' %
            repr(starttags), repr(endtags))
      sections = map(lambda s,e,l=lines: l[s:e+1], starttags, endtags)
    else:
      sections = map(lambda s,e,l=lines: l[s:e+1], starttags[:-1], starttags[1:])

    for s,e in zip(starttags,endtags):
      if e < s:
        raise ParseNM1Error(
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
    except ParseNM1Error, s:
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
#     cable.smod
#     cable.sparam
#     cable.type
#     cable.dmod
#     cable.dparam
#     cable.type
#   param = module.params[i]
#   custom = module.custom
#     custom.parameters
#   morph = patch.morphs[i]
#     morph.knob
#     mophr.keyassign
#     map = morph.maps[i]
#       map.module
#       map.param
#       map.range
#   knob = patch.knobs[i]
#     knob.module
#     knob.param
#     knob.knob
#   ctrl = patch.ctrls[i]
#     ctrl.module
#     ctrl.param
#     ctrl.cc
#   patch.notes
