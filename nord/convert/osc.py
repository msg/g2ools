#
# osc.py - Osc tab convertion objects
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
from nord.nm1.colors import nm1cablecolors
from convert import *

def addlevconv(conv):
  levconv = conv.addmodule('LevConv')
  setv(levconv.params.OutputType,5)
  conv.connect(conv.g2module.outputs.Out,levconv.inputs.In)
  return levconv

def handlepw(conv,levconv,pw,haspw):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params,g2m.params
  # add mix2-1b so input can be doubled/inverted
  pwmod = None
  if len(nmm.inputs.PwMod.cables):
    clip = conv.addmodule('Clip',name='PWLimit')
    mix11a = conv.addmodule('Mix1-1A',name='ShapeMod')
    if haspw:
      constswt = conv.addmodule('ConstSwT',name='Shape')
    mix21b = conv.addmodule('Mix2-1B',name='ModIn')
    conv.connect(clip.outputs.Out,g2m.inputs.ShapeMod)
    conv.connect(mix11a.outputs.Out,clip.inputs.In)
    if haspw:
      conv.connect(constswt.outputs.Out,mix11a.inputs.Chain)
      conv.connect(mix21b.outputs.Out,mix11a.inputs.In)
      setv(constswt.params.Lev,getv(nmmp.PulseWidth))
    else:
      conv.connect(mix21b.outputs.Out,mix11a.inputs.In)
    conv.connect(mix21b.inputs.In1,mix21b.inputs.In2)
    setv(clip.params.ClipLev,2)
    setv(mix21b.params.Lev1,127)
    setv(mix21b.params.Lev2,127)
    setv(g2mp.Shape,0)
    setv(g2mp.ShapeMod,127)
    setv(mix11a.params.Lev,getv(nmmp.PwMod))
    return mix21b.inputs.In1
  if pw < 64:
    pw = 64-pw
    setv(levconv.params.OutputType,4) # Bip
  else:
    pw -= 64
  setv(g2mp.Shape,pw*2)
  return pwmod

# FMAmod conversion table calculated by 3phase from SpectralOsc
fmmod = [ # [fmmod,mix,inv]
 [  0,  0,  0],  [  1,  0, 55],  [  1, 49,  0],  [  1, 76,  0],
 [  2,  0, 87],  [  2,  0, 77],  [  2,  0, 58],  [  2, 37,  0],
 [  2, 71,  0],  [  3,  0, 64],  [  3,  0, 17],  [  3, 62,  0],
 [  4,  0, 55],  [  4, 37,  0],  [  5,  0, 61],  [  5, 20,  0],
 [  6,  0, 60],  [  6,  0,  0],  [  7,  0, 57],  [  7, 29,  0],
 [  8,  0, 52],  [  8, 41,  0],  [  9,  0, 44],  [  9, 50,  0],
 [ 10,  0, 25],  [ 11,  0, 52],  [ 11, 38,  0],  [ 12,  0,  0],
 [ 12, 51,  0],  [ 13, 24,  0],  [ 14,  0, 44],  [ 14, 47,  0],
 [ 15, 16,  0],  [ 16,  0, 43],  [ 16, 47, 16],  [ 17, 22,  7],
 [ 18,  7,  7],  [ 18, 49, 16],  [ 19, 32,  4],  [ 20,  7, 32],
 [ 21, 11, 46],  [ 21, 41,  7],  [ 22, 19,  7],  [ 23, 10, 36],
 [ 23, 49, 10],  [ 24, 39,  3],  [ 25, 21,  0],  [ 26, 10, 32],
 [ 27, 11, 42],  [ 27, 42,  0],  [ 28, 33, 11],  [ 29,  0,  6],
 [ 30,  0, 31],  [ 31, 11, 31],  [ 31, 43, 13],  [ 32, 36, 11],
 [ 33, 25,  0],  [ 34,  0, 16],  [ 35,  6, 30],  [ 36, 13, 37],
 [ 37, 12, 41],  [ 37, 39, 41],  [ 38, 34,  7],  [ 39, 28,  7],
 [ 40, 17,  0],  [ 41,  2, 17],  [ 42,  4, 26],  [ 43,  7, 31],
 [ 44,  2, 34],  [ 45,  9, 37],  [ 46,  9, 39],  [ 46, 37,  7],
 [ 47, 36, 17],  [ 48, 32, 17],  [ 49, 32, 19],  [ 50, 26,  6],
 [ 51, 22,  2],  [ 52, 18,  4],  [ 53, 11,  3],  [ 54,  0,  9],
 [ 55,  2, 16],  [ 56,  5, 20],  [ 57,  5, 22],  [ 58,  6, 24],
 [ 59,  4, 25],  [ 60,  3, 26],  [ 61,  4, 27],  [ 62,  7, 28],
 [ 63,  0, 28],  [ 64,  6, 29],  [ 65,  0, 29],  [ 66,  0, 30],
 [ 67,  5, 30],  [ 68,  1, 30],  [ 69, 10, 31],  [ 70, 10, 31],
 [ 71,  6, 31],  [ 72,  4, 31],  [ 73,  1, 31],  [ 74, 11, 32],
 [ 75,  9, 32],  [ 76,  9, 32],  [ 77,  6, 32],  [ 78,  3, 32],
 [ 78, 33,  7],  [ 79, 33, 11],  [ 80, 33, 14],  [ 81, 31,  3],
 [ 82, 31,  9],  [ 83, 30,  7],  [ 84, 29,  4],  [ 85, 28,  1],
 [ 86, 28, 10],  [ 87, 27,  9],  [ 88, 25,  3],  [ 89, 24,  5],
 [ 90, 22,  2],  [ 91, 20,  0],  [ 92, 19,  0],  [ 93, 15,  3],
 [ 94, 10,  3],  [ 95,  0,  6],  [ 96,  5, 15],  [ 97,  2, 18],
 [ 98,  4, 21],  [ 99,  4, 24],  [100,  4, 26],  [101,  9, 28], 
]

# PitchMod conversion table calculated by 3phase from SpectralOsc
pitchmod = [ # [pitchmod,mix,inv]
 [  0,  0,  0],  [  1, 41,  0],  [  2, 41,  0],  [  2, 41,  0],
 [  2, 37,  0],  [  2, 48,  0],  [  2, 64,  0],  [  4,  0, 41],
 [  4,  0, 41],  [  5,  0, 41],  [  6,  0, 67],  [  6,  0, 61],
 [  6,  0,  0],  [  7,  0,  0],  [  7,  0,  0],  [  8,  0, 46],
 [  9,  0, 47],  [ 10,  0, 48],  [ 10,  0, 25],  [ 11,  0, 59],
 [ 12,  0, 46],  [ 12, 22,  0],  [ 13,  0, 37],  [ 13, 48,  0],
 [ 14, 24,  0],  [ 15,  0, 13],  [ 16,  0, 44],  [ 17,  0, 50],
 [ 17, 34,  0],  [ 18,  0, 12],  [ 19,  0, 46],  [ 19, 46, 11],
 [ 20, 33,  0],  [ 21, 25,  5],  [ 22,  0, 27],  [ 23,  0, 39],
 [ 24,  0, 41],  [ 25,  0, 48],  [ 25, 37,  0],  [ 26, 17,  0],
 [ 27,  0,  0],  [ 28,  0, 24],  [ 29,  0, 34],  [ 30,  0, 37],
 [ 31,  0, 38],  [ 32, 20, 44],  [ 33,  0, 43],  [ 34,  0, 42],
 [ 34, 39,  0],  [ 35, 39,  0],  [ 37,  0, 45],  [ 37, 35, 11],
 [ 38, 37,  9],  [ 40,  0, 43],  [ 41, 16, 43],  [ 42,  0, 43],
 [ 42, 39,  0],  [ 43, 39,  2],  [ 44, 41,  5],  [ 46,  1, 35],
 [ 47,  0, 32],  [ 48, 12, 29],  [ 49,  0, 22],  [ 50,  0, 15],
 [ 51, 17,  1],  [ 52, 26,  7],  [ 53, 31,  9],  [ 54, 35,  6],
 [ 56,  0, 34],  [ 57,  0, 29],  [ 58,  0, 22],  [ 59, 14,  0],
 [ 60, 24,  3],  [ 61, 31,  0],  [ 62, 36,  5],  [ 64,  5, 29],
 [ 65,  0, 19],  [ 66, 16,  0],  [ 68,  6, 39],  [ 69,  6, 35],
 [ 70,  0, 28],  [ 71,  7, 21],  [ 72, 17,  0],  [ 73, 28,  4],
 [ 75,  0, 32],  [ 76,  0, 25],  [ 77,  0, 10],  [ 78, 24, 10],
 [ 79, 31,  6],  [ 81, 15, 30],  [ 82,  0, 17],  [ 83, 18,  0],
 [ 84, 28,  0],  [ 86, 10, 30],  [ 87,  5, 21],  [ 88, 15,  0],
 [ 89, 26,  0],  [ 91,  7, 30],  [ 92,  6, 22],  [ 93, 11,  2],
 [ 94, 24,  0],  [ 96, 16, 32],  [ 97, 13, 25],  [ 98,  0,  4],
 [ 99, 22,  0],  [100, 29,  4],  [102, 29, 25],  [103,  2, 13],
 [104, 19,  1],  [105, 28, 11],  [107,  0, 26],  [108,  3, 18],
 [109, 12,  0],  [110, 25, 11],  [111, 29,  5],  [113,  5, 23],
 [114,  7, 14],  [115, 17,  2],  [116, 26, 12],  [118,  3, 27],
 [119,  4, 22],  [120,  4, 13],  [122,  5, 34],  [123,  0, 31],
 [124,  6, 28],  [125,  6, 24],  [126,  3, 18],  [127,  0, 18], 
]

# handledualpitchmod -> p1,p2
# handle pitch inputs and if necessary, create a Mix2-1B for input
# NOTE: could check the PitchMod1 and PitchMod2 for maximum modulation.
#       in that case, the Pitch input could be used (if no knob tied
#       to the said PitchModX dial).
pitchmodnum = 1
def handledualpitchmod(conv,mod1param,mod2param):
  global pitchmodnum
  nmm, g2m = conv.nmmodule, conv.g2module
  p1 = p2 = None
  if len(nmm.inputs.PitchMod1.cables) and len(nmm.inputs.PitchMod2.cables):
    setv(g2m.params.PitchMod,127)
    mix21b = conv.addmodule('Mix2-1B',name='PitchMod%d' % pitchmodnum)
    adj1 = conv.addmodule('Mix2-1B',name='PitchAdj1-%d' % pitchmodnum)
    adj2 = conv.addmodule('Mix2-1B',name='PitchAdj2-%d' % pitchmodnum)

    conv.connect(mix21b.outputs.Out,g2m.inputs.PitchVar)
    conv.connect(adj1.outputs.Out,mix21b.inputs.In1)
    conv.connect(adj1.inputs.Chain,adj1.inputs.In1)
    conv.connect(adj1.inputs.In1,adj1.inputs.In2)
    conv.connect(adj2.outputs.Out,mix21b.inputs.In2)
    conv.connect(adj2.inputs.Chain,adj2.inputs.In1)
    conv.connect(adj2.inputs.In1,adj2.inputs.In2)

    pmod1 = getv(nmm.params.PitchMod1)
    setv(mix21b.params.Lev1,pitchmod[pmod1][0])
    setv(adj1.params.Inv2, 1)
    setv(adj1.params.Lev1, pitchmod[pmod1][1])
    setv(adj1.params.Lev2, pitchmod[pmod1][2])

    pmod2 = getv(nmm.params.PitchMod2)
    setv(mix21b.params.Lev2,pitchmod[pmod2][0])
    setv(adj2.params.Inv2, 1)
    setv(adj2.params.Lev1, pitchmod[pmod2][1])
    setv(adj2.params.Lev2, pitchmod[pmod2][2])

    conv.params[mod1param] = mix21b.params.Lev1
    conv.params[mod2param] = mix21b.params.Lev2
    p1,p2 = adj1.inputs.Chain,adj2.inputs.Chain

  elif len(nmm.inputs.PitchMod1.cables):
    setv(g2m.params.PitchMod,127)
    adj = conv.addmodule('Mix2-1B',name='PitchAdj1-%d' % pitchmodnum)
    conv.connect(adj.outputs.Out,g2m.inputs.PitchVar)
    conv.connect(adj.inputs.Chain,adj.inputs.In1)
    conv.connect(adj.inputs.In1,adj.inputs.In2)

    pmod = getv(nmm.params.PitchMod1)
    setv(g2m.params.PitchMod,pitchmod[pmod][0])
    setv(adj.params.Inv2, 1)
    setv(adj.params.Lev1,pitchmod[pmod][1])
    setv(adj.params.Lev2,pitchmod[pmod][2])

    conv.params[mod1param] = g2m.params.PitchMod
    p1 = adj.inputs.Chain

  elif len(nmm.inputs.PitchMod2.cables):
    setv(g2m.params.PitchMod,127)
    adj = conv.addmodule('Mix2-1B',name='PitchAdj2-%d' % pitchmodnum)
    conv.connect(adj.outputs.Out,g2m.inputs.PitchVar)
    conv.connect(adj.inputs.Chain,adj.inputs.In1)
    conv.connect(adj.inputs.In1,adj.inputs.In2)

    pmod = getv(nmm.params.PitchMod2)
    setv(g2m.params.PitchMod,pitchmod[pmod][0])
    setv(adj.params.Inv2, 1)
    setv(adj.params.Lev1,pitchmod[pmod][1])
    setv(adj.params.Lev2,pitchmod[pmod][2])

    conv.params[mod2param] = g2m.params.PitchMod
    p2 = adj.inputs.Chain

  pitchmodnum += 1
  return p1, p2

fmmodnum = 1
def handlefm(conv):
  global fmmodnum
  nmm, g2m = conv.nmmodule, conv.g2module
  fma = getv(g2m.params.FmAmount) # setup from Conv..() constructor
  setv(g2m.params.FmAmount,fmmod[fma][0])
  if len(nmm.inputs.FmMod.cables):
    mix21b = conv.addmodule('Mix2-1B', name='FmMod%d' % fmmodnum)
    fmmodnum += 1
    conv.connect(mix21b.outputs.Out,g2m.inputs.FmMod)
    conv.connect(mix21b.inputs.Chain,mix21b.inputs.In1)
    conv.connect(mix21b.inputs.In1,mix21b.inputs.In2)
    setv(mix21b.params.Lev1,fmmod[fma][1])
    setv(mix21b.params.Inv2,1)
    setv(mix21b.params.Lev2,fmmod[fma][2])
    return mix21b.inputs.Chain
  return g2m.inputs.FmMod # won't be used anyways

ammodnum = 1
def handleam(conv):
  global ammodnum
  nmm, g2m = conv.nmmodule, conv.g2module
  aminput = None
  output = g2m.outputs.Out
  if len(nmm.inputs.Am.cables):
    am = conv.addmodule('LevMod',name='AM%d' % ammodnum)
    ammodnum += 1
    conv.connect(g2m.outputs.Out,am.inputs.In)
    aminput = am.inputs.Mod
    output = am.outputs.Out
  return aminput, output

slvoutnum=1
def handleslv(conv):
  global slvoutnum
  nmm, g2m = conv.nmmodule, conv.g2module
  if len(nmm.outputs.Slv.cables):
    # add a masterosc
    master = conv.addmodule('OscMaster',name='SlvOut%d' % slvoutnum)
    slvoutnum += 1
    setv(master.params.FreqCoarse,getv(g2m.params.FreqCoarse))
    setv(master.params.FreqFine,getv(g2m.params.FreqFine))
    setv(master.params.FreqMode,getv(g2m.params.FreqMode))
    return master.outputs.Out
  else:
    return None

class ConvMasterOsc(Convert):
  maing2module = 'OscMaster'
  parammap = ['FreqCoarse','FreqFine','Kbt',None,None]
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    # handle special inputs
    p1,p2 = handledualpitchmod(self,3,4)
    self.inputs[:2] = [p1,p2]

class ConvOscA(Convert):
  maing2module = 'OscB'
  parammap = ['FreqCoarse','FreqFine',None,['Shape','PulseWidth'],
              'Waveform',None,None,
              ['FmAmount','FmMod'],['ShapeMod','PwMod'],['Active','Mute']]
  inputmap = [ 'Sync','FmMod',None,None,'ShapeMod' ]
  outputmap = [ 'Out', None ]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    # invert output if waveform is Saw or Square
    waveform = getv(nmmp.Waveform)
    if waveform == 2 or waveform == 3:
      levconv = addlevconv(self)
      self.outputs[0] = levconv.outputs.Out
    if waveform == 3:
      self.inputs[4] = handlepw(self,levconv,getv(nmmp.PulseWidth),1)

    if getv(nmmp.Kbt) == 0:
      setv(g2mp.Kbt,0)
    self.params[2] = g2mp.Kbt
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    # handle special inputs
    p1,p2 = handledualpitchmod(self,5,6)
    self.inputs[2:4] = p1,p2

    self.inputs[1] = handlefm(self)
    self.outputs[1] = handleslv(self)

class ConvOscB(Convert):
  maing2module = 'OscB'
  parammap = ['FreqCoarse','FreqFine',None,'Waveform',None,None,
              ['FmAmount','FmMod'],['ShapeMod','PwMod'],['Active','Mute']]
  inputmap = [ 'FmMod',None,None,'ShapeMod' ]
  outputmap = [ 'Out', None ]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special special parameters
    if getv(nmmp.Kbt) == 0:
      setv(g2mp.Kbt,0)
    self.params[2] = g2mp.Kbt
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    # invert output if waveform is Saw
    waveform = getv(g2mp.Waveform)
    if waveform == 2 or waveform == 3:
      levconv = addlevconv(self)
      self.outputs[0] = levconv.outputs.Out
    if waveform == 3:
      pwmod = handlepw(self,levconv,64,0)
      notequant = self.addmodule('NoteQuant',name='BlueRate')
      self.connect(notequant.outputs.Out,pwmod)
      setv(notequant.params.Range,127)
      setv(notequant.params.Notes,0)
      self.inputs[3] = notequant.inputs.In

    # handle special inputs
    p1,p2 = handledualpitchmod(self,4,5)
    self.inputs[1:3] = p1, p2
    self.inputs[0] = handlefm(self)
    self.outputs[1] = handleslv(self)

class ConvOscC(Convert):
  maing2module = 'OscC'
  parammap = ['FreqCoarse', 'FreqFine','Kbt',
              ['PitchMod','FreqMod'],['FmAmount','FmMod'],['Active','Mute']]
  inputmap = [ 'FmMod','Pitch',None]
  outputmap = [ 'Out',None ]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # make OscC's waveform a sine
    g2m.modes.Waveform.value = 0

    # handle special parameters
    # handle KBT later = nmmp.FreqKbt)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])
    
    self.inputs[0] = handlefm(self)
    # add AM if needed, handle special io
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[2] = aminput
    output = handleslv(self)
    if self.g2modules[-1].type.shortnm == 'OscMaster':
      oscmaster = self.g2modules[-1]
      self.outputs[1] = g2m.inputs.Pitch
      self.connect(oscmaster.outputs.Out,g2m.inputs.Pitch)
      self.inputs[1] = oscmaster.inputs.Pitch

class ConvSpectralOsc(Convert):
  maing2module = 'OscShpA'
  #                                  SpShp,Part,PMd1,PMd2
  parammap = ['FreqCoarse','FreqFine',None,None,None,None,
  #                                ShpM
              ['FmAmount','FmMod'],None,'Kbt',['Active','Mute']]
  inputmap = ['FmMod',None,None,None]
  outputmap = [None,None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # NOTE: this must be done before adding the rest of the structure
    #       as it should be placed right below the OscC.
    p1,p2 = handledualpitchmod(self,4,5)
    self.inputs[1:3] = p1,p2
    self.inputs[0] = handlefm(self)

    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.Waveform,[3,4][getv(nmmp.Partials)])
    self.params[3] = g2mp.Waveform
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])
    setv(g2mp.ShapeMod,127)

    if len(nmm.inputs.SpectralShapeMod.cables):
      shape = self.addmodule('Mix1-1A',name='Shape')
      setv(shape.params.Lev,getv(nmmp.SpectralShapeMod))
      self.params[7] = shape.params.Lev
      setv(shape.params.On,1)
      self.connect(shape.outputs.Out,g2m.inputs.Shape)
      shapemod = shape.inputs.Chain
      self.inputs[3] = shape.inputs.In
    else:
      shapemod = g2m.inputs.Shape
    mods = []
    for modnm in ['Constant','ShpStatic','LevMult','Mix2-1B']:
      mod = self.addmodule(modnm,name=modnm)
      mods.append(mod)
    # setup parameters
    const,shpstatic,levmult,mix=mods
    setv(const.params.BipUni,1)
    setv(const.params.Level,getv(nmmp.SpectralShape))
    self.params[2] = const.params.Level
    setv(shpstatic.params.Mode,2)
    setv(mix.params.Lev1,127)
    setv(mix.params.Lev2,127)
    # setup connections
    self.connect(const.outputs.Out,shapemod)
    self.connect(const.outputs.Out,shpstatic.inputs.In)
    self.connect(shpstatic.outputs.Out,levmult.inputs.Mod)
    self.connect(g2m.outputs.Out,levmult.inputs.In)
    self.connect(levmult.outputs.Out,mix.inputs.Chain)
    self.connect(levmult.inputs.In,mix.inputs.In2)
    self.connect(mix.inputs.In1,mix.inputs.In2)
    self.outputs[0] = mix.outputs.Out

    # place master osc (if needed)
    self.outputs[1] = handleslv(self)

class ConvFormantOsc(Convert):
  maing2module = 'OscC'
  parammap = ['FreqCoarse','FreqFine','Kbt',['Active','Mute'],None,None,None]
  inputmap = [None,None,None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])
    setv(g2mp.Active,1-getv(nmmp.Mute))
    # handle special inputs
    # NOTE: this must be done before adding the rest of the structure
    #       as it should be placed right below the OscC.
    p1,p2 = handledualpitchmod(self,5,6)
    self.inputs[:2] = p1,p2

    modules =[]
    for modnm in ['Invert','RndClkB','EqPeak','Mix4-1A',
                  'ConstSwT','NoteQuant','LevAmp']:
      mod = self.addmodule(modnm,name=modnm)
      modules.append(mod)

    inv,rndclkb,eqpeak,mix41a,constswt,notequant,levamp = modules
    self.connect(g2m.outputs.Out,inv.inputs.In2)
    self.connect(g2m.outputs.Out,rndclkb.inputs.Rst)
    self.connect(inv.outputs.Out1,inv.inputs.In1)
    self.connect(inv.inputs.In1,rndclkb.inputs.Clk)
    self.connect(rndclkb.outputs.Out,eqpeak.inputs.In)
    self.connect(mix41a.outputs.Out,rndclkb.inputs.Seed)
    self.connect(constswt.outputs.Out,mix41a.inputs.In4)
    self.connect(notequant.outputs.Out,mix41a.inputs.In3)
    self.connect(levamp.outputs.Out,notequant.inputs.In)

    rndclkb.modes.Character.value = 1
    setv(rndclkb.params.StepProb,61)
    setv(eqpeak.params.Freq,109)
    setv(eqpeak.params.Gain,104)
    setv(eqpeak.params.Bandwidth,2)
    setv(constswt.params.Lev,getv(nmm.params.Timbre))
    self.params[4] = constswt.params.Lev
    setv(notequant.params.Range,127)
    setv(notequant.params.Notes,1)
    setv(levamp.params.Type,1)
    setv(levamp.params.Gain,20)

    self.inputs[2] = levamp.inputs.In
    self.outputs = [eqpeak.outputs.Out,handleslv(self)]

class ConvOscSlvA(Convert):
  maing2module = 'OscB'
  parammap = [['FreqCoarse','DetuneCoarse'],['FreqFine','DetuneFine'],
              'Waveform',['FmAmount','FmMod'],['Active','Mute']]
  inputmap = ['Pitch','FmMod','Pitch','Sync']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    if len(nmm.inputs.Mst.cables):
      setv(g2mp.Kbt,0)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[2,3,1][nmm.modes[0].value])

    # invert output if waveform is Saw
    if g2mp.Waveform == 2:
      self.outputs[0] = addlevconv(self).outputs.Out
    self.inputs[1] = handlefm(self)
    # handle special io
    # add AM if needed
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[2] = aminput

class ConvOscSlvB(Convert):
  maing2module = 'OscB'
  parammap = [['FreqCoarse','DetuneCoarse'],['FreqFine','DetuneFine'],
              ['Shape','PulseWidth'],['ShapeMod','PwMod'],['Active','Mute']]
  inputmap = ['Pitch','ShapeMod']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    self.inputs[1] = handlepw(self,addlevconv(self),64,1)
    # handle special parameters 
    if len(nmm.inputs.Mst.cables):
      setv(g2mp.Kbt,0)
    setv(g2mp.Waveform,3) # square
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[2,3,1][nmm.modes[0].value])

    # NOTE: since shape can be 0% - 100%, a LevConv could be used
    #       to get the actual waveform, if necessary.
    setv(g2m.params.Shape,abs(getv(nmm.params.PulseWidth)-64)*2)

class ConvOscSlvC(Convert):
  maing2module = 'OscC'
  waveform = 2 # saw
  parammap = [['FreqCoarse','DetuneCoarse'],['FreqFine','DetuneFine'],
              ['FmAmount','FmMod'],['Active','Mute']]
  inputmap = ['Pitch','FmMod',None] # no Mst, possible AM
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # invert output if waveform is Saw
    if self.__class__.__name__ == 'ConvOscSlvC':
      self.outputs[0] = addlevconv(self).outputs.Out

    # handle special parameters
    if len(nmm.inputs.Mst.cables):
      setv(g2mp.Kbt,0)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[2,3,1][nmm.modes[0].value])
    g2m.modes.Waveform.value = self.waveform
    self.inputs[1] = handlefm(self)

class ConvOscSlvD(ConvOscSlvC):
  waveform = 1 # tri

class ConvOscSlvE(ConvOscSlvC):
  waveform = 0 # sine
   
  def domodule(self):
    ConvOscSlvC.domodule(self)
    nmm,g2m = self.nmmodule,self.g2module

    # handle special io
    # add AM if needed
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[2] = aminput

class ConvOscSineBank(Convert):
  maing2module = 'Mix8-1B'
  parammap = [ None ] * 24
  outputmap = ['Out']
  #           Mst  Mixin   Sync O1Am O2Am O3Am O4Am O5Am O6Am
  inputmap = [None,'Chain',None,None,None,None,None,None,None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    levamp = self.addmodule('LevAmp',name='LevAmp')
    setv(levamp.params.Type,1)
    setv(levamp.params.Gain,68)
    self.connect(g2m.outputs.Out,levamp.inputs.In)
    self.outputs[0] = levamp.outputs.Out
    # if sync connected, use OscC, otherwise use OscD
    if len(nmm.inputs.Sync.cables):
      osctype = 'OscC'
    else:
      osctype = 'OscD'
    oscs = []
    for i in range(1,7): # 6 Sine Osc
      # if osc muted, don't addit
      if getv(getattr(nmmp,'Osc%dMute'%i)):
        if len(getattr(nmm.inputs,'Osc%dAm'%i).cables) == 0:
          continue
      osc = self.addmodule(osctype,name='Osc%d' % i)
      oscs.append(osc)
      if len(nmm.inputs.Mst.cables):
        setv(osc.params.Kbt,0)
      setv(osc.params.FreqCoarse,getv(getattr(nmmp,'Osc%dCoarse'%i)))
      self.params[(i-1)*3] = osc.params.FreqCoarse
      setv(osc.params.FreqFine,getv(getattr(nmmp,'Osc%dFine'%i)))
      self.params[(i-1)*3+1] = osc.params.FreqFine
      setv(osc.params.FreqMode,3) 
      l = getattr(g2mp,'Lev%d' % i)
      setv(l,getv(getattr(nmmp,'Osc%dLevel'%i)))
      self.params[(i-1)*3+2] = l
      setv(osc.params.Active,1-getv(getattr(nmmp,'Osc%dMute'%i)))
      self.params[(i-1)+18] = osc.params.Active
      if len(getattr(nmm.inputs,'Osc%dAm'%i).cables):
        mod = self.addmodule('LevMult',name='Am%d' % i)
        self.connect(osc.outputs.Out,mod.inputs.In)
        self.connect(mod.outputs.Out,getattr(g2m.inputs,'In%d'%i))
        self.inputs[2+i] = mod.inputs.Mod
      else:
        self.connect(osc.outputs.Out,getattr(g2m.inputs,'In%d'%i))
    if len(nmm.inputs.Sync.cables):
      self.inputs[2] = oscs[0].inputs.Sync
      if len(oscs) > 1:
        for i in range(1,len(oscs)):
          self.connect(oscs[i-1].inputs.Sync,oscs[i].inputs.Sync)
    if len(nmm.inputs.Mst.cables):
      print osc.name
      self.inputs[0] = oscs[0].inputs.Pitch
      if len(oscs) > 1:
        for i in range(1,len(oscs)):
          self.connect(oscs[i-1].inputs.Pitch,oscs[i].inputs.Pitch)

class ConvOscSlvFM(ConvOscSlvC):
  waveform = 0 # sine
  parammap = [['FreqCoarse','DetuneCoarse'],['FreqFine','DetuneFine'],
              None,['FmAmount','FmMod'],['Active','Mute']]
  inputmap = ['Pitch','FmMod','Sync'] # no Mst
 
class ConvNoise(Convert):
  maing2module = 'Noise'
  parammap = ['Color']
  outputmap = ['Out']

class ConvPercOsc(Convert):
  maing2module = 'OscPerc'
  parammap = ['FreqCoarse','Click','Decay','Punch','PitchMod','FreqFine',
              ['Active','Mute']]
  inputmap = ['Trig',None,'PitchVar']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    # add AM if needed
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[1] = aminput

class ConvDrumSynth(Convert):
  maing2module = 'DrumSynth'
  parammap = [None]*16
  inputmap = ['Trig','Vel','Pitch']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # parameters are exactly the same
    for i in range(len(nmm.params)):
      setv(g2mp[i],getv(nmmp[i]))
      self.params[i] = g2mp[i]

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))
