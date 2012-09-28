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
  __slots__ = ( 'module', 'type', 'index', 'rate', 'cables', 'net', 'conv' )
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
  __slots__ = ( 'module', 'type', 'index', 'rate', 'cables', 'net', 'conv' )
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
  __slots__ = (
    'module', 'type', 'index', 'variations', 'knob', 'ctrl', 'morph', 'labels'
  )
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
  __slots__ = ( 'module', 'type', 'index', 'value' )
  '''Mode class representing static parameters for a nord modular Module.'''
  def __init__(self, module, type, index):
    '''Mode(module, type, index) -> Mode object'''
    self.module = module
    self.type = type
    self.index = index
    self.value = type.type.default

class Array(list):
  '''Array class for managing arrays within a Module object (internal).'''
  def __init__(self, parent, items, item_class):
    self[:] = [ item_class(parent, e, i) for i, e in enumerate(items) ]
    for o in self:
      self.__dict__[o.type.name] = o

  #def __setattr__(self, nm, val):
  #  self.__dict__[nm] = val

  #def __getattr__(self, nm):
  #  return self.__dict__[nm]

class Module(object):
  '''Module class representing a nord modular module within a patch.'''
  def __init__(self, type, area, **kw):
    '''Module(type, area, **kw) -> Module object'''
    #self.__dict__ = kw
    self.name = ''
    self.type = type
    self.area = area
    self.__dict__.update(kw)

    self.inputs  = Array(self, type.inputs,  Input)
    self.outputs = Array(self, type.outputs, Output)
    self.params  = Array(self, type.params,  Param)
    self.modes   = Array(self, type.modes,   Mode)

    if type.id == 121: # SeqNote mag/octave additions
      # [0, 1, mag, 0, 1, octave]
      # mag: 0=3-octaves, 1=2-octaves, 2=1-octave
      # octave: 0-9 (c0-c9)
      self.editmodes = [ 0, 1, 1, 0, 1, 5]

