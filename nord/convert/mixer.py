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
from nord.utils import *
from convert import *
from nord.g2.colors import g2conncolors
from table import modtable

def mixeroptimize(nmmodule, parammap, inputmap, maxinputs, usepad=False):

  # if Mixer8 (has -6Db param), and used, gotta use Mix8-1B
  if hasattr(nmmodule.params,'-6Db'):
    if getv(getattr(nmmodule.params,'-6Db')) != 0:
      usepad = True
    
  # remove all inputs and parameters (level settings)
  for i in range(maxinputs):
    parammap[i] = None
    inputmap[i] = None

  # get levels and inputs 
  ins = range(1,maxinputs+1)
  levels = [ getattr(nmmodule.params,'Lev%d' % i) for i in ins ]
  inputs = [ getattr(nmmodule.inputs,'In%d' % i) for i in ins ]

  # levels[i].knob and levels[i].ctrl and levels[i].morph
  # move inputs/levels to lowest available and count them
  o = 1
  for i in range(maxinputs):
    if inputs[i].net:
      parammap[i] = [ 'Lev%d' % o, 'Lev%d' % (i+1) ]
      inputmap[i] = 'In%d' % o
      o += 1
  o -= 1
  # based on number of inputs connected, use smallest possible mixer
  if o < 2:
    maing2mod = 'Mix1-1A'
    # Mix1-1A doesn't have Lev1 or In1, has Lev and In
    for i in range(len(parammap)):
      if i < maxinputs and parammap[i]:
        parammap[i] = [ 'Lev', 'Lev%d' % (i+1) ]
	inputmap[i] = 'In'
      else:  # remove all other parameters but Lev
        parammap[i] = None
  elif o < 3 and usepad == False:
    maing2mod = 'Mix2-1A'
  elif o < 5 and usepad == False:
    maing2mod = 'Mix4-1B'
  elif o < 5:
    maing2mod = 'Mix4-1C'
  elif o < 9:
    maing2mod = 'Mix8-1B'
    
  # if not usingMix8-1B, remove Pad param
  if maing2mod != 'Mix8-1B':
    for i in range(len(parammap)):
      if type(parammap[i]) == type([]) and parammap[i][0] == 'Pad':
        parammap[i] = None
  #print 'mixeroptimize "%s" mod="%s" o=%d' % (nmmodule.name, maing2mod, o)
  return maing2mod,o

class Conv3Mixer(Convert):

  def initmixerparams(self):
    self.maing2module = 'Mix4-1B'
    self.maxinputs = 3
    self.parammap = ['Lev1','Lev2','Lev3']
    self.inputmap = ['In1','In2','In3']
    self.outputmap = ['Out']

  def __init__(self, nmarea, g2area, nmmodule, options):
    self.initmixerparams()
    self.maing2module,self.maxinputs = mixeroptimize(nmmodule, self.parammap,
	  self.inputmap, self.maxinputs, options.padmixer)
    super(Conv3Mixer,self).__init__(nmarea, g2area, nmmodule, options)

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    g2m.outputs.Out.rate = g2conncolors.red
    g2m.uprate = 1

    if self.maing2module == 'Mix1-1A':
      setv(g2mp.On,1)
      setv(g2mp.Lev, modtable[getv(g2mp.Lev)][0])
      return
    elif self.maing2module == 'Mix2-1A':
      setv(g2mp.On1,1)
      setv(g2mp.On2,1)
    elif self.maing2module == 'Mix4-1C':
      setv(g2mp.On1,1)
      setv(g2mp.On2,1)
      setv(g2mp.On3,1)
      setv(g2mp.On4,1)

    for i in range(1,self.maxinputs+1):
      getattr(g2m.inputs,'In%d' % i).rate = g2conncolors.red
      l = getattr(g2mp,'Lev%d' % i)
      setv(l, modtable[getv(l)][0])

class Conv8Mixer(Conv3Mixer):
  def initmixerparams(self):
    self.maing2module = 'Mix8-1B'
    self.maxinputs = 8
    self.parammap = ['Lev1','Lev2','Lev3','Lev4','Lev5','Lev6','Lev7','Lev8',
		['Pad','-6Db']]
    self.inputmap = ['In1','In2','In3','In4','In5','In6','In7','In8']
    self.outputmap = ['Out']

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

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.LogLin,1) # Lin
class ConvPan(Convert):
  maing2module = 'Pan'
  parammap = ['PanMod','Pan']
  inputmap = ['In','Mod']
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.LogLin,1) # Lin

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
  maing2module = 'LevMult'
  parammap = [None,None]
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    shpexp = self.addmodule('ShpExp')
    setv(shpexp.params.Curve,2) # x4
    setv(shpexp.params.Amount,127)
    constswt = self.addmodule('ConstSwT')
    setv(constswt.params.On,1)
    setv(constswt.params.Lev,getv(nmmp.Gain))
    setv(constswt.params.BipUni,getv(nmmp.Unipolar))
    self.connect(shpexp.outputs.Out,g2m.inputs.Mod)
    self.connect(constswt.outputs.Out,shpexp.inputs.In)
    self.params = constswt.params.Lev,constswt.params.BipUni

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

  def __init__(self, nmarea, g2area, nmmodule, options):
    # use mixer if knobs, morphs, or midi cc's assigned and connected
    usemixer = False
    for i in range(1,5):
      level = getattr(nmmodule.params,'Level%d' % i)
      innet = getattr(nmmodule.inputs,'In%d' % i).net
      if not innet:
        continue
      if level.knob or level.morph or level.ctrl:
        usemixer = True
      if getv(level) != 127 and getv(level) != 0:
        usemixer = True
    if usemixer:
      self.maing2module = 'Mix4-1C'
      self.parammap[0] = None
    super(Conv4_1Switch,self).__init__(nmarea, g2area, nmmodule, options)

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    if self.maing2module == 'Sw4-1':
      # add a LevAmp and reorient inputs
      for i in range(1,5):
        level = getv(getattr(nmmp,'Level%d' % i))
        if level == 0 or level == 127:
          continue
        if len(nmm.inputs[i-1].cables):
          mix11a = self.addmodule('Mix1-1A')
          self.connect(mix11a.outputs.Out,getattr(g2m.inputs,'In%d' % i))
          setv(mix11a.params.On,1)
          setv(mix11a.params.Lev,modtable[level][0])
          self.params[i] = mix11a.params.Lev
          self.inputs[i-1] = mix11a.inputs.In
    else:
      sel = getv(nmmp.Sel)
      for i in range(1,5):
        level = getv(getattr(nmmp,'Level%d' % i))
        setv(getattr(g2mp,'Lev%d' % i),modtable[level][0])
        setv(getattr(g2mp,'On%d' % i),sel == i-1)

class Conv1_4Switch(Convert):
  maing2module = 'Sw1-4'
  parammap = ['Sel',None,None]
  inputmap = ['In']
  outputmap = ['Out1','Out2','Out3','Out4']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # note going to handle this as there is no Active.
    #setv(g2mp.Active,1-getv(nmmp.Mute))

    level = getv(nmmp.Level)
    if level != 0 or level != 127 or \
      nmmp.Level.knob or nmmp.Level.morph or nmmp.Level.ctrl:
      # add LevAmp module
      mix11a = self.addmodule('Mix1-1A')
      self.connect(mix11a.outputs.Out,g2m.inputs.In)
      setv(mix11a.params.On,1)
      setv(mix11a.params.Lev,modtable[level][0])
      self.params[1] = mix11a.params.Lev
      self.inputs[0] = mix11a.inputs.In

class ConvAmplifier(Convert):
  maing2module = 'LevAmp'
  parammap = ['Gain']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    updatevals(g2mp,['Gain'],nm1levamp,g2levamp)
