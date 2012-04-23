#!/usr/bin/env python2
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
from nord import printf
from nord.nm1.file import PchFile, NM1Error

def printpatch(patch):
  for areanm in ['voice','fx']:
    area = getattr(patch, areanm)
    printf('%s:\n', areanm)

    printf(' modules:\n')
    for module in area.modules:
      mtype = module.type
      printf('  %s: %d "%s" (%d,%d)\n', mtype.shortnm,
          module.index, module.name, module.horiz, module.vert)

      for param in range(len(mtype.params)):
        printf('   %s(%d): %d\n', mtype.params[param].name,
            param, module.params[param].variations[0])

      for mode in range(len(mtype.modes)):
        printf('   >%s(%d): %d\n', mtype.modes[mode].name,
            mode, module.modes[mode].value)

    printf(' cables:\n')
    for cable in area.cables:
      source,dest = cable.source,cable.dest
      smod,dmod = source.module,dest.module
      stype,dtype = smod.type, dmod.type
      #c = cable
      #printf('%d %d %d %d %d %d %d\n', c.color,c.dest.index,c.dest.conn,c.dest.type,
      #      c.source.index,c.source.conn,c.source.type)
      printf('  %s.%s - %s.%s: c=%d\n', smod.name, source.type.name,
      		dmod.name, dest.type.name, cable.color)
          
    printf(' nets:\n')
    for net in area.netlist.nets:
      source = net.output
      if source:
        smod = area.find_module(source.module.index)
        s = '%s.%s' % (smod.name, source.type.name)
      else:
        s = 'nosrc'
      t = []
      for dest in net.inputs:
        dmod = area.find_module(dest.module.index)
        dtype = dmod.type
        t.append('%s.%s' % (dmod.name, dest.type.name))
      printf('  %s -> %s\n', s, ','.join(t))
        
  printf('knobs:\n')
  for knob in patch.knobs:
    if hasattr(knob.param,'module'):
      printf(' %02d: %s:%s\n', knob.knob,knob.param.module.name,knob.param.type.name)
    else:
      printf(' %02d: morph %d\n', knob.knob,knob.param.index)

  printf('ctrls:\n')
  for ctrl in patch.ctrls:
    if hasattr(ctrl.param,'module'):
      printf(' %02d: %s:%s\n', ctrl.midicc,ctrl.param.module.name,ctrl.param.type.name)
    else:
      printf(' %02d: morph %d\n', ctrl.midicc,ctrl.param.index)
    
  printf('morphs:\n')
  for morph in patch.morphs:
    if morph.knob:
      knob = morph.knob.knob
    else:
      knob = 0
    printf(' %d: %d %s\n', morph.index, knob,
        ['none','vel','note'][morph.keyassign])
    for map in morph.maps:
      printf('  %s:%s range %d\n', map.param.module.name,map.param.type.name,
          map.range)
    
prog = sys.argv.pop(0)
while len(sys.argv):
  filename = sys.argv.pop(0)
  printf('"%s"\n', filename)
  try:
    pch = PchFile(filename)
    printpatch(pch.patch)
  except NM1Error, s:
    printf('%s: NM1Error %s\n', filename, s)
    sys.exit(1)

