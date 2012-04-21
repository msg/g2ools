#
# logic.py - Logic tab conversion objects
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
from nord.convert.table import logicdel
from nord.g2.colors import g2conncolors

class ConvPosEdgeDly(Convert):
  maing2module = 'Delay'
  parammap = ['Time']
  inputmap = ['In']
  outputmap = ['Out']
  mode = 0

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    setv(g2mp.Range, 1) # Lo
    setv(g2mp.Time, logicdel[getv(nmmp.Time)])
    g2m.modes.Mode.value = self.mode

class ConvNegEdgeDly(ConvPosEdgeDly):
  mode = 1

class ConvPulse(ConvPosEdgeDly):
  maing2module = 'Pulse'
  inputmap = ['In']
  outputmap = ['Out']
  mode = 0

class ConvLogicDelay(ConvPosEdgeDly):
  mode = 2

class ConvLogicInv(Convert):
  maing2module = 'Invert'
  inputmap = ['In2']
  outputmap = ['Out2']

class ConvLogicProc(Convert):
  maing2module = 'Gate'
  parammap = [None]
  inputmap = ['In2_1', 'In2_2']
  outputmap = ['Out2']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    g2m.modes.GateMode2.value = [0, 2, 4][getv(nmmp.Mode)]

class ConvCompareLev(Convert):
  maing2module = 'CompLev'
  parammap = [['C', 'Level']]
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    self.g2module.inputs.In.rate = g2conncolors.blue

class ConvCompareAB(Convert):
  maing2module = 'CompSig'
  inputmap = ['A', 'B']
  outputmap = ['Out']

  def domodule(self):
    self.g2module.inputs.A.rate = g2conncolors.blue
    self.g2module.inputs.B.rate = g2conncolors.blue

class ConvClkDiv(Convert):
  maing2module = 'ClkDiv'
  parammap = ['Divider']
  inputmap = ['Clk', 'Rst']
  outputmap = ['Out', None, None]

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    g2m.modes.DivMode.value = 1

class ConvClkDivFix(Convert):
  maing2module = 'ClkDiv'
  inputmap = ['Clk', 'Rst']
  outputmap = [None, None, None]  # 16, T8, 8

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    oclks = [[5, '16', 0], [7, 'T8', 1], [11, '8', 2]]
    clks = oclks[:]
    while len(clks):
      clk = clks.pop(0)
      if len(getattr(nmm.outputs, clk[1]).cables) != 0:
        break
    if len(clks) == 0:
      clk = oclks[0]

    g2m.modes.DivMode.value = 1
    setv(g2mp.Divider, clk[0])
    g2m.name = clk[1]
    self.outputs[clk[2]] = g2m.outputs.Out

    rst, midiclk = g2m.inputs.Rst, g2m.inputs.Clk
    for div, nm, out in clks:
      if len(getattr(nmm.outputs, nm).cables) == 0:
        continue
      clk = self.add_module('ClkDiv', name=nm)
      clk.modes.DivMode.value = 1
      setv(clk.params.Divider, div)
      self.connect(rst, clk.inputs.Rst)
      self.connect(midiclk, clk.inputs.Clk)
      rst, midiclk = clk.inputs.Rst, clk.inputs.Clk
      self.outputs[out] = clk.outputs.Out

