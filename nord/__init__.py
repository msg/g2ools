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
def printf(fmt, *a):
  import sys
  sys.stdout.write(fmt % a)

def sprintf(fmt, *a):
  return fmt % a

class Struct(object):
  '''Struct class for creating objects with named parameters.'''
  def __init__(self, **kw):
    '''Struct(**kw) -> Struct object

\tmembers become **kw keys.
'''
    self.__dict__ = kw

class Mapping(object):
  '''Mapping class for creating objects with named/value mappings.'''
  def __init__(self, **kw):
    '''Mapping(**kw) -> Mapping object

\tname/value and value/name become **kw keys.
'''
    self.__dict = {}
    for name, value in kw.items():
      self.add_mapping(name, value)

  def add_mappings(self, **kw):
    for name, value in kw.items():
      self.add_mapping(name, value)

  def add_mapping(self, name, value):
    self.__dict__[name] = value
    self.__dict[value] = name

  def __getattr__(self, name):
    try:
      return self.__dict__[name]
    except:
      return self.__dict[name]

  def __getitem__(self, name):
    return self.__getattr__(name)

