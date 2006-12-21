#
# env.py - Env tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

# ***** NOTE *****
# The times for A,D,S,R,H are all incorrect and need to be fixed.
# ****************

class ConvADSR_Env(Convert):
  maing2module = 'EnvADSR'
  parammap = ['Attack','Decay','Sustain','Release',['Shape','AttackShape']]
  inputmap = ['In','Gate',None,'AM'] # No Retrig
  outputmap = ['Env','Out']
              
  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.OutputType,[0,3][getv(nmmp.Invert)])

class ConvAD_Env(Convert):
  maing2module = 'EnvADR'
  parammap = ['Attack',['Release','Decay'],['TG','Gate']]
  inputmap = ['Gate','In','AM']
  outputmap = ['Env','Out']

class ConvMod_Env(Convert):
  maing2module = 'ModADSR'
  parammap = ['Attack','Decay','Sustain','Release',
              'AttackMod','DecayMod','SustainMod','ReleaseMod']
  inputmap = ['Gate',None,'AttackMod','DecayMod','SustainMod','ReleaseMod',
              'In','AM']
  outputmap = ['Env','Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    # NOTE: fix Attack, Decay, Release time as they are different
    setv(g2mp.OutputType,[0,3][getv(nmmp.Invert)])

class ConvAHD_Env(Convert):
  maing2module = 'ModAHD'
  parammap = ['Attack','Hold','Decay','AttackMod','HoldMod','DecayMod']
  inputmap = ['Trig','AttackMod','HoldMod','DecayMod','In','AM']
  outputmap = ['Env','Out']

class ConvMulti_Env(Convert):
  maing2module = 'EnvMulti'
  parammap = ['Level1','Level2','Level3','Level4',
              'Time1','Time2','Time3','Time4',['NR','Time5'],
              ['SustainMode','Sustain'],['OutputType','Curve']]
  inputmap = ['Gate','In','AM']
  outputmap = ['Env','Out']

class ConvEnvFollower(Convert):
  maing2module = 'EnvFollow'
  parammap = ['Attack','Release']
  inputmap = ['In']
  outputmap = ['Out']

