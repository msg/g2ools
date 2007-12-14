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
  def __init__(self, **kw):
    self.__dict__ = kw

class ParamDef(Struct):
  pass

class Type(object):
  def __init__(self, name, type, horiz=0, vert=0):
    self.name = name
    self.type = type
    self.horiz = horiz
    self.vert = vert

class InputType(Type):
  cls = Input

class OutputType(Type):
  cls = Output

class ParamType(object):
  cls = Param
  def __init__(self, name, type, labels=[]):
    self.name = name
    self.type = type
    self.labels = labels

class ModeType(Type):
  cls = Mode

class PageType(object):
  def __init__(self, page, index):
    self.page = page
    self.index = index

class ModuleType(Struct):
  cls = Module
