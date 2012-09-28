#
# inout.py - In/Out tab conversion objects
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
from nord.convert import Convert
from nord.convert.table import modtable

class ConvKeyboard(Convert):
  maing2module = 'Keyboard'
  outputmap = ['Pitch', 'Gate', 'Lin', 'Release']
  def domodule(self):
    self.g2module.area.keyboard = self.g2module
  def finalize(self):
    noconnections = True
    for output in ['Pitch', 'Note', 'Gate', 'Lin', 'Exp', 'Release']:
      if getattr(self.g2module.outputs, output).net:
        noconnections = False
    if noconnections:
      self.g2module.area.del_module(self.g2module)

class ConvKeyboardPatch(Convert):
  maing2module = 'MonoKey'
  outputmap = ['Pitch', 'Gate', 'Vel', 'Vel'] # just use on vel for off vel

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    setv(g2mp.Mode, 0)

class ConvMIDIGlobal(Convert):
  maing2module = 'ClkGen'
  outputmap = ['1/96', 'Sync', 'ClkActive']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    setv(g2mp.Source, 1) # Master

class ConvAudioIn(Convert):
  maing2module = '2-In'
  outputmap = ['OutL', 'OutR']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module

class ConvPolyAreaIn(Convert):
  maing2module = 'Fx-In'
  parammap = [['Pad', '+6Db']]
  outputmap = ['OutL', 'OutR']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.Pad, [2, 1][getv(getattr(nmmp, '+6Db'))])
    lboost = self.add_module('LevAmp', name='L-Boost')
    setv(lboost.params.Type, 0) # Lin
    setv(lboost.params.Gain, 96) # x2.00
    self.connect(g2m.outputs.OutL, lboost.inputs.In)
    self.outputs[0] = lboost.outputs.Out

    rboost = self.add_module('LevAmp', name='R-Boost')
    setv(rboost.params.Type, 0) # Lin
    setv(rboost.params.Gain, 96) # x2.00
    self.connect(g2m.outputs.OutR, rboost.inputs.In)
    self.outputs[1] = rboost.outputs.Out

def isxoutput(module):
  return module.type.id in [ 3, 4, 5]

class Conv1Output(Convert):
  maing2module = 'Mix1-1A'
  parammap = [None, None, None] # Level, Destination, Mute
  inputmap = ['']

  def __init__(self, nmarea, g2area, nmmodule, options):
    lev = nmmodule.params.Level
    if getv(lev) == 127 and not lev.knob and not lev.morph and not lev.ctrl:
      self.maing2module = '2-Out'
    elif len(filter(isxoutput, nmarea.modules)) < 2:
      self.maing2module = '2-Out'
    else:
      self.inputmap = ['In']
    Convert.__init__(self, nmarea, g2area, nmmodule, options)

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    if self.maing2module == 'Mix1-1A':
      setv(g2mp.On, 1)
      setv(g2mp.ExpLin, 2)
      setv(g2mp.Lev, modtable[getv(nmmp.Level)][0])
      out2 = self.add_module('2-Out')
      lev = g2m.params.Lev
    else:
      out2 = g2m
      lev = None

    dest = getv(nmmp.Destination)
    setv(out2.params.Destination, dest/2)
    setv(out2.params.Active, 1-getv(nmmp.Mute))

    inp = [out2.inputs.InL, out2.inputs.InR][dest % 2]
    if self.maing2module == 'Mix1-1A':
      self.connect(g2m.outputs.Out, inp)
    else:
      self.inputs = [inp]

    self.params = [lev, out2.params.Destination, out2.params.Active]

class Conv2Output(Convert):
  maing2module = 'Mix1-1S'
  parammap = [None, None, None] # Level, Destination, Mute
  inputmap = ['InL', 'InR']

  def __init__(self, nmarea, g2area, nmmodule, options):
    lev = nmmodule.params.Level
    if getv(lev) == 127 and not lev.knob and not lev.morph and not lev.ctrl:
      self.maing2module = '2-Out'
    if len(filter(isxoutput, nmarea.modules)) < 2:
      self.maing2module = '2-Out'
    Convert.__init__(self, nmarea, g2area, nmmodule, options)

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    if self.maing2module == 'Mix1-1S':
      setv(g2mp.Lev, modtable[getv(nmmp.Level)][0])
      setv(g2mp.On, 1)
      out2 = self.add_module('2-Out')
      self.connect(g2m.outputs.OutL, out2.inputs.InL)
      self.connect(g2m.outputs.OutR, out2.inputs.InR)
      lev = g2mp.Lev
    else:
      out2 = g2m
      lev = None

    setv(out2.params.Destination, getv(nmmp.Destination))
    setv(out2.params.Active, 1-getv(nmmp.Mute))

    self.params = [lev, out2.params.Destination, out2.params.Active]

class Conv4Output(Convert):
  maing2module = '4-Out'
  parammap = [None]
  inputmap = ['In1', 'In2', 'In3', 'In4']
  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    #setv(self.g2area.patch.settings.patchvol, modtable[getv(nmmp.Level)][0])

class ConvNoteDetect(Convert):
  maing2module = 'NoteDet'
  parammap = ['Note']
  outputmap = ['Gate', 'Vel', 'RelVel']

class ConvKeyboardSplit(Convert):
  maing2module = 'Name'
  #          Lower, Upper
  parammap = [None, None]

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    g2m.name = 'KbdSplit'

    # now lets create the structure
    struct = [ ['Constant', 'Upper'],
               ['CompLev', 'Lower'],
               ['CompSig', '<=Upper'],
               ['Gate', 'Gate'], ]
    for mod, nm in struct:
      self.add_module(mod, name=nm)

    u, l, lu, g = self.g2modules

    setv(u.params.Level, getv(nmmp.Upper))
    setv(l.params.C, getv(nmmp.Lower))

    self.connect(u.outputs.Out, lu.inputs.A)
    self.connect(l.inputs.In, lu.inputs.B)
    self.connect(l.outputs.Out, g.inputs.In1_1)
    self.connect(lu.outputs.Out, g.inputs.In1_2)
    self.connect(g.outputs.Out1, g.inputs.In2_2)

    gout = g.outputs.Out2

    nout = None
    if len(nmm.outputs.Note.cables):
      n = self.add_module('DlyClock', name='Note')
      self.connect(gout, n.inputs.Clk)
      self.connect(lu.inputs.B, n.inputs.In)
      gout = n.inputs.Clk
      nout = n.outputs.Out

    vin = vout = None
    if len(nmm.outputs.Vel.cables) or len(nmm.inputs.Vel.cables):
      v = self.add_module('DlyClock', name='Vel')
      self.connect(gout, v.inputs.Clk)
      vin = v.inputs.In
      vout = v.outputs.Out

    self.params = [l.params.C, u.params.Level]
    self.outputs = [nout, g.outputs.Out2, vout]
    self.inputs = [l.inputs.In, g.inputs.In2_1, vin]

