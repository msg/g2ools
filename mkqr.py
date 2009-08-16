#!/usr/bin/env python

import nord.g2.modules

pagemap = {
  'In/Out': 0,
  'Note': 1,
  'Osc': 2,
  'LFO': 3,
  'Rnd': 4,
  'Env': 5,
  'Filter': 6,
  'FX': 7,
  'Delay': 8,
  'Shaper': 9,
  'Level': 10,
  'Mixer': 11,
  'Switch': 12,
  'Logic': 13,
  'Seq': 14,
  'MIDI': 15,
}

pages = [ [] for p in range(16) ]
for mod in nord.g2.modules.modules:
  pages[pagemap[mod.page.name]].append(mod)

def byindex(a, b):
  return cmp(a.page.index, b.page.index)
for page in pages:
  page.sort(byindex)

def printdata(name, items):
  if len(items) == 0:
    return ''
  lines = []
  s = '%s: ' % name
  for item in items:
    nm = item.name.lower()
    if len(s) + 5 + len(nm) > 80:
      lines.append(s)
      s = ''
    s += item.name.lower() + ' '
  lines.append(s)
  return '\n    '.join(lines)

for page in pages:
  print '%s:' % page[0].page.name.lower()
  for mod in page:
    s = ' %s: ' % mod.shortnm.lower()
    ins = printdata('in', mod.inputs)
    outs = printdata('out', mod.outputs)
    params = printdata('params', mod.params)
    strs = [ins, outs, params]
    ns = ' %s ' % s.strip()
    for i in range(len(strs)):
      t = strs[i].strip()
      if not t:
        continue
      if len(ns) + len(t) + 1 > 80:
        ns = ns.rstrip()
	if ns[-1] == ',': ns = ns[:-1]
        print ns
	ns = '  '
      ns += t + ', '
    if ns.strip() != '':
      ns = ns.rstrip()
      if ns[-1] == ',': ns = ns[:-1]
      print ns
