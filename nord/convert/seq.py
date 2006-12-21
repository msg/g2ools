
#
# seq.py - Seq tab conversion objects
#
from nord.g2.modules import fromname as g2name
from convert import *

class ConvEventSeq(Convert):
  maing2module = 'SeqEvent'
  parammap = ['Length',['TG1','Gate1'],['TG2','Gate2']]
  inputmap = ['Clk','Rst']
  outputmap = ['Trig1','Trig2',None,'Link'] # no Snc

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for j in range(2):
      for i in range(16):
        s = 'Seq%dStep%d' % (j+1,i+1)
        setv(getattr(g2mp,s),getv(getattr(nmmp,s)))

class ConvCtrlSeq(Convert):
  maing2module = 'SeqLev'
  parammap = ['Loop','Length',['BipUni','Uni']]
  inputmap = ['Clk','Rst']
  outputmap = ['Val',None,'Link'] # no Snc

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for i in range(16):
      s = 'Seq1Step%d' % (i+1)
      t = 'Ctrl%d' % (i+1)
      setv(getattr(g2mp,s),getv(getattr(nmmp,t)))

class ConvNoteSeqA(Convert):
  maing2module = 'SeqLev'
  parammap = ['Loop','Length','Loop']
  inputmap = ['Clk','Rst']
  outputmap = ['Val',None,'Link','Trig'] # no Snc

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for i in range(16):
      s = 'Seq1Step%d' % (i+1)
      t = 'Note%d' % (i+1)
      setv(getattr(g2mp,s),getv(getattr(nmmp,t)))
      # setup trigger as GClk
      s = 'Seq2Step%d' % (i+1)
      setv(getattr(g2mp,s),1)
    setv(g2mp.TG,0) # simulate GClk (maybe?)

class ConvNoteSeqB(Convert):
  maing2module = 'SeqNote'
  parammap = ['Loop','Length','Loop']
  inputmap = ['Clk','Rst']
  outputmap = ['Note',None,'Link','Trig'] # no Snc

  def domodule(self):
    nmm,g2m = self.nmmodule, self.g2module
    nmmp,g2mp = nmm.params, g2m.params

    for i in range(16):
      s = 'Seq1Step%d' % (i+1)
      t = 'Note%d' % (i+1)
      setv(getattr(g2mp,s),getv(getattr(nmmp,t)))
      # setup trigger as GClk
      s = 'Seq2Step%d' % (i+1)
      setv(getattr(g2mp,s),1)
    setv(g2mp.TG,0) # simulate GClk (maybe?)
