#
# env.py - Env tab conversion objects
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
from convert import *
from units import *

def handleretrig(conv):
  gatein,retrig = conv.g2module.inputs.Gate,None
  if len(conv.nmmodule.inputs.Retrig.cables):
    flipflop = conv.addmodule('FlipFlop')
    gate = conv.addmodule('Gate')
    gate.modes.GateMode2.value = 1
    conv.connect(flipflop.outputs.Q,flipflop.inputs.Res)
    conv.connect(flipflop.outputs.NotQ,gate.inputs.In1_1)
    conv.connect(gate.outputs.Out1,conv.g2module.inputs.Gate)
    conv.connect(gate.inputs.In2_1,gate.inputs.In2_2)
    conv.connect(gate.outputs.Out2,flipflop.inputs.In)
    gatein = gate.inputs.In1_2
    retrig = flipflop.inputs.Clk
  return gatein,retrig

class ConvADSR_Env(Convert):
  maing2module = 'EnvADSR'
  parammap = [['Shape','AttackShape'],'Attack','Decay','Sustain','Release',None]
  inputmap = ['In','Gate',None,'AM']
  outputmap = ['Env','Out']
              
  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    updatevals(g2mp,['Attack','Decay','Release'],nm1adsrtime,g2adsrtime)
    setv(g2mp.OutputType,[0,3][getv(nmmp.Invert)])
    self.inputs[1:3] = handleretrig(self)

class ConvAD_Env(Convert):
  maing2module = 'EnvADR'
  parammap = ['Attack',['Release','Decay'],['TG','Gate']]
  inputmap = ['Gate','In','AM']
  outputmap = ['Env','Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    updatevals(g2mp,['Attack','Release'],nm1adsrtime,g2adsrtime)

class ConvMod_Env(Convert):
  maing2module = 'ModADSR'
  parammap = ['Attack','Decay','Sustain','Release',
              'AttackMod','DecayMod','SustainMod','ReleaseMod',None]
  inputmap = ['Gate',None,'AttackMod','DecayMod','SustainMod','ReleaseMod',
              'In','AM']
  outputmap = ['Env','Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    updatevals(g2mp,['Attack','Decay','Release'],nm1adsrtime,g2adsrtime)
    setv(g2mp.OutputType,[0,3][getv(nmmp.Invert)])
    self.inputs[:2] = handleretrig(self)

class ConvAHD_Env(Convert):
  maing2module = 'ModAHD'
  parammap = ['Attack','Hold','Decay','AttackMod','HoldMod','DecayMod']
  inputmap = ['Trig','AttackMod','HoldMod','DecayMod','In','AM']
  outputmap = ['Env','Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    updatevals(g2mp,['Attack','Hold','Decay'],nm1adsrtime,g2adsrtime)

class ConvMulti_Env(Convert):
  maing2module = 'EnvMulti'
  parammap = ['Level1','Level2','Level3','Level4',
              'Time1','Time2','Time3','Time4',None,
              ['SustainMode','Sustain'],['Shape','Curve']]
  inputmap = ['Gate','In','AM']
  outputmap = ['Env','Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Shape,[3,2,1][getv(nmmp.Curve)])
    # handle special parameters
    updatevals(g2mp,['Time%d' % i for i in range(1,5)]+['NR'],
        nm1adsrtime, g2adsrtime)
    # if L4 is sustain, deal with it.
    if getv(nmmp.Sustain) == 4:
      adsr = self.addmodule('EnvADSR')
      setv(adsr.params.Shape,[3,2,1][getv(nmmp.Curve)])
      setv(adsr.params.KB,0)
      setv(adsr.params.Attack,0)
      setv(adsr.params.Decay,0)
      setv(adsr.params.Sustain,127)
      updatevals(adsr.params,['Release'],nm1adsrtime,g2adsrtime)
      self.connect(g2m.inputs.Gate,adsr.inputs.Gate)
      self.connect(adsr.outputs.Env,g2m.inputs.AM)
      self.inputs[2] = adsr.inputs.AM

class ConvEnvFollower(Convert):
  maing2module = 'EnvFollow'
  parammap = ['Attack','Release']
  inputmap = ['In']
  outputmap = ['Out']

