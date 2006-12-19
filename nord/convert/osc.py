#
# osc.py - Osc tab convertion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvMasterOsc(Convert):
  maing2module = 'OscMaster'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'MasterOsc not implemented'

class ConvOscA(Convert):
  maing2module = 'OscB'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    p1,p2 = dualpitchmod(nmm,g2m,self)

    # handle parameters
    cpv(g2mp.Waveform,nmmp.Waveform)
    cpv(g2mp.FreqCoarse,nmmp.FreqCoarse)
    cpv(g2mp.FreqFine,nmmp.FreqFine)
    cpv(g2mp.FmAmount,nmmp.FmaMod)
    # NOTE: since shape can be 0% - 100%, a LevConv could be used
    #       to get the actual waveform, if necessary.
    setv(g2mp.Shape,abs(getv(nmmp.PulseWidth)-64)*2)
    cpv(g2mp.ShapeMod,nmmp.PwMod)
    setv(g2mp.Active,1-getv(nmmp.Mute))

    # build output array that maps nm1 outputs
    #                                    vvvv no Slv
    self.outputs = [g2m.outputs.Out,None]
      
    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.Sync,g2m.inputs.FmMod,
                   p1, p2,
                   g2m.inputs.ShapeMod]

class ConvOscB(Convert):
  maing2module = 'OscB'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    p1,p2 = dualpitchmod(nmm,g2m,self)

    # update parameters
    cpv(g2mp.Waveform,nmmp.Waveform)
    cpv(g2mp.FreqCoarse,nmmp.FreqCoarse)
    cpv(g2mp.FreqFine,nmmp.FreqFine)
    # handle KBT later = nmm.params.FreqKbt)
    cpv(g2mp.FmAmount,nmmp.FmaMod)
    cpv(g2mp.ShapeMod,nmmp.Pwidth)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2m.params.FreqMode,nmm.modes[0]]

    # build output array that maps nm1 outputs
    #                               vvvv no Slv
    self.outputs = [g2m.outputs.Out,None]
      
    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.FmMod,
                   p1, p2,
                   g2m.inputs.ShapeMod]

class ConvOscC(Convert):
  maing2module = 'OscC'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # make OscC's waveform a sine
    g2m.modes.Waveform.value = 0

    # update parameters
    cpv(g2mp.FreqCoarse,nmmp.FreqCoarse)
    cpv(g2mp.FreqFine,nmmp.FreqFine)
    # handle KBT later = nmmp.FreqKbt)
    cpv(g2mp.PitchMod,nmmp.FreqMod)
    cpv(g2mp.FmAmount,nmmp.Fma)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2mp.FreqMode,nmm.modes[0])
    
    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.Out,None]
      
    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.FmMod,
                   g2m.inputs.Pitch,
                   None] # noe Am input

class ConvSpectralOsc(Convert):
  maing2module = 'OscShpA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'ConvSpectialOsc not implemented'

class ConvFormantOsc(Convert):
  maing2module = 'OscShpA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'ConvFormantOsc not implemented'

class ConvOscSlvA(Convert):
  maing2module = 'OscB'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    cpv(g2mp.Waveform,nmmp.Waveform)
    cpv(g2mp.FreqCoarse,nmmp.DetuneCoarse)
    cpv(g2mp.FreqFine,nmmp.DetuneFine)
    cpv(g2mp.FmAmount,nmmp.FmaMod)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2mp.FreqMode,nmm.modes[0])

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.Out]
      
    # build input array that nmps nm1 inputs
    self.inputs = [None, # no Mst input
                   g2m.inputs.FmMod,
                   None, # no AM input
                   g2m.inputs.Sync]

    # need to search Mst input for Slv output
    # this way the connection can be removed
    # each Conv.. object should be responsible
    # it's own connect.  I need to add code to
    # remove cables within the NM1 patch.  It's
    # easier to handle it here.  Plus I want thte
    # converter to fail when there is an unknown
    # connection.

class ConvOscSlvB(Convert):
  maing2module = 'OscB'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters 
    setv(g2mp.Waveform,3) # square
    cpv(g2mp.FreqCoarse,nmmp.DetuneCoarse)
    cpv(g2mp.FreqFine,nmmp.DetuneFine)
    cpv(g2mp.ShapeMod,nmmp.PwMod)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2mp.FreqMode,nmm.modes[0])

    # NOTE: since shape can be 0% - 100%, a LevConv could be used
    #       to get the actual waveform, if necessary.
    setv(g2m.params.Shape,abs(getv(nmm.params.PulseWidth)-64)*2)
    cpv(g2mp.ShapeMod,nmmp.PwMod)

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.Out]
      
    # build input array that nmps nm1 inputs
    self.inputsi = [None, # no Mst
                    g2m.inputs.ShapeMod]

class ConvOscSlvC(Convert):
  maing2module = 'OscC'
  waveform = 2 # saw

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    setv(g2mp.Waveform,self.waveform)
    cpv(g2mp.FreqCoarse,nmmp.DetuneCoarse)
    cpv(g2mp.FreqFine,nmmp.DetuneFine)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    cpv(g2mp.FmAmount,nmmp.FmaMod)
    #setv(g2mp.FreqMode,nmm.modes[0])

    # build output array that maps nm1 outputs
    self.outputs = [g2m.outputs.Out]
      
    # build input array that maps nm1 inputs
    self.inputs = [None, # no Mst
                   g2m.inputs.FmMod]

class ConvOscSlvD(ConvOscSlvC):
  waveform = 1 # tri

class ConvOscSlvE(ConvOscSlvC):
  waveform = 0 # sine
   
  def domodule(self):
    ConvOscSlvC.domodule(self)

    # replace input array that maps nm1 inputs
    self.inputs = [None, # no Mst
                   g2m.inputs.FmMod,
                   None ] # no AM
 
class ConvOscSineBank(Convert):
  maing2module = 'NameBar'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'ConvOscSineBank not implemented'

class ConvOscSlvFM(ConvOscSlvC):
  waveform = 0 # sine
  def domodule(self):
    ConvOscSlvC.domodule(self)

    # replace input array that maps nm1 inputs
    self.inputs = [None, # no Mst
                   g2m.inputs.FmMod,
                   g2m.inputs.Sync ]
 
class ConvNoise(Convert):
  maing2module = 'Noise'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.Color, nmmp.Color)

    self.outputs = [g2m.outputs.Out]

class ConvPercOsc(Convert):
  maing2module = 'OscPerc'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.FreqCoarse,nmmp.Pitch)
    cpv(g2mp.FreqFine,nmmp.PitchFine)
    cpv(g2mp.Click,nmmp.Click)
    cpv(g2mp.Decay,nmmp.Decay)
    cpv(g2mp.Punch,nmmp.Punch)
    cpv(g2mp.PitchMod,nmmp.PitchMod)
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.outputs = [g2m.outputs.Out]

    #                               vvvv no AM input
    self.inputs = [g2m.inputs.Trig, None, g2m.inputs.PitchVar]

class ConvDrumSynth(Convert):
  maing2module = 'DrumSynth'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # parameters are exactly the same
    for i in range(len(nmm.params)):
      cpv(g2mp[i],nmmp[i])

    self.outputs = [g2m.outputs.Out]

    self.inputs = [ g2m.inputs.Trig,g2m.inputs.Vel,g2m.inputs.PitchVar ]

