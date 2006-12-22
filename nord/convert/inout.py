#
# inout.py - In/Out tab conversion objects
#
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from convert import *

class ConvKeyboard(Convert):
  maing2module = 'Keyboard'
  outputmap = ['Note','Gate','Lin','Release']

class ConvKeyboardPatch(Convert):
  maing2module = 'Status'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    g2area = self.g2area

    # gotta do some work here
    # basically use Status, Keyboard and Delay Clock modules to get
    # all the KbdStatus signals.
    self.g2modules = []
    s=g2m
    vert = g2m.type.height
    for nm in ['Keyboard'] + [ 'DlyClock' ] * 3:
      m = g2area.addmodule(g2name[nm],name='',horiz=nmm.horiz,vert=vert)
      self.g2modules.append(m)
      vert += m.type.height
    self.height = vert

    # internally connect the modules
    k,d1,d2,d3 = self.g2modules
    g2area.connect(k.outputs.Gate,d1.inputs.Clk,g2cablecolors.yellow)
    g2area.connect(k.outputs.Note,d1.inputs.In,g2cablecolors.blue)
    g2area.connect(d1.inputs.Clk,d2.inputs.Clk,g2cablecolors.yellow)
    g2area.connect(k.outputs.Lin,d2.inputs.In,g2cablecolors.blue)
    g2area.connect(d2.inputs.Clk,d3.inputs.Clk,g2cablecolors.yellow)
    g2area.connect(k.outputs.Release,d3.inputs.In,g2cablecolors.blue)

    # build output array that maps nm1 outputs
    self.outputs = [d1.outputs.Out,
                    s.outputs.PatchActive,
                    d2.outputs.Out,
                    d3.outputs.Out]

class ConvMIDIGlobal(Convert):
  maing2module = 'ClkGen'
  outputmap = ['1/96','Sync','ClkActive']

class ConvAudioIn(Convert):
  maing2module = '2-In'
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module

class ConvPolyAreaIn(Convert):
  maing2module = 'Fx-In'
  parammap = [['Pad','+6Db']]
  outputmap = ['OutL','OutR']

class Conv1Output(Convert):
  maing2module = '2-Out'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    dest = getv(nmmp.Dest)
    inp = [g2m.inputs.InL,g2m.inputs.InR][dest%2]
    setv(g2mp.Destination,dest/2)

    self.inputs = [inp]

class Conv4Output(Convert):
  maing2module = '4-Out'
  inputmap = ['In1','In2','In3','In4']

class Conv2Output(Convert):
  maing2module = '2-Out'
  parammap = ['Destination']
  inputmap = ['InL','InR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # handle special parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))

    # maybe adjust patch level from nmm.params.Level

class ConvNoteDetect(Convert):
  maing2module = 'NoteDet'
  parammap = ['Note']
  outputmap = ['Gate','Vel','RelVel']

class ConvKeyboardSplit(Convert):
  maing2module = 'Name'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    g2area = self.g2area
    g2m.name = 'KbdSplit'

    # now lets create the structure
    vert = g2m.type.height
    struct = [ ['Constant','Upper'],
               ['CompLev','Lower'],
               ['CompSig','<=Upper'],
               ['Gate','Gate'],
               ['DlyClock','Note'],
               ['DlyClock','Vel'] ]
    for mod,nm in struct:
      m = g2area.addmodule(g2name[mod],name=nm,vert=vert,horiz=g2m.horiz)
      self.g2modules.append(m)
      vert += m.type.height
    self.height = vert

    u,l,lu,g,n,v = self.g2modules
    g2area.connect(u.outputs.Out,lu.inputs.A,g2cablecolors.blue)
    g2area.connect(l.inputs.In,lu.inputs.B,g2cablecolors.blue)
    g2area.connect(l.outputs.Out,g.inputs.In1_1,g2cablecolors.yellow)
    g2area.connect(lu.inputs.B,n.inputs.In,g2cablecolors.blue)
    g2area.connect(lu.outputs.Out,g.inputs.In1_2,g2cablecolors.yellow)
    g2area.connect(g.outputs.Out1,g.inputs.In2_2,g2cablecolors.yellow)
    g2area.connect(g.outputs.Out2,n.inputs.Clk,g2cablecolors.yellow)
    g2area.connect(n.inputs.Clk,v.inputs.Clk,g2cablecolors.yellow)

    self.outputs = [n.outputs.Out,g.outputs.Out2,v.outputs.Out]

    self.inputs = [l.inputs.In,g.inputs.In2_1,v.inputs.In]

