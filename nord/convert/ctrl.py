#
# ctrl.py - Ctrl tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvConstant(Convert):
  maing2module = 'Constant'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2m.params.Level,nmm.params.Value)
    cpv(g2m.params.BipUni,nmm.params.Unipolar)

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.Out]
      
