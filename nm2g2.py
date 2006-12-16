#!/usr/bin/env python

import sys
sys.path.append('.')
#from nord.nm1.file import PchFile
from nord.g2.file import *
from nord.g2 import colors

def Convert2Output(module, newpatch):
  pass

def ConvertOscB(module, newpatch):
  pass

def ConvertADSR_Env(module, newpatch):
  pass

def ConvertKeyboard(module, newpatch):
  pass

moduleconvertion = {
    4: Convert2Output,
    8: ConvertOscB,
   20: ConvertADSR_Env,
  100: ConvertKeyboard, 
}

def convert(pch):
  #   loop through each module
  #     determine and store separation from module above >= 0
  #     if mod in convertion table
  #       call convertion table module function
  #   loop through each cable
  #     if source and dest in convertion table
  #       call convertion table cable function
  #   update midi controller assignments
  #   update knob assignments (on pags A1:1, A1:2 and A1:3)
  #   update morph assignments
  #   reorder modules top to bottom, left to right
  #   relocate modules top to bottom, left to right based on separation
  #   add name bar with my name and convertion info
  #   add name bar with errors/comments etc.
  #   save g2 file

  # other ideas:
  # create patch equal function
  # create patch merge function that updates variations
  #   of one patch from another.
  pch2 = Pch2File('initpatch.pch2')
  nmpatch = pch.patch
  g2patch = pch2.patch
  for module in nmpatch.modules:
    if module.type.type in moduleconvertion:
      typeconvert(module.type.type, g2patch)
    else:
      print 'No converter for module "%s"' % module.type.name
  print 'Writing patch'
  pch2.write(pch.fname+'2')
  
prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print '"%s"' % fname
  # general algorithm for converter:
  convert(PchFile(fname)

sys.exit(0)

pch2 = Pch2File('initpatch.pch2')
patch = pch2.patch

colorlist = [
'grey',
'red1', 'red2', 'red3', 'red4',
'yellow1', 'yellow2', 'yellow3', 'yellow4',
'green1', 'green2', 'green3', 'green4',
'cyan1', 'cyan2', 'cyan3', 'cyan4',
'blue1', 'blue2', 'blue3', 'blue4',
'magenta1', 'magenta2', 'magenta3', 'magenta4',
]
message = '''
Copyright qfingers 2006. This patch was converted by the nm2g2.py
converter and the patch was creatd by some unknown author who
doesn't need recognition anyways.  This was specifically created
as a joke for 3phase's amusement.  No hard feelings...
'''
lines = []
words = message.split()
line = words.pop(0)
for word in words:
  if len(line) + len(word) + 1> 16:
    lines.append(line)
    line = word
  else:
    line += ' ' + word
lines.append(line)
print '\n'.join(lines)

allcolors = [ eval('colors.%s' % colorlist[i]) for i in range(len(colorlist)) ]
#sys.exit(0)
#for i in range(len(colorlist)):
#  m = patch.voice.addmodule(modules.modulemap.Name)
#  m.name = colorlist[i]
#  m.color = eval('colors.%s' % colorlist[i])
for i in range(len(lines)):
  line = lines[i]
  m = patch.voice.addmodule(modules.modulemap.Name)
  m.color = allcolors[i%len(allcolors)]
  m.name = line
  m.vert = i

oscb = patch.voice.addmodule(modules.fromname['OscB'],horiz=1,vert=0)
flt = patch.voice.addmodule(modules.fromname['FltNord'],horiz=1,vert=5)
out = patch.voice.addmodule(modules.fromname['2-Out'],horiz=1,vert=10)

patch.voice.addcable(oscb.outputs.Out,flt.inputs.In,0)
patch.voice.addcable(flt.outputs.Out,out.inputs.InL,0)
patch.voice.addcable(flt.outputs.Out,out.inputs.InR,0)

print 'Writing patch'
pch2.write('newpatch.pch2')

