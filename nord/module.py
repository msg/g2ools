#!/usr/bin/env python
#
# module.py - create a module from it's type
#

from nord.g2 import modules as g2mods

class Member:
  def __init__(self, module, type, index):
    self.module = module
    self.type = type
    self.index = index

class Input(Member):
  direction = 0

class Output(Member):
  direction = 1

class Param(Member):
  def __init__(self, module, type, index):
    Member.__init__(self, module, type, index)
    self.variations = [ type.type.default for variation in range(9) ]

class Mode(Member):
  pass

def sattr(obj,nm,val):
  if hasattr(obj,nm):
    print '  %s name "%s" exists' % (obj.type.shortnm, nm)
  setattr(obj,nm,val)

class Array(list):
  pass

class Module:
  def __init__(self, type):
    self.type = type
    entries = [ ['inputs', Input ], ['outputs', Output ],
                ['params', Param ], ['modes', Mode ] ]
    for nm,cls in entries:
      sattr(self, nm, Array())
      for i in range(len(getattr(type,nm))):
        t = getattr(type,nm)
        o = cls(self,t[i],i)
        a = getattr(self,nm)
        a.append(o)
        sattr(a,t[i].name,o)

