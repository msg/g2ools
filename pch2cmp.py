#!/usr/bin/env python2

import os, sys, traceback
from nord import printf
from nord.g2.file import Pch2File

def compare_shortnm(a, b):
  x = cmp(a.module.type.shortnm, b.module.type.shortnm)
  if x: return x
  return cmp(a.type.name, b.type.name)

def compare_ports(aport, bport):
  if not aport and bport: return 1
  if aport and not bport: return -1
  return 0

def get_nets(pch2):
  # sort each net's inputs by mod-name/port-name
  nets = [ n for n in pch2.patch.voice.netlist.nets if n.output ]
  for net in nets:
    #ins = net.inputs[:]
    net.inputs.sort(compare_shortnm)

  def ordernets(a, b):
    x = compare_shortnm(a.output, b.output)
    if x: return x
    x = cmp(len(a.inputs), len(b.inputs))
    if x: return x
    for i in range(len(a.inputs)):
      x = compare_shortnm(a.inputs[i], b.inputs[i])
      if x: return x
    return 0

  nets.sort(ordernets)

def check_ports(modmap, aport, bport):
  x = compare_ports(aport, bport)
  if x: return x
  x = compare_shortnm(aport, bport)
  if x: return x
  # if index of aport.module not seen, create a new mapping to bport.module
  aidx, bidx = aport.module.index, bport.module.index
  if modmap.has_key(aidx):
    return cmp(modmap[aidx], bidx)
  modmap[aidx] = bidx
  return 0 # only have one to check against, have to assume it's correct.

def check_net(modmap, anet, bnet):
  # output module/port must match
  if anet.output == None:
    return -1
  if bnet.output == None:
    return 1
  x = check_ports(modmap, anet.output, bnet.output)
  if x: return x
  # length of netlist must match
  x = cmp(len(anet.inputs),len(bnet.inputs))
  if x: return x
  # all inputs must match
  for ain, bin in zip(anet.inputs, bnet.inputs):
    x = check_ports(modmap, ain, bin)
    if x: return x
  return 0

def compare_netlist(a, b):
  x = cmp(len(a.nets), len(b.nets))
  if x: return x
  modmap = {}
  for anet, bnet in zip(a.nets, b.nets):
    x = check_net(modmap, anet, bnet)
    if x: return x
  return 0

def matchingnets(a, b):
  modmap = {}
  matches = 0
  for anet in a.nets:
    for bnet in b.nets:
      if check_net(modmap, anet, bnet) == 0:
        match += 1
  return matches

filenames = [ f for f in sys.argv[1:] if f[-4:] == 'pch2' ]
filenames.sort()
pch2s = []
for filename in filenames:
  printf('%s\n', os.path.basename(filename))
  p = Pch2File(filename)
  get_nets(p)
  pch2s.append(p)

def bynetsize(a, b):
  return cmp(len(a.patch.voice.netlist.nets), len(b.patch.voice.netlist.nets))
pch2s.sort(bynetsize)

p = {}
for pch2 in pch2s:
  k = len(pch2.patch.voice.netlist.nets)
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
      try:
        if compare_netlist(b.patch.voice.netlist,a[j].patch.voice.netlist) == 0:
          matches.append(a.pop(j))
        else:
          j += 1
      except:
        raise Exception('%s\n patches: %s %s' % (
            traceback.format_exc(),
            os.path.basename(b.filename), os.path.basename(a[j].filename)))

    if len(matches) == 1:
      continue
    printf(' matches:\n')
    for match in matches:
      filename = os.path.basename(match.filename)
      printf('  %s\n', filename)

