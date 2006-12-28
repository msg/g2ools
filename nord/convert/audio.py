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
from nord.g2.modules import fromname as g2name
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
  parammap = [['Time1Mod','Modulation']]
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
  parammap = ['Detune','Amount']
  inputmap = ['In']
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Active,1-getv(nmmp.Bypass))

class ConvPhaser(Convert):
  maing2module = 'FltPhase'
  parammap = ['Freq',['PitchMod','FreqMod'],'Spread','SpreadMod',
              ['FB','Feedback'],['NotchCount','Peaks'],'Level']
  inputmap = ['In',None,'Spr']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    area = self.g2area

    setv(g2mp.Active,1-getv(nmmp.Bypass))
    setv(g2mp.FBMod,getv(nmmp.Depth))
    setv(g2mp.Type,3)
    
    vert = self.height
    if len(nmm.inputs.FreqMod.cables):
      # add mixer
      mix = area.addmodule(g2name['Mix2-1B'],horiz=g2m.horiz,vert=vert)
      self.g2modules.append(mix)
      vert += mix.type.height
      area.connect(mix.outputs.Out,g2m.inputs.PitchVar,g2cablecolors.blue)
      modinp = mix.inputs.In1
      self.inputs[1] = mix.inputs.In2
      setv(g2mp.PitchMod,127)
      setv(mix.params.Lev1,getv(nmmp.FreqMod))
      depthparam = mix.params.Lev1
    else:
      modinp = g2m.inputs.PitchVar
      depthparam = g2mp.PitchMod
    lfo = area.addmodule(g2name['LfoC'],horiz=g2m.horiz,vert=vert)
    self.g2modules.append(lfo)
    vert += lfo.type.height
    self.height = vert
    setv(lfo.params.Rate,getv(nmmp.Rate))
    setv(lfo.params.Active,getv(nmmp.Lfo))
    area.connect(lfo.outputs.Out,modinp,g2cablecolors.blue)
    setv(depthparam,getv(nmmp.Depth))

class ConvInvLevShift(Convert):
  maing2module = 'LevConv'
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
  parammap = ['Threshold','Ratio','Attack','Release','RefLevel']
  inputmap = ['InL','InR','SideChain']
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    if len(nmm.inputs.Side.cables):
      setv(g2mp.SideChain,1)
    
class ConvDigitizer(Convert):
  maing2module = 'Digitizer'
  parammap = ['Bits','Rate','RateMod']
  inputmap = ['In','Rate']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    quantoff = getv(nmmp.QuantOff)
    if quantoff:
      setv(g2mp.Bits,0)
    setv(g2mp.Active,1-getv(nmmp.SamplingOff))

class ConvRingMod(Convert):
  maing2module = 'LevMod'
  parammap = ['ModDepth',['ModType','RingmodDepth']]
  inputmap = ['In','Mod','ModDepth']
  outputmap = ['Out']

