#!/usr/bin/env python

import sys
sys.path.append('.')
from nord.nm1.file import PchFile
from nord.g2.file import *
from nord.g2 import colors

def printpatch(patch):
  for areanm in ['voice','fx']:
    area = getattr(patch, areanm)
    print '%s:' % areanm
    print ' modules:'
    for module in area.modules:
      mtype = module.type
      print '  %s: %d "%s" type=%d loc=(%d,%d) ht=%d' % (mtype.name,
          module.mod, module.name, module.type,
          module.col, module.row, mtype.height)
      for param in range(len(mtype.parameters)):
        print '   %s(%d): %d' % (mtype.parameters[param].name,
            param, module.params[param])
      for custom in range(len(mtype.customs)):
        print '   >%s(%d): %d' % (mtype.customs[custom].name,
            custom, module.custom.parameters[custom])
    print ' cables:'
    for cable in area.cables:
      source,dest = cable.source,cable.dest
      smod,dmod = source.module, dest.module
      stype,dtype = smod.type, dmode.type
      #c = cable
      #print c.color,c.dest.mod,c.dest.conn,c.dest.type,c.source.mod,c.source.conn,c.source.type
      if source.type:
        snm = stype.outputs[source.conn].name
      else:
        snm = stype.inputs[source.conn].name
      if dest.type:
        dnm = dtype.outputs[dest.conn].name
      else:
        dnm = dtype.inputs[dest.conn].name
      print '  %s.%s - %s.%s: c=%d' % (
          stype.name, snm, dtype.name, dnm, cable.color)
    print ' nets:'
    for net in area.netlist:
      source = net.output
      if source:
        smod = source.module
        stype = smod.type
        snm = stype.outputs[source.conn].name
        s = '%s.%s' % (stype.name, snm)
      else:
        s = 'nosrc'
      t = []
      for dest in net.inputs:
        dmod = dest.module
        dtype = dmod.type
        dnm = dtype.inputs[dest.conn].name
        t.append('%s.%s' % (dtype.name, dnm))
      print '  %s -> %s' % (s, ','.join(t))
        
def Convert2Output(module, connections, newpatch):
  pass

def ConvertOscB(module, connections, newpatch):
  pass

def ConvertADSR_Env(module, connections, newpatch):
  pass

def ConvertKeyboard(module, connections, newpatch):
  pass

moduleconvertion = {
    4: Convert2Output,
    8: ConvertOscB,
   20: ConvertADSR_Env,
  100: ConvertKeyboard, 
}

def convert(patch):
  pass
  
prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print '"%s"' % fname
  pch = PchFile(fname)
  printpatch(pch.patch)

  # general algorithm for converter:
  convert(pch.patch)
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
oscb = patch.voice.addmodule(modules.modulemap.OscB,horiz=1,vert=0)
flt = patch.voice.addmodule(modules.modulemap.FltNord,horiz=1,vert=5)
# build module so that in/out connections can be easily done like:
# patch.voice.addcable(oscb.Out,flt.In,0)
# output = oscb.Out
# Cable(oscb.Out.module,oscb.Out.index,oscb.Out.type,
#       flt.In.module,flt.Out.index,flt.In.type,color)
# input = flt.In
# input.index = 0, input.type = 0

patch.voice.addcable(oscb,0,1,flt,0,0)

print 'Writing patch'
pch2.write('newpatch.pch2')

