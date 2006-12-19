#
# filter.py - Filter tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvFilterC(Convert):
  maing2module = 'FltMulti'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    cpv(g2mp.Freq,nmmp.Freq)
    cpv(g2mp.Res,nmmp.Resonance)
    cpv(g2mp.GC,nmmp.GainControl)

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.LP,g2m.outputs.BP,g2m.outputs.HP]
      
    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.In]

class ConvFilterD(Convert):
  maing2module = 'FltMulti'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    cpv(g2mp.Freq,nmmp.Freq)
    cpv(g2mp.Res,nmmp.Resonance)
    #cpv(g2mp.GC,nmmp.GainControl)
    cpv(g2mp.PitchMod,nmmp.FreqMod)

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.LP,g2m.outputs.BP,g2m.outputs.HP]
      
    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.PitchVar, g2m.inputs.In]

class ConvFilterE(Convert):
  maing2module = 'FltNord'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    cpv(g2mp.Freq,nmmp.Freq)
    cpv(g2mp.Res,nmmp.Resonance)
    #cpv(g2mp.GC,nmmp.GainControl)
    cpv(g2mp.PitchMod,nmmp.FreqMod)

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.LP,g2m.outputs.BP,g2m.outputs.HP]
      
    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.PitchVar, g2m.inputs.In]

