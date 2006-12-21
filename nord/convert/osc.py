#
# osc.py - Osc tab convertion objects
#
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from convert import *

def handleam(nmm, g2m, conv):
  aminput = None
  output = g2m.outputs.Out
  if len(nmm.inputs.Am.cables):
    am = conv.g2area.addmodule(g2name['LevMod'])
    conv.g2modules.append(am)
    am.name = 'AM'
    am.vert = g2m.type.height
    am.horiz = g2m.horiz
    conv.height = am.vert + am.type.height
    conv.g2area.connect(g2m.outputs.Out,am.inputs.In,g2cablecolors.red)
    aminput = am.inputs.Mod
    output = am.outputs.Out
  return aminput, output

class ConvMasterOsc(Convert):
  maing2module = 'OscMaster'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'MasterOsc not implemented'

class ConvOscA(Convert):
  maing2module = 'OscB'
  parammap = ['Waveform', 'FreqCoarse', 'FreqFine',
              ['FmAmount','FmMod'],['ShapeMod','PwMod']]
  inputmap = [ 'Sync','FmMod',None,None,'ShapeMod' ]
  outputmap = [ 'Out', None ]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    # NOTE: since shape can be 0% - 100%, a LevConv could be used
    #       to get the actual waveform, if necessary.
    setv(g2mp.Shape,abs(getv(nmmp.PulseWidth)-64)*2)
    setv(g2mp.Active,1-getv(nmmp.Mute))

    # handle special inputs
    p1,p2 = dualpitchmod(nmm,g2m,self)
    self.inputs[2:4] = [p1,p2]

class ConvOscB(Convert):
  maing2module = 'OscB'
  parammap = ['Waveform', 'FreqCoarse', 'FreqFine',
              ['FmAmount','FmMod'],['ShapeMod','PulseWidth']]
  inputmap = [ 'FmMod',None,None,'ShapeMod' ]
  outputmap = [ 'Out', None ]

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special special parameters
    # handle KBT later = nmm.params.FreqKbt)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2m.params.FreqMode,nmm.modes[0]]

    # handle special inputs
    p1,p2 = dualpitchmod(nmm,g2m,self)
    self.inputs[1:3] = [p1, p2]

class ConvOscC(Convert):
  maing2module = 'OscC'
  parammap = ['FreqCoarse', 'FreqFine',
              ['PitchMod','FreqMod'],['FmAmount','FmMod']]
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
    #setv(g2mp.FreqMode,nmm.modes[0])
    
    # add AM if needed, handle special io
    aminput, output = handleam(nmm,g2m,self)
    self.outputs[0] = output
    self.inputs[2] = aminput

class ConvSpectralOsc(Convert):
  maing2module = 'OscShpA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'ConvSpectialOsc not implemented'

class ConvFormantOsc(Convert):
  maing2module = 'OscShpA'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'ConvFormantOsc not implemented'

class ConvOscSlvA(Convert):
  maing2module = 'OscB'
  parammap = ['Waveform',
              ['FreqCoarse','DetuneCoarse'],
              ['FreqFine','DetuneFine'],
              ['FmAmount','FmMod'],]
  inputmap = ['FmMod','Pitch',None]
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2mp.FreqMode,nmm.modes[0])

    # handle special io
    # add AM if needed
    aminput, output = handleam(nmm,g2m,self)
    self.outputs[0] = output
    self.inputs[2] = aminput

    # need to search Mst input for Slv output
    # this way the connection can be removed
    # each Conv.. object should be responsible
    # it's own connect.  I need to add code to
    # remove cables within the NM1 patch.  It's
    # easier to handle it here.  Plus I want thte
    # converter to fail when there is an unknown
    # connection.

class ConvOscSlvB(Convert):
  maing2module = 'OscB'
  parammap = [['FreqCoarse','DetuneCoarse'],
              ['FreqFine','DetuneFine'],
              ['ShapeMod','PwMod'],]
  inputmap = [None,'ShapeMod']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters 
    setv(g2mp.Waveform,3) # square
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2mp.FreqMode,nmm.modes[0])

    # NOTE: since shape can be 0% - 100%, a LevConv could be used
    #       to get the actual waveform, if necessary.
    setv(g2m.params.Shape,abs(getv(nmm.params.PulseWidth)-64)*2)

class ConvOscSlvC(Convert):
  maing2module = 'OscC'
  waveform = 2 # saw
  parammap = [['FreqCoarse','DetuneCoarse'],
              ['FreqFine','DetuneFine'],
              ['FmAmount','FmMod'],]
  inputmap = [None,'FmMod',None] # no Mst, possible AM
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))
    #setv(g2mp.FreqMode,nmm.modes[0])
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
    aminput, output = handleam(nmm,g2m,self)
    self.outputs[0] = output
    self.inputs[2] = aminput

class ConvOscSineBank(Convert):
  maing2module = 'NameBar'

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    raise 'ConvOscSineBank not implemented'

class ConvOscSlvFM(ConvOscSlvC):
  waveform = 0 # sine
  inputmap = [None,'FmMod','Sync'] # no Mst
 
class ConvNoise(Convert):
  maing2module = 'Noise'
  parammap = ['Color']
  outputmap = ['Out']

class ConvPercOsc(Convert):
  maing2module = 'OscPerc'
  parammap = [['FreqCoarse','Pitch'],['FreqFine','PitchFine'],
              'Click','Decay','Punch','PitchMod']
  inputmap = ['Trig',None,'PitchVar']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))

    # add AM if needed
    aminput, output = handleam(nmm,g2m,self)
    self.outputs[0] = output
    self.inputs[1] = aminput

class ConvDrumSynth(Convert):
  maing2module = 'DrumSynth'
  inputmap = ['Trig','Vel','Pitch']
  outputmap = ['Out']

  def domodule(self):
    nmm,g2m = self.nmmodule,self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # parameters are exactly the same
    for i in range(len(nmm.params)):
      cpv(g2mp[i],nmmp[i])

