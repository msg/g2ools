#
# inout.py - In/Out tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvKeyboard(Convert):
  maing2module = 'Keyboard'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module

    # build output array that nmps nm1 outputs
    self.outputs = [g2m.outputs.Note,
                    g2m.outputs.Gate,
                    g2m.outputs.Lin,
                    g2m.outputs.Release]

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
      m = g2area.addmodule(g2name[nm])
      m.name = ''
      self.g2modules.append(m)
      m.horiz = nmm.horiz
      m.vert = vert
      vert += m.type.height
    self.height = vert

    # internally connect the modules
    k,d1,d2,d3 = self.g2modules
    g2area.connect(k.outputs.Gate,d1.inputs.Clk,2)
    g2area.connect(k.outputs.Note,d1.inputs.In,1)
    g2area.connect(d1.inputs.Clk,d2.inputs.Clk,2)
    g2area.connect(k.outputs.Lin,d2.inputs.In,1)
    g2area.connect(d2.inputs.Clk,d3.inputs.Clk,2)
    g2area.connect(k.outputs.Release,d3.inputs.In,1)

    # build output array that maps nm1 outputs
    self.outputs = [d1.outputs.Out,
                    s.outputs.PatchActive,
                    d2.outputs.Out,
                    d3.outputs.Out]

class ConvMIDIGlobal(Convert):
  maing2module = 'ClkGen'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module

    # build output array the maps nm1 outputs
    # below, the __dict__['1/96'] is used because it's not a valid identifier
    self.outputs = [g2m.outputs.__dict__['1/96'],
                    g2m.outputs.Sync,
                    g2m.outputs.ClkActive]

class ConvAudioIn(Convert):
  maing2module = '2-In'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module

    setv(g2m.params.Active,1)

    # build output array the maps nm1 outputs
    self.outputs = [g2m.outputs.OutL,g2m.outputs.OutR]

class ConvPolyAreaIn(Convert):
  maing2module = 'Fx-In'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    # below, the __dict__['+6Db'] is used because it's not a valid identifier
    cpv(g2mp.Pad,nmm.params.__dict__['+6Db'])

    # build output array the maps nm1 outputs
    self.outputs = [g2m.outputs.OutL,g2m.outputs.OutR]

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

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # ignore level

    self.inputs = [g2m.inputs.In1,g2m.inputs.In2,g2m.inputs.In3,g2m.inputs.In4]

class Conv2Output(Convert):
  maing2module = '2-Out'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    setv(g2mp.Active,1-getv(nmmp.Mute))
    cpv(g2mp.Destination,nmmp.Destination)

    # maybe adjust patch level from nmm.params.Level

    # build input array that nmps nm1 inputs
    self.inputs = [g2m.inputs.InL, g2m.inputs.InR]

class ConvNoteDetect(Convert):
  maing2module = 'NoteDet'

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    # update parameters
    cpv(g2mp.Note,nmmp.Note)

    # build output array the maps nm1 outputs
    self.outputs = [g2m.outputs.Gate,g2m.outputs.Vel,g2m.outputs.RelVel]

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
      m = g2area.addmodule(g2name[mod])
      self.g2modules.append(m)
      m.name = nm
      m.vert = vert
      vert += m.type.height
    self.height = vert

    u,l,lu,g,n,v = self.g2modules
    g2area.connect(u.outputs.Out,lu.inputs.A,1)
    g2area.connect(l.inputs.In,lu.inputs.B,1)
    g2area.connect(l.outputs.Out,g.inputs.In1_1,2)
    g2area.connect(lu.inputs.B,n.inputs.In,1)
    g2area.connect(lu.outputs.Out,g.inputs.In1_2,2)
    g2area.connect(g.outputs.Out1,g.inputs.In2_2,2)
    g2area.connect(g.outputs.Out2,n.inputs.Clk,2)
    g2area.connect(n.inputs.Clk,v.inputs.Clk,2)

    self.outputs = [n.outputs.Out,g.outputs.Out2,v.outputs.Out]

    self.inputs = [l.inputs.In,g.inputs.In2_1,v.inputs.In]
