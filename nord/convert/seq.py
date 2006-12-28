#
# seq.py - Seq tab conversion objects
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

class ConvEventSeq(Convert):
  maing2module = 'SeqEvent'
  parammap = ['Length','Loop',['TG1','Gate1'],['TG2','Gate2']]+[None]*32
  inputmap = ['Clk','Rst']
  outputmap = ['Trig1','Trig2','Link','Link']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for j in range(2):
      for i in range(16):
        s = 'Seq%dStep%d' % (j+1,i+1)
        step = getattr(g2mp,s)
        setv(step,getv(getattr(nmmp,s)))
        self.params[4+j*16+i] = step

class ConvCtrlSeq(Convert):
  maing2module = 'SeqLev'
  parammap = [None]*16 + ['Length',['BipUni','Uni'],'Loop']
  inputmap = ['Clk','Rst']
  outputmap = ['Val','Link','Link']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for i in range(16):
      s = 'Seq1Step%d' % (i+1)
      step = getattr(g2mp,s)
      t = 'Ctrl%d' % (i+1)
      setv(step,getv(getattr(nmmp,t)))
      self.params[i] = step

class ConvNoteSeqA(Convert):
  maing2module = 'SeqLev'
  parammap = [None]*16 + ['Length',None,None,None,'Loop']
  inputmap = ['Clk','Rst']
  outputmap = ['Val','Link','Link','Trig']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for i in range(16):
      s = 'Seq1Step%d' % (i+1)
      t = 'Note%d' % (i+1)
      step = getattr(g2mp,s)
      setv(step,getv(getattr(nmmp,t)))
      self.params[i] = step
      # setup trigger as GClk
      s = 'Seq2Step%d' % (i+1)
      setv(getattr(g2mp,s),1)
    setv(g2mp.TG,0) # simulate GClk (maybe?)

class ConvNoteSeqB(Convert):
  maing2module = 'SeqNote'
  parammap = [None]*16 + ['Length',None,None,None,'Loop']
  inputmap = ['Clk','Rst']
  outputmap = ['Note','Link','Link','Trig']

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for i in range(16):
      s = 'Seq1Step%d' % (i+1)
      t = 'Note%d' % (i+1)
      step = getattr(g2mp,s)
      setv(step,getv(getattr(nmmp,t)))
      self.params[i] = step
      # setup trigger as GClk
      s = 'Seq2Step%d' % (i+1)
      setv(getattr(g2mp,s),1)
    setv(g2mp.TG,0) # simulate GClk (maybe?)

