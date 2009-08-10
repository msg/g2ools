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
from net import addnet, delnet, printnet
from nord.module import Module

def out(x):
  if x < 32 or x > 127:
    return '.'
  return chr(x)

def hexdump(bytes,addr=0,size=1):
  from array import array
  '''hexdump(bytes,addr,size) -> return hex dump of size itmes using addr as address'''
  s = []
  if size == 4:
    a = array('L', [])
    fmt = '%08x'
    l = 17
  elif size == 2:
    a = array('H', [])
    fmt = '%04x'
    l = 19
  else:
    a = array('B', [])
    fmt = '%02x'
    l = 23
  a.fromstring(bytes)
  for off in range(0,len(bytes),16):
    hex = [fmt % i for i in a[off/size:(off+16)/size]]
    s.append('%06x: %-*s  %-*s | %s' % (addr+off,
      l, ' '.join(hex[:8/size]), l, ' '.join(hex[8/size:]),
      ''.join([out(ord(byte)) for byte in bytes[off:off+16]])))
  return '\n'.join(s)

def binhexdump(bytes, addr=0, bits=[]):
  from array import array
  def bin(byte):
    return ''.join([ '01'[(byte>>(7-i))&1] for i in range(8) ])
  def hex(byte):
    return '%x   %x   ' % (byte>>4, byte&0xf)
  a = array('B', bytes)
  s = []
  for off in range(0,len(a),8):
    s.append('%04x: %s' % (addr+off, ' '.join([hex(b) for b in a[off:off+8]])))
    s.append('      %s' % (' '.join([bin(b) for b in a[off:off+8]])))
  # add bits
  # single bits represented by: 0 or 1
  # two bits represented by: [0 thru [3
  # < five bits represented by: [0] thru [f]
  # < nine bits represented by: [00    ] thru [ff     ]
  # < thirteen bits represented by: [000    ] thru [fff    ]
  # > twelve bits represented by: [0000      ] thru [ffff     ]
  # 00000000 00000000 
  # 0[3[f ][1f   ]
  return '\n'.join(s)

class Note(object):
  '''Note class for nord patch notes.'''
  pass

class Cable(object):
  '''Cable class for patch cables.'''
  def __init__(self, area):
    self.area = area

class MorphMap(object):
  '''MorphMap class for patch morph parameters.'''
  pass

class Knob(object):
  '''Knob class for patch knob settings.'''
  pass

class Ctrl(object):
  '''Ctrl class for patch midi assignments.'''
  pass

class Area(object):
  '''Area class for patch voice and fx area data (modules, cables, etc...)

This class maintains the modules, cable connections, and netlist
for the voice and fx areas of a nord modules g2 patch.

\tuseful members:
\tpatch\tpatch containing area.
\tmodules\tarray of modules within area.
\tcables\tarray of cables connections within area.
'''

  def __init__(self, patch, index, name):
    self.patch = patch
    self.index = index
    self.name = name
    self.modules = []
    self.cables = []
    self.netlist = []

  def findmodule(self, index):
    '''findmodule(index) -> module at index or None'''
    for module in self.modules:
      if module.index == index:
        return module
    return None

  modmembers = [ 'name','index','color','horiz','vert','uprate','leds' ]

  def addmodule(self, shortnm, **kw):
    '''addmodule(shortnm, **kw) -> Module
\tshortnm\tmodule short type name to add.

\t**kw:
\tname\tname of module (label displayed in upper left corner.
\tcolor\tcolor of module (nord.g2.color.g2modulecolors.
\thoriz\tcolumn where module is placed (<32).
\tvert\trow where module is placed (<127)
'''
    # get next available index
    type = self.patch.fromname(shortnm)
    indexes = [ m.index for m in self.modules ]
    for index in range(1,128):
      if not index in indexes:
        break
    if index < 128:
      m = Module(type,self)
      m.name = type.shortnm
      m.index = index
      m.color = 0
      m.horiz = 0
      m.vert = 0
      m.uprate = 0
      m.leds = 0
      for member in Area.modmembers:
        if kw.has_key(member):
          setattr(m,member,kw[member])
      self.modules.append(m)
      return m

  def delmodule(self, module):
    '''delmodule(module) -> None

\tdelete module from modules sequence.
'''
    self.modules.remove(module)


  def connect(self, source, dest, color):
    '''connect(source, dest, color) -> None

\tconnect input/output to input from source port to dest port using color.
\tcolor is in nord.g2.colors.g2cablecolors or nord.nm1.colors.nm1cablecolors.

\tcannot connect 2 Outputs together.
'''
    sid = (source.module.index << 16) + source.index
    did = (dest.module.index << 16) + dest.index
    if source.direction == dest.direction and sid > did:
      source,dest = dest,source

    cable = Cable(self)
    self.cables.append(cable)

    cable.color = color

    cable.source = source
    source.cables.append(cable)

    cable.dest = dest
    dest.cables.append(cable)

    addnet(self.netlist, cable.source, cable.dest)

  def disconnect(self, cable):
    '''disconnect(cable) -> None

\tdisconnect a input or output port - update all cables connected to port
'''
    source,dest = cable.source,cable.dest

    #printf('disconnect %s:%s -> %s:%s\n' (
    #  cable.source.module.name,cable.source.type.name,
    #  cable.dest.module.name,cable.dest.type.name)
    #printf(' cable ')
    #printnet(cable.source.net)

    # collect all the cables on the net
    cables = []
    for input in source.net.inputs:
      for c in input.cables:
        if not c in cables:
          cables.append(c)

    cables.remove(cable)
    source.cables.remove(cable)
    dest.cables.remove(cable)
    self.cables.remove(cable)
    delnet(self.netlist,source,dest)

    source.net = dest.net = None
    for c in cables:
      #printf('connect\n')
      #printf(' source ')
      #printnet(c.source.net)
      #printf(' dest ')
      #printnet(c.dest.net)
      addnet(self.netlist,c.source,c.dest)

    #printf('after disconnect\n')
    #printf(' source')
    #printnet(source.net)
    #printf(' dest')
    #printnet(dest.net)

  def removeconnector(self, connector):
    '''removeconnector(connector) -> connector

\tremove connector from the cable net and cable connections.
\tconnector is a member of the Module object.
'''
    connectors = []
    minconn = None
    mindist = 1000000

    #printf('removeconnector %s:%s\n', connector.module.name,connector.type.name)
    #printf('before remove ')
    #printnet(connector.net)
    while len(connector.cables):
      cable = connector.cables[0]
      source,dest = cable.source,cable.dest
      self.disconnect(cable)
      if connector == source:
        other = dest
      else:
        other = source
      dist = self.connectionlength(connector,other)
      if dist < mindist:
        if minconn:
          connectors.append(minconn)
        mindist = dist
        minconn = other
      elif not other in connectors:
        connectors.append(other)

    if len(connectors) != 0:
      for connector in connectors:
        #printf(' new %s:%s -> %s:%s\n', minconn.module.name,minconn.type.name,
        #    connector.module.name,connector.type.name)
        if minconn.direction:
          self.connect(minconn,connector,0)
        else:
          self.connect(connector,minconn,0)
        #printf(' done ')
        #printnet(connector.net)

    #printf('after remove ')
    #printnet(minconn.net)
    #printf('\n')
    return minconn

  # quick cable length calculation
  def cablelength(self, cable):
    '''cablelength(cable) -> length of cable'''
    return self.connectionlength(cable.source, cable.dest)

  # quick connection length calculation (returns square distance)
  def connectionlength(self, start, end):
    '''connectionlength(start, end) -> distance from start port to end port'''
    # horiz coordinates about 20 times bigger.
    sm,em=start.module,end.module
    dh = (19*em.horiz+end.type.horiz)-(19*sm.horiz+start.type.horiz)
    dv = (em.vert+end.type.vert)-(sm.vert+start.type.vert)
    return (dh**2)+(dv**2)

  def shortencables(self):
    '''shortencables()

\tmake all cable as short as possible.
'''
    netlist = self.netlist[:]
    # remove all cables
    cables = self.cables[:]
    while len(cables):
      cable = cables.pop(0)
      cable.source.net.color = cable.color
      self.disconnect(cable)

    def findclosest(g2area,fromlist,tolist):
      mincablelen = 1000000
      mincable = None
      for fromconn in fromlist:
        for toconn in tolist:
          cablelen = g2area.connectionlength(fromconn,toconn)
          if cablelen < mincablelen:
            mincablelen = cablelen
            mincable = [fromconn,toconn]
      return mincable

    # on each net, successively connect closet connector
    for net in netlist:
      inputs = net.inputs
      if net.output:
        fromconn, toconn = findclosest(self,[net.output],inputs)
      else:
        conn = inputs.pop(0)
        fromconn, toconn = findclosest(self,[conn],inputs)
      self.connect(fromconn,toconn,net.color)
      inputs.remove(toconn)
      connected = [fromconn,toconn]
      while len(inputs):
        fromconn, toconn = findclosest(self,connected,inputs)
        self.connect(fromconn,toconn,net.color)
        inputs.remove(toconn)
        connected.append(toconn)

class Patch(object):
  '''Patch class for a nord modular patch.

\tThis class maintains the areas, controls, notes.  
A holder object for a g2 patch (the base of all fun/trouble/glory/nightmares).

This class is normally not instanced directly but reimplemented in
the nm1 and g2 implementations.
'''

  def __init__(self,fromname):
    '''Patch(fromname) -> Patch object

\tfromname is a list names to module types.
'''
    self.fx = Area(self,0,'fx')
    self.voice = Area(self,1,'voice')
    self.fromname = fromname
    self.ctrls = []
    self.lastnote = None
    self.notes = []

# holder object for Performances
class Performance(object):
  '''Performance class representing a nord modular performance.

Basically a holder for 4 patches, one each for slot a, slot b,
slot c, and slot d.
'''
  def __init__(self,fromname):
    self.patches = [ Patch(fromname) for slot in range(4) ]

