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
from nord.g2.modules import fromname as g2name
from convert import *
from units import *

class ConvADSR_Env(Convert):
  maing2module = 'EnvADSR'
  parammap = [['Shape','AttackShape'],'Attack','Decay','Sustain','Release',None]
  inputmap = ['In','Gate',None,'AM'] # No Retrig
  outputmap = ['Env','Out']
              
  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    updatevals(g2mp,['Attack','Decay','Release'],nm1adsrtime,g2adsrtime)
    setv(g2mp.OutputType,[0,3][getv(nmmp.Invert)])

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
              'Time1','Time2','Time3','Time4',['NR','Time5'],
              ['SustainMode','Sustain'],['OutputType','Curve']]
  inputmap = ['Gate','In','AM']
  outputmap = ['Env','Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    updatevals(g2mp,['Time%d' % i for i in range(1,5)]+['NR'],
        nm1adsrtime, g2adsrtime)

class ConvEnvFollower(Convert):
  maing2module = 'EnvFollow'
  parammap = ['Attack','Release']
  inputmap = ['In']
  outputmap = ['Out']

