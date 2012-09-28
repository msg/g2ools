#
# convert.py - main convert object
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
from nord.utils import setv, getv
from nord.g2.colors import g2cablecolors
from nord.nm1.colors import nm1conncolors
from nord.units import nm2g2val
from nord.utils import toascii
from nord.convert.table import kbttable

def updatevals(g2mp, params, nm1g2_map):
  '''updatevals(g2mp, params, nm1g2_map) -> None
  change the time values of g2 module based on tables in ./units.py.
  '''
  for param in params:
    midival = getv(getattr(g2mp, param))
    setv(getattr(g2mp, param), nm1g2_map[midival])

class Convert(object):

  parammap = []
  inputmap = []
  outputmap = []

  def __init__(self, nmarea, g2area, nmmodule, options):
    '''Convert(nmarea, g2area, nmmodule, options) -> Convert
    create a convert object from a nm1 module in nmarea to g2area.
    '''
    self.nmarea = nmarea
    self.g2area = g2area
    nmm = self.nmmodule = nmmodule
    nmm.conv = self # to get back here when needed (cables)
    self.options = options
    # use for cabling
    for output in nmmodule.outputs:
      output.conv = self 
    for input in nmmodule.inputs:
      input.conv = self 
    self.g2modules = []
    self.params = []
    self.outputs = []
    self.inputs = []

    # create main module and setup size requirements
    g2m = self.g2module = g2area.add_module(self.maing2module)
    g2m.name = toascii(nmm.name)
    self.horiz = g2m.horiz = nmm.horiz
    self.height = g2m.type.height

    # setup parameters from parammap static member of convert module class
    self.params = [ None ] * len(self.parammap)
    for i, param in enumerate(self.parammap):
      if type(param) == type(''):
        setv(getattr(g2m.params, param), getv(getattr(nmm.params, param)))
        self.params[i] = getattr(g2m.params, param)
      elif type(param) == type([]):
        setv(getattr(g2m.params, param[0]), getv(getattr(nmm.params, param[1])))
        self.params[i] = getattr(g2m.params, param[0])
      else:
        self.params[i] = param # None: placeholder for other parameters

    # setup inputs from inputmap static member of convert module class
    self.inputs = [ getattr(g2m.inputs, i, None) for i in self.inputmap ]

    # setup outputs from outputmap static member of convert module class
    self.outputs = [ getattr(g2m.outputs, o, None) for o in self.outputmap ]

  def add_module(self, shortnm, **kw):
    '''add_module(shortnm, **kw) -> module
    add module to pch2, area, and conver object, then update convert height.
    '''
    mod = self.g2area.add_module(shortnm, **kw)
    mod.horiz = self.g2module.horiz
    mod.vert = self.height
    self.height += mod.type.height
    self.g2modules.append(mod)
    return mod
  
  def del_module(self, module):
    '''del_module(module) -> None
    remove module from pch2, area, and convert object and update geometry.
    '''
    self.g2area.del_module(module)
    self.g2modules.remove(module)
    # update vertical position of all modules with the one removed
    def byvert(a, b):
      return cmp(a.vert, b.vert)
    self.g2modules.sort(byvert)
    for i in xrange(1, len(self.g2modules)):
      above = self.g2modules[i-1]
      self.g2modules[i].vert = above.vert + above.height

  def connect(self, source, dest):
    '''connect(source, dest) -> None
    create a cable connection from port source to port dest.
    '''
    self.g2area.connect(source, dest, g2cablecolors.blue) # change color later

  def domodule(self):
    '''domodule() -> none
    process module, setup paramaters, inputs, outputs.
    '''
    pass

  def dogroup(self, group):
    '''dogroup(group) -> None
    process group of modules once.
    '''
    pass

  def precables(self):
    '''precables() -> None
    process modules after after all domodules() are done
    but before cabling starts.
    '''

  def finalize(self):
    '''finailize() -> None
    after all cables, colors, repositioning, uprate,
    knobs, morphs, midiccs, and current notes.
    '''
    pass

  def domorphrange(self, paramindex, morphrange):
    return morphrange

  def reposition(self, convabove):
    '''reposition(convabove) -> None
    reposition module based on nm1's separation from module above.
    '''
    nmm, g2m = self.nmmodule, self.g2module
    if not convabove:
      g2m.vert += nmm.vert
      for g2mod in self.g2modules:
        g2mod.vert += nmm.vert
      return

    nma, g2a = convabove.nmmodule, convabove.g2module
    sep = nmm.vert - nma.vert - nma.type.height
    vert = g2a.vert + convabove.height + sep
    g2m.vert += vert
    for g2mod in self.g2modules:
      g2mod.vert += vert

  def emptyspace(self, column, rowstart, rowend):
    '''emptyspace(column, rowstart, rowend) -> True or False
    return True of no modules in column from rowstart to rowend.
    '''
    pass
    
  def insertcolumn(self, column):
    '''insertcolumn(column) -> None
    readjust horiz>=column for all modules in both g2area, nmarea
    '''
    for module in self.nmarea.modules:
      if module.horiz >= column:
        module.horiz += 1

    for module in self.g2area.modules:
      if module.horiz >= column:
        module.horiz += 1

def handlekbt(conv, input, kbt100, addalways=False):
  '''handlekbt(conv, input, kbt100, addalways=False) -> input
  '''
  nmm, g2m = conv.nmmodule, conv.g2module
  nmmp, g2mp = nmm.params, g2m.params

  kbt = getv(nmmp.Kbt)
  if addalways:
    pass
  elif kbt == 0:
    setv(conv.kbt, kbt)
    return None
  elif kbt == 64:
    setv(conv.kbt, kbt100)
    return None

  if not g2m.area.keyboard:
    g2m.area.keyboard = conv.add_module('Keyboard')
  keyboard = g2m.area.keyboard

  setv(conv.kbt, 0)
  mix21b = conv.add_module('Mix2-1B', name='Kbt')
  conv.connect(keyboard.outputs.Note, mix21b.inputs.In1)
  conv.connect(mix21b.inputs.In1, mix21b.inputs.In2)
  conv.connect(mix21b.outputs.Out, input)
  setv(mix21b.params.ExpLin, 1) # Lin
  setv(mix21b.params.Lev1, kbttable[kbt][0])
  setv(mix21b.params.Lev2, kbttable[kbt][1])
  return input
  
def handleoscmasterslv(conv, mst, left, bp, right, lev1, lev2, sub48=False):
  '''handleoscmasterslv(conv, msg, left, bp, right, lev1, lev2, sub48=False)
          -> output
  '''
  nmm, g2m = conv.nmmodule, conv.g2module

  conv.nonslaves = []
  conv.slaves = []
  slv = nmm.outputs.Slv
  if mst.type.shortnm != 'OscMaster' or len(slv.cables) == 0:
    return None

  out = mst.outputs.Out
  conv.slvoutput = out

  for input in slv.net.inputs:
    if input.rate != nm1conncolors.slave:
      conv.nonslaves.append(input)
    else:
      conv.slaves.append(input)

  if len(conv.nonslaves) == 0:
    return mst.outputs.Out

  if sub48:
    sub48 = conv.add_module('LevAdd', name='-48')
    setv(sub48.params.Level, 16)
    conv.connect(out, sub48.inputs.In)
    out = sub48.outputs.Out
    
  # Grey to Blue handling
  levscaler = conv.add_module('LevScaler', name='GreyIn')
  setv(levscaler.params.Kbt, 0)
  setv(levscaler.params.L, 16)
  setv(levscaler.params.BP, 127)
  setv(levscaler.params.R, 112)
  levscaler2 = conv.add_module('LevScaler', name='GreyIn')
  setv(levscaler2.params.Kbt, 0)
  setv(levscaler2.params.L, left)
  setv(levscaler2.params.BP, bp)
  setv(levscaler2.params.R, right)
  mix21b = conv.add_module('Mix2-1B')
  setv(mix21b.params.Lev1, lev1)
  setv(mix21b.params.Lev2, lev2)
  greyout = conv.add_module('LevAmp', name='GreyOut')
  setv(greyout.params.Gain, 127)
  conv.connect(out, levscaler.inputs.Note)
  conv.connect(levscaler.inputs.Note, levscaler2.inputs.Note)
  conv.connect(levscaler.outputs.Level, mix21b.inputs.In1)
  conv.connect(levscaler.outputs.Level, levscaler2.inputs.In)
  conv.connect(levscaler2.outputs.Out, mix21b.inputs.In2)
  conv.connect(mix21b.outputs.Out, greyout.inputs.In)

  return greyout.outputs.Out

def doslvcables(conv):
  '''doslvcables(conv) -> None
  '''
  if not hasattr(conv, 'slvoutput'):
    return
  for input in conv.slaves:
    conv.nmmodule.area.removeconnector(input)
    conv.connect(conv.slvoutput, input.module.conv.inputs[input.index])

