#!/usr/bin/env python2
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
from nord import printf

class Input(object):
  '''Input IOMember subclass'''
  direction = 0
  def __init__(self, module, type, index):
    '''Input(module, type, index) -> Input object'''
    self.module = module
    self.type = type
    self.index = index
    self.rate = type.type
    self.cables = []
    self.net = None

class Output(object):
  '''Output IOMember subclass'''
  direction = 1
  def __init__(self, module, type, index):
    '''Output(module, type, index) -> Output object'''
    self.module = module
    self.type = type
    self.index = index
    self.rate = type.type
    self.cables = []
    self.net = None

class Param(object):
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
    self.module = module
    self.type = type
    self.index = index
    self.variations = [ type.type.default ] * 9
    self.knob = None
    self.ctrl = None
    self.morph = None
    if len(type.labels):
      self.labels = type.labels[:] # make a copy so they can be changed.

class Mode(object):
  '''Mode class representing static parameters for a nord modular Module.'''
  def __init__(self, module, type, index):
    '''Mode(module, type, index) -> Mode object'''
    self.module = module
    self.type = type
    self.index = index
    self.value = type.type.default

def sattr(obj, nm, val):
  '''sattr(obj, nm, val) -> None  helper function for Array (internal).'''
  if hasattr(obj, nm):
    printf('  %s name "%s" exists\n', obj.__class__.__name__, nm)
  setattr(obj, nm, val)

class Array(list):
  '''Array class for managing arrays within a Module object (internal).'''
  def add(self, nm, obj, index):
    setattr(self, nm.lower(), obj)
    self[index] = obj

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

    for nm, cls in Module.Groups:
      t = getattr(type, nm)
      a = Array([ None ] * len(t))
      setattr(self, nm, a)
      for i in range(len(t)):
        o = cls(self, t[i], i)
        a.add(t[i].name, o, i)
    if type.id == 121: # SeqNote mag/octave additions
      # [0, 1, mag, 0, 1, octave]
      # mag: 0=3-octaves, 1=2-octaves, 2=1-octave
      # octave: 0-9 (c0-c9)
      self.editmodes = [ 0, 1, 1, 0, 1, 5]

