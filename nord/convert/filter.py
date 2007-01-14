#
# filter.py - Filter tab conversion objects
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
from units import *

class ConvFilter(Convert):
  def domodule(self):
    updatevals(self.g2module.params,['Freq'],nm1fltfreq,g2fltfreq)

class ConvFilterA(ConvFilter):
  maing2module = 'FltLP'
  parammap = ['Freq']
  inputmap = ['In']
  outputmap = ['Out']

class ConvFilterB(ConvFilter):
  maing2module = 'FltHP'
  parammap = ['Freq']
  inputmap = ['In']
  outputmap = ['Out']

class ConvFilterC(ConvFilter):
  maing2module = 'FltMulti'
  parammap = ['Freq','Res',['GC','GainControl']]
  inputmap = ['In']
  outputmap = ['LP','BP','HP']

class ConvFilterD(ConvFilter):
  maing2module = 'FltMulti'
  parammap = ['Freq',None,'Res',['PitchMod','FreqMod']]
  inputmap = ['PitchVar','In']
  outputmap = ['HP','BP','LP']

  def domodule(self):
    ConvFilter.domodule(self)
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

  def postmodule(self):
    self.kbt = self.g2module.params.Kbt
    handlekbt(self,self.g2module.inputs.Pitch,4) # 4=Kbt 100%

# copied from convert.py for osc.py (maybe it can be unified?)
def fltdualpitchmod(nmm,g2m,conv,mod1,mod2):
  p1 = p2 = None
  if len(nmm.inputs.FreqMod1.cables) and len(nmm.inputs.FreqMod2.cables):
    mix21b = conv.addmodule('Mix2-1B',name='FreqMod')
    setv(mix21b.params.ExpLin,1) # lin
    conv.connect(mix21b.outputs.Out,g2m.inputs.PitchVar)
    setv(g2m.params.PitchMod,127)
    p1,p2 = mix21b.inputs.In1,mix21b.inputs.In2
    setv(mix21b.params.Lev1,getv(nmm.params.FreqMod1))
    conv.params[mod1] = mix21b.params.Lev1
    setv(mix21b.params.Lev2,getv(nmm.params.FreqMod2))
    conv.params[mod2] = mix21b.params.Lev2
  elif len(nmm.inputs.FreqMod1.cables):
    p1 = g2m.inputs.PitchVar
    setv(g2m.params.PitchMod,getv(nmm.params.FreqMod1))
    conv.params[mod1] = g2m.params.PitchMod
  elif len(nmm.inputs.FreqMod2.cables):
    p2 = g2m.inputs.PitchVar
    setv(g2m.params.PitchMod,getv(nmm.params.FreqMod2))
    conv.params[mod2] = g2m.params.PitchMod

  return p1, p2

class ConvFilterE(ConvFilter):
  maing2module = 'FltNord'
  parammap = ['FilterType',['GC','GainControl'],None,
              'Freq',None,'ResMod','Res',
              'Slope',None,['Active','Bypass']]
  inputmap = ['PitchVar','Res','In',None]
  outputmap = ['Out']

  def domodule(self):
    ConvFilter.domodule(self)
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Active,1-getv(nmmp.Bypass))
    # handle special inputs
    p1,p2 = fltdualpitchmod(nmm,g2m,self,2,8)
    self.inputs[0] = p1
    self.inputs[3] = p2

  def postmodule(self):
    self.kbt = self.g2module.params.Kbt
    handlekbt(self,self.g2module.inputs.Pitch,4) # 4=Kbt 100%

class ConvFilterF(ConvFilter):
  maing2module = 'FltClassic'
  parammap = ['Freq',None,'Res',None,None,
              'Slope',['Active','Bypass']]
  inputmap = ['PitchVar',None,'In',None]
  outputmap = ['Out']

  def domodule(self):
    ConvFilter.domodule(self)
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Active,1-getv(nmmp.Bypass))
    # handle special inputs
    p1,p2 = fltdualpitchmod(nmm,g2m,self,3,4)
    self.inputs[0:2] = p1,p2

  def postmodule(self):
    self.kbt = self.g2module.params.Kbt
    handlekbt(self,self.g2module.inputs.Pitch,4) # 4=Kbt 100%

class ConvVocalFilter(ConvFilter):
  maing2module = 'FltVoice'
  parammap = ['Vowel1','Vowel2','Vowel3','Level','Vowel','VowelMod',
              'Freq','FreqMod', 'Res']
  inputmap = ['In','VowelMod','FreqMod']
  outputmap = ['Out']

class ConvVocoder(Convert):
  maing2module = 'Vocoder'
  parammap = ['Band%d' % i for i in range(1,17)]+[None,'Emphasis','Monitor']
  inputmap = ['Ctrl','In']
  outputmap = ['Out']

class ConvFilterBank(Convert):
  maing2module = 'LevAmp'
  parammap = [None]*14
  inputmap = ['In']
  outputmap = [None]

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Type,0) # Lin
    setv(g2mp.Gain,44)

    hc18 = self.addmodule('FltLP',name='HC 1-8')
    hc18.modes.SlopeMode.value = 2 # 18
    setv(hc18.params.Kbt,0)
    setv(hc18.params.Freq,87)
    self.connect(g2m.outputs.Out,hc18.inputs.In)

    lp1 = self.addmodule('FltLP',name='')
    lp1.modes.SlopeMode.value = 1 # 12
    setv(lp1.params.Kbt,0)
    setv(lp1.params.Freq,55)
    self.connect(hc18.outputs.Out,lp1.inputs.In)

    band13 = self.addmodule('FltLP',name='1-3')
    band13.modes.SlopeMode.value = 2 # 18
    setv(band13.params.Kbt,0)
    setv(band13.params.Freq,36)
    self.connect(lp1.outputs.Out,band13.inputs.In)

    band45 = self.addmodule('FltStatic',name='4-5')
    setv(band45.params.Freq,51)
    setv(band45.params.Res,44)
    setv(band45.params.FilterType,1) # BP
    setv(band45.params.GC,1)
    self.connect(band13.inputs.In,band45.inputs.In)

    band45out = self.addmodule('LevConv',name='4-5 Out')
    setv(band45out.params.InputType,0) # Bip
    setv(band45out.params.OutputType,5) # BipInv
    self.connect(band45.outputs.Out,band45out.inputs.In)

    lc68 = self.addmodule('FltHP',name='LC 6-8')
    lc68.modes.SlopeMode.value = 1 # 12
    setv(lc68.params.Kbt,0)
    setv(lc68.params.Freq,57)
    self.connect(lp1.inputs.In,lc68.inputs.In)

    levconv1 = self.addmodule('LevConv',name='')
    setv(levconv1.params.InputType,0) # Bip
    setv(levconv1.params.OutputType,5) # BipInv
    self.connect(lc68.outputs.Out,levconv1.inputs.In)

    band6 = self.addmodule('FltStatic',name='6')
    setv(band6.params.Freq,57)
    setv(band6.params.Res,75)
    setv(band6.params.FilterType,1) # BP
    setv(band6.params.GC,0)
    self.connect(levconv1.outputs.Out,band6.inputs.In)

    band7 = self.addmodule('FltStatic',name='7')
    setv(band7.params.Freq,65)
    setv(band7.params.Res,74)
    setv(band7.params.FilterType,1) # BP
    setv(band7.params.GC,1)
    self.connect(band6.inputs.In,band7.inputs.In)

    band8 = self.addmodule('FltStatic',name='8')
    setv(band8.params.Freq,71)
    setv(band8.params.Res,74)
    setv(band8.params.FilterType,1) # BP
    setv(band8.params.GC,1)
    self.connect(band7.inputs.In,band8.inputs.In)

    lc914 = self.addmodule('FltHP',name='LC 9-14')
    lc914.modes.SlopeMode.value = 3 # 24
    setv(lc914.params.Kbt,0)
    setv(lc914.params.Freq,76)
    self.connect(hc18.inputs.In,lc914.inputs.In)

    band910 = self.addmodule('FltStatic',name='9-10')
    setv(band910.params.Freq,83)
    setv(band910.params.Res,29)
    setv(band910.params.FilterType,1) # BP
    setv(band910.params.GC,0)
    self.connect(lc914.outputs.Out,band910.inputs.In)

    band1112 = self.addmodule('FltStatic',name='11-12')
    setv(band1112.params.Freq,97)
    setv(band1112.params.Res,30)
    setv(band1112.params.FilterType,1) # BP
    setv(band1112.params.GC,0)
    self.connect(band910.inputs.In,band1112.inputs.In)

    band1314 = self.addmodule('FltHP',name='13-14')
    band1314.modes.SlopeMode.value = 3 # 24
    setv(band1314.params.Kbt,0)
    setv(band1314.params.Freq,99)
    self.connect(band910.inputs.In,band1314.inputs.In)

    band1314out = self.addmodule('LevConv',name='13-14 Out')
    setv(band1314out.params.InputType,0) # Bip
    setv(band1314out.params.OutputType,5) # BipInv
    self.connect(band1314.outputs.Out,band1314out.inputs.In)

    mixfader = self.addmodule('MixFader',name='FilterBank')
    mixfaderp = mixfader.params
    onnms = ['1-3','4-5','6','7','8','9-10','11-12','13-14']
    setv(mixfaderp.ExpLin,2) # dB
    for i in range(len(onnms)):
      onp = getattr(mixfaderp,'On%d'%(i+1))
      setv(onp,1)
      onp.labels = [onnms[i]]
    def gv(p,nm):
      return getv(getattr(p,nm))
    setv(mixfaderp.Lev1,
       (gv(nmmp,'50')+gv(nmmp,'75')+gv(nmmp,'110'))/3)
    setv(mixfaderp.Lev2,(gv(nmmp,'170')+gv(nmmp,'250'))/2)
    setv(mixfaderp.Lev3,gv(nmmp,'380'))
    setv(mixfaderp.Lev4,gv(nmmp,'570'))
    setv(mixfaderp.Lev5,gv(nmmp,'850'))
    setv(mixfaderp.Lev6,(gv(nmmp,'1.3')+gv(nmmp,'1.9'))/2)
    setv(mixfaderp.Lev7,(gv(nmmp,'2.9')+gv(nmmp,'4.2'))/2)
    setv(mixfaderp.Lev8,(gv(nmmp,'6.4')+gv(nmmp,'8.3'))/2)
    self.connect(band13.outputs.Out,mixfader.inputs.In1)
    self.connect(band45out.outputs.Out,mixfader.inputs.In2)
    self.connect(band6.outputs.Out,mixfader.inputs.In3)
    self.connect(band7.outputs.Out,mixfader.inputs.In4)
    self.connect(band8.outputs.Out,mixfader.inputs.In5)
    self.connect(band910.outputs.Out,mixfader.inputs.In6)
    self.connect(band1112.outputs.Out,mixfader.inputs.In7)
    self.connect(band1314out.outputs.Out,mixfader.inputs.In8)

    mix11a = self.addmodule('Mix1-1A',name='Out/Boost')
    setv(mix11a.params.On,1)
    mix11a.params.On.labels = ['Out']
    setv(mix11a.params.Lev,110)
    self.connect(mixfader.outputs.Out,mix11a.inputs.Chain)
    self.connect(mix11a.outputs.Out,mix11a.inputs.In)

    self.outputs[0] = mix11a.outputs.Out


class ConvEqMid(ConvFilter):
  maing2module = 'EqPeak'
  parammap = ['Freq','Gain','Bandwidth',['Active','Bypass'],'Level']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Active,1-getv(nmmp.Bypass))

class ConvEqShelving(ConvFilter):
  maing2module = 'EqPeak'
  parammap = ['Freq','Gain',None,['Active','Bypass'],'Level']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Bandwidth,0)
    setv(g2mp.Active,1-getv(nmmp.Bypass))

