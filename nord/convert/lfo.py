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

def handleslv(conv,kbt):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params, g2m.params

  net = nmm.outputs.Slv.net
  for cable in net.output.cables:
    cable.color = nm1cablecolors.blue
  for input in net.inputs:
    for cable in input.cables:
      cable.color = nm1cablecolors.blue

  mst,ratemod=None,g2m.inputs.Rate
  if len(nmm.outputs.Slv.cables):
    mix21b = conv.addmodule('Mix2-1B',name='MasterRate')
    conv.connect(mix21b.outputs.Out,g2m.inputs.Rate)
    setv(mix21b.params.Lev1,127)
    setv(mix21b.params.Lev2,127)
    mst = mix21b.outputs.Out
    if kbt:
      keyboard = conv.addmodule('Keyboard',name='KBT')
      conv.connect(keyboard.outputs.Note,mix21b.inputs.Chain)
    if len(nmm.inputs.Rate.cables):
      mix11a = conv.addmodule('Mix1-1A',name='Rate')
      conv.connect(mix11a.outputs.Out,mix21b.inputs.In1)
      setv(mix11a.params.Lev,getv(nmm.params.RateMod))
      ratemod = mix11a.inputs.In
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
    conv.connect(constswt.outputs.Out,mix21b.inputs.In1)
    mstlfo = nmm.inputs.Mst.net.output.module.conv.g2module
    setv(g2mp.Rate,getv(mstlfo.params.Rate))
    setv(g2mp.PolyMono,getv(mstlfo.params.PolyMono))
    setv(g2mp.Range,getv(mstlfo.params.Range))
    return mix21b.inputs.Chain
  return None

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

    kbt = getv(nmmp.RateKbt)
    if kbt == 64:
      kbt = 1
    else:
      kbt = 0
    self.inputs[0],self.outputs[0] = handleslv(self,kbt)

class ConvLFOB(Convert):
  maing2module = 'LfoShpA'
  parammap = ['Rate','Range','Phase','RateMod',['PolyMono','Mono'],
              None,['PhaseMod','PwMod'],['Shape','Pw']]
  inputmap = ['Rate','Rst','ShapeMod']
  outputmap = ['Out',None] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,5)
    setv(g2mp.PhaseMod,getv(nmmp.PwMod))

    kbt = getv(nmmp.RateKbt)
    if kbt == 64:
      kbt = 1
    else:
      kbt = 0
    self.inputs[0],self.outputs[1] = handleslv(self,kbt)

class ConvLFOC(Convert):
  maing2module = 'LfoA'
  parammap = ['Rate','Range','Waveform','RateMod',['PolyMono','Mono'],
              ['Active','Mute']]
  inputmap = ['RateVar']
  outputmap = ['Out',None] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Waveform,[0,1,2,2,3][getv(nmmp.Waveform)])
    setv(g2mp.Active,1-getv(nmmp.Mute))

    self.inputs[0],self.outputs[1] = handleslv(self,0)

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
  outputmap = ['1/96','1/16',None,'Sync'] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Active,getv(getattr(nmmp,'On/Off')))

class ConvClkRndGen(Convert):
  maing2module = 'RndClkA'
  parammap = [['PolyMono','Mono'],['StepProb','Color']]
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
    setv(g2mp.StepProb,127-64*getv(nmmp.LowDelta))

