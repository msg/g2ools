#!/usr/bin/env python

import string

def getnumbers(fname):
  lines = map(string.strip, open(fname).readlines())
  return map(lambda line: map(lambda n: eval(n), line.split()), lines)
  #return map(lambda a: eval(a.split()[-1]), lines)

def interpolate(indexvals):
  lastindex,lastval = indexvals[0]
  interpolated = [[lastindex,lastval]]
  for indexval in indexvals[1:]:
    index,val = indexval
    slope = float(val-lastval)/(index-lastindex)
    if index-lastindex>1:
      for i in range(lastindex,index):
        interpolated.append([i,int(lastval+slope*(i-lastindex)+0.5)])
    else:
      interpolated.append([index,val])
    lastindex,lastval=index,val
  return interpolated

mix21b = getnumbers('mix2-1b.txt')    # val, mix %
spectral = getnumbers('spectral.txt') # val, fmmod, fmmod %, mix %, inv %
pitchmod = getnumbers('nm1pitch.txt') # val, pitchmod, pmod %, invpmod %
kbt = getnumbers('kbt.txt')           # val, lev1, lev2
notescale = getnumbers('notescale.txt') # nmval, 24db G2 val, 8db G2 val
glides = getnumbers('glide.txt')      # val, [glide, [phase]]
glideindexes = [ gp[:2] for gp in glides if len(gp) > 1 ]
glides = interpolate(glideindexes)
fmb = getnumbers('fmb.txt')           # val, g2phasemod, mix %, inv %
wavewrap = getnumbers('wavewrap.txt') # val, g2wrap
logicdel = getnumbers('logicdel.txt') # val, g2del
lphpfreq = getnumbers('lphpfreq.txt') # nmlpfreq,g2lpfrew,nmhpfreq,g2hpfreq

f=open('../nord/convert/table.py','w')
f.write('''
#
# table.py - convertion tables
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
# FMAmod conversion table calculated by 3phase
# mod conversion table calculated by 3phase
# kbt conversion table calculated by 3phase 
''')
f.write('fmamod = [ # [fmmod,mix,inv]\n')
for i in range(128):
  if i and i % 4 == 0:
    f.write('\n')
  for j in range(128):
    if int(10*mix21b[j][1]) == int(10*spectral[i][3]):
      mix = j
    if int(10*mix21b[j][1]) == int(10*spectral[i][4]):
      inv = j
  f.write('  [%3d,%3d,%3d],' % (spectral[i][1],mix,inv))
f.write('''
]

modtable = [ # [pitchmod,mix,inv]
''')
for i in range(128):
  if i and i % 4 == 0:
    f.write('\n')
  for j in range(128):
    if int(10*mix21b[j][1]) == int(10*pitchmod[i][2]):
      mix = j
    if int(10*mix21b[j][1]) == int(10*pitchmod[i][3]):
      inv = j
  f.write('  [%3d,%3d,%3d],' % (pitchmod[i][1],mix,inv))
f.write('''
]

kbttable = [ # [lev1,lev2]
''')
for i in range(128):
  if i and i % 4 == 0:
    f.write('\n')
  f.write('  [%3d,%3d],' % (kbt[i][1],kbt[i][2]))
f.write('''
]

notescale = [ # [24g2,8g2]
''')
for i in range(len(notescale)):
  if i and i % 4 == 0:
    f.write('\n')
  f.write(' [%3d,%3d],' % (notescale[i][1],notescale[i][2]))
f.write('''
]

glide = [
 ''')
for i in range(len(glides)):
  if i and i % 16 == 0:
    f.write('\n ')
  f.write('%3d,' % (glides[i][1]))
f.write('''
]

fmbmod = [ # [phasemod,mix,inv]
''')
for i in range(128):
  if i and i % 4 == 0:
    f.write('\n')
  f.write(' [%3d,%3d,%3d],' % (fmb[i][1],fmb[i][2],fmb[i][3]))
f.write('''
]

wavewrap = [
 ''')
for i in range(len(glides)):
  if i and i % 16 == 0:
    f.write('\n ')
  f.write('%3d,' % (wavewrap[i][1]))
f.write('''
]

logicdel = [
 ''')
for i in range(len(glides)):
  if i and i % 16 == 0:
    f.write('\n ')
  f.write('%3d,' % (logicdel[i][1]))
f.write('''
]

lphpfreq = [
''')
for i in range(len(lphpfreq)):
  if i and i % 4 == 0:
    f.write('\n')
  f.write(' [%3d,%3d],' % (lphpfreq[i][1],lphpfreq[i][3]))

f.write('''
]
''')
