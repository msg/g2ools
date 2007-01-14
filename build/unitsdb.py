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

import string

def formatarray(data):
  s = ''
  for i in range(len(data)):
    if i%8 ==0:
      s += '\n  '
    s += '%7s,' % data[i]
  return s

def formattimes(times):
  data = []
  for i in range(len(times)):
    tm = times[i]
    if tm < 10:
      t = '%.2f' % tm
    elif tm < 100:
      t = '%.1f' % tm
    else:
      t = '%d' % tm
    data.append(t)
  return formatarray(data)
  
def formatfreq(freqs):
  data = []
  for i in range(len(freqs)):
    fr = freqs[i]
    if fr < 100:
      t = '%.2f' % fr
    elif fr < 1000:
      t = '%.1f' % fr
    else:
      t = '%.0f.' % fr
    data.append(t)
  return formatarray(data)

def getnumbers(fname):
  lines = map(string.strip, open(fname).readlines())
  return map(lambda a: eval(a.split()[-1]), lines)

nm1adsrtime = getnumbers('nm1adsrtime.txt')
g2adsrtime = getnumbers('g2adsrtime.txt')

nm1fltfreq = getnumbers('nm1fltfreq.txt')
g2fltfreq = getnumbers('g2fltfreq.txt')

nm1logictime = getnumbers('nm1logictime.txt')
g2logictime = getnumbers('g2logictime.txt')

nm1levamp = getnumbers('nm1levamp.txt')
g2levamp = getnumbers('g2levamp.txt')

ratios = getnumbers('ratios.txt')

g2glidetime = getnumbers('g2glidetime.txt')
nm1smoothtime = getnumbers('nm1smoothtime.txt')

f = open('../nord/convert/units.py','w')
s = '''#
# units.py - unit convertion tables and functions
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

def nm2g2val(nm1midival,nm1vals,g2vals):
  nm1val = nm1vals[nm1midival]
  g2min = 1000000 # nothing here will never be that big
  g2midival = 0
  for midival in range(128):
    g2val = g2vals[midival]
    if abs(g2val-nm1val) < g2min:
      g2min = abs(g2val-nm1val)
      g2midival = midival
  return g2midival

nm1adsrtime = [%s
]

g2adsrtime = [%s
]

nm1fltfreq = [%s
]

g2fltfreq = [%s
]

nm1logictime = [%s
]

g2logictime = [%s
]

nm1levamp = [%s
]

g2levamp = [%s
]

ratios = [%s
]

g2glidetime = [%s
]

nm1smoothtime = [%s
]
''' % (formattimes(nm1adsrtime), formattimes(g2adsrtime),
       formatfreq(nm1fltfreq), formatfreq(g2fltfreq),
       formatfreq(nm1logictime), formatfreq(g2logictime),
       formatfreq(nm1levamp), formatfreq(g2levamp),
       formatarray([ '%.4f' % ratios[i] for i in range(len(ratios))]),
       formattimes(g2glidetime),formattimes(nm1smoothtime))

print s
f.write(s)
f.close()
