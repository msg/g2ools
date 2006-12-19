#
# mixer.py - Mixer tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvMixer(Convert):
  maing2module = 'Mix4-1B'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    cpv(g2mp.Lev1,nmmp.Lev1)
    cpv(g2mp.Lev2,nmmp.Lev2)
    cpv(g2mp.Lev3,nmmp.Lev3)

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.Out]
      
    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.In1, g2m.inputs.In2, g2m.inputs.In3]

