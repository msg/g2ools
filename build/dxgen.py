#!/usr/bin/env python

import string

def getnumbers(fname):
  lines = map(string.strip, open(fname).readlines())
  def emptyzero(s):
    s = s.strip().upper()
    if not s:
      return ''
    elif s == 'LO':
      return 1
    elif s == 'HI':
      return 2
    else:
      return eval(s)
  a = [ lines[0].split('\t')]
  a += map(lambda line: map(emptyzero, line.split('\t')), lines[1:])
  return a

def interpolate(indexvals):
  lastindex,lastval = indexvals[0]
  interpolated = [[lastindex,lastval]]
  for indexval in indexvals[1:]:
    index,val = indexval
    slope = float(val-lastval)/(index-lastindex)
    if index-lastindex>1:
      for i in range(lastindex+1,index+1):
        interpolated.append([i,int(lastval+slope*(i-lastindex)+0.5)])
    else:
      interpolated.append([index,val])
    lastindex,lastval=index,val
  return interpolated

dxamodsens = getnumbers('dxamodsens.txt')[1:]
dxlfo = getnumbers('dxlfo.txt')
dxlfomod = interpolate(
   [ [l[0],l[2]] for l in filter(lambda a: len(a) > 2, dxlfo[1:])])
dxlforate = interpolate(
   [ [l[0],l[3]] for l in filter(lambda a: len(a) > 3, dxlfo[1:])])
dxlfodelay = getnumbers('dxlfodelay.txt')
dxlfoattack = interpolate(
   [ l for l in filter(lambda a: len(a) > 1, dxlfodelay[1:])])
 
print len(dxlfo),len(dxlforate),len(dxlfomod),len(dxlfoattack)
dxlfo = [ [dxlfo[i+1][1],dxlforate[i][1],dxlfomod[i][1],dxlfoattack[i][1]]
    for i in range(len(dxlfo)-1)]

dxpitchegrate = getnumbers('dxpitchegrate.txt')[1:]
dxpitcheg = getnumbers('dxpitcheg.txt')
dxpitcheglev = interpolate(
   [ [l[0],l[1]] for l in filter(lambda a: len(a)>1 and a[1], dxpitcheg[1:])])
dxpitchegtime = interpolate(
   [ [l[0],l[2]] for l in filter(lambda a: len(a)>2 and a[2]!='', dxpitcheg[1:])])
print len(dxpitcheglev),len(dxpitchegtime)
dxpitcheg = [
  [dxpitcheglev[i][1]+64,dxpitchegrate[i][0]] for i in range(len(dxpitcheglev))]
dxpmodsens = getnumbers('dxpmodsens.txt')[1:]

f=open('../dxtable.py','w')
f.write('''
#
# dxtable.py - DX7 convertion tables
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
f.write('amodsens = [ # [dxamod, g2mod]\n')
for i in range(len(dxamodsens)):
  if i and i % 4 == 0:
    f.write('\n')
  f.write('  [%3d,%3d],' % tuple(dxamodsens[i]))
f.write('''
]

lfo = [ # [lforange,lforate,lfomod,lfoattack]
 ''')
for i in range(len(dxlfo)):
  if i and i % 4 == 0:
    f.write('\n ')
  f.write(' [%3d,%3d,%3d,%3d],' % tuple(dxlfo[i]))
f.write('''
]

pitcheg = [ # [lev,rate10]
 ''')
for i in range(len(dxpitcheg)):
  if i and i % 4 == 0:
    f.write('\n ')
  f.write(' [%3d,%4d],' % tuple(dxpitcheg[i]))
f.write('''
]

pmodsens = [ # [pmods, g2, lev1, lev2, moffset]
 ''')
for i in range(len(dxpmodsens)):
  if i and i % 2 == 0:
    f.write('\n ')
  f.write(' [%3d,%3d,%3d,%3d,%3d],' % tuple(dxpmodsens[i]))

f.write('\n]\n')
