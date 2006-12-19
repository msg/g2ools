#
# lfo.py - Lfo tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvLFOA(Convert):
  maing2module = 'LfoB'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.Rate,nmmp.Rate)
    cpv(g2mp.Range,nmmp.Range)
    setv(g2mp.Waveform,[0,1,2,2,3][getv(nmmp.Waveform)])
    cpv(g2mp.RateMod,nmmp.RateMod)
    cpv(g2mp.PolyMono,nmmp.Mono)
    # deal with RateKbt later
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.outputs = [ None, g2m.inputs.Out ] # no Slv

    self.inputs = [ g2m.inputs.Rate, g2m.inputs.Rst ]

class ConvLFOB(Convert):
  maing2module = 'LfoShpA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,5)
    cpv(g2mp.Rate,nmmp.Rate)
    cpv(g2mp.Range,nmmp.Range)
    cpv(g2mp.Phase,nmmp.Phase)
    cpv(g2mp.RateMod,nmmp.RateMod)
    cpv(g2mp.PolyMono,nmmp.Mono)
    # deal with RateKbt later
    cpv(g2mp.PhaseMod,nmmp.PwMod)
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.outputs = [ g2m.inputs.Out, None ] # no Slv

    self.inputs = [ g2m.inputs.Rate, g2m.inputs.Rst, g2m.inputs.ShapeMod  ]

class ConvLFOC(Convert):
  maing2module = 'LfoA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.Rate,nmmp.Rate)
    cpv(g2mp.Range,nmmp.Range)
    cpv(g2mp.Waveform,nmmp.Waveform)
    cpv(g2mp.RateMod,nmmp.RateMod)

    self.outputs = [ g2m.outputs.Out, None ] # no Slv

    self.inputs = [ g2m.inputs.RateVar ]

class ConvLFOSlvA(Convert):
  maing2module = 'LfoB'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.Rate,nmmp.Rate)
    cpv(g2mp.Phase,nmmp.Phase)
    setv(g2mp.Waveform,[0,1,2,2,3][getv(nmmp.Waveform)])
    cpv(g2mp.PolyMono,nmmp.Mono)
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.outputs = [g2m.outputs.Out]

    self.inputs = [None,g2m.inputs.Rst]

class ConvLFOSlvB(Convert):
  maing2module = 'LfoC'
  waveform = 2

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.Rate,nmmp.Rate)
    g2m.modes.Waveform.value = self.waveform

    self.outputs = [g2m.outputs.Out]

    self.inputs = [None]

class ConvLFOSlvC(ConvLFOSlvB):
  waveform = 0

class ConvLFOSlvD(ConvLFOSlvB):
  waveform = 3

class ConvLFOSlvE(ConvLFOSlvC):
  waveform = 1

class ConvClkGen(Convert):
  maing2module = 'ClkGen'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.Tempo,nmmp.Rate)
    cpv(g2mp.Active,nmmp.__dict__['On/Off'])

    self.outputs = [ g2mp.outputs.__dict__['1/96'],
                     g2mp.outputs.__dict__['1/16'],
                     None, # no Slv
                     g2mp.outputs.Sync ]

    self.inputs = [ g2mp.inputs.Rst ]

class ConvClkRndGen(Convert):
  maing2module = 'RndClkA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    cpv(g2mp.PolyMono,nmmp.Mono)
    # deal with nmmp.Color later

    self.outputs = [g2m.outputs.Out]

    self.inputs = [g2m.inputs.Clk]

class ConvRndStepGen(ConvLFOSlvB):
  waveform = 4

class ConvRandomGen(ConvLFOSlvB):
  waveform = 5

class ConvRndPulseGen(ConvLFOSlvB):
  waveform = 7

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    ConvLFOSlvB.domodule(self)
    self.outputs = [g2m.outputs.Out]

class ConvPatternGen(Convert):
  maing2module = 'RndClkA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    self.g2area.connect(g2m.inputs.A,g2m.inputs.B,1) 
    cpv(g2mp.PatternA,nmmp.Pattern)
    cpv(g2mp.PatternB,nmmp.Pattern)
    cpv(g2mp.LoopCount,nmmp.Step)
    # deal with nmmp.LowDelta later

    self.outputs = [g2m.outputs.Out]
    
    self.inputs = [g2m.inputs.Clk,g2m.inputs.Rst]

