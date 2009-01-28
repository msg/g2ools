#
# types.py - type definitions for various nord modular objects
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
from nord.module import Input, Output, Param, Mode, Module

class Struct(object):
  '''Struct class for creating objects with named parameters.'''
  def __init__(self, **kw):
    '''Struct(**kw) -> Struct object

\tmembers become **kw keys.
'''
    self.__dict__ = kw

class ParamDef(Struct):
  '''ParamDef Struct subclass for handling module parameter definitions.'''
  pass

class Type(object):
  '''Type abstract class maintaining types.'''
  def __init__(self, name, type, horiz=0, vert=0):
    self.name = name
    self.type = type
    self.horiz = horiz
    self.vert = vert

class TypeList(list):
  def __init__(self, types):
    super(TypeList,self).__init__(types)
    for type in types:
      setattr(self, type.name, type)

class InputType(Type):
  '''InputType Type subclass maintaining module type Inputs.'''
  cls = Input

InputList = TypeList

class OutputType(Type):
  '''OutputType Type subclass maintaining module type Outputs.'''
  cls = Output

OutputList = TypeList

class ParamType(object):
  '''ParamType Type subclass maintaining module type Parameters.'''
  cls = Param
  def __init__(self, name, type, labels=[]):
    self.name = name
    self.type = type
    self.labels = labels

ParamList = TypeList

class ModeType(Type):
  '''ModeType Type subclass maintaining module type Parameters.'''
  cls = Mode

ModeList = TypeList

class PageType(object):
  '''PageType class maintaining page where module type resides.'''
  def __init__(self, page, index):
    self.page = page
    self.index = index

class ModuleType(Struct):
  '''ModuleType class maintaining a module type with
inputs/outputs/parameters/modes.'''
  cls = Module

