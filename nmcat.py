#!/usr/bin/env python

import sys
sys.path.append('.')
from nord.nm1.file import PchFile

def printpatch(patch):
  for areanm in ['voice','fx']:
    area = getattr(patch, areanm)
    print '%s:' % areanm
    print ' modules:'
    for module in area.modules:
      mtype = module.type
      print '  %s: %d "%s" type=%d loc=(%d,%d) ht=%d' % (mtype.name,
          module.index, module.name, module.type.type,
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
      smod,dmod = source.module,dest.module
      stype,dtype = smod.type, dmod.type
      #c = cable
      #print c.color,c.dest.index,c.dest.conn,c.dest.type,c.source.index,c.source.conn,c.source.type
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
        smod = area.findmodule(source.module.index)
        stype = smod.type
        snm = stype.outputs[source.conn].name
        s = '%s.%s' % (stype.name, snm)
      else:
        s = 'nosrc'
      t = []
      for dest in net.inputs:
        dmod = area.findmodule(dest.module.index)
        dtype = dmod.type
        dnm = dtype.inputs[dest.conn].name
        t.append('%s.%s' % (dtype.name, dnm))
      print '  %s -> %s' % (s, ','.join(t))
        

prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print '"%s"' % fname
  pch = PchFile(fname)
  printpatch(pch.patch)
