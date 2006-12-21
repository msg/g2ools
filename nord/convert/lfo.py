#
# lfo.py - Lfo tab conversion objects
#
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from convert import *

class ConvLFOA(Convert):
  maing2module = 'LfoB'
  parammap = ['Rate','Range','RateMod',['PolyMono','Mono']]
  inputmap = ['Rate','Rst']
  outputmap = [None,'Out'] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Waveform,[0,1,2,2,3][getv(nmmp.Waveform)])
    # deal with RateKbt later
    setv(g2mp.Active,1-getv(nmmp.Mute))

class ConvLFOB(Convert):
  maing2module = 'LfoShpA'
  parammap = ['Rate','Range','Phase','RateMod',['PolyMono','Mono'],
              ['Shape','Pw'],
              ['PhaseMod','PwMod']]
  inputmap = ['Rate','Rst','ShapeMod']
  outputmap = ['Out',None] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,5)
    # deal with RateKbt later
    cpv(g2mp.PhaseMod,nmmp.PwMod)

class ConvLFOC(Convert):
  maing2module = 'LfoA'
  parammap = ['Rate','Range','RateMod']
  inputmap = ['RateVar']
  outputmap = ['Out',None] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,[0,1,2,2,3][getv(nmmp.Waveform)])

class ConvLFOSlvA(Convert):
  maing2module = 'LfoB'
  parammap = ['Rate','Phase',['PolyMono','Mono']]
  inputmap = [None,'Rst'] # no Mst
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    waveform = getv(nmmp.Waveform)
    setv(g2mp.Waveform,[0,1,2,2,3][waveform])
    if waveform == 2:
      setv(g2mp.OutputType,1)
    setv(g2mp.Active,1-getv(nmmp.Mute))

class ConvLFOSlvB(Convert):
  maing2module = 'LfoC'
  waveform = 2
  parammap = ['Rate']
  inputmap = [None] # no Mst
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    g2m.modes.Waveform.value = self.waveform

class ConvLFOSlvC(ConvLFOSlvB):
  waveform = 0

class ConvLFOSlvD(ConvLFOSlvB):
  waveform = 3

class ConvLFOSlvE(ConvLFOSlvC):
  waveform = 1

class ConvClkGen(Convert):
  maing2module = 'ClkGen'
  parammap = [['Tempo','Rate'],['Active','On/Off']]
  inputmap = ['Rst']
  outputmap = ['1/96','1/16',None,'Sync'] # n oSlv

class ConvClkRndGen(Convert):
  maing2module = 'RndClkA'
  parammap = [['PolyMono','Mono']]
  inputmap = ['Clk']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # deal with nmmp.Color later

class ConvRndStepGen(ConvLFOSlvB):
  waveform = 4

class ConvRandomGen(ConvLFOSlvB):
  waveform = 5

class ConvRndPulseGen(Convert):
  maing2module = 'RndTrig'
  parampam = [['Prob','Density']]
  outputmap = ['Out']

class ConvPatternGen(Convert):
  maing2module = 'RndPattern'
  parammap = [['PatternA','Pattern'],['PatternB','Pattern'],
              ['LoopCount','Step']]
  inputmap = ['Clk','Rst','A']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # PatternA and PatternB receive same input
    self.g2area.connect(g2m.inputs.A,g2m.inputs.B,g2cablecolors.blue) 
    # deal with nmmp.LowDelta later

