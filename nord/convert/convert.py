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
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from units import *

def setv(g2param,val):
  g2param.variations = [ val for variation in range(9) ]

def getv(nmparam):
  return nmparam.variations[0]

def setav(g2param,array):
  g2param.variations = array[:9]

def cpv(g2param,nmparam):
  g2param.variations = nmparam.variations[:]

# updatevals - parameters set from constructor, this changes the times
#              based on the convertion tables in ./units.py.
def updatevals(g2mp,params,nm1tab,g2tab):
  for param in params:
    midival = getv(getattr(g2mp,param))
    newmidival = nm2g2val(midival,nm1tab,g2tab)
    setv(getattr(g2mp,param),newmidival)

class Convert:
  def __init__(self, nmarea, g2area, nmmodule):
    self.nmarea = nmarea
    self.g2area = g2area
    nmm = self.nmmodule = nmmodule
    # use for cabling
    for output in nmmodule.outputs:
      output.conv = self 
    for input in nmmodule.inputs:
      input.conv = self 
    self.nmmodule.conv = self # to get back here when needed (cables)
    self.g2modules = []
    self.outputs = []
    self.inputs = []

    g2m = self.g2module = g2area.addmodule(g2name[self.maing2module])
    g2m.name = nmm.name
    self.horiz = g2m.horiz = nmm.horiz
    #self.vert = g2m.vert = nmm.vert # calculated later
    self.height = g2m.type.height

    if hasattr(self,'parammap'):
      for param in self.parammap:
        if type(param) == type(''):
          cpv(getattr(g2m.params,param),getattr(nmm.params,param))
        elif type(param) == type([]):
          cpv(getattr(g2m.params,param[0]),getattr(nmm.params,param[1]))
        else:
          raise 'Invalid param %r in parammap' % (param)

    if hasattr(self,'inputmap'):
      for input in self.inputmap:
        if input:
          input = getattr(g2m.inputs,input)
        self.inputs.append(input)
          
    if hasattr(self,'outputmap'):
      for output in self.outputmap:
        if output:
          output = getattr(g2m.outputs,output)
        self.outputs.append(output)

  # domodule - process module, setup paramaters, inputs, outputs
  def domodule(self):
    pass

  # reposition module based on nm1's separation from module above
  def reposition(self, convabove):
    nmm,g2m = self.nmmodule,self.g2module
    if not convabove:
      g2m.vert = nmm.vert
      return

    nma,g2a = convabove.nmmodule,convabove.g2module
    sep = nmm.vert - nma.vert - nma.type.height
    g2m.vert = g2a.vert + convabove.height + sep
    for g2mod in self.g2modules:
      g2mod.vert += g2m.vert

