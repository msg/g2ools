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
  maing2module = 'X-Fade'
  parammap = [None,None]
  inputmap = [None,'In2']
  outputmap = [None]

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.LogLin,1) # Lin
    setv(g2mp.Mix,25)
    setv(g2mp.MixMod,74)

    constswt = self.addmodule('ConstSwT')
    setv(constswt.params.On,1)
    constswt.params.On.labels = ['Drive']
    setv(constswt.params.BipUni,1) # Uni
    setv(constswt.params.Lev,getv(nmmp.Overdrive))
    mix11a = self.addmodule('Mix1-1A')
    setv(mix11a.params.On,1)
    setv(mix11a.params.ExpLin,1) # Lin
    mix11a.params.On.labels = ['Amount']
    setv(mix11a.params.Lev,getv(nmmp.OverdriveMod))
    shpstatic = self.addmodule('ShpStatic',name='ModIn')
    setv(shpstatic.params.Mode,0)
    saturate = self.addmodule('Saturate')
    setv(saturate.params.Curve,2) # 3
    setv(saturate.params.AmountMod,127)
    setv(saturate.params.Amount,0)
    clip = self.addmodule('Clip')
    setv(clip.params.Shape,1) # Sym
    setv(clip.params.ClipLev,0)
    xfade = self.addmodule('X-Fade')
    setv(xfade.params.LogLin,1) # Lin
    setv(xfade.params.Mix,64)
    setv(xfade.params.MixMod,127)

    self.connect(g2m.inputs.In2,xfade.inputs.In1)
    self.connect(g2m.outputs.Out,saturate.inputs.In)
    self.connect(constswt.outputs.Out,mix11a.inputs.Chain)
    self.connect(mix11a.outputs.Out,shpstatic.inputs.In)
    self.connect(shpstatic.outputs.Out,g2m.inputs.Mod)
    self.connect(shpstatic.outputs.Out,saturate.inputs.Mod)
    self.connect(saturate.inputs.Mod,clip.inputs.Mod)
    self.connect(saturate.outputs.Out,clip.inputs.In)
    self.connect(clip.inputs.Mod,xfade.inputs.Mod)
    self.connect(clip.outputs.Out,xfade.inputs.In2)

    self.inputs = [g2m.inputs.In2,mix11a.inputs.In]
    self.outputs = [xfade.outputs.Out]

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
  parammap = [['Time1Mod','Modulation'],['Time1','Time']]
  inputmap = ['In','Time1']
  outputmap = ['Out2','Out1']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    # just divide parameters by 2 to get in ball park
    setv(g2mp.Time2,64)
    # fixed delay
    setv(g2mp.Time1,getv(nmmp.Time)/2)


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
    
class ConvExpander(Convert):
  maing2module = 'Sw2-1'
  parammap = [None]*9
  inputmap = [None,None,'In1'] # L, R
  outputmap = [None,None] # L, R

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Sel,getv(nmmp.Act))
    self.params[6] = g2mp.Sel
    envfollow = self.addmodule('EnvFollow')
    setv(envfollow.params.Attack,getv(nmmp.Attack))
    setv(envfollow.params.Release,getv(nmmp.Release))
    self.params[:2] = envfollow.params.Attack,envfollow.params.Release
    ratio = self.addmodule('ShpExp',name='Ratio/Thresh')
    setv(ratio.params.Curve,2) # x4
    setv(ratio.params.Amount,getv(nmmp.Ratio))
    self.params[3] = ratio.params.Amount
    left = self.addmodule('LevMult',name='Left')
    right = self.addmodule('LevMult',name='Right')
    # MISSING Gate,Hold,Mon, and Bypass  parameters

    self.connect(g2m.inputs.In1,left.inputs.In)
    self.connect(g2m.outputs.Out,envfollow.inputs.In)
    self.connect(envfollow.outputs.Out,ratio.inputs.In)
    self.connect(ratio.outputs.Out,left.inputs.Mod)
    self.connect(left.inputs.Mod,right.inputs.Mod)

    self.inputs[:] = left.inputs.In,right.inputs.In,g2m.inputs.In2
    self.outputs = left.outputs.Out,right.outputs.Out

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

