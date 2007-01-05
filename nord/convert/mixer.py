#
# mixer.py - Mixer tab conversion objects
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
from table import modtable

class Conv3Mixer(Convert):
  maing2module = 'Mix4-1B'
  parammap = ['Lev1','Lev2','Lev3']
  inputmap = ['In1','In2','In3']
  outputmap = ['Out']
  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Lev1,modtable[getv(g2mp.Lev1)][0])
    setv(g2mp.Lev2,modtable[getv(g2mp.Lev2)][0])
    setv(g2mp.Lev3,modtable[getv(g2mp.Lev3)][0])

class Conv8Mixer(Convert):
  maing2module = 'Mix8-1B'
  parammap = ['Lev1','Lev2','Lev3','Lev4','Lev5','Lev6','Lev7','Lev8',
              ['Pad','-6Db']]
  inputmap = ['In1','In2','In3','In4','In5','In6','In7','In8']
  outputmap = ['Out']
  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Lev1,modtable[getv(g2mp.Lev1)][0])
    setv(g2mp.Lev2,modtable[getv(g2mp.Lev2)][0])
    setv(g2mp.Lev3,modtable[getv(g2mp.Lev3)][0])
    setv(g2mp.Lev4,modtable[getv(g2mp.Lev4)][0])
    setv(g2mp.Lev5,modtable[getv(g2mp.Lev4)][0])
    setv(g2mp.Lev5,modtable[getv(g2mp.Lev5)][0])
    setv(g2mp.Lev6,modtable[getv(g2mp.Lev6)][0])
    setv(g2mp.Lev7,modtable[getv(g2mp.Lev7)][0])
    setv(g2mp.Lev8,modtable[getv(g2mp.Lev8)][0])

class ConvGainControl(Convert):
  maing2module = 'LevMult'
  parammap = [None]
  inputmap = ['Mod','In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    shift = getv(nmmp.Shift)
    if shift:
      conv = self.addmodule('LevConv')
      self.connect(conv.outputs.Out,g2m.inputs.Mod)
      setv(conv.params.OutputType,0) # Pos
      self.params[0] = conv.params.OutputType
      self.inputs[0] = conv.inputs.In

class ConvX_Fade(Convert):
  maing2module = 'X-Fade'
  parammap = ['MixMod','Mix']
  inputmap = ['In1','In2','Mod']
  outputmap = ['Out']

class ConvPan(Convert):
  maing2module = 'Pan'
  parammap = ['PanMod','Pan']
  inputmap = ['In','Mod']
  outputmap = ['OutL','OutR']

class Conv1to2Fade(Convert):
  maing2module = 'Fade1-2'
  parammap = ['Mix']
  inputmap = ['In']
  outputmap = ['Out1','Out2']

class Conv2to1Fade(Convert):
  maing2module = 'Fade2-1'
  parammap = ['Mix']
  inputmap = ['In1','In2']
  outputmap = ['Out']

class ConvLevMult(Convert):
  maing2module = 'LevAmp'
  parammap = ['Gain',None]
  inputmap = ['In']
  outputmap = ['Out']

class ConvLevAdd(Convert):
  maing2module = 'LevAdd'
  parammap = ['Level',['BipUni','Unipolar']]
  inputmap = ['In']
  outputmap = ['Out']

class ConvOnOff(Convert):
  maing2module = 'SwOnOffT'
  parammap = ['On']
  inputmap = ['In']
  outputmap = ['Out']

class Conv4_1Switch(Convert):
  maing2module = 'Sw4-1'
  parammap = ['Sel',None,None,None,None,None]
  inputmap = ['In1','In2','In3','In4']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # add a LevAmp and reorient inputs
    for i in range(1,5):
      level = getv(getattr(nmmp,'Level%d' % i))
      #print '%d level=%d' % (i,level)
      if level == 0 or level == 127:
        continue
      if len(nmm.inputs[i-1].cables):
        amp = self.addmodule('LevAmp')
        self.connect(amp.outputs.Out,getattr(g2m.inputs,'In%d' % i))
        setv(amp.params.Gain,getv(getattr(nmmp,'Level%d' % i)))
        self.params[i] = amp.params.Gain
        self.inputs[i-1] = amp.inputs.In

class Conv1_4Switch(Convert):
  maing2module = 'Sw1-4'
  parammap = ['Sel',None,None]
  inputmap = ['In']
  outputmap = ['Out1','Out2','Out3','Out4']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # note going to handle this as it's probably never used
    #setv(g2mp.Active,1-getv(nmmp.Mute))

    level = getv(nmmp.Level)
    if level != 0 or level != 127:
      # add LevAmp module
      amp = self.addmodule('LevAmp')
      self.connect(amp.outputs.Out,g2m.inputs.In)
      setv(amp.params.Gain,level)
      self.params[1] = amp.params.Gain
      self.inputs[0] = amp.inputs.In

class ConvAmplifier(Convert):
  maing2module = 'LevAmp'
  parammap = ['Gain']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    updatevals(g2mp,['Gain'],nm1levamp,g2levamp)
