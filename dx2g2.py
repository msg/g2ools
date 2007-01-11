#!/usr/bin/env python

import os,string,sys
from array import array
sys.path.append('.')
from nord.g2.file import Pch2File, MorphMap
from nord.g2.colors import g2modulecolors, g2cablecolors, g2portcolors

class DX7Converter: 
  def __init__(self):
    self.pch2 = Pch2File('dx7.pch2')
    self.dxrouter = self.modulebyname('DXRouter1')
    self.operators = [self.modulebyname('Operator%d'%i) for i in range(1,7)]
    self.lfo = self.modulebyname('LFO')
    self.pitcheg = self.modulebyname('PitchEG')

  def modulebyname(self, name):
    for module in self.pch2.patch.voice.modules:
      if module.name == name:
        return module
    return None

class Struct:
  def __init__(self, **kw):
    self.__dict__ = kw

class Operator:
  pass

class LFO:
  pass

class PitchEG:
  pass

class DX7Patch:
  def __init__(self):
    self.operators = [ Operator() for i in range(6) ]

def parsedx7(data):
  x = array('B',data)
  patch = DX7Patch()
  for i in range(6):
    op = patch.operators[5-i]
    op.R1,op.R2,op.R3,op.R4 = x[:4]; x = x[4:]
    op.L1,op.L2,op.L3,op.L4 = x[:4]; x = x[4:]
    op.BrPoint,op.LDepth,op.RDepth = x[:3]; x = x[3:]
    c = x.pop(0); op.LDepthMode,op.RDepthMode = (c>>2),c&3
    c = x.pop(0); op.FreqDetune,op.RateScale = c>>4,c&7
    c = x.pop(0); op.Vel,op.AMod = c>>2,c&3
    op.OutLevel = x.pop(0)
    c = x.pop(0); op.FreqCoarse,op.RatioFixed = c>>1,c&1
    op.FreqFine = x.pop(0)
  pitcheg = patch.pitcheg = PitchEG()
  pitcheg.R1,pitcheg.R2,pitcheg.R3,pitcheg.R4 = x[:4]; x = x[4:]
  pitcheg.L1,pitcheg.L2,pitcheg.L3,pitcheg.L4 = x[:4]; x = x[4:]
  patch.Algorithm = x.pop(0)
  c = x.pop(0)
  patch.OscKeySync,patch.Feedback = c>>3,c&7
  lfo = patch.lfo = LFO()
  lfo.Rate,lfo.Delay,lfo.PitchMod,lfo.AmMod = x[:4]; x = x[4:]
  c = x.pop(0)
  lfo.PitchModSens,lfo.Waveform,lfo.Sync = c>>5,(c>>1)&0xf,c&1
  patch.Transpose = x.pop(0)
  patch.Name = x.tostring()
  return patch
  
prog = sys.argv.pop(0)
for fname in sys.argv:
  if fname[-4:].lower() != '.syx':
    continue
  f = open(fname,'r')
  data = f.read()
  voice1 = '\xf0\x43\x00\x00\x01\x1b'
  voice32 = '\xf0\x43\x00\x09\x20\x00'
  patches = []
  while data:
    syx = data.find('\xf0')
    if syx < 0:
      break
    esx = data.find('\xf7',syx)
    if data[syx:syx+len(voice1)] == voice1:
      print fname, '1 voice'
    elif data[syx:syx+len(voice32)] == voice32:
      print fname, '32 voice'
      v32data = data[syx+len(voice32):esx]
      for i in range(len(v32data)/128):
	patch = parsedx7(v32data[i*128:i*128+128])
        patch.number = i+1
	patches.append(patch)
    data = data[esx+1:]
  outname = fname[:-4]
  groups = [ patches[i:i+8] for i in range(0,len(patches),8)]
  bank = 1
  opparamnms = [
    'R1','L1','R2','L2','R3','L3','R4','L4','AMod',
    'BrPoint','LDepthMode','LDepth','RDepthMode','RDepth',
    'OutLevel'
  ]
  for group in groups:
    dxconv = DX7Converter()
    for i in range(len(group)):
      dxpatch = group[i]
      nm = '%2d. %s' % (dxpatch.number, dxpatch.Name)
      print nm
      dxconv.pch2.patch.voice.addmodule('Name',name=nm,horiz=0,vert=i)
      # set DXRouter stuff
      dxconv.dxrouter.params.Algorithm.variations[i] = dxpatch.Algorithm
      dxconv.dxrouter.params.Feedback.variations[i] = dxpatch.Feedback
      # set all Operator's parameters
      for op in range(len(dxpatch.operators)):
        dxop = dxpatch.operators[op]
        g2op = dxconv.operators[op]
        for paramnm in opparamnms:
          g2param = getattr(g2op.params,paramnm)
          dxparam = getattr(dxop,paramnm)
          g2param.variations[i] = dxparam
      # set LFO parameters
      # set PitchEG parameters
    #
    def addnamebars(pch2, lines, horiz, vert):
      for line in lines:
        m = pch2.patch.voice.addmodule('Name',name=line)
        m.horiz = horiz
        m.vert = vert
        vert += 1
      return vert

    lines = ['dx2g2 converter','by','Matt Gerassimoff']
    vert = 0
    for module in dxconv.pch2.patch.voice.modules:
      if module.horiz != 0:
        continue
      v = module.vert + module.type.height
      #print '',module.name, module.vert, module.type.height, v
      if v > vert:
        vert = v
    vert = addnamebars(dxconv.pch2,lines,0,vert+1)
    vert = addnamebars(dxconv.pch2,['All rights','reserved'],0,vert+1)


    dxconv.pch2.write(outname+'b%d.pch2' % bank)
    bank += 1

