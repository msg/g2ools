#!/usr/bin/env python

from nord import printf
from nord.g2.modules import *

for m in modules:
  paramnms = [ p.name for p in m.params ]
  outputnms = [ o.name for o in m.outputs ]
  inputnms = [ i.name for i in m.inputs ]
  for name in paramnms:
    if name in outputnms:
      printf('%s: %s p and o\n', m.shortnm, name)
    if name in inputnms:
      printf('%s: %s p and i\n', m.shortnm, name)
  for name in inputnms:
    if name in outputnms:
      printf('%s: %s i and o\n', m.shortnm, name)
