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
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    updatevals(g2m.params,['Freq'],nm1fltfreq,g2fltfreq)

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

  def postmodule(self):
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
  maing2module = 'Eq3Band'
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Active,1-getv(nmmp.Bypass))

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

