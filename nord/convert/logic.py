#
# logic.py - Logic tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvPosEdgeDly(Convert):
  maing2module = 'Delay'
  parammap = ['Time']
  inputmap = ['In']
  outputmap = ['Out']
  delaymode = 0

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    g2m.modes.DelayMode.value = self.delaymode

class ConvNegEdgeDly(ConvPosEdgeDly):
  delaymode = 1

class ConvPulse(Convert):
  maing2module = 'Pulse'
  parammap = ['Time']
  inputmap = ['In']
  outputmap = ['Out']

class ConvLogicDelay(ConvPosEdgeDly):
  delaymode = 2

class ConvLogicInv(Convert):
  maing2module = 'Invert'
  inputmap = ['In2']
  outputmap = ['Out2']

class ConvLogicProc(Convert):
  maing2module = 'Gate'
  inputmap = ['In2_1','In2_2']
  outputmap = ['Out2']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    g2m.modes.GateMode1.value = [0,2,4][getv(nmmp.Mode)]

class ConvCompareLev(Convert):
  maing2module = 'CompLev'
  parammap = [['C','Level']]
  inputmap = ['In']
  outputmap = ['Out']

class ConvCompareAB(Convert):
  maing2module = 'CompSig'
  inputmap = ['A','B']
  outputmap = ['Out']

class ConvClkDiv(Convert):
  maing2module = 'ClkDiv'
  parammap = ['Divider']
  inputmap = ['Clk','Rst']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    g2m.modes.DivMode.value = 1

class ConvClkDivFix(Convert):
  maing2module = 'ClkDiv'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'ClkDivFix not implemented'

