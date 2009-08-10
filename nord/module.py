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

class Member(object):
  '''Member abstract class for all Module members.'''
  def __init__(self, module, type, index):
    '''Member(module, type, index) -> Member object'''
    self.module = module
    self.type = type
    self.index = index

class IOMember(Member):
  '''IOMember abstract Member subclass for all Module Input/Output objects.'''
  def __init__(self, module, type, index):
    '''IOMember(module, type, index) -> IOMember object'''
    super(IOMember,self).__init__(module, type, index)
    self.rate = type.type
    self.cables = []
    self.net = None

class Input(IOMember):
  '''Input IOMember subclass'''
  direction = 0

class Output(IOMember):
  '''Output IOMember subclass'''
  direction = 1

class Param(Member):
  '''Param class representing dynamic parameters for a nord modular Module.'''
  def __init__(self, module, type, index):
    '''Param(module, type, index) -> Param object

\tmembers:
\tvariations\t9 variations for parameter (nm1 patch just uses 1st variation.
\tknob\tKnob object if a controller knob is assigned.
\tctrl\tCtrl object if a midi controller is assigned.
\tmorph\tMorph object if a morph is assigned.
\tlabels\tif module type parameter has labels, this is an array of those.
'''
    super(Param, self).__init__(module, type, index)
    self.variations = [ type.type.default for variation in range(9) ]
    self.knob = None
    self.ctrl = None
    self.morph = None
    if len(type.labels):
      self.labels = type.labels[:] # make a copy so they can be changed.

class Mode(Member):
  '''Mode class representing static parameters for a nord modular Module.'''
  def __init__(self, module, type, index):
    '''Mode(module, type, index) -> Mode object'''
    super(Mode,self).__init__(module, type, index)
    self.value = type.type.default

def sattr(obj,nm,val):
  '''sattr(obj,nm,val) -> None  helper function for Array (internal).'''
  if hasattr(obj,nm):
    printf('  %s name "%s" exists\n', obj.__class__.__name__, nm)
  setattr(obj,nm,val)

class Array(list):
  '''Array class for managing arrays within a Module object (internal).'''
  def add(self, nm, obj, index):
    setattr(self, nm.lower(), obj)
    self[index] = obj
    #self.append(obj)

  def __setattr__(self, nm, val):
    self.__dict__[nm.lower()] = val

  def __getattr__(self, nm):
    return self.__dict__[nm.lower()]
  

class Module(object):
  '''Module class representing a nord modular module within a patch.'''
  Groups = [ ['inputs', Input ], ['outputs', Output ],
             ['params', Param ], ['modes', Mode ] ]

  def __init__(self, type, area, **kw):
    '''Module(type, area, **kw) -> Module object'''
    self.name = ''
    self.type = type
    self.area = area
    self.__dict__.update(kw)
    for nm,cls in Module.Groups:
      t = getattr(type, nm)
      a = Array([ None ] * len(t))
      setattr(self, nm, a)
      for i in range(len(t)):
        o = cls(self, t[i], i)
        a.add(t[i].name, o, i)
    if type.type == 121: # SeqNote mag/octave additions
      self.editmodes=[ 0, 1, 1, 0, 1, 5]

