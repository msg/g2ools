#
# mixer.py - Mixer tab conversion objects
#
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from convert import *

class Conv3Mixer(Convert):
  maing2module = 'Mix4-1B'
  parammap = ['Lev1','Lev2','Lev3']
  inputmap = ['In1','In2','In3']
  outputmap = ['Out']

class Conv8Mixer(Convert):
  maing2module = 'Mix8-1B'
  parammap = ['Lev1','Lev2','Lev3','Lev4','Lev5','Lev6','Lev7','Lev8',
              ['Pad','-6Db']]
  inputmap = ['In1','In2','In3','In4','In5','In6','In7','In8']
  outputmap = ['Out']

class ConvGainControl(Convert):
  maing2module = 'LevMult'
  inputmap = ['Mod','In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    shift = getv(nmmp.Shift)
    if shift:
      conv = self.g2area.addmodule(g2name['LevConv'])
      setv(conv.params.OutpuType,2) # Pos (I think)
      conv.horiz = g2m.horiz
      conv.vert = g2m.type.height
      self.height = conv.vert + conv.type.height
      self.g2modules.append(conv)
      self.g2area.connect(conv.outputs.Out,g2m.inputs.Mod)
      self.inputs[0] = conv.inputs.In

class ConvX_Fade(Convert):
  maing2module = 'X-Fade'
  parammap = [['Mix','Crossfade'],['MixMod','Modulation']]
  inputmap = ['In1','In2','Mod']
  outputmap = ['Out']

class ConvPan(Convert):
  maing2module = 'Pan'
  parammap = ['PanMod','Pan']
  inputmap = ['In','Mod']
  outputmap = ['OutL','OutR']

class Conv1to2Fade(Convert):
  maing2module = 'Fade1-2'
  parammap = [['Mix','Fade']]
  inputmap = ['In']
  outputmap = ['Out1','Out2']

class Conv2to1Fade(Convert):
  maing2module = 'Fade2-1'
  parammap = [['Mix','Fade']]
  inputmap = ['In1','In2']
  outputmap = ['Out']

class ConvLevMult(Convert):
  maing2module = 'LevAmp'
  parammap = [['Gain','Multiplier']]
  inputmap = ['In']
  outputmap = ['Out']

class ConvLevAdd(Convert):
  maing2module = 'LevAdd'
  parammap = [['Level','Offset']]
  inputmap = ['In']
  outputmap = ['Out']

class ConvOnOff(Convert):
  maing2module = 'SwOnOffT'
  parammap = [['On','On/Off']]
  inputmap = ['In']
  outputmap = ['Out']

class Conv4_1Switch(Convert):
  maing2module = 'Sw4-1'
  parammap = [['Sel','In']]
  inputmap = ['In1','In2','In3','In4']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    vert = g2m.type.height
    # add a LevAmp and reorient inputs
    for i in range(1,5):
      level = getv(getattr(nmmp,'Level%d' % i))
      print '%d level=%d' % (i,level)
      if level == 0 or level == 127:
        continue
      if len(nmm.inputs[i-1].cables):
        amp = self.g2area.addmodule(g2name['LevAmp'])
        self.g2modules.append(amp)
        amp.horiz = g2m.horiz
        amp.vert = vert
        vert += amp.type.height
        setv(amp.params.Gain,getv(getattr(nmmp,'Level%d' % i)))
        self.g2area.connect(amp.outputs.Out,getattr(g2m.inputs,'In%d' % i),
           g2cablecolors.blue)
        self.inputs[i-1] = amp.inputs.In
    self.height = vert

class Conv1_4Switch(Convert):
  maing2module = 'Sw1-4'
  parammap = [['Sel','Out']]
  inputmap = ['In']
  outputmap = ['Out1','Out2','Out3','Out4']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # note going to handle this as it's probably never used
    #setv(g2mp.Active,1-getv(nmmp.Mute))

    vert = g2m.type.height
    level = getv(nmmp.Level)
    if level != 0 or level != 127:
      # add LevAmp module
      amp = self.g2area.addmodule(g2name['LevAmp'])
      self.g2modules.append(amp)
      amp.horiz = g2m.horiz
      amp.vert = vert
      vert += amp.type.height
      setv(amp.params.Gain,level)
      self.g2area.connect(amp.outputs.Out,g2m.inputs.In,g2cablecolors.blue)
      self.inputs[0] = amp.inputs.In

class ConvAmplifier(Convert):
  maing2module = 'LevAmp'
  parammap = ['Gain']
  inputmap = ['In']
  outputmap = ['Out']

