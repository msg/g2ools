#
# types.py - type definitions for various nord modular objects
#

class Struct:
  def __init__(self, **kw):
    self.__dict__ = kw

class ParameterDef(Struct):
  pass

class Type:
  def __init__(self, name, type):
    self.name = name
    self.type = type

class InputType(Type):
  pass

class OutputType(Type):
  pass

class ParameterType:
  def __init__(self, name, type, labels=[]):
    self.name = name
    self.type = type
    self.labels = labels

class ModeType(Type):
  pass

class PageType:
  def __init__(self, page, index):
    self.page = page
    self.index = index

class ModuleType(Struct):
  pass
