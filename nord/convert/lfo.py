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
from nord.nm1.colors import nm1cablecolors
from convert import *

def handleslv(conv):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params, g2m.params

  mst,ratemod=None,None
  if hasattr(g2m.inputs,'Rate'):
    ratemod = g2m.inputs.Rate
  if len(nmm.outputs.Slv.cables):
    mix21b = conv.addmodule('Mix2-1B',name='MasterRate')
    if hasattr(g2m.inputs,'Rate'):
      conv.connect(mix21b.outputs.Out,g2m.inputs.Rate)
    setv(mix21b.params.Lev1,127)
    setv(mix21b.params.Lev2,127)
    mst = mix21b.outputs.Out
    if hasattr(nmm.inputs,'Rate'):
      if len(nmm.inputs.Rate.cables):
        mix11a = conv.addmodule('Mix1-1A',name='Rate')
        setv(mix11a.params.On,1)
        conv.connect(mix11a.outputs.Out,mix21b.inputs.In2)
        setv(mix11a.params.Lev,getv(nmm.params.RateMod))
        ratemod = mix11a.inputs.In
        mst = mix21b.inputs.In2
  return ratemod,mst

def handlemst(conv):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params, g2m.params

  if len(nmm.inputs.Mst.cables):
    mix21b = conv.addmodule('Mix2-1B',name='SlaveRate')
    conv.connect(mix21b.outputs.Out,g2m.inputs.Rate)
    setv(mix21b.params.Lev1,127)
    setv(mix21b.params.Lev2,127)
    constswt = conv.addmodule('ConstSwT',name='RateFactor')
    setv(constswt.params.On,1)
    setv(constswt.params.Lev,modtable[getv(nmmp.Rate)][0])
    conv.connect(constswt.outputs.Out,mix21b.inputs.In1)
    return mix21b.inputs.In2
  return None

def postmst(conv):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params, g2m.params

  if len(nmm.inputs.Mst.cables):
    mstlfo = nmm.inputs.Mst.net.output.module.conv.g2module
    range = 3
    if hasattr(mstlfo.params,'Rate'):
      setv(g2mp.Rate,getv(mstlfo.params.Rate))
      range = 1
    if hasattr(mstlfo.params,'PolyMono'):
      setv(g2mp.PolyMono,getv(mstlfo.params.PolyMono))
    if hasattr(mstlfo.params,'Range'):
      setv(g2mp.Range,getv(mstlfo.params.Range))
    else:
      setv(g2mp.Range,range)

class ConvLFOA(Convert):
  maing2module = 'LfoB'
  parammap = ['Rate','Range','Waveform','RateMod',['PolyMono','Mono'],
              None,'Phase',['Active','Mute']]
  inputmap = ['Rate','Rst']
  outputmap = [None,'Out'] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Waveform,[0,1,2,2,3][getv(nmmp.Waveform)])
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.inputs[0],self.outputs[0] = handleslv(self)

class ConvLFOB(Convert):
  maing2module = 'LfoShpA'
  parammap = ['Rate','Range','Phase','RateMod',['PolyMono','Mono'],
              None,['PhaseMod','PwMod'],['Shape','Pw']]
  inputmap = ['Rate','Rst','ShapeMod']
  outputmap = ['Out',None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,5)
    setv(g2mp.PhaseMod,getv(nmmp.PwMod))

    self.inputs[0],self.outputs[1] = handleslv(self)

class ConvLFOC(Convert):
  maing2module = 'LfoA'
  parammap = ['Rate','Range','Waveform','RateMod',['PolyMono','Mono'],
              ['Active','Mute']]
  inputmap = ['RateVar']
  outputmap = ['Out',None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,[0,1,2,2,3][getv(nmmp.Waveform)])
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.inputs[0],self.outputs[1] = handleslv(self)

class ConvLFOSlvA(Convert):
  maing2module = 'LfoB'
  parammap = ['Rate','Phase','Waveform',['PolyMono','Mono'],['Active','Mute']]
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

    self.inputs[0] = handlemst(self)

  def postmodule(self):
    postmst(self)

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

    self.inputs[0] = handlemst(self)

  def postmodule(self):
    postmst(self)

class ConvLFOSlvC(ConvLFOSlvB):
  waveform = 0

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
    setv(g2mp.Source,1)  # Master
    self.outputs[2] = handleslv(self)[1]

class ConvClkRndGen(Convert):
  maing2module = 'RndClkA'
  parammap = [['PolyMono','Mono'],['StepProb','Color']]
  inputmap = ['Clk']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

class ConvRndStepGen(ConvLFOSlvB):
  waveform = 4

class ConvRandomGen(ConvLFOSlvB):
  waveform = 5

class ConvRndPulseGen(Convert):
  maing2module = 'RndTrig'
  parammap = [['StepProb','Density']]
  outputmap = ['Out']

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

