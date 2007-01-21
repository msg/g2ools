#
# lfo.py - Lfo tab conversion objects
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
from nord.utils import *
from nord.nm1.colors import nm1cablecolors, nm1conncolors
from convert import *
from table import *

def handleslv(conv,ratemodin,ratemodparam):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params, g2m.params

  slv,kbt=None,g2m.inputs.Rate

  if len(nmm.outputs.Slv.cables):
    oscmaster = conv.addmodule('OscMaster')
    setv(g2mp.Rate,64)
    setv(oscmaster.params.Kbt,0) # Off
    setv(oscmaster.params.FreqCoarse,getv(nmmp.Rate))
    #setv(oscmaster.params.PitchMod,modtable[getv(nmmp.RateMod)][0])
    conv.connect(oscmaster.outputs.Out,g2m.inputs.Rate)
    ratemodin = oscmaster.inputs.PitchVar
    ratemodparam = oscmaster.params.PitchMod
    slv = g2m.inputs.Rate
    kbt = oscmaster.inputs.Pitch
    conv.kbt = oscmaster.params.Kbt

    if getv(nmmp.Range) == 1: # Lo
      slv = handleoscmasterslv(conv,oscmaster,64,40,50,103,41,True)
    else:
      slv = handleoscmasterslv(conv,oscmaster,76,64,52,104,35,False)

  # add fine tuning 
  if len(nmm.inputs.Rate.cables):
    mod = getv(nmmp.RateMod)
    if mod == 0 or mod == 127:
      setv(ratemodparam,mod)
    else:
      setv(ratemodparam,modtable[mod][0])
      adj = conv.addmodule('Mix2-1B',name='PitchAdj')
      conv.connect(adj.outputs.Out,ratemodin)
      conv.connect(adj.inputs.Chain,adj.inputs.In1)
      conv.connect(adj.inputs.In1,adj.inputs.In2)
      setv(adj.params.Inv1,1)
      setv(adj.params.Lev1,modtable[mod][1])
      setv(adj.params.Lev2,modtable[mod][2])
      ratemodin = adj.inputs.Chain

  return ratemodin,ratemodparam,slv,kbt

def postmst(conv,mstindex):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params, g2m.params

  mstin = nmm.inputs.Mst
  if not len(mstin.cables):
    return

  if not mstin.net.output:
    return

  mstconv = mstin.net.output.module.conv
  mst = mstconv.g2module
  if hasattr(mst.params,'PolyMono'):
    setv(g2mp.PolyMono,getv(mst.params.PolyMono))
  if hasattr(mst.params,'Kbt') and hasattr(g2mp,'Kbt'):
    setv(g2mp.Kbt,getv(mst.params.Kbt))

  if mstin.net.output.rate != nm1conncolors.slave:
    oscc = conv.addmodule('OscC',name='')
    setv(oscc.params.FreqCoarse,0)
    setv(oscc.params.FmAmount,79)
    setv(oscc.params.Kbt,0)
    pout = conv.addmodule('ZeroCnt',name='')
    conv.connect(oscc.outputs.Out,pout.inputs.In)
    conv.connect(pout.outputs.Out,g2m.inputs.Rate)
    setv(g2mp.Range,2)
    conv.inputs[mstindex] = oscc.inputs.FmMod
    return

  if isnm1osc(mst):
    setv(g2mp.Range,2)
  elif hasattr(mst.params,'Range'):
    setv(g2mp.Range,getv(mst.params.Range))
  else:
    setv(g2mp.Range,1)

class ConvLFOA(Convert):
  maing2module = 'LfoB'
  parammap = ['Rate','Range','Waveform','RateMod',['PolyMono','Mono'],
              None,'Phase',['Active','Mute']]
  inputmap = ['Rate','Rst']
  outputmap = [None,'Out'] # Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    waveform = getv(nmmp.Waveform)
    setv(g2mp.Waveform,[0,1,2,2,3][waveform])
    if waveform != 3:
      setv(g2mp.OutputType,5) # BipInv
    else:
      # 180 phase
      setv(g2mp.Phase,(range(64,128)+range(64))[getv(nmmp.Phase)])
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.kbt = g2m.params.Kbt
    # update Rate input, Slv Output
    ratemodin,rateparam,slv,kbt = handleslv(self,g2m.inputs.RateVar,g2mp.Rate)
    self.inputs[0],self.outputs[0],kbt = ratemodin,slv,kbt
    self.kbtout = handlekbt(self,kbt,4,False)

  def precables(self):
    doslvcables(self)

class ConvLFOB(Convert):
  maing2module = 'LfoShpA'
  parammap = ['Rate','Range','Phase','RateMod',['PolyMono','Mono'],
              None,['PhaseMod','PwMod'],['Shape','Pw']]
  inputmap = ['Rate','Rst','ShapeMod']
  outputmap = ['Out',None] # Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,5)
    setv(g2mp.OutputType,5) # BipInv
    setv(g2mp.PhaseMod,getv(nmmp.PwMod))

    self.kbt = g2m.params.Kbt

    ratemodin,rateparam,slv,kbt = handleslv(self,g2m.inputs.RateVar,g2mp.Rate)
    self.inputs[0],self.outputs[1],kbt = ratemodin,slv,kbt
    self.kbtout = handlekbt(self,kbt,4,False)

  def precables(self):
    doslvcables(self)

class ConvLFOC(Convert):
  maing2module = 'LfoA'
  parammap = ['Rate','Range','Waveform','RateMod',['PolyMono','Mono'],
              ['Active','Mute']]
  inputmap = ['RateVar']
  outputmap = ['Out',None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    waveform = getv(nmmp.Waveform)
    setv(g2mp.Waveform,[0,1,2,2,3][waveform])
    if waveform != 3:
      setv(g2mp.OutputType,5) # BipInv
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.kbt = g2m.params.Kbt
    ratemodin,rateparam,slv,kbt = handleslv(self,g2m.inputs.RateVar,g2mp.Rate)
    self.inputs[0],self.outputs[1],kbt = ratemodin,slv,kbt

  def precables(self):
    doslvcables(self)

class ConvLFOSlvA(Convert):
  maing2module = 'LfoB'
  parammap = ['Rate','Phase','Waveform',['PolyMono','Mono'],['Active','Mute']]
  inputmap = ['Rate','Rst']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    waveform = getv(nmmp.Waveform)
    setv(g2mp.Waveform,[0,1,2,2,3][waveform])
    if waveform != 3:
      setv(g2mp.OutputType,5) # BipInv
    else:
      # 180 phase
      setv(g2mp.Phase,(range(64,128)+range(64))[getv(nmmp.Phase)])
    setv(g2mp.Active,1-getv(nmmp.Mute))

    postmst(self,0)

class ConvLFOSlvB(Convert):
  maing2module = 'LfoC'
  waveform = 2
  parammap = ['Rate']
  inputmap = ['Rate']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    g2m.modes.Waveform.value = self.waveform
    if self.waveform != 2:
      setv(g2mp.OutputType,4) # Bip
    else:
      setv(g2mp.OutputType,5) # BipInv

    postmst(self,0)

class ConvLFOSlvC(ConvLFOSlvB):
  waveform = 0

  #3phase thinks we may need this.  I'm leaving it as a comment for now.
  #def domodule(self):
  #  ConvLFOSlvB.domodule(self)
  #  setv(self.g2module.params.OutputType,5) # BipInv

class ConvLFOSlvD(ConvLFOSlvB):
  waveform = 3

class ConvLFOSlvE(ConvLFOSlvC):
  waveform = 1

class ConvClkGen(Convert):
  maing2module = 'ClkGen'
  parammap = ['Rate',['Active','On/Off']]
  inputmap = ['Rst']
  outputmap = ['1/96','1/16',None,'Sync']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Active,getv(getattr(nmmp,'On/Off')))
    setv(g2mp.Source,0)  # Internal
    pulse = self.addmodule('Pulse')
    setv(pulse.params.Time,32)
    self.connect(g2m.outputs.ClkActive,pulse.inputs.In)
    self.outputs[3] = pulse.outputs.Out
    
    #handle Slv connections
    if len(nmm.outputs.Slv.cables):
      zerocnt = self.addmodule('ZeroCnt',name='96th In')
      oscmaster = self.addmodule('OscMaster',name='26-241 BPM')
      setv(oscmaster.params.FreqCoarse,9) # -55 semi
      setv(oscmaster.params.Kbt,0) # off
      self.connect(getattr(g2m.outputs,'1/96'),zerocnt.inputs.In)
      self.connect(zerocnt.outputs.Out,oscmaster.inputs.Pitch)
      self.outputs[2] = oscmaster.outputs.Out

class ConvClkRndGen(Convert):
  maing2module = 'RndClkA'
  parammap = [['PolyMono','Mono'],['StepProb','Color']]
  inputmap = ['Clk']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    if getv(nmmp.Color) == 1:
      setv(g2mp.StepProb,43)
    else:
      setv(g2mp.StepProb,127)

class ConvRndStepGen(ConvLFOSlvB):
  waveform = 4

class ConvRandomGen(ConvLFOSlvB):
  waveform = 5

class ConvRndPulseGen(Convert):
  maing2module = 'RndTrig'
  parammap = [['StepProb','Density']]
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.StepProb,96)
    lfoc = self.addmodule('LfoC',name='Clk')
    self.connect(lfoc.outputs.Out,g2m.inputs.Clk)
    setv(lfoc.params.Rate,getv(nmmp.Density))
    self.params[0] = lfoc.params.Rate

class ConvPatternGen(Convert):
  maing2module = 'RndPattern'
  parammap = [['PatternA','Pattern'],['PatternB','Bank'],
              ['StepProb','LowDelta'],['LoopCount','Step'],
              None]
  inputmap = ['Clk','Rst','A']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    pattern = (getv(nmmp.Pattern) + 64) % 128
    setv(g2mp.PatternA,pattern)
    bank = (getv(nmmp.Bank) + 64) % 128
    setv(g2mp.PatternB,bank)

    # PatternA and PatternB receive same input
    if len(getattr(nmm.inputs,'Pattern&Bank').cables):
      self.connect(g2m.inputs.A,g2m.inputs.B) 
    lowdelta = getv(nmmp.LowDelta)
    if lowdelta:
      notequant = self.addmodule('NoteQuant')
      self.connect(g2m.outputs.Out,notequant.inputs.In)
      setv(notequant.params.Range,77)
      setv(notequant.params.Notes,1)
      self.outputs[0] = notequant.outputs.Out
      stepprob,add = 55,75
      setv(g2mp.StepProb,55)
    else:
      stepprob,add = 127,74
    setv(g2mp.StepProb,stepprob)
    levadd = self.addmodule('LevAdd')
    self.connect(self.outputs[0],levadd.inputs.In)
    setv(levadd.params.Level,add)
    self.outputs[0] = levadd.outputs.Out

