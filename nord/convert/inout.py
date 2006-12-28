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
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors
from convert import *

class ConvKeyboard(Convert):
  maing2module = 'Keyboard'
  outputmap = ['Note','Gate','Lin','Release']

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
  parammap = [None,'Destination',['Active','Mute']]

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    dest = getv(nmmp.Destination)
    inp = [g2m.inputs.InL,g2m.inputs.InR][dest%2]
    setv(g2mp.Destination,dest/2)
    setv(g2mp.Active,1-getv(nmmp.Mute))
    # maybe adjust patch level from nmm.params.Level
    self.inputs = [inp]

class Conv4Output(Convert):
  maing2module = '4-Out'
  parammap = [None]
  inputmap = ['In1','In2','In3','In4']
  # maybe adjust patch level from nmm.params.Level

class Conv2Output(Convert):
  maing2module = '2-Out'
  parammap = [None,'Destination',['Active','Mute']]
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
  #          Lower,Upper
  parammap = [None,None]

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

    setv(u.params.Level,getv(nmmp.Lower))
    setv(l.params.C,getv(nmmp.Upper))

    g2area.connect(u.outputs.Out,lu.inputs.A,g2cablecolors.blue)
    g2area.connect(l.inputs.In,lu.inputs.B,g2cablecolors.blue)
    g2area.connect(l.outputs.Out,g.inputs.In1_1,g2cablecolors.yellow)
    g2area.connect(lu.inputs.B,n.inputs.In,g2cablecolors.blue)
    g2area.connect(lu.outputs.Out,g.inputs.In1_2,g2cablecolors.yellow)
    g2area.connect(g.outputs.Out1,g.inputs.In2_2,g2cablecolors.yellow)
    g2area.connect(g.outputs.Out2,n.inputs.Clk,g2cablecolors.yellow)
    g2area.connect(n.inputs.Clk,v.inputs.Clk,g2cablecolors.yellow)

    self.params = [l.params.C,u.params.Level]
    self.outputs = [n.outputs.Out,g.outputs.Out2,v.outputs.Out]
    self.inputs = [l.inputs.In,g.inputs.In2_1,v.inputs.In]

