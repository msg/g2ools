#!/usr/bin/env python

import sys
sys.path.append('.')
from nord.g2.file import Pch2File
from nord.g2.modules import fromname as g2name
from nord.nm1.file import PchFile
from nord.g2 import colors
from nord.convert import typetable

def convert(pch):
  #   loop through each module
  #     determine and store separation from module above >= 0
  #     if mod in convertion table
  #       call convertion table module function
  #   loop through each cable
  #     if source and dest in convertion table
  #       create new connection
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
  cablecolors = {
    'Audio': 0,
    'Control': 1,
    'Logic': 2,
    'Slave': 3,
    'User1': 4,
    'User2': 5,
    'NoSrc': 6,
  }
  for areanm in 'voice','fx':
    nmarea = getattr(nmpatch,areanm)
    g2area = getattr(g2patch,areanm)
    print 'Area %s' % areanm

    converters = []
    # do the modules
    for module in nmarea.modules:
      if module.type.type in typetable:
        conv = typetable[module.type.type](nmarea,g2area,module)
        converters.append(conv)
        conv.domodule()
        #g2module = conv.g2module
        #print '%s (%d,%d)' % (g2module.type.shortnm,
        #    g2module.horiz, g2module.vert)
      else:
        print 'No converter for module "%s"' % module.type.shortnm

    # reposition modules
    locsorted = converters[:]
    def loccmp(a, b):
      if a.horiz == b.horiz:
        return cmp(a.nmmodule.vert, b.nmmodule.vert)
      return cmp(a.nmmodule.horiz,b.nmmodule.horiz)
    locsorted.sort(loccmp)

    if len(locsorted):
      locsorted[0].reposition(None)
      for i in range(1,len(locsorted)):
        ca = locsorted[i-1]
        cb = locsorted[i]
        if ca.nmmodule.horiz == cb.nmmodule.horiz:
          cb.reposition(ca)
        else:
          cb.reposition(None)

    # now do the cables
    for cable in nmarea.cables:
      source = cable.source
      g2source = None
      if source.direction:
        if source.index < len(source.conv.outputs):
          g2source = source.conv.outputs[source.index]
      elif source.index < len(source.conv.inputs):
        g2source = source.conv.inputs[source.index]
      dest = cable.dest
      print '%s:%s -> %s:%s:' % (source.module.type.shortnm,source.type.name,
          dest.module.type.shortnm,dest.type.name),
      if dest.index >= len(dest.conv.inputs) or not g2source:
        print ' UNCONNECTED'
      else:
        print ' connected'
        g2dest = dest.conv.inputs[dest.index]
        #print source.index, dest.index
        #print source.module.type.shortnm, dest.module.type.shortnm
        #print source.module.type.shortnm, dest.module.type.shortnm
        g2area.connect(g2source,g2dest,cablecolors[source.type.type])


  print 'Writing patch "%s2"' % (pch.fname)
  pch2.write(pch.fname+'2')
  
prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print '"%s"' % fname
  # general algorithm for converter:
  convert(PchFile(fname))

sys.exit(0)

# test code ...

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

patch.voice.connect(oscb.outputs.Out,flt.inputs.In,0)
patch.voice.connect(flt.outputs.Out,out.inputs.InL,0)
patch.voice.connect(flt.outputs.Out,out.inputs.InR,0)

print 'Writing patch'
pch2.write('newpatch.pch2')

