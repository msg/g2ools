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
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from convert import *

def handlemst(conv):
  pass
  # if the mst connection used
  #   if net.output.module is a Lfo
  #     get the ratio from the slave lfo
  #     set rate of the g2 module as the ratio of the masters Lfo's rate
  #     disconnect slv cable
  #   

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
  parammap = [['Tempo','Rate']]
  inputmap = ['Rst']
  outputmap = ['1/96','1/16',None,'Sync'] # no Slv

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Active,getv(getattr(nmmp,'On/Off')))

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
    if len(getattr(nmm.inputs,'Pattern&Bank').cables):
      self.g2area.connect(g2m.inputs.A,g2m.inputs.B,g2cablecolors.blue) 
    # deal with nmmp.LowDelta later

