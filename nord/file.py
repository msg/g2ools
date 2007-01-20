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

class Note:
  pass

# holder object for patch cables
class Cable:
  def __init__(self, area):
    self.area = area

# holder object for patch morph parameters
class MorphMap:
  pass

# holder object of patch knob settings
class Knob:
  pass

# holder object of patch midi assignments
class Ctrl:
  pass

# holder object for Performances (currently unused)
#   - when then additional section is parsed/formatted for .prf2
#     files, it will be.
class Performance:
  pass

# holder object for patch voice and fx area data (modules, cables, etc..)
class Area:
  def __init__(self,patch,index):
    self.patch = patch
    self.index = index
    self.modules = []
    self.cables = []
    self.netlist = []

  def findmodule(self, index):
    for i in range(len(self.modules)):
      if self.modules[i].index == index:
        return self.modules[i]
    return None

  def addmodule(self, shortnm, **kw):
    members = [ 'name','index','color','horiz','vert','uprate','leds' ]
    # get next available index
    type = self.patch.fromname[shortnm]
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
      for member in members:
        if kw.has_key(member):
          setattr(m,member,kw[member])
      self.modules.append(m)
      return m

  # connect input/output to input
  def connect(self, source, dest, color):
    cable = Cable(self)
    self.cables.append(cable)

    cable.color = color

    cable.source = source
    source.cables.append(cable)

    cable.dest = dest
    dest.cables.append(cable)

    addnet(self.netlist, cable.source, cable.dest)

  # disconnect a input or output port - update all cables connected to port
  def disconnect(self, cable):
    source,dest = cable.source,cable.dest

    #print 'disconnect %s:%s -> %s:%s' % (
    #  cable.source.module.name,cable.source.type.name,
    #  cable.dest.module.name,cable.dest.type.name)
    #print ' cable',
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
      #print 'connect'
      #print ' source',
      #printnet(c.source.net)
      #print ' dest',
      #printnet(c.dest.net)
      addnet(self.netlist,c.source,c.dest)

    #print 'after disconnect'
    #print ' source',
    #printnet(source.net)
    #print ' dest',
    #printnet(dest.net)

  # removeconnector - remove a port from a cable net
  def removeconnector(self, connector):
    connectors = []
    minconn = None
    mindist = 1000000

    #print 'removeconnector %s:%s' % (connector.module.name,connector.type.name)
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
        #print ' new %s:%s -> %s:%s' % (minconn.module.name,minconn.type.name,
        #    connector.module.name,connector.type.name)
        if minconn.direction:
          self.connect(minconn,connector,0)
        else:
          self.connect(connector,minconn,0)
        #print ' done',
        #printnet(connector.net)

    #print 'after remove',
    #printnet(minconn.net)
    #print

  # quick cable length calculation
  def cablelength(self, cable):
    return self.connectionlength(cable.source, cable.dest)

  # quick connection length calculation (returns square distance)
  def connectionlength(self, start, end):
    # horiz coordinates about 20 times bigger.
    dh = end.module.horiz - start.module.horiz
    dv = end.module.vert - start.module.vert
    return (dh*20)**2+dv**2

# holder object for the patch (the base of all fun/trouble/glory/nightmares)
class Patch:
  def __init__(self,fromname):
    self.fx = Area(self,0)
    self.voice = Area(self,1)
    self.fromname = fromname
    self.ctrls = []
    self.lastnote = None
    self.notes = []

