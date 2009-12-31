#!/usr/bin/env python

import sys, os
from nord import printf
from nord.g2.file import Pch2File

def cmpnm(a, b):
  x = cmp(a.module.type.shortnm, b.module.type.shortnm)
  if x:
    return x
  return cmp(a.type.name, b.type.name)

def getnets(pch2):
  def ordernets(a, b):
    ao = a.output
    bo = b.output
    x = cmpnm(ao, bo)
    if x: return x
    ains = len(a.inputs)
    bins = len(b.inputs)
    if ains != bins:
      return cmp(ains, bins)
    for i in range(len(a.inputs)):
      x = cmpnm(a.inputs[i], b.inputs[i])
      if x: return x
    return 0

  nets = [ n for n in pch2.patch.voice.netlist if n.output ]
  for net in nets:
    ins = net.inputs[:]
    ins.sort(cmpnm)
  nets.sort(ordernets)

def chkports(modmap, aport, bport):
  x = cmpnm(aport, bport)
  if x: return x
  # if index of aport.module not seen, create a new mapping to bport.module
  idx = aport.module.index
  if modmap.has_key(idx):
    return cmp(modmap[idx], bport.module.index)
  modmap[idx] = bport.module.index
  return 0 # only have one to check against, have to assume it's correct.

def cmpnetlist(a, b):
  x = cmp(len(a), len(b))
  if x: return x
  modmap = {}
  for i in range(len(a)):
    anet = a[i]
    bnet = b[i]
    # output module/port must match
    x = chkports(modmap, anet.output, bnet.output)
    if x: return x
    # length of netlist must match
    x = cmp(len(anet.inputs),len(bnet.inputs))
    if x: return x
    for j in range(len(anet.inputs)):
      # input module/port must match
      x = chkports(modmap, anet.inputs[j],bnet.inputs[j])
      if x: return x
  return 0
    

fnames = [ f for f in sys.argv[1:] if f[-4:] == 'pch2' ]
fnames.sort()
pch2s = []
for fname in fnames:
  printf('%s\n', fname)
  p = Pch2File(fname)
  pch2s.append(p)

def ordernetsize(a, b):
  return cmp(len(a.patch.voice.netlist), len(b.patch.voice.netlist))

pch2s.sort(ordernetsize)
p = {}
for pch2 in pch2s:
  k = len(pch2.patch.voice.netlist)
  d = p.get(k, None)
  if not d:
    d = p[k] = []
  d.append(pch2)

for k in p.keys():
  a = p[k]
  printf('net size %s:\n', k)
  while len(a):
    b = a.pop(0)
    matches = [b]
    j = 0
    while j < len(a):
      if cmpnetlist(b.patch.voice.netlist,a[j].patch.voice.netlist) == 0:
        matches.append(a.pop(j))
      else:
        j += 1
    if len(matches) == 1:
      continue
    printf(' matches:\n')
    for match in matches:
      fname = os.path.basename(match.fname)
      printf('  %s\n', fname)
      
