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
      print '  %s: %d "%s" type=%d loc=(%d,%d) ht=%d' % (mtype.shortnm,
          module.index, module.name, module.type.type,
          module.horiz, module.vert, mtype.height)

      for param in range(len(mtype.params)):
        print '   %s(%d): %d' % (mtype.params[param].name,
            param, module.params[param].variations[0])

      for mode in range(len(mtype.modes)):
        print '   >%s(%d): %d' % (mtype.modes[mode].name,
            mode, module.modes[mode])

    print ' cables:'
    for cable in area.cables:
      source,dest = cable.source,cable.dest
      smod,dmod = source.module,dest.module
      stype,dtype = smod.type, dmod.type
      #c = cable
      #print c.color,c.dest.index,c.dest.conn,c.dest.type,c.source.index,c.source.conn,c.source.type
      print '  %s.%s - %s.%s: c=%d' % (
          stype.shortnm, source.type.name, dtype.shortnm, dest.type.name, cable.color)
          
    print ' nets:'
    for net in area.netlist:
      source = net.output
      if source:
        smod = area.findmodule(source.module.index)
        s = '%s.%s' % (smod.type.shortnm, source.type.name)
      else:
        s = 'nosrc'
      t = []
      for dest in net.inputs:
        dmod = area.findmodule(dest.module.index)
        dtype = dmod.type
        t.append('%s.%s' % (dmod.type.shortnm, dest.type.name))
      print '  %s -> %s' % (s, ','.join(t))
        

prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print '"%s"' % fname
  pch = PchFile(fname)
  printpatch(pch.patch)
