#
# inout.py - In/Out tab conversion objects
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

class ConvKeyboard(Convert):
  maing2module = 'Keyboard'
  outputmap = ['Pitch','Gate','Lin','Release']
  def domodule(self):
    self.g2module.area.keyboard = self.g2module

class ConvKeyboardPatch(Convert):
  maing2module = 'MonoKey'
  outputmap = ['Pitch','Gate','Vel','Vel'] # just use on vel for off vel

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    setv(g2mp.Mode,0)

class ConvMIDIGlobal(Convert):
  maing2module = 'ClkGen'
  outputmap = ['1/96','Sync','ClkActive']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    setv(g2mp.Source,1) # Master

class ConvAudioIn(Convert):
  maing2module = '2-In'
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module

class ConvPolyAreaIn(Convert):
  maing2module = 'Fx-In'
  parammap = [['Pad','+6Db']]
  outputmap = ['OutL','OutR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Pad,[2,1][getv(getattr(nmmp,'+6Db'))])

class Conv1Output(Convert):
  maing2module = 'Mix1-1A'
  parammap = [None,None,None] # Level,Destination,Mute
  inputmap = ['In']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.On,1)
    setv(g2mp.ExpLin,2)

    setv(g2mp.Lev,getv(nmmp.Level))
    out2 = self.addmodule('2-Out')
    dest = getv(nmmp.Destination)
    setv(out2.params.Destination,dest/2)
    setv(out2.params.Active,1-getv(nmmp.Mute))

    inp = [out2.inputs.InL,out2.inputs.InR][dest%2]
    self.connect(g2m.outputs.Out,inp)

    self.params = [g2m.params.Lev,out2.params.Destination,out2.params.Active]

class Conv2Output(Convert):
  maing2module = 'Mix1-1S'
  parammap = [None,None,None] # Level,Destination,Mute
  inputmap = ['InL','InR']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    setv(g2mp.Lev,getv(nmmp.Level))
    setv(g2mp.On,1)
    out2 = self.addmodule('2-Out')
    self.connect(g2m.outputs.OutL,out2.inputs.InL)
    self.connect(g2m.outputs.OutR,out2.inputs.InR)
    setv(out2.params.Destination,getv(nmmp.Destination))
    setv(out2.params.Active,1-getv(nmmp.Mute))

    self.params = [g2mp.Lev,out2.params.Destination,out2.params.Active]

class Conv4Output(Convert):
  maing2module = '4-Out'
  parammap = [None]
  inputmap = ['In1','In2','In3','In4']
  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    setv(self.g2area.patch.settings.patchvol,getv(nmmp.Level))

class ConvNoteDetect(Convert):
  maing2module = 'NoteDet'
  parammap = ['Note']
  outputmap = ['Gate','Vel','RelVel']

class ConvKeyboardSplit(Convert):
  maing2module = 'Name'
  #          Lower,Upper
  parammap = [None,None]

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params
    g2m.name = 'KbdSplit'

    # now lets create the structure
    struct = [ ['Constant','Upper'],
               ['CompLev','Lower'],
               ['CompSig','<=Upper'],
               ['Gate','Gate'],
               ['DlyClock','Note'],
               ['DlyClock','Vel'] ]
    for mod,nm in struct:
      m = self.addmodule(mod,name=nm)

    u,l,lu,g,n,v = self.g2modules

    setv(u.params.Level,getv(nmmp.Upper))
    setv(l.params.C,getv(nmmp.Lower))

    self.connect(u.outputs.Out,lu.inputs.A)
    self.connect(l.inputs.In,lu.inputs.B)
    self.connect(l.outputs.Out,g.inputs.In1_1)
    self.connect(lu.inputs.B,n.inputs.In)
    self.connect(lu.outputs.Out,g.inputs.In1_2)
    self.connect(g.outputs.Out1,g.inputs.In2_2)
    self.connect(g.outputs.Out2,n.inputs.Clk)
    self.connect(n.inputs.Clk,v.inputs.Clk)

    self.params = [l.params.C,u.params.Level]
    self.outputs = [n.outputs.Out,g.outputs.Out2,v.outputs.Out]
    self.inputs = [l.inputs.In,g.inputs.In2_1,v.inputs.In]

