#!/usr/bin/env python

import sys
from nord.g2.file import Pch2File, Prf2File

prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print(fname)
  if fname[-4:].lower() == 'prf2':
    prf2 = Prf2File(fname)
    for p in range(4):
      patch = prf2.performance.patches[p]
      patch.voice.shortencables()
      patch.fx.shortencables()
    prf2.write(fname)
  else:
    pch2 = Pch2File(fname)
    pch2.patch.voice.shortencables()
    pch2.patch.fx.shortencables()
    pch2.write(fname)
