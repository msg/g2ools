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
from nord.utils import setv, getv, isnm1lfo
from nord.units import nm1adsrtime, g2adsrtime, adsrtime_map
from nord.nm1.colors import nm1conncolors
from nord.g2.colors import g2conncolors
from nord.convert.convert import Convert, \
    handleoscmasterslv, doslvcables, handlekbt, updatevals
from nord.convert.table import modtable, fmamod, fmbmod

def handlepw(conv, pw, haspw, shape, shapemod):
  nmm, g2m = conv.nmmodule, conv.g2module
  nmmp, g2mp = nmm.params, g2m.params
  # add mix2-1b so input can be doubled/inverted
  pwmod = None
  if haspw:
    pw = getv(nmmp.PulseWidth)
  else:
    pw = 0
  if len(nmm.inputs.PwMod.cables):
    clip = conv.add_module('Clip', name='PWLimit')
    setv(clip.params.Shape, 1) # Sym
    mix11a = conv.add_module('Mix1-1A', name='ShapeMod')
    setv(mix11a.params.ExpLin, 1) # Lin
    setv(mix11a.params.On, 1)
    mix11a.params.On.labels = ['Mod']
    if haspw and pw != 64:
      constswt = conv.add_module('ConstSwT', name='Shape')
      setv(constswt.params.On, 1)
      constswt.params.On.labels = ['Shape']
    mix21b = conv.add_module('Mix2-1B', name='ModIn')
    conv.connect(clip.outputs.Out, g2m.inputs.ShapeMod)
    conv.connect(mix11a.outputs.Out, clip.inputs.In)
    if haspw and pw != 64:
      conv.connect(constswt.outputs.Out, mix11a.inputs.Chain)
      conv.connect(mix21b.outputs.Out, mix11a.inputs.In)
      setv(constswt.params.Lev, pw)
    else:
      conv.connect(mix21b.outputs.Out, mix11a.inputs.In)
    conv.connect(mix21b.inputs.In1, mix21b.inputs.In2)
    setv(clip.params.ClipLev, 2)
    setv(mix21b.params.Lev1, 126)
    setv(mix21b.params.Lev2, 127)
    setv(g2mp.Shape, 0)
    setv(g2mp.ShapeMod, 127)
    setv(mix11a.params.Lev, getv(nmmp.PwMod))
    conv.params[shapemod] = mix11a.params.Lev
    if shape > -1 and pw != 64:
      conv.params[shape] = constswt.params.Lev
    return mix21b.inputs.In1
  elif haspw and pw != 64:
    constswt = conv.add_module('ConstSwT', name='Shape')
    setv(constswt.params.On, 1)
    constswt.params.On.labels = ['Shape']
    setv(constswt.params.Lev, pw)
    setv(g2mp.Shape, 0)
    setv(g2mp.ShapeMod, 126)
    conv.connect(constswt.outputs.Out, g2m.inputs.ShapeMod)
  return pwmod

class ModIndexes:
  def __init__(self):
    self.reset()

  def reset(self):
    self.__dict__['__values__'] = {}
  
  def __getattr__(self, name):
    d = self.__dict__['__values__']
    if not d.has_key(name):
      d[name] = 1
    ret = d[name]
    d[name] += 1
    return ret

modindex = ModIndexes()

def pitchadj(conv, pitchparam, pitchinput, tableentry):
  global modindex
  setv(pitchparam, tableentry[0])
  if tableentry[1] == 0 and tableentry[2] == 0:
    return pitchinput
  adj1 = conv.add_module('Mix2-1B', name='PitchAdj%d' % modindex.pitchadj)
  conv.connect(adj1.inputs.Chain, adj1.inputs.In1)
  conv.connect(adj1.inputs.In1, adj1.inputs.In2)
  conv.connect(adj1.outputs.Out, pitchinput)
  setv(adj1.params.Inv2, 1)
  setv(adj1.params.Lev1, tableentry[1])
  setv(adj1.params.Lev2, tableentry[2])
  return adj1.inputs.Chain

# handledualpitchmod -> p1, p2
# handle pitch inputs and if necessary, create a Mix2-1B for input
# NOTE: could check the PitchMod1 and PitchMod2 for maximum modulation.
#       in that case, the Pitch input could be used (if no knob tied
#       to the said PitchModX dial).
def handledualpitchmod(conv, modinput, modinputparam, mod1param, mod2param):
  global modindex
  nmm, g2m = conv.nmmodule, conv.g2module
  p1 = p2 = None

  mix21b = None

  pmod1 = getv(nmm.params.PitchMod1)
  pmod2 = getv(nmm.params.PitchMod2)

  if len(nmm.inputs.PitchMod1.cables) and len(nmm.inputs.PitchMod2.cables):
    setv(modinputparam, 127)

    mix21b = conv.add_module('Mix2-1B', name='PitchMod%d' % modindex.pitchmod)
    conv.connect(mix21b.outputs.Out, modinput)

    if pmod1 == 0 or pmod1 == 127:
      setv(mix21b.params.Lev1, pmod1)
      p1 = mix21b.inputs.In1
    elif pmod1:
      p1 = pitchadj(conv, mix21b.params.Lev1, mix21b.inputs.In1,
          modtable[pmod1])
    else:
      p1 = mix21b.inputs.In1

    if pmod2 == 0 or pmod2 == 127:
      setv(mix21b.params.Lev2, pmod2)
      p2 = mix21b.inputs.In2
    elif pmod2:
      p2 = pitchadj(conv, mix21b.params.Lev2, mix21b.inputs.In2,
          modtable[pmod2])

    conv.params[mod1param] = mix21b.params.Lev1
    conv.params[mod2param] = mix21b.params.Lev2

  elif len(nmm.inputs.PitchMod1.cables):
    if pmod1 == 0  or pmod1 == 127:
      setv(modinputparam, pmod1)
      p1 = modinput
    else:
      p1 = pitchadj(conv, modinputparam, modinput, modtable[pmod1])

    conv.params[mod1param] = modinputparam

  elif len(nmm.inputs.PitchMod2.cables):
    if pmod2 == 0 or pmod2 == 127:
      setv(modinputparam, pmod2)
      p2 = modinput
    else:
      p2 = pitchadj(conv, modinputparam, modinput, modtable[pmod2])

    conv.params[mod2param] = modinputparam

  return p1, p2

def handlefm(conv, fminput, fmparam, fmtable):
  global modindex
  nmm, g2m = conv.nmmodule, conv.g2module
  if len(nmm.inputs.FmMod.cables) == 0:
    return fminput
  fma = getv(nmm.params.FmMod)
  if fmparam and fminput:
    setv(fmparam, fmtable[fma][0])
  if fma:
    if fmtable[fma][1] == 0 and fmtable[fma][2] == 0:
      return fminput
    mix21b = conv.add_module('Mix2-1B', name='FmMod%d' % modindex.fmmod)
    conv.connect(mix21b.outputs.Out, fminput)
    conv.connect(mix21b.inputs.Chain, mix21b.inputs.In1)
    conv.connect(mix21b.inputs.In1, mix21b.inputs.In2)
    setv(mix21b.params.Lev1, fmtable[fma][1])
    setv(mix21b.params.Inv2, 1)
    setv(mix21b.params.Lev2, fmtable[fma][2])
    return mix21b.inputs.Chain
  return fminput

def handleam(conv):
  global modindex
  nmm, g2m = conv.nmmodule, conv.g2module
  aminput = None
  output = g2m.outputs.Out
  if len(nmm.inputs.Am.cables):
    am = conv.add_module('LevMult', name='AM%d' % modindex.ammod)
    conv.connect(g2m.outputs.Out, am.inputs.In)
    aminput = am.inputs.Mod
    output = am.outputs.Out
  return aminput, output

def handleslv(conv):
  global modindex
  conv.nonslaves = []
  conv.slaves = []
  nmm, g2m = conv.nmmodule, conv.g2module
  if len(nmm.outputs.Slv.cables):
    # add a masterosc
    master = conv.add_module('OscMaster', name='SlvOut%d' % modindex.slvout)
    setv(g2m.params.Kbt, 0)
    conv.kbt = master.params.Kbt
    conv.connect(master.outputs.Out, g2m.inputs.Pitch)
    setv(master.params.FreqCoarse, getv(g2m.params.FreqCoarse))
    setv(master.params.FreqFine, getv(g2m.params.FreqFine))
    setv(master.params.FreqMode, getv(g2m.params.FreqMode))
    setv(master.params.PitchMod, getv(g2m.params.PitchMod))
    setv(g2m.params.FreqCoarse, 64)
    setv(g2m.params.FreqFine, 64)
    out = handleoscmasterslv(conv, master, 44, 64, 69, 103, 42)
    if out:
      return out, master
    else:
      return g2m.inputs.Pitch, master
  else:
    conv.kbt = g2m.params.Kbt
    return None, g2m

def handlemst(conv, fmmod, fmparam):
  global modindex
  nmm, g2m = conv.nmmodule, conv.g2module
  mst = g2m.inputs.Pitch

  if not len(nmm.inputs.Mst.cables):
    return mst, fmmod, fmparam

  if not nmm.inputs.Mst.net.output:
    return mst, fmmod, fmparam

  if nmm.inputs.Mst.net.output.rate == nm1conncolors.slave:
    return mst, fmmod, fmparam

  # Blue to Grey handling
  coarsefreq = getv(nmm.params.DetuneCoarse)
  if hasattr(nmm.inputs, 'FmMod'):
    hasfmmod = len(nmm.inputs.FmMod.cables) != 0
  else:
    hasfmmod = False
  
  if not hasfmmod and coarsefreq == 64:
    setv(g2m.params.FreqCoarse, 0)
    if fmparam:
      setv(fmparam, 79)
      mst = g2m.inputs.FmMod
    return mst, fmmod, fmparam
    
  if coarsefreq != 64:
    # OscC/ZeroCnt
    tune = conv.add_module('Mix2-1B', name='Tune')
    setv(tune.params.Inv2, 1)
    setv(tune.params.Lev1, 32)
    setv(tune.params.Lev2, 11)
    conv.connect(tune.inputs.Chain, tune.inputs.In1)
    conv.connect(tune.inputs.In1, tune.inputs.In2)

    greyto = conv.add_module('OscC', name='Grey To')
    setv(greyto.params.FreqCoarse, 0)
    setv(greyto.params.FmAmount, 79)
    greyto.modes.Waveform.value = 0 # Sine
    conv.connect(tune.outputs.Out, greyto.inputs.FmMod)

    zerocnt = conv.add_module('ZeroCnt', name='Pitch')
    conv.connect(greyto.outputs.Out, zerocnt.inputs.In)

    conv.connect(zerocnt.outputs.Out, g2m.inputs.Pitch)

    mst = tune.inputs.Chain
    return mst, fmmod, fmparam

  setv(g2m.params.FreqCoarse, 0)

  mstinnum = modindex.mstin
  mix11a = conv.add_module('Mix1-1A', name='MstIn%d' % mstinnum)
  setv(mix11a.params.On, 1)
  setv(mix11a.params.Lev, 79)
  conv.connect(mix11a.outputs.Out, fmmod)

  setv(fmparam, 127)

  mst = mix11a.inputs.In
  fmmod, fmparam = None, None
  if hasfmmod:
    fmmodinput = conv.add_module('Mix1-1A', name='FMA%d' % mstinnum)
    setv(fmmodinput.params.On, 1)
    conv.connect(fmmodinput.outputs.Out, mix11a.inputs.Chain)
    fmparam = fmmodinput.params.Lev
    fmmod = fmmodinput.inputs.In

  return mst, fmmod, fmparam

def postmst(conv, mstindex):
  nmm, g2m = conv.nmmodule, conv.g2module
  nmmp, g2mp = nmm.params, g2m.params

  mstin = nmm.inputs.Mst
  if not len(mstin.cables):
    return
  if not mstin.net.output or mstin.net.output.rate != nm1conncolors.slave:
    return
  mstconv = mstin.net.output.module.conv
  mst = mstconv.g2module

  if not isnm1lfo(mstconv.nmmodule):
    return

  if not hasattr(mst.params, 'Range'):
    return

  prange = getv(mst.params.Range)
  if prange < 2: # sub or lo
    # insert LevAdd with -48
    levadd = conv.add_module('LevAdd', name='-48')
    conv.connect(levadd.outputs.Out, conv.inputs[mstindex])
    setv(levadd.params.BipUni, 0) # Bip
    setv(levadd.params.Level, 16) # -48
    conv.inputs[mstindex] = levadd.inputs.In
  if prange == 0:
    # NOTE: handle sine bank
    if nmm.type.shortnm == 'OscSineBank':
      for osc in conv.oscs:
        oscp = osc.params
        setv(oscp.FreqCoarse, max(0, getv(oscp.FreqCoarse)-79))
        setv(oscp.FreqFine, min(127, getv(oscp.FreqFine)+42))
    else:
      setv(g2mp.FreqCoarse, max(0, getv(g2mp.FreqCoarse)-79))
      setv(g2mp.FreqFine, min(127, getv(g2mp.FreqFine)+42))

class ConvMasterOsc(Convert):
  maing2module = 'OscMaster'
  parammap = ['FreqCoarse', 'FreqFine', 'Kbt', None, None]
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.FreqMode, [1, 0][nmm.modes[0].value])

    # handle special inputs
    p1, p2 = handledualpitchmod(self, g2m.inputs.PitchVar, g2m.params.PitchMod,
        3, 4)
    self.inputs[:2] = [p1, p2]
    self.outputs[0] = handleoscmasterslv(self, g2m, 44, 64, 69, 103, 42)

  def precables(self):
    doslvcables(self)

class ConvOscA(Convert):
  maing2module = 'OscB'
  parammap = ['FreqCoarse', 'FreqFine', None, ['Shape', 'PulseWidth'],
              'Waveform', None, None,
              ['FmAmount', 'FmMod'], ['ShapeMod', 'PwMod'], ['Active', 'Mute']]
  inputmap = [ 'Sync', 'FmMod', '', '', 'ShapeMod' ]
  outputmap = [ 'Out', '' ]

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.Shape, 0)
    # handle special parameters
    self.inputs[4] = handlepw(self, getv(nmmp.PulseWidth), 1, 3, 8)

    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.FreqMode, [1, 0][nmm.modes[0].value])

    # handle special inputs/outputs
    self.outputs[1], inputmod = handleslv(self)
    self.inputmod = inputmod
    inp = inputmod.params
    self.params[:3] = inp.FreqCoarse, inp.FreqFine, inp.Kbt
    p1, p2 = handledualpitchmod(self, inputmod.inputs.PitchVar,
        inputmod.params.PitchMod, 5, 6)
    self.inputs[2:4] = p1, p2

    self.inputs[1] = handlefm(self, g2m.inputs.FmMod, g2mp.FmAmount, fmamod)
    handlekbt(self, self.inputmod.inputs.Pitch, 1) # 0=off, 1=on

  def precables(self):
    doslvcables(self)

class ConvOscB(Convert):
  maing2module = 'OscB'
  parammap = ['FreqCoarse', 'FreqFine', None, 'Waveform', None, None,
              ['FmAmount', 'FmMod'], ['ShapeMod', 'PwMod'], ['Active', 'Mute']]
  inputmap = [ 'FmMod', '', '', 'ShapeMod' ]
  outputmap = [ 'Out', '' ]

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    # handle special special parameters
    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.FreqMode, [1, 0][nmm.modes[0].value])

    setv(g2mp.Shape, 0)
    if getv(g2mp.Waveform) == 3:
      pwmod = handlepw(self, 64, 0, -1, 7)
      if pwmod:
        notequant = self.add_module('NoteQuant', name='BlueRate')
        self.connect(notequant.outputs.Out, pwmod)
        setv(notequant.params.Range, 127)
        setv(notequant.params.Notes, 0)
        self.inputs[3] = notequant.inputs.In

    # handle special inputs
    self.outputs[1], inputmod = handleslv(self)
    self.inputmod = inputmod
    inp = inputmod.params
    self.params[:3] = inp.FreqCoarse, inp.FreqFine, inp.Kbt
    p1, p2 = handledualpitchmod(self, inputmod.inputs.PitchVar,
        inputmod.params.PitchMod, 4, 5)
    self.inputs[1:3] = p1, p2
    self.inputs[0] = handlefm(self, g2m.inputs.FmMod, g2mp.FmAmount, fmamod)
    handlekbt(self, self.inputmod.inputs.Pitch, 1) # 0=off, 1=on

  def precables(self):
    doslvcables(self)

class ConvOscC(Convert):
  maing2module = 'OscC'
  parammap = ['FreqCoarse', 'FreqFine', 'Kbt', ['PitchMod', 'FreqMod'],
      ['FmAmount', 'FmMod'], ['Active', 'Mute']]
  inputmap = [ 'FmMod', 'Pitch', '']
  outputmap = [ 'Out', '' ]

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    # make OscC's waveform a sine
    g2m.modes.Waveform.value = 0

    # handle special parameters
    # handle KBT later = nmmp.FreqKbt)
    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.FreqMode, [1, 0][nmm.modes[0].value])
    
    self.inputs[0] = handlefm(self, g2m.inputs.FmMod, g2mp.FmAmount, fmamod)
    # add AM if needed, handle special io
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[2] = aminput
    self.outputs[1], inputmod = handleslv(self)
    inp = inputmod.params
    self.params[:4] = inp.FreqCoarse, inp.FreqFine, inp.Kbt, inp.PitchMod
    self.inputs[1] = inputmod.inputs.PitchVar
    inp = inputmod.params
    self.params[:4] = inp.FreqCoarse, inp.FreqFine, inp.Kbt, inp.PitchMod

  def precables(self):
    doslvcables(self)

class ConvSpectralOsc(Convert):
  maing2module = 'OscShpA'
  #                                  SpShp, Part, PMd1, PMd2
  parammap = ['FreqCoarse', 'FreqFine', None, None, None, None,
  #                                ShpM
              ['FmAmount', 'FmMod'], None, 'Kbt', ['Active', 'Mute']]
  inputmap = ['FmMod', '', '', '']
  outputmap = ['', '']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    # NOTE: this must be done before adding the rest of the structure
    #       as it should be placed right below the OscC.
    self.outputs[1], inputmod = handleslv(self)
    inp = inputmod.params
    self.params[:2] = inp.FreqCoarse, inp.FreqFine
    self.params[8] = inp.Kbt
    p1, p2 = handledualpitchmod(self, inputmod.inputs.PitchVar,
        inputmod.params.PitchMod, 4, 5)
    self.inputs[1:3] = p1, p2
    self.inputs[0] = handlefm(self, g2m.inputs.FmMod, g2mp.FmAmount, fmamod)

    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.Waveform, [3, 2][getv(nmmp.Partials)])
    self.params[3] = g2mp.Waveform
    setv(g2mp.FreqMode, [1, 0][nmm.modes[0].value])
    setv(g2mp.ShapeMod, 125)
    setv(g2mp.Shape, 2)

    shape = self.add_module('ConstSwT', name='Shape')
    setv(shape.params.BipUni, 1) # Uni
    setv(shape.params.On, 1)
    shape.params.On.labels = ['Shape']
    setv(shape.params.Lev, getv(nmmp.Shape))
    self.params[2] = shape.params.Lev

    hasshapemod = len(nmm.inputs.ShapeMod.cables) != 0
    if hasshapemod:
      shapemod = self.add_module('Mix1-1A', name='ShapeMod')
      setv(shapemod.params.ExpLin, 1) # Line
      setv(shapemod.params.On, 1)
      shapemod.params.On.labels = ['Amount']
      setv(shapemod.params.Lev, getv(nmmp.ShapeMod))
      self.params[7] = shapemod.params.Lev
      self.inputs[3] = shapemod.inputs.In

    levmult = self.add_module('LevMult')
    levmult2 = self.add_module('LevMult')

    out = self.add_module('Mix2-1A', name='Out')
    setv(out.params.ExpLin, 1) # Lin
    setv(out.params.On1, 1)
    out.params.On1.labels = ['High']
    setv(out.params.Lev1, 127)
    setv(out.params.On2, 1)
    out.params.On2.labels = ['Low']
    setv(out.params.Lev2, 98)

    output = self.add_module('Mix1-1A', name='Output')
    setv(output.params.ExpLin, 1) # Line
    setv(output.params.On, 1)
    output.params.On.labels = ['Output']
    setv(output.params.Lev, 79)

    self.connect(g2m.outputs.Out, levmult2.inputs.In)
    if hasshapemod:
      self.connect(shape.outputs.Out, shapemod.inputs.Chain)
      self.connect(shapemod.outputs.Out, g2m.inputs.ShapeMod)
      self.connect(shapemod.outputs.Out, levmult.inputs.In)
    else:
      self.connect(shape.outputs.Out, g2m.inputs.ShapeMod)
      self.connect(shape.outputs.Out, levmult.inputs.In)
    self.connect(levmult.inputs.In, levmult.inputs.Mod)
    self.connect(levmult.outputs.Out, levmult2.inputs.Mod)
    self.connect(levmult2.inputs.In, out.inputs.In2)
    self.connect(levmult2.outputs.Out, out.inputs.In1)
    self.connect(out.inputs.In1, out.inputs.Chain)
    self.connect(out.outputs.Out, output.inputs.Chain)
    self.connect(output.outputs.Out, output.inputs.In)

    self.outputs[0] = output.outputs.Out

class ConvFormantOsc(Convert):
  maing2module = 'OscC'                                    #Timbre, PMod1, PMod2
  parammap = ['FreqCoarse', 'FreqFine', 'Kbt', None, None, None, None]
  inputmap = ['', '', '']
  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.FreqMode, [1, 0][nmm.modes[0].value])
    # handle special inputs
    # NOTE: this must be done before adding the rest of the structure
    #       as it should be placed right below the OscC.
    p1, p2 = handledualpitchmod(self, g2m.inputs.PitchVar, g2m.params.PitchMod,
        5, 6)
    self.inputs[:2] = p1, p2

    timbreinput = nmm.inputs.Timbre.net != None
    if timbreinput:
      modnms = ['Invert', 'RndClkB', 'EqPeak', 'Mix4-1A',
                'ConstSwT', 'NoteQuant', 'LevAmp']
    else:
      modnms = ['Invert', 'RndClkB', 'EqPeak', 'ConstSwT']

    modules = [ None ] * len(modnms)
    for i, modnm in enumerate(modnms):
      mod = self.add_module(modnm, name=modnm)
      modules[i] = mod

    if timbreinput:
      inv, rndclkb, eqpeak, mix41a, constswt, notequant, levamp = modules
    else:
      inv, rndclkb, eqpeak, constswt = modules

    self.connect(g2m.outputs.Out, inv.inputs.In2)
    self.connect(inv.inputs.In2, rndclkb.inputs.Rst)
    self.connect(inv.outputs.Out1, inv.inputs.In1)
    self.connect(inv.inputs.In1, rndclkb.inputs.Clk)
    self.connect(rndclkb.outputs.Out, eqpeak.inputs.In)
    if timbreinput:
      self.connect(mix41a.outputs.Out, rndclkb.inputs.Seed)
      self.connect(constswt.outputs.Out, mix41a.inputs.In4)
      setv(constswt.params.On, 1)
      self.connect(notequant.outputs.Out, mix41a.inputs.In3)
      self.connect(levamp.outputs.Out, notequant.inputs.In)
    else:
      self.connect(constswt.outputs.Out, rndclkb.inputs.Seed)

    inv.uprate = 1
    inv.outputs.Out1.rate = g2conncolors.orange
    rndclkb.uprate = 1
    rndclkb.modes.Character.value = 0
    setv(rndclkb.params.StepProb, 61)
    setv(rndclkb.params.Active, 1-getv(nmmp.Mute))
    setv(eqpeak.params.Freq, 109)
    setv(eqpeak.params.Gain, 100)
    setv(eqpeak.params.Bandwidth, 2)
    setv(eqpeak.params.Level, 100)
    setv(constswt.params.Lev, getv(nmm.params.Timbre))
    self.params[4] = constswt.params.Lev

    if timbreinput:
      setv(notequant.params.Range, 127)
      setv(notequant.params.Notes, 1)
      setv(levamp.params.Type, 1)
      setv(levamp.params.Gain, 20)

      self.inputs[2] = levamp.inputs.In

    output, inputmod = handleslv(self)
    inp = inputmod.params
    self.params[:3] = inp.FreqCoarse, inp.FreqFine, inp.Kbt
    self.outputs = [eqpeak.outputs.Out, output]

class ConvOscSlvA(Convert):
  maing2module = 'OscB'
  parammap = [['FreqCoarse', 'DetuneCoarse'], ['FreqFine', 'DetuneFine'],
              'Waveform', ['FmAmount', 'FmMod'], ['Active', 'Mute']]
  inputmap = ['Pitch', 'FmMod', 'Pitch', 'Sync']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Kbt, 0)
    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.FreqMode, [2, 3, 1][nmm.modes[0].value])

    # mst connection if not
    self.inputs[0], fmmod, fmparam = handlemst(self,
        g2m.inputs.FmMod, g2m.params.FmAmount)
    self.inputs[1] = handlefm(self, fmmod, fmparam, fmamod)
    # handle special io
    # add AM if needed
    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs[2] = aminput

    postmst(self, 0)

class ConvOscSlvB(Convert):
  maing2module = 'OscB'
  parammap = [['FreqCoarse', 'DetuneCoarse'], ['FreqFine', 'DetuneFine'],
              ['Shape', 'PulseWidth'], ['ShapeMod', 'PwMod'],
              ['Active', 'Mute']]
  inputmap = ['Pitch', 'ShapeMod']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    self.inputs[1] = handlepw(self, 64, 1, 2, 3)
    # handle special parameters 
    setv(g2mp.Kbt, 0)
    setv(g2mp.Waveform, 3) # square
    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.FreqMode, [2, 3, 1][nmm.modes[0].value])

    self.inputs[0], fmmod, fmparam = handlemst(self,
        g2m.inputs.FmMod, g2m.params.FmAmount)

    postmst(self, 0)

class ConvOscSlvC(Convert):
  maing2module = 'OscC'
  waveform = 2 # saw
  parammap = [['FreqCoarse', 'DetuneCoarse'], ['FreqFine', 'DetuneFine'],
              ['FmAmount', 'FmMod'], ['Active', 'Mute']]
  inputmap = ['Pitch', 'FmMod']
  outputmap = ['Out']

  def __init__(self, nmarea, g2area, nmmodule, options):
    if len(nmmodule.inputs.FmMod.cables) == 0:
      self.parammap[2] = None
      self.inputmap[1] = '' # None
      self.maing2module = 'OscD'
    super(ConvOscSlvC, self).__init__(nmarea, g2area, nmmodule, options)

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Kbt, 0)
    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.FreqMode, [2, 3, 1][nmm.modes[0].value])
    g2m.modes.Waveform.value = self.waveform
    if self.maing2module == 'OscD':
      fmmod = None
      fmamt = None
    else:
      fmmod = g2m.inputs.FmMod
      fmamt = g2m.params.FmAmount
    self.inputs[0], fmmod, fmparam = handlemst(self, fmmod, fmamt)
    self.inputs[1] = handlefm(self, fmmod, fmparam, fmamod)

    postmst(self, 0)

class ConvOscSlvD(ConvOscSlvC):
  waveform = 1 # tri

class ConvOscSlvE(ConvOscSlvC):
  waveform = 0 # sine
   
  def domodule(self):
    super(ConvOscSlvE, self).domodule()
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    aminput, output = handleam(self)
    self.outputs[0] = output
    self.inputs.append(aminput)

def sinepostmst(conv, mstindex):
  nmm, g2m = conv.nmmodule, conv.g2module
  nmmp, g2mp = nmm.params, g2m.params

  mstin = nmm.inputs.Mst
  if not len(mstin.cables):
    return

  if not mstin.net.output:
    return

  mstconv = mstin.net.output.module.conv

  if mstin.net.output.rate != nm1conncolors.slave:
    oscc = conv.add_module('OscC', name='')
    setv(oscc.params.FreqCoarse, 0)
    setv(oscc.params.FmAmount, 79)
    setv(oscc.params.Kbt, 0)
    pout = conv.add_module('ZeroCnt', name='')
    conv.connect(oscc.outputs.Out, pout.inputs.In)
    conv.connect(pout.outputs.Out, conv.inputs[mstindex])
    conv.inputs[mstindex] = oscc.inputs.FmMod
    return

  postmst(conv, mstindex)

class ConvOscSineBank(Convert):
  maing2module = 'Mix8-1B'
  parammap = [ None ] * 24
  outputmap = ['Out']
  #           Mst  Mixin   Sync O1Am O2Am O3Am O4Am O5Am O6Am
  inputmap = ['', 'Chain', '', '', '', '', '', '', '']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    levamp = self.add_module('LevAmp', name='LevAmp')
    setv(levamp.params.Type, 1)
    setv(levamp.params.Gain, 68)
    self.connect(g2m.outputs.Out, levamp.inputs.In)
    self.outputs[0] = levamp.outputs.Out
    # if sync connected, use OscC, otherwise use OscD
    if len(nmm.inputs.Sync.cables):
      osctype = 'OscC'
    else:
      osctype = 'OscD'
    oscs = []
    for i in xrange(6, 0, -1): # 6 Sine Osc
      # if osc muted, don't addit
      if getv(getattr(nmmp, 'Osc%dMute'%i))==0:
        if len(getattr(nmm.inputs, 'Osc%dAm'%i).cables) == 0 and \
           len(nmm.inputs.Sync.cables) == 0 and \
           len(nmm.inputs.Mst.cables) == 0:
          continue
      osc = self.add_module(osctype, name='Osc%d' % i)
      oscs.append(osc)
      setv(osc.params.Kbt, 0)
      setv(osc.params.FreqCoarse, getv(getattr(nmmp, 'Osc%dCoarse'%i)))
      self.params[(i-1)*3] = osc.params.FreqCoarse
      setv(osc.params.FreqFine, getv(getattr(nmmp, 'Osc%dFine'%i)))
      self.params[(i-1)*3+1] = osc.params.FreqFine
      setv(osc.params.FreqMode, 2) 
      l = getattr(g2mp, 'Lev%d' % i)
      setv(l, getv(getattr(nmmp, 'Osc%dLevel'%i)))
      self.params[(i-1)*3+2] = l
      setv(osc.params.Active, 1-getv(getattr(nmmp, 'Osc%dMute'%i)))
      self.params[(i-1)+18] = osc.params.Active
      if len(getattr(nmm.inputs, 'Osc%dAm'%i).cables):
        mod = self.add_module('LevMult', name='Am%d' % i)
        self.connect(osc.outputs.Out, mod.inputs.In)
        self.connect(mod.outputs.Out, getattr(g2m.inputs, 'In%d'%i))
        self.inputs[2+i] = mod.inputs.Mod
      else:
        self.connect(osc.outputs.Out, getattr(g2m.inputs, 'In%d'%i))
    if len(nmm.inputs.Sync.cables):
      self.inputs[2] = oscs[0].inputs.Sync
      if len(oscs) > 1:
        for i in xrange(1, len(oscs)):
          self.connect(oscs[i-1].inputs.Sync, oscs[i].inputs.Sync)
    if len(nmm.inputs.Mst.cables):
      self.inputs[0] = oscs[0].inputs.Pitch
      if len(oscs) > 1:
        for i in xrange(1, len(oscs)):
          self.connect(oscs[i-1].inputs.Pitch, oscs[i].inputs.Pitch)
    self.oscs = oscs

    sinepostmst(self, 0)

class ConvOscSlvFM(Convert):
  maing2module = 'OscPM'
  waveform = 0 # sine
  parammap = [['FreqCoarse', 'DetuneCoarse'], ['FreqFine', 'DetuneFine'],
              None, ['PhaseMod', 'FmMod'], ['Active', 'Mute']]
  inputmap = ['Pitch', 'PhaseMod', 'Sync']
  outputmap = ['Out']
 
  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.Kbt, 0)
    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.FreqMode, [2, 3, 1][nmm.modes[0].value])
    g2m.modes.Waveform.value = self.waveform

    # must happen after handle mst to get Range
    if getv(getattr(nmmp, '-3Oct')):
      freqmode = getv(g2mp.FreqMode)
      nm1freqcoarse = getv(nmmp.DetuneCoarse)
      g2freqcoarse = getv(g2mp.FreqCoarse)
      if freqmode == 3: # Part
        offset = 8
      else:
        offset = 36
      if g2freqcoarse - offset < 0:
        constswt = self.add_module('ConstSwT', name='Offset')
        setv(constswt.params.On, 1)
        constswt.params.On.labels = ['Offset']
        setv(constswt.params.Lev, g2freqcoarse-offset)
        setv(g2mp.PitchVar, 127)
        self.connect(constswt.outputs.Out, g2m.inputs.PitchVar)
      else:
        setv(g2mp.FreqCoarse, g2freqcoarse-offset)
      
    self.inputs[1] = handlefm(self, g2m.inputs.PhaseMod, g2mp.PhaseMod, fmbmod)

    sinepostmst(self, 0)

class ConvNoise(Convert):
  maing2module = 'Noise'
  parammap = ['Color']
  outputmap = ['Out']

class ConvPercOsc(Convert):
  maing2module = 'OscPerc'
  parammap = ['FreqCoarse', 'Click', 'Decay', 'Punch', 'PitchMod', 'FreqFine',
              ['Active', 'Mute']]
  inputmap = ['Trig', '', 'PitchVar']
  outputmap = ['Out']

  def domodule(self):
    global modindex
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Active, 1-getv(nmmp.Mute))
    setv(g2mp.Kbt, 0)
    setv(g2mp.FreqMode, [1, 0][nmm.modes[0].value])

    # add AM if needed
    if len(nmm.inputs.Am.cables):
      sh = self.add_module('S&H', name='Amp In')
      levmult = self.add_module('LevMult', name='Out')
      self.connect(g2m.inputs.Trig, sh.inputs.Ctrl)
      self.connect(g2m.outputs.Out, levmult.inputs.In)
      self.connect(sh.outputs.Out, levmult.inputs.Mod)
      self.inputs[1] = sh.inputs.In
      self.outputs[0] = levmult.outputs.Out
      
    # add pitchmod if needed
    if len(nmm.inputs.PitchMod.cables):
      adj = self.add_module('Mix2-1B', name='PitchAdj1-%d' % modindex.pitchmod)
      self.connect(adj.outputs.Out, g2m.inputs.PitchVar)
      self.connect(adj.inputs.Chain, adj.inputs.In1)
      self.connect(adj.inputs.In1, adj.inputs.In2)

      pmod = getv(nmm.params.PitchMod)
      setv(g2mp.PitchMod, modtable[pmod][0])
      setv(adj.params.Inv2, 1)
      setv(adj.params.Lev1, modtable[pmod][1])
      setv(adj.params.Lev2, modtable[pmod][2])

      self.inputs[2] =  adj.inputs.Chain

class ConvDrumSynth(Convert):
  maing2module = 'DrumSynth'
  parammap = [None]*16
  inputmap = ['Trig', 'Vel', 'Pitch']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    # parameters are exactly the same
    for i in xrange(len(nmm.params)):
      setv(g2mp[i], getv(nmmp[i]))
      self.params[i] = g2mp[i]

    updatevals(g2mp,
        ['MasterDecay', 'SlaveDecay', 'NoiseFltDecay', 'BendDecay'],
        adsrtime_map)

    setv(g2mp.MasterLevel, modtable[getv(g2mp.MasterLevel)][0])
    setv(g2mp.SlaveLevel, modtable[getv(g2mp.SlaveLevel)][0])
    setv(g2mp.BendAmount, modtable[getv(g2mp.BendAmount)][0])
    setv(g2mp.Click, modtable[getv(g2mp.Click)][0])
    setv(g2mp.Noise, modtable[getv(g2mp.Noise)][0])

    # handle special parameters
    setv(g2mp.Active, 1-getv(nmmp.Mute))
