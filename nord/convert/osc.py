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
from nord.nm1.colors import nm1portcolors
from convert import *
from table import *

def handlepw(conv,pw,haspw):
  nmm,g2m = conv.nmmodule,conv.g2module
  nmmp,g2mp = nmm.params,g2m.params
  # add mix2-1b so input can be doubled/inverted
  pwmod = None
  if len(nmm.inputs.PwMod.cables):
    clip = conv.addmodule('Clip',name='PWLimit')
    setv(clip.params.Shape,1) # Sym
    mix11a = conv.addmodule('Mix1-1A',name='ShapeMod')
    setv(mix11a.params.ExpLin, 1) # Lin
    setv(mix11a.params.On,1)
    if haspw:
      constswt = conv.addmodule('ConstSwT',name='Shape')
      setv(constswt.params.On,1)
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
    setv(mix21b.params.Lev1,126)
    setv(mix21b.params.Lev2,127)
    setv(g2mp.Shape,0)
    setv(g2mp.ShapeMod,127)
    setv(mix11a.params.Lev,getv(nmmp.PwMod))
    return mix21b.inputs.In1
  if pw < 64:
    pw = 64-pw
  else:
    pw -= 64
  setv(g2mp.Shape,pw*2)
  return pwmod

# handledualpitchmod -> p1,p2
# handle pitch inputs and if necessary, create a Mix2-1B for input
# NOTE: could check the PitchMod1 and PitchMod2 for maximum modulation.
#       in that case, the Pitch input could be used (if no knob tied
#       to the said PitchModX dial).
pitchmodnum = 1
def handledualpitchmod(conv,modinput,modinputparam,mod1param,mod2param):
  global pitchmodnum
  nmm, g2m = conv.nmmodule, conv.g2module
  p1 = p2 = None
  if len(nmm.inputs.PitchMod1.cables) and len(nmm.inputs.PitchMod2.cables):
    setv(modinputparam,127)
    mix21b = conv.addmodule('Mix2-1B',name='PitchMod%d' % pitchmodnum)
    adj1 = conv.addmodule('Mix2-1B',name='PitchAdj1-%d' % pitchmodnum)
    adj2 = conv.addmodule('Mix2-1B',name='PitchAdj2-%d' % pitchmodnum)

    conv.connect(mix21b.outputs.Out,modinput)
    conv.connect(adj1.outputs.Out,mix21b.inputs.In1)
    conv.connect(adj1.inputs.Chain,adj1.inputs.In1)
    conv.connect(adj1.inputs.In1,adj1.inputs.In2)
    conv.connect(adj2.outputs.Out,mix21b.inputs.In2)
    conv.connect(adj2.inputs.Chain,adj2.inputs.In1)
    conv.connect(adj2.inputs.In1,adj2.inputs.In2)

    pmod1 = getv(nmm.params.PitchMod1)
    setv(mix21b.params.Lev1,modtable[pmod1][0])
    setv(adj1.params.Inv2, 1)
    setv(adj1.params.Lev1, modtable[pmod1][1])
    setv(adj1.params.Lev2, modtable[pmod1][2])

    pmod2 = getv(nmm.params.PitchMod2)
    setv(mix21b.params.Lev2,modtable[pmod2][0])
    setv(adj2.params.Inv2, 1)
    setv(adj2.params.Lev1, modtable[pmod2][1])
    setv(adj2.params.Lev2, modtable[pmod2][2])

    conv.params[mod1param] = mix21b.params.Lev1
    conv.params[mod2param] = mix21b.params.Lev2
    p1,p2 = adj1.inputs.Chain,adj2.inputs.Chain

  elif len(nmm.inputs.PitchMod1.cables):
    setv(modinputparam,127)
    adj = conv.addmodule('Mix2-1B',name='PitchAdj1-%d' % pitchmodnum)
    conv.connect(adj.outputs.Out,modinput)
    conv.connect(adj.inputs.Chain,adj.inputs.In1)
    conv.connect(adj.inputs.In1,adj.inputs.In2)

    pmod = getv(nmm.params.PitchMod1)
    setv(modinputparam,modtable[pmod][0])
    setv(adj.params.Inv2, 1)
    setv(adj.params.Lev1,modtable[pmod][1])
    setv(adj.params.Lev2,modtable[pmod][2])

    conv.params[mod1param] = modinputparam
    p1 = adj.inputs.Chain

  elif len(nmm.inputs.PitchMod2.cables):
    setv(modinputparam,127)
    adj = conv.addmodule('Mix2-1B',name='PitchAdj2-%d' % pitchmodnum)
    conv.connect(adj.outputs.Out,modinput)
    conv.connect(adj.inputs.Chain,adj.inputs.In1)
    conv.connect(adj.inputs.In1,adj.inputs.In2)

    pmod = getv(nmm.params.PitchMod2)
    setv(modinputparam,modtable[pmod][0])
    setv(adj.params.Inv2, 1)
    setv(adj.params.Lev1,modtable[pmod][1])
    setv(adj.params.Lev2,modtable[pmod][2])

    conv.params[mod2param] = modinputparam
    p2 = adj.inputs.Chain

  pitchmodnum += 1
  return p1, p2

fmmodnum = 1
def handlefm(conv,fminput,fmparam):
  global fmmodnum
  nmm, g2m = conv.nmmodule, conv.g2module
  fma = getv(nmm.params.FmMod)
  if fmparam and fmmod:
    setv(fmparam,fmmod[fma][0])
  if len(nmm.inputs.FmMod.cables):
    mix21b = conv.addmodule('Mix2-1B', name='FmMod%d' % fmmodnum)
    fmmodnum += 1
    conv.connect(mix21b.outputs.Out,fminput)
    conv.connect(mix21b.inputs.Chain,mix21b.inputs.In1)
    conv.connect(mix21b.inputs.In1,mix21b.inputs.In2)
    setv(mix21b.params.Lev1,fmmod[fma][1])
    setv(mix21b.params.Inv2,1)
    setv(mix21b.params.Lev2,fmmod[fma][2])
    return mix21b.inputs.Chain
  return fminput

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

def handleoscmasterslv(conv,mst):
  nmm, g2m = conv.nmmodule, conv.g2module

  if mst.type.shortnm != 'OscMaster' or len(nmm.outputs.Slv.cables) == 0:
    return None

  onlyslave = 1
  for inputs in nmm.outputs.Slv.net.inputs:
    if inputs.rate != nm1portcolors.slave:
      onlyslave = 0

  if onlyslave:
    return mst.outputs.Out

  levscaler = conv.addmodule('LevScaler',name='GreyIn')
  setv(levscaler.params.Kbt,0)
  setv(levscaler.params.L,16)
  setv(levscaler.params.BP,127)
  setv(levscaler.params.R,112)
  levscaler2 = conv.addmodule('LevScaler',name='GreyIn')
  setv(levscaler2.params.Kbt,0)
  setv(levscaler2.params.L,91)
  setv(levscaler2.params.BP,64)
  setv(levscaler2.params.R,10)
  mix21b = conv.addmodule('Mix2-1B')
  setv(mix21b.params.Lev1,105)
  setv(mix21b.params.Lev2,25)
  greyout = conv.addmodule('LevAmp',name='GreyOut')
  setv(greyout.params.Gain,127)
  conv.connect(mst.outputs.Out,levscaler.inputs.Note)
  conv.connect(levscaler.inputs.Note,levscaler2.inputs.Note)
  conv.connect(levscaler.outputs.Level,mix21b.inputs.In1)
  conv.connect(mix21b.inputs.In1,levscaler2.inputs.In)
  conv.connect(levscaler2.outputs.Out,mix21b.inputs.In2)
  conv.connect(mix21b.outputs.Out,greyout.inputs.In)

  return greyout.outputs.Out


slvoutnum=1
def handleslv(conv):
  global slvoutnum
  nmm, g2m = conv.nmmodule, conv.g2module
  if len(nmm.outputs.Slv.cables):
    # add a masterosc
    master = conv.addmodule('OscMaster',name='SlvOut%d' % slvoutnum)
    setv(g2m.params.Kbt,0)
    conv.kbt = master.params.Kbt
    slvoutnum += 1
    conv.connect(master.outputs.Out,g2m.inputs.Pitch)
    setv(master.params.FreqCoarse,getv(g2m.params.FreqCoarse))
    setv(master.params.FreqFine,getv(g2m.params.FreqFine))
    setv(master.params.FreqMode,getv(g2m.params.FreqMode))
    out = handleoscmasterslv(conv,master)
    if out:
      return out,master
    else:
      return g2m.inputs.Pitch,master
  else:
    conv.kbt = g2m.params.Kbt
    return None,g2m

mstinnum = 1
def handlemst(conv):
  global mstinnum
  nmm, g2m = conv.nmmodule, conv.g2module
  mst,fmmod,fmparam = g2m.inputs.Pitch,g2m.inputs.FmMod,g2m.params.FmAmount
  if len(nmm.inputs.Mst.cables):
    if nmm.inputs.Mst.net.output:
      if nmm.inputs.Mst.net.output.rate != nm1portcolors.slave:
        mix11a = conv.addmodule('Mix1-1A',name='MstIn%d' % mstinnum)
        setv(mix11a.params.On,1)
        constswt = conv.addmodule('ConstSwT',name='Offset -64')
        setv(constswt.params.On,1)
        conv.connect(mix11a.outputs.Out,g2m.inputs.FmMod)
        conv.connect(constswt.outputs.Out,g2m.inputs.Pitch)
        setv(g2m.params.FmAmount,127)
        setv(mix11a.params.Lev,79)
        setv(constswt.params.Lev,0)
        mst = mix11a.inputs.In
        fmmod, fmparam = None, None
        if hasattr(nmm.inputs,'FmMod') and len(nmm.inputs.FmMod.cables):
          fmmodinput = conv.addmodule('Mix1-1A',name='FMA%d' % mstinnum)
          setv(fmmodinput.params.On,1)
          conv.connect(fmmodinput.outputs.Out,mix11a.inputs.Chain)
          fmparam = fmmodinput.params.Lev
          fmmod = fmmodinput.inputs.In
        mstinnum += 1
  return mst,fmmod,fmparam

class ConvMasterOsc(Convert):
  maing2module = 'OscMaster'
  parammap = ['FreqCoarse','FreqFine','Kbt',None,None]
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    # handle special inputs
    p1,p2 = handledualpitchmod(self,g2m.inputs.PitchVar,g2m.params.PitchMod,3,4)
    self.inputs[:2] = [p1,p2]
    self.outputs[0] = handleoscmasterslv(self,g2m)

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

    setv(g2mp.Shape,0)
    # handle special parameters
    self.inputs[4] = handlepw(self,getv(nmmp.PulseWidth),1)

    self.params[2] = g2mp.Kbt
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    # handle special inputs/outputs
    self.outputs[1],inputmod = handleslv(self)
    self.inputmod = inputmod
    p1,p2 = handledualpitchmod(self,inputmod.inputs.PitchVar,
        inputmod.params.PitchMod,5,6)
    self.inputs[2:4] = p1,p2

    self.inputs[1] = handlefm(self,g2m.inputs.FmMod,g2mp.FmAmount)
    handlekbt(self,self.inputmod.inputs.Pitch,1) # 0=off,1=on

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
    self.params[2] = g2mp.Kbt
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    setv(g2mp.Shape,0)
    if getv(g2mp.Waveform) == 3:
      pwmod = handlepw(self,64,0)
      if pwmod:
        notequant = self.addmodule('NoteQuant',name='BlueRate')
        self.connect(notequant.outputs.Out,pwmod)
        setv(notequant.params.Range,127)
        setv(notequant.params.Notes,0)
        self.inputs[3] = notequant.inputs.In

    # handle special inputs
    self.outputs[1],inputmod = handleslv(self)
    self.inputmod = inputmod
    p1,p2 = handledualpitchmod(self,inputmod.inputs.PitchVar,
        inputmod.params.PitchMod,4,5)
    self.inputs[1:3] = p1, p2
    self.inputs[0] = handlefm(self,g2m.inputs.FmMod,g2mp.FmAmount)
    handlekbt(self,self.inputmod.inputs.Pitch,1) # 0=off,1=on

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
    
    self.inputs[0] = handlefm(self,g2m.inputs.FmMod,g2mp.FmAmount)
    # add AM if needed, handle special io
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[2] = aminput
    self.outputs[1],inputmod = handleslv(self)
    self.inputs[1] = inputmod.inputs.Pitch

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
    self.outputs[1],inputmod = handleslv(self)
    p1,p2 = handledualpitchmod(self,inputmod.inputs.PitchVar,
        inputmod.params.PitchMod,4,5)
    self.inputs[1:3] = p1,p2
    self.inputs[0] = handlefm(self,g2m.inputs.FmMod,g2mp.FmAmount)

    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.Waveform,[3,2][getv(nmmp.Partials)])
    self.params[3] = g2mp.Waveform
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])
    setv(g2mp.ShapeMod,127)

    constswt = self.addmodule('ConstSwT',name='Shape')
    setv(constswt.params.BipUni,1) # Uni
    setv(constswt.params.On,1)
    constswt.params.On.labels = ['Shape']
    setv(constswt.params.Lev,getv(nmmp.Shape))
    mix11a = self.addmodule('Mix1-1A',name='ShapeMod')
    setv(mix11a.params.ExpLin,1) # Line
    setv(mix11a.params.On,1)
    mix11a.params.On.labels = ['Amount']
    setv(mix11a.params.Lev,getv(nmmp.ShapeMod))
    levmult = self.addmodule('LevMult')
    levmult2 = self.addmodule('LevMult')
    mix21a = self.addmodule('Mix2-1A',name='Out')
    setv(mix21a.params.ExpLin,1) # Lin
    setv(mix21a.params.On1,1)
    mix21a.params.On1.labels = ['High']
    setv(mix21a.params.Lev1,127)
    setv(mix21a.params.On2,1)
    mix21a.params.On2.labels = ['Low']
    setv(mix21a.params.Lev2,98)

    self.connect(g2m.outputs.Out,levmult2.inputs.In)
    self.connect(constswt.outputs.Out,mix11a.inputs.Chain)
    self.connect(mix11a.outputs.Out,g2m.inputs.ShapeMod)
    self.connect(mix11a.outputs.Out,levmult.inputs.In)
    self.connect(levmult.inputs.In,levmult.inputs.Mod)
    self.connect(levmult.outputs.Out,levmult2.inputs.Mod)
    self.connect(levmult2.inputs.In,mix21a.inputs.In2)
    self.connect(levmult2.outputs.Out,mix21a.inputs.In1)
    self.connect(mix21a.inputs.In1,mix21a.inputs.Chain)

    self.inputs[3] = mix11a.inputs.In
    self.outputs[0] = mix21a.outputs.Out

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
    p1,p2 = handledualpitchmod(self,g2m.inputs.PitchVar,g2m.params.PitchMod,5,6)
    self.inputs[:2] = p1,p2

    modules =[]
    for modnm in ['Invert','RndClkB','EqPeak','Mix4-1A',
                  'ConstSwT','NoteQuant','LevAmp']:
      mod = self.addmodule(modnm,name=modnm)
      modules.append(mod)

    inv,rndclkb,eqpeak,mix41a,constswt,notequant,levamp = modules
    self.connect(g2m.outputs.Out,inv.inputs.In2)
    self.connect(inv.inputs.In2,rndclkb.inputs.Rst)
    self.connect(inv.outputs.Out1,inv.inputs.In1)
    self.connect(inv.inputs.In1,rndclkb.inputs.Clk)
    self.connect(rndclkb.outputs.Out,eqpeak.inputs.In)
    self.connect(mix41a.outputs.Out,rndclkb.inputs.Seed)
    self.connect(constswt.outputs.Out,mix41a.inputs.In4)
    setv(constswt.params.On,1)
    self.connect(notequant.outputs.Out,mix41a.inputs.In3)
    self.connect(levamp.outputs.Out,notequant.inputs.In)

    rndclkb.modes.Character.value = 1
    setv(rndclkb.params.StepProb,61)
    setv(eqpeak.params.Freq,109)
    setv(eqpeak.params.Gain,104)
    setv(eqpeak.params.Bandwidth,2)
    setv(eqpeak.params.Level,100)
    setv(constswt.params.Lev,getv(nmm.params.Timbre))
    self.params[4] = constswt.params.Lev
    setv(notequant.params.Range,127)
    setv(notequant.params.Notes,1)
    setv(levamp.params.Type,1)
    setv(levamp.params.Gain,20)

    self.inputs[2] = levamp.inputs.In
    self.outputs = [eqpeak.outputs.Out,handleslv(self)[0]]

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

    # mst connection if not
    self.inputs[0],fmmod,fmparam = handlemst(self)
    self.inputs[1] = handlefm(self,fmmod,fmparam)
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

    setv(g2mp.Shape,0)
    self.inputs[1] = handlepw(self,64,1)
    # handle special parameters 
    if len(nmm.inputs.Mst.cables):
      setv(g2mp.Kbt,0)
    setv(g2mp.Waveform,3) # square
    setv(g2mp.Active,1-getv(nmmp.Mute))
    setv(g2mp.FreqMode,[2,3,1][nmm.modes[0].value])

    self.inputs[0],fmmod,fmparam = handlemst(self)
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
    self.inputs[0],fmmod,fmparam = handlemst(self)
    self.inputs[1] = handlefm(self,fmmod,fmparam)

class ConvOscSlvD(ConvOscSlvC):
  waveform = 1 # tri

class ConvOscSlvE(ConvOscSlvC):
  waveform = 0 # sine
   
  def domodule(self):
    ConvOscSlvC.domodule(self)
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.FmAmount,phase[getv(nmmp.FmMod)])
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
      if getv(getattr(nmmp,'Osc%dMute'%i))==0:
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
      setv(osc.params.FreqMode,2) 
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
      print oscs
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
    setv(g2mp.Kbt,0)
    setv(g2mp.FreqMode,[1,0][nmm.modes[0].value])

    # add AM if needed
    if len(nmm.inputs.Am.cables):
      sh = self.addmodule('S&H',name='Amp In')
      levmult = self.addmodule('LevMult',name='Out')
      self.connect(g2m.inputs.Trig,sh.inputs.Ctrl)
      self.connect(g2m.outputs.Out,levmult.inputs.In)
      self.connect(sh.outputs.Out,levmult.inputs.Mod)
      self.inputs[1] = sh.inputs.In
      self.outputs[0] = levmult.outputs.Out
      
    # add pitchmod if needed
    if len(nmm.inputs.PitchMod.cables):
      adj = self.addmodule('Mix2-1B',name='PitchAdj1-%d' % pitchmodnum)
      self.connect(adj.outputs.Out,g2m.inputs.PitchVar)
      self.connect(adj.inputs.Chain,adj.inputs.In1)
      self.connect(adj.inputs.In1,adj.inputs.In2)

      pmod = getv(nmm.params.PitchMod)
      setv(g2mp.PitchMod,modtable[pmod][0])
      setv(adj.params.Inv2, 1)
      setv(adj.params.Lev1,modtable[pmod][1])
      setv(adj.params.Lev2,modtable[pmod][2])

      self.inputs[2] =  adj.inputs.Chain

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

    updatevals(g2mp,['MasterDecay','SlaveDecay','NoiseFltDecay','BendDecay'],
        nm1adsrtime,g2adsrtime)

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))
