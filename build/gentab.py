#!/usr/bin/env python

import string

def getnumbers(fname):
  lines = map(string.strip, open(fname).readlines())
  return map(lambda line: map(lambda n: eval(n), line.split()), lines)
  #return map(lambda a: eval(a.split()[-1]), lines)

mix21b = getnumbers('mix2-1b.txt')    # val, mix %
spectral = getnumbers('spectral.txt') # val, fmmod, fmmod %, mix %, inv %
pitchmod = getnumbers('nm1pitch.txt') # val, pitchmod, pmod %, invpmod %
kbt = getnumbers('kbt.txt')           # val, lev1, lev2

print 'fmmod = [ # [fmmod,mix,inv]'
for i in range(128):
  if i and i % 4 == 0:
    print
  for j in range(128):
    if int(10*mix21b[j][1]) == int(10*spectral[i][3]):
      mix = j
    if int(10*mix21b[j][1]) == int(10*spectral[i][4]):
      inv = j
  print ' [%3d,%3d,%3d],' % (spectral[i][1],mix,inv),
print '\n]'

print 'modtable = [ # [pitchmod,mix,inv]'
for i in range(128):
  if i and i % 4 == 0:
    print
  for j in range(128):
    if int(10*mix21b[j][1]) == int(10*pitchmod[i][2]):
      mix = j
    if int(10*mix21b[j][1]) == int(10*pitchmod[i][3]):
      inv = j
  print ' [%3d,%3d,%3d],' % (pitchmod[i][1],mix,inv),
print '\n]'

print 'kbttable = [ # [lev1,lev2]'
for i in range(128):
  if i and i % 4 == 0:
    print
  print ' [%3d,%3d],' % (kbt[i][1],kbt[i][2]),
print '\n]'
