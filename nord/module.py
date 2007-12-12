#!/usr/bin/env python
#
# module.py - create a module from it's type
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

class Member:
  def __init__(self, module, type, index):
    self.module = module
    self.type = type
    self.index = index

class IOMember(Member):
  def __init__(self, module, type, index):
    Member.__init__(self, module, type, index)
    self.rate = type.type
    self.cables = []
    self.net = None

class Input(IOMember):
  direction = 0

class Output(IOMember):
  direction = 1

class Param(Member):
  def __init__(self, module, type, index):
    Member.__init__(self, module, type, index)
    self.variations = [ type.type.default for variation in range(9) ]
    self.knob = None
    self.ctrl = None
    self.morph = None

class Mode(Member):
  def __init__(self, module, type, index):
    Member.__init__(self, module, type, index)
    self.value = type.type.default

def sattr(obj,nm,val):
  if hasattr(obj,nm):
    print '  %s name "%s" exists' % (obj.__class__.__name__, nm)
  setattr(obj,nm,val)

class Array(list):
  def add(self, nm, obj, index):
    setattr(self, nm, obj)
    self[index] = obj
    #self.append(obj)

class Module:
  Groups = [ ['inputs', Input ], ['outputs', Output ],
	     ['params', Param ], ['modes', Mode ] ]

  def __init__(self, type, area, **kw):
    self.name = ''
    self.type = type
    self.area = area
    self.__dict__.update(kw)
    for nm,cls in Module.Groups:
      a = Array()
      setattr(self, nm, a)
      t = getattr(type,nm)
      a += [ None ] * len(t)
      for i in range(len(t)):
        o = cls(self,t[i],i)
	a.add(t[i].name,o, i)
    if type.type == 121: # SeqNote mag/octave additions
      self.editmodes=[0,1,1,0,1,5]

