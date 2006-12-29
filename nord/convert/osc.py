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
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from nord.nm1.colors import nm1cablecolors
from convert import *

# handledualpitchmod -returns p1,p2,g2mm
# handle pitch inputs and if necessary, create a Mix2-1B for input
# NOTE: could check the PitchMod1 and PitchMod2 for maximum modulation.
#       in that case, the Pitch input could be used (if no knob tied
#       to the said PitchModX dial).
def handledualpitchmod(conv,mod1param,mod2param):
  nmm, g2m = conv.nmmodule, conv.g2module
  p1 = p2 = None
  if len(nmm.inputs.PitchMod1.cables) and len(nmm.inputs.PitchMod2.cables):
    g2area = conv.g2area
    g2mm = g2area.addmodule(g2name['Mix2-1B'],
        horiz=g2m.horiz,vert=conv.height)
    g2mm.name = 'PitchMod'
    conv.g2modules.append(g2mm)
    conv.height += g2mm.type.height
    color=g2cablecolors.blue
    g2area.connect(g2mm.outputs.Out,g2m.inputs.PitchVar,color)
    p1,p2 = g2mm.inputs.In1,g2mm.inputs.In2
    setv(g2m.params.PitchMod,127)
    cpv(g2mm.params.Lev1,nmm.params.PitchMod1)
    cpv(g2mm.params.Lev2,nmm.params.PitchMod2)
    conv.params[mod1param] = g2mm.params.Lev1
    conv.params[mod2param] = g2mm.params.Lev2
  elif len(nmm.inputs.PitchMod1.cables):
    p1 = g2m.inputs.PitchVar
    cpv(g2m.params.PitchMod,nmm.params.PitchMod1)
    conv.params[mod1param] = g2m.params.PitchMod
  elif len(nmm.inputs.PitchMod2.cables):
    p2 = g2m.inputs.PitchVar
    cpv(g2m.params.PitchMod,nmm.params.PitchMod2)
    conv.params[mod2param] = g2m.params.PitchMod

  return p1, p2

# FMAmod convertion table calculated by 3phase from SpectralOsc
fmmod = [
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
def handlefm(conv):
  nmm, g2m = conv.nmmodule, conv.g2module
  area = conv.g2area
  fma = getv(g2m.params.FmAmount) # setup from Conv..() constructor
  setv(g2m.params.FmAmount,fmmod[fma][0])
  if len(nmm.inputs.FmMod.cables):
    vert = conv.height
    mix21b = area.addmodule(g2name['Mix2-1B'],horiz=g2m.horiz,vert=vert)
    conv.g2modules.append(mix21b)
    conv.height += mix21b.type.height
    area.connect(mix21b.outputs.Out,g2m.inputs.FmMod,g2cablecolors.blue)
    area.connect(mix21b.inputs.Chain,mix21b.inputs.In1,g2cablecolors.blue)
    area.connect(mix21b.inputs.In1,mix21b.inputs.In2,g2cablecolors.blue)
    setv(mix21b.params.Lev1,fmmod[fma][1])
    setv(mix21b.params.Inv2,1)
    setv(mix21b.params.Lev2,fmmod[fma][2])
    return mix21b.inputs.Chain
  return g2m.inputs.FmMod # won't be used anyways

def handleam(conv):
  nmm, g2m = conv.nmmodule, conv.g2module
  aminput = None
  output = g2m.outputs.Out
  if len(nmm.inputs.Am.cables):
    am = conv.g2area.addmodule(g2name['LevMod'],name='AM',
      horiz=g2m.horiz,vert=conv.height)
    conv.g2modules.append(am)
    conv.height += am.type.height
    conv.g2area.connect(g2m.outputs.Out,am.inputs.In,g2cablecolors.red)
    aminput = am.inputs.Mod
    output = am.outputs.Out
  return aminput, output

def handleslv(conv):
  nmm, g2m = conv.nmmodule, conv.g2module
  if len(nmm.outputs.Slv.cables):
    # add a masterosc
    master = conv.g2area.addmodule(g2name['OscMaster'],
        horiz=g2m.horiz,vert=conv.height)
    setv(master.params.FreqCoarse,getv(g2m.params.FreqCoarse))
    setv(master.params.FreqFine,getv(g2m.params.FreqFine))
    setv(master.params.FreqMode,getv(g2m.params.FreqMode))
    conv.g2modules.append(master)
    conv.height += master.type.height
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

    for cable in nmm.outputs.Slv.cables:
      cable.color = nm1cablecolors.blue

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
    # NOTE: since shape can be 0% - 100%, a LevConv could be used
    #       to get the actual waveform, if necessary.
    setv(g2mp.Shape,abs(getv(nmmp.PulseWidth)-64)*2)
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
              ['FmAmount','FmMod'],['ShapeMod','PulseWidth'],['Active','Mute']]
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
    self.outputs[1] = handleslv(self)

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
    area = self.g2area


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

    vert = self.height
    if len(nmm.inputs.SpectralShapeMod.cables):
      shape = area.addmodule(g2name['Mix1-1A'],horiz=g2m.horiz,vert=vert)
      self.g2modules.append(shape)
      vert += shape.type.height
      setv(shape.params.Lev,getv(nmmp.SpectralShapeMod))
      self.params[7] = shape.params.Lev
      setv(shape.params.On,1)
      area.connect(shape.outputs.Out,g2m.inputs.Shape,g2cablecolors.blue)
      shapemod = shape.inputs.Chain
      self.inputs[3] = shape.inputs.In
    else:
      shapemod = g2m.inputs.Shape
    mods = []
    for modnm in ['Constant','ShpStatic','LevMult','Mix2-1B']:
      mod = area.addmodule(g2name[modnm],horiz=g2m.horiz,vert=vert)
      vert += mod.type.height
      self.g2modules.append(mod)
      mods.append(mod)
    self.height = vert
    # setup parameters
    const,shpstatic,levmult,mix=mods
    setv(const.params.BipUni,1)
    setv(const.params.Level,getv(nmmp.SpectralShape))
    self.params[2] = const.params.Level
    setv(shpstatic.params.Mode,2)
    setv(mix.params.Lev1,127)
    setv(mix.params.Lev2,127)
    # setup connections
    area.connect(const.outputs.Out,shapemod,g2cablecolors.blue)
    area.connect(const.outputs.Out,shpstatic.inputs.In,g2cablecolors.blue)
    area.connect(shpstatic.outputs.Out,levmult.inputs.Mod,g2cablecolors.blue)
    area.connect(g2m.outputs.Out,levmult.inputs.In,g2cablecolors.red)
    area.connect(levmult.outputs.Out,mix.inputs.Chain,g2cablecolors.red)
    area.connect(levmult.inputs.In,mix.inputs.In2,g2cablecolors.red)
    area.connect(mix.inputs.In1,mix.inputs.In2,g2cablecolors.red)
    self.outputs[0] = mix.outputs.Out

    # place master osc (if needed)
    self.outputs[1] = handleslv(self)

class ConvFormantOsc(Convert):
  maing2module = 'OscC'
  parammap = ['FreqCoarse','FreqFine','Kbt',['Active','Mute'],None,None,None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    area = self.g2area

    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])
    # handle special inputs
    # NOTE: this must be done before adding the rest of the structure
    #       as it should be placed right below the OscC.
    p1,p2 = handledualpitchmod(self,5,6)
    self.inputs[:2] = p1,p2

    vert = self.height
    modules =[]
    for mod in ['Invert','RndClkA','ConstSwT']:
      m = area.addmodule(g2name[mod],horiz=g2m.horiz,vert=vert)
      modules.append(m)
      vert += m.type.height
    self.g2modules.extend(modules)
    self.height = vert

    # NOTE: not handling Timbre input (yet)
    inv,rndclka,constswt = modules
    area.connect(g2m.outputs.Out,inv.inputs.In2,g2cablecolors.red)
    area.connect(g2m.outputs.Out,rndclka.inputs.Rst,g2cablecolors.red)
    area.connect(inv.outputs.Out1,inv.inputs.In1,g2cablecolors.orange)
    area.connect(inv.inputs.In1,rndclka.inputs.Clk,g2cablecolors.orange)
    area.connect(constswt.outputs.Out,rndclka.inputs.Seed,g2cablecolors.blue)

    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(constswt.params.Lev,getv(nmm.params.Timbre))
    self.params[4] = constswt.params.Lev

    self.outputs = [rndclka.outputs.Out,handleslv(self)]

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
    g2area = self.g2area
    # if sync connected, use OscC, otherwise use OscD
    if len(nmm.inputs.Sync.cables):
      osctype = 'OscC'
    else:
      osctype = 'OscD'
    vert = self.height
    oscs = []
    for i in range(1,7): # 6 Sine Osc
      # if osc muted, don't addit
      #if getv(getattr(nmmp,'Osc%dMute'%i)):
      #  continue
      osc = g2area.addmodule(g2name[osctype],horiz=g2m.horiz,vert=vert)
      osc.name = 'Osc%d' % i
      vert += osc.type.height
      self.g2modules.append(osc)
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
        mod = g2area.addmodule(g2name['LevMod'],horiz=g2m.horiz,vert=vert)
	mod.name = 'Am%d' % i
        vert += mod.type.height
        self.g2modules.append(mod)
        g2area.connect(osc.outputs.Out,mod.inputs.In,g2cablecolors.red)
        g2area.connect(mod.outputs.Out,getattr(g2m.inputs,'In%d'%i),
                       g2cablecolors.red)
        self.inputs[2+i] = mod.inputs.Mod
      else:
        g2area.connect(osc.outputs.Out,getattr(g2m.inputs,'In%d'%i),
                       g2cablecolors.red)
    self.height = vert
    if len(nmm.inputs.Sync.cables):
      self.inputs[2] = oscs[0].inputs.Sync
      if len(oscs) > 1:
        for i in range(1,len(oscs)):
          g2area.connect(oscs[i-1].inputs.Sync,
                         oscs[i].inputs.Sync,g2cablecolors.red)
    if len(nmm.inputs.Mst.cables):
      print osc.name
      self.inputs[0] = oscs[0].inputs.Pitch
      if len(oscs) > 1:
        for i in range(1,len(oscs)):
          g2area.connect(oscs[i-1].inputs.Pitch,
                         oscs[i].inputs.Pitch,g2cablecolors.blue)

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
      cpv(g2mp[i],nmmp[i])
      self.params[i] = g2mp[i]

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))
