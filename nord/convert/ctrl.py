#
# ctrl.py - Ctrl tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

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

    setv(g2mp.Glide,0)
    
class ConvPortamentoB(Convert):
  maing2module = 'Glide'
  parammap = ['Time']
  inputmap = ['In','On']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    
    setv(g2mp.Glide,0)

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
  maing2module = 'Name'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'PartialGen not implemented'

class ConvControlMixer(Convert):
  maing2module = 'Mix2-1B'
  parammap = ['Inv1',['Lev1','Level1'],'Inv2',['Lev2','Level2'],
              ['ExpLin','Mode']]
  inputmap = ['In1','In2']
  outputmap = ['Out']

class ConvNoteVelScal(Convert):
  maing2module = 'LevScaler'
  parammap = [['L','LeftGain'],['BP','Breakpoint'],['R','RightGain']]
  inputmap = [None,'Note'] # no Vel
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module

