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
from nord.g2.modules import fromname as g2name
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
  pass

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

