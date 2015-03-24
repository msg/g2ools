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
from nord.g2.file import Prf2File
from nord.g2.pprint import printpatch

def printf(fmt, *a):
  return sys.stdout.write(fmt % a)

prog = sys.argv.pop(0)
while len(sys.argv):
  filename = sys.argv.pop(0)
  printf('"%s"\n', filename)
  prf2 = Prf2File(filename)
  perf = prf2.performance
  printf(' focus: %s\n',                'abcd'[perf.description.focus])
  printf(' range enable: %s\n',         ['off','on'][perf.description.rangesel])
  printf(' master clock: %d BPM: %s\n', perf.description.bpm,
      ['stop','run'][perf.description.clock])
  printf(' kb split: %s\n',             ['off','on'][perf.description.split])
  for sloti, slot in enumerate(perf.slots):
    description = slot.description
    name = '"%s"' % slot.name
    printf(' slot %s: %d:%d %-16s\n', 'abcd'[sloti],
        description.bank+1, description.patch+1, name)
    printf('  active: %-3s, ',          ['off','on'][description.active])
    printf('key: %-3s, ',               ['off','on'][description.keyboard])
    printf('hold: %-3s, ',              ['off','on'][description.hold])
    printf('range: %d-%d\n',            description.keylow, description.keyhigh)
  for sloti, slot in enumerate(perf.slots, 1):
    printf('Patch %d: "%s"\n', sloti, slot.name)
    printpatch(slot.patch)

