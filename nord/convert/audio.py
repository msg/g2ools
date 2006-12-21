#
# audio.py - Audio tab conversion objects
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
  maing2module = 'FltPhaser'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'Phaser not implemented'

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

