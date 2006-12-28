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
    
    # add AM if needed, handle special io
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[2] = aminput
    self.outputs[1] = handleslv(self)

# FMAmod convertion table from SpectralOsc
specfmamod = [
  0,   1,   1,   1,   1,   2,   2,   2,   2,   3,   3,   3,   4,   4,   4,   5,
  6,   6,   7,   7,   8,   8,   9,   9,  10,  11,  11,  12,  12,  13,  14,  14,
 15,  16,  16,  17,  18,  18,  19,  20,  21,  21,  22,  23,  23,  24,  25,  26,
 27,  27,  28,  29,  30,  31,  31,  32,  33,  34,  35,  36,  37,  37,  38,  39,
 40,  41,  42,  43,  44,  45,  46,  46,  47,  48,  49,  50,  51,  52,  53,  54,
 55,  56,  57,  58,  59,  60,  61,  62,  63,  64,  65,  66,  67,  68,  69,  70,
 71,  72,  73,  74,  75,  76,  77,  78,  78,  79,  80,  81,  82,  83,  84,  85,
 86,  87,  88,  89,  90,  91,  92,  93,  94,  95,  96,  97,  98,  99, 100, 101,
]

class ConvSpectralOsc(Convert):
  maing2module = 'OscShpA'
  #                                  SpShp,Part,PMd1,PMd2
  parammap = ['FreqCoarse','FreqFine',None,None,None,None,
  #                                ShpM
              ['FmAmount','FmMod'],None,'Kbt',['Active','Mute']]
  inputmap = ['FM',None,None,None]
  outputmap = [None,None]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    area = self.g2area

    setv(g2mp.FmAmount,specfmamod[getv(g2mp.FmAmount)])
    # NOTE: this must be done before adding the rest of the structure
    #       as it should be placed right below the OscC.
    p1,p2 = handledualpitchmod(self,4,5)
    self.inputs[1:3] = p1,p2

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
