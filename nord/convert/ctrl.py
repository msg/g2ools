#
# ctrl.py - Ctrl tab conversion objects
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

class ConvConstant(Convert):
  maing2module = 'Constant'
  parammap = [['Level','Value'],['BipUni','Unipolar']]
  outputmap = ['Out']

class ConvSmooth(Convert):
  maing2module = 'Glide'
  parammap = ['Time']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Glide,1)
    setv(g2mp.Time, glide[getv(nmmp.Time)])
    
class ConvPortamentoA(Convert):
  maing2module = 'Glide'
  parammap = ['Time']
  inputmap = ['In','On']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    porttime = [ .5*val for val in g2adsrtime]
    nm1midival = getv(nmmp.Time)
    g2midival = nm2g2val(nm1midival,nm1adsrtime,porttime)
    setv(g2mp.Time,g2midival)
    setv(g2mp.Glide,0)
    
class ConvPortamentoB(ConvPortamentoA):
  def domodule(self):
    ConvPortamentoA.domodule(self)
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    invert = self.addmodule('Invert')
    self.connect(invert.outputs.Out1,g2m.inputs.On)
    self.inputs[1] = invert.inputs.In1

class ConvNoteScaler(Convert):
  maing2module = 'NoteScaler'
  parammap = [['Range','Transpose']]
  inputmap = ['In']
  outputmap = ['Out']

class ConvNoteQuant(Convert):
  maing2module = 'NoteQuant'
  parammap = ['Range','Notes']
  inputmap = ['In']
  outputmap = ['Out']

class ConvKeyQuant(Convert):
  maing2module = 'KeyQuant'
  parammap = ['Range',['Capture','Cont'],
              'E','F','F#','G','G#','A','A#','B','C','C#','D','D#']
  inputmap = ['In']
  outputmap = ['Out']

class ConvPartialGen(Convert):
  maing2module = 'PartQuant'
  parammap = ['Range']
  inputmap = ['In']
  outputmap = ['Out']

class ConvControlMixer(Convert):
  maing2module = 'Mix2-1B'
  parammap = ['Inv1',['Lev1','Level1'],'Inv2',['Lev2','Level2'],
              ['ExpLin','Mode']]
  inputmap = ['In1','In2']
  outputmap = ['Out']

class ConvNoteVelScal(Convert):
  maing2module = 'LevScaler'
  parammap = [None,['L','LeftGain'],['BP','Breakpoint'],['R','RightGain']]
  inputmap = [None,'Note'] # no Vel
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module

    nmmp,g2mp = nmm.params, g2m.params
    l = getv(nmmp.LeftGain)
    r = getv(nmmp.RightGain)
    velsens = getv(nmmp.VelocitySensitivity)
    external = 0
    for paramnm in ['VelocitySensitivity','LeftGain','RightGain']:
      param = getattr(nmmp,paramnm)
      for checknm in ['knob','ctrl','morph']:
        if getattr(param,checknm) != None:
          external = 1
    less8db = (abs(l-24) > 8 or abs(r-24) > 8)
    velinp = len(nmm.inputs.Velocity.cables) != 0
    if not external and less8db and not velinp and velsens == 0 :
      setv(g2mp.L,notescale[l][1])
      setv(g2mp.R,notescale[r][1])
      return

    setv(g2mp.L,notescale[l][0])
    setv(g2mp.R,notescale[r][0])
    levmult1 = self.addmodule('LevMult',name='24db')
    self.connect(g2m.outputs.Level,g2m.inputs.In)
    self.connect(g2m.outputs.Level,levmult1.inputs.Mod)
    self.connect(g2m.outputs.Out,levmult1.inputs.In)

    if not velinp and velsens == 0:
      self.outputs[0] = levmult1.outputs.Out
      return

    mix21b = self.addmodule('Mix2-1B', name='Vel')
    setv(mix21b.params.Inv2,1)
    setv(mix21b.params.Lev1,88)
    setv(mix21b.params.Lev2,15)
    self.connect(mix21b.inputs.Chain,mix21b.inputs.In1)
    self.connect(mix21b.inputs.In1,mix21b.inputs.In2)
    levmult2 = self.addmodule('LevMult',name='')
    xfade = self.addmodule('X-Fade',name='VelSens')
    setv(xfade.params.LogLin,1) # Lin
    self.connect(mix21b.outputs.Out,levmult2.inputs.Mod)
    self.connect(levmult1.outputs.Out,levmult2.inputs.In)
    self.connect(levmult2.inputs.In,xfade.inputs.In1)
    self.connect(levmult2.outputs.Out,xfade.inputs.In2)
    setv(xfade.params.Mix,velsens)
    self.params[0] = xfade.params.Mix
    self.inputs[0] = mix21b.inputs.Chain
    self.outputs[0] = xfade.outputs.Out

