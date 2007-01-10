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

    mix11a = self.addmodule('Mix1-1A',name='Reduction')
    setv(mix11a.params.On,1)
    mix11a.params.On.labels = ['Fix101']
    setv(mix11a.params.Lev,101)
    levamp = self.addmodule('LevAmp',name='HPOut')
    setv(levamp.params.Type,1) # Lin
    setv(levamp.params.Gain,74)
    levamp2 = self.addmodule('LevAmp',name='LPOut')
    setv(levamp2.params.Type,1) # Lin
    setv(levamp2.params.Gain,78)

    self.connect(mix11a.outputs.Out,g2m.inputs.In)
    self.connect(g2m.outputs.HP,levamp.inputs.In)
    self.connect(g2m.outputs.LP,levamp2.inputs.In)
    
    self.inputs[1] = mix11a.inputs.In
    self.outputs[0] = levamp.outputs.Out
    self.outputs[2] = levamp2.outputs.Out

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
  maing2module = 'Mix8-1B'
  parammap = [None]*14
  inputmap = [None]
  outputmap = [None]

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    mix81b = self.addmodule('Mix8-1B',name='Upper')
    self.connect(g2m.outputs.Out,mix81b.inputs.Chain)
    filters = []
    banksettings = [
      ['50',23],['75',29],['110',37],['170',44],
      ['250',50],['380',57],['570',65],
      ['850',71],['1.3',79],['1.9',85],['2.9',93],
      ['4.2',99],['6.4',106],['8.3',111],
    ]
    for i in range(len(banksettings)):
      name,freq = banksettings[i]
      filter = self.addmodule('FltStatic',name=name)
      setv(filter.params.Freq,freq)
      setv(filter.params.GC,1)  # On
      setv(filter.params.FilterType,1) # BP
      setv(filter.params.Res,64)
      if freq > 65:
        self.connect(filter.outputs.Out,mix81b.inputs[i-7])
        setv(mix81b.params[i-7],getv(nmm.params[i-7]))
      else:
        self.connect(filter.outputs.Out,g2m.inputs[i])
        setv(g2m.params[i],getv(nmm.params[i]))
      if i > 0:
        self.connect(filters[i-1].inputs.In,filter.inputs.In)
      filters.append(filter)
    self.inputs[0] = filters[0].inputs.In
    self.outputs[0] = mix81b.outputs.Out

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

