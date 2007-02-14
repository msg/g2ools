#!/usr/bin/env python
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
      print '  %s: %d "%s" (%d,%d)' % (mtype.shortnm,
          module.index, module.name, module.horiz, module.vert)

      for param in range(len(mtype.params)):
        print '   %s(%d): %d' % (mtype.params[param].name,
            param, module.params[param].variations[0])

      for mode in range(len(mtype.modes)):
        print '   >%s(%d): %d' % (mtype.modes[mode].name,
            mode, module.modes[mode].value)

    print ' cables:'
    for cable in area.cables:
      source,dest = cable.source,cable.dest
      smod,dmod = source.module,dest.module
      stype,dtype = smod.type, dmod.type
      #c = cable
      #print c.color,c.dest.index,c.dest.conn,c.dest.type,c.source.index,c.source.conn,c.source.type
      print '  %s.%s - %s.%s: c=%d' % (
          smod.name, source.type.name, dmod.name, dest.type.name, cable.color)
          
    print ' nets:'
    for net in area.netlist:
      source = net.output
      if source:
        smod = area.findmodule(source.module.index)
        s = '%s.%s' % (smod.name, source.type.name)
      else:
        s = 'nosrc'
      t = []
      for dest in net.inputs:
        dmod = area.findmodule(dest.module.index)
        dtype = dmod.type
        t.append('%s.%s' % (dmod.name, dest.type.name))
      print '  %s -> %s' % (s, ','.join(t))
        
  print 'knobs:'
  for knob in patch.knobs:
    if hasattr(knob.param,'module'):
      print ' %02d: %s:%s' % (knob.knob,knob.param.module.name,knob.param.type.name)
    else:
      print ' %02d: morph %d' % (knob.knob,knob.param.index)

  print 'ctrls:'
  for ctrl in patch.ctrls:
    if hasattr(ctrl.param,'module'):
      print ' %02d: %s:%s' % (ctrl.midicc,ctrl.param.module.name,ctrl.param.type.name)
    else:
      print ' %02d: morph %d' % (ctrl.midicc,ctrl.param.index)
    
  print 'morphs:'
  for morph in patch.morphs:
    if morph.knob:
      knob = morph.knob.knob
    else:
      knob = 0
    print ' %d: %d %s' % (morph.index, knob,
        ['none','vel','note'][morph.keyassign])
    for map in morph.maps:
      print '  %s:%s range %d' % (map.param.module.name,map.param.type.name,
          map.range)
    
prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print '"%s"' % fname
  pch = PchFile(fname)
  printpatch(pch.patch)
