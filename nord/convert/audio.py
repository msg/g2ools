#
# audio.py - Audio tab conversion objects
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

class ConvClip(Convert):
  maing2module = 'Clip'
  parammap = [['ClipLevMod','ClipMod'],['ClipLev','Clip'],['Shape','Sym']]
  inputmap = ['In','Mod']
  outputmap = ['Out']

class ConvOverdrive(Convert):
  maing2module = 'Overdrive'
  parammap = [['AmountMod','OverdriveMod'],['Amount','Overdrive']]
  inputmap = ['In','Mod']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # set up special parameters
    setv(g2mp.Type,1)
    setv(g2mp.Shape,1)

    clip = self.addmodule('Clip',name='OverdriveClip')
    self.connect(g2m.outputs.Out,clip.inputs.In)
    setv(clip.params.ClipLev,35)
    levamp = self.addmodule('LevAmp',name='OverdriveAmp')
    self.connect(clip.outputs.Out,levamp.inputs.In)
    setv(levamp.params.Type,1)
    setv(levamp.params.Gain,85)
    self.outputs[0] = levamp.outputs.Out

class ConvWaveWrap(Convert):
  maing2module = 'WaveWrap'
  parammap = [['AmountMod','WrapMod'],['Amount','Wrap']]
  inputmap = ['In','Mod']
  outputmap = ['Out']

class ConvQuantizer(Convert):
  maing2module = 'Digitizer'
  parammap = ['Bits']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Rate,127) # max sample rate

class ConvDelay(Convert):
  maing2module = 'DelayDual'
  parammap = [['Time1Mod','Modulation'],['Time1','Modulation']]
  inputmap = ['In','Time1']
  outputmap = ['Out2','Out1']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    # just divide parameters by 2 to get in ball park
    setv(g2mp.Time2,64)
    # fixed delay
    setv(g2mp.Time1,getv(nmmp.Modulation)/2)

class ConvSampleNHold(Convert):
  maing2module = 'S&H'
  inputmap = ['Ctrl','In']
  outputmap = ['Out']

class ConvDiode(Convert):
  maing2module = 'Rect'
  parammap = ['Mode']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    mode = getv(nmmp.Mode)
    setv(g2mp.Mode,[0,0,2][mode])
    if mode == 0:
      setv(g2mp.Active,0)

class ConvStereoChorus(Convert):
  maing2module = 'StChorus'
  parammap = ['Detune','Amount',['Active','Bypass']]
  inputmap = ['In']
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Active,1-getv(nmmp.Bypass))

class ConvPhaser(Convert):
  maing2module = 'FltPhase'
  parammap = [None,None,['PitchMod','FreqMod'],'Freq','SpreadMod',
              ['FB','Feedback'],['NotchCount','Peaks'],'Spread','Level',
              ['Active','Bypass'],None]
  inputmap = ['In',None,'Spr']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Active,1-getv(nmmp.Bypass))
    setv(g2mp.FBMod,getv(nmmp.Depth))
    setv(g2mp.Type,3)
    
    if len(nmm.inputs.FreqMod.cables):
      # add mixer
      mix = self.addmodule('Mix2-1B',name='FreqMod')
      self.connect(mix.outputs.Out,g2m.inputs.PitchVar)
      modinp = mix.inputs.In1
      self.inputs[1] = mix.inputs.In2
      setv(g2mp.PitchMod,127)
      setv(mix.params.Lev1,getv(nmmp.FreqMod))
      depthparam = mix.params.Lev1
    else:
      modinp = g2m.inputs.PitchVar
      depthparam = g2mp.PitchMod
    lfo = self.addmodule('LfoC')
    setv(lfo.params.Rate,getv(nmmp.Rate))
    self.params[0] = lfo.params.Rate
    setv(lfo.params.Active,getv(nmmp.Lfo))
    self.params[1] = lfo.params.Active
    self.connect(lfo.outputs.Out,modinp)
    setv(depthparam,getv(nmmp.Depth))
    self.params[9] = depthparam

class ConvInvLevShift(Convert):
  maing2module = 'LevConv'
  parammap = [['OutputType','Mode'],None]
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.InputType,0) # Pos
    mode = getv(nmmp.Mode)
    inv = getv(nmmp.Inv)
    setv(g2mp.OutputType,[4,2,0,5,3,1][inv*3+mode])

class ConvShaper(Convert):
  maing2module = 'ShpStatic'
  parammap = ['Mode']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    mode = getv(nmmp.Mode)
    setv(g2mp.Mode,[0,1,0,2,3][mode])
    if mode == 2:
      setv(g2mp.Active,0)
    
class ConvCompressor(Convert):
  maing2module = 'Compressor'
  parammap = ['Attack','Release','Threshold','Ratio','RefLevel',None,
              ['SideChain','Act'],['SideChain','Mon'],['Active','Bypass']]
  inputmap = ['InL','InR','SideChain']
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Active,1-getv(nmmp.Bypass))
    setv(g2mp.SideChain,getv(nmmp.Act))
    
class ConvDigitizer(Convert):
  maing2module = 'Digitizer'
  parammap = ['Bits','Rate','RateMod',['Bits','QuantOff'],
              ['Active','SamplingOff']]
  inputmap = ['In','Rate']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Bits,getv(nmmp.Bits)) # becuase it's also used for QuantOff
    quantoff = getv(nmmp.QuantOff)
    if quantoff:
      setv(g2mp.Bits,0)
    setv(g2mp.Active,1-getv(nmmp.SamplingOff))

class ConvRingMod(Convert):
  maing2module = 'LevMod'
  parammap = ['ModDepth',['ModType','RingmodDepth']]
  inputmap = ['In','Mod','ModDepth']
  outputmap = ['Out']

