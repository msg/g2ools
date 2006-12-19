#
# env.py - Env tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvADSR_Env(Convert):
  maing2module = 'EnvADSR'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    # fix Attack, Decay, Release
    cpv(g2mp.Attack,nmmp.Attack)
    cpv(g2mp.Decay,nmmp.Decay)
    cpv(g2mp.Sustain,nmmp.Sustain)
    cpv(g2mp.Release,nmmp.Release)
    cpv(g2mp.Shape,nmmp.AttackShape)
    setv(g2mp.OutputType,[0,3][getv(nmmp.Invert)])

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.Env,g2m.outputs.Out]
      
    # build input array that nmps nm1 inputs
    #                                            vvvv No Retrig
    self.inputs = [g2m.inputs.In,g2m.inputs.Gate,None,g2m.inputs.AM]

class ConvAD_Env(Convert):
  maing2module = 'EnvADR'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.Attack,nmmp.Attack)
    cpv(g2mp.Release,nmmp.Decay)
    cpv(g2mp.TG,nmmp.Gate)

    self.outputs = [g2m.outputs.Env,g2m.outputs.Out]

    self.inputs = [g2m.inputs.Gate,g2m.inputs.In,g2m.inputs.AM]


