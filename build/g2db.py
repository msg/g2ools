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

import re, sys, string
sys.path.append('..')
from nord import printf

def grab_entries(fname, classnm, arraynm):
  # read file, remove first and last line
  lines = map(string.strip, open(fname).readlines())[1:-1]
  # search for start of first object, removing lines
  while lines[0].find('%s' % classnm) < 0:
    lines.pop(0)
  lines.pop(0) # remove start of first object
  # split on start of preceding objects
  entries = '\n'.join(lines).split('\n)\n%s(' % classnm)
  def fixup(s):
    s = re.sub('\\(','=', s).strip()
    s = re.sub('\\)\n',',\n', s).strip()
    return filter(lambda a: a, s[:-1].split('\n'))
  entries = map(fixup, entries)
  return entries

def build_table(fname, classnm, arraynm):
  entries = grab_entries(fname, classnm, arraynm)
  return entries

class Struct:
  def __init__(self, **kw):
    self.__dict__ = kw

paramlabels = { # [ param#, [ strlist ] ]
   50: { 1: ['Switch'], },                        # ConstSwM
  180: { 1: ['Switch'], },                        # ConstSwT
  195: { 1: ['On'],     },                        # ModAmt
  184: { 1: ['Ch 1'],   },                        # Mix1-1A
  185: { 1: ['Ch 2'],   },                        # Mix1-1S
  194: { 1: ['Ch 1'],  3: ['Ch 2'], },            # Mix2-1A
  123: { 4: ['Ch 1'],  5: ['Ch 2'],
         6: ['Ch 3'],  7: ['Ch 4'], },            # Mix4-1C
  140: { 4: ['Ch 1'],  5: ['Ch 2'],
         6: ['Ch 3'],  7: ['Ch 4'], },            # Mix4-1S
  161: { 8: ['Ch 1'],  9: ['Ch 2'],           
        10: ['Ch 3'], 11: ['Ch 4'],
        12: ['Ch 5'], 13: ['Ch 6'],        
        14: ['Ch 7'], 15: ['Ch 8'], },            # MixFader
   36: { 0: ['On'], },                            # SwOnOffM
   76: { 0: ['On'], },                            # SwOnOffT
  187: { 0: ['Switch'], },                        # Sw2-1M
  100: { 0: ['In 1','In 2'], },                   # Sw2-1
   79: { 0: ['In 1','In 2','In 3','In 4'], },     # Sw4-1
   15: { 0: ['In 1','In 2','In 3','In 4',           
             'In 5','In 6','In 7','In 8'], },     # Sw8-1
  186: { 0: ['Switch'], },                        # Sw1-2M
   17: { 0: ['Out 1','Out 2'], },                 # ValSw1-2
   88: { 0: ['Out 1','Out 2','Out 3','Out 4'], }, # Sw1-4
   78: { 0: ['Out 1','Out 2','Out 3','Out 4',
             'Out 5','Out 6','Out 7','Out 8'], }, # Sw1-8
}                                                      

params = build_table('param_table.txt', 'param', 'parameters')
for param in params:
  param.pop(0)
paramstructs = [ eval('Struct('+''.join(param)+')') for param in params ]

prog = sys.argv.pop(0)

f=open('../nord/g2/params.py','w')
f.write('''#!/usr/bin/env python

from nord import printf
from nord.types import Struct

class ParamMap(Struct): pass
class ParamDef(Struct): pass

params = [
''')

for param in params:
  f.write('  ParamDef(%s\n  ),\n' % ('\n    '.join(param)))

f.write(''']

parammap = ParamMap()
for param in params:
  setattr(parammap, param.name, param)

''')

parammap = Struct()
for struct in paramstructs:
  setattr(parammap, struct.name, struct)

modules = build_table('module_table.txt', 'module', 'modules')
modulestructs = [ eval('Struct('+''.join(module)+')') for module in modules ]

f=open('../nord/g2/modules.py','w')
f.write('''#!/usr/bin/env python

from nord import printf
from nord.types import *
from nord.g2.colors import g2conncolors
from params import parammap

class ModuleMap(Struct): pass


modules = [
''')

for struct in modulestructs:
  printf('%s\n', struct.shortnm)
  s = '''    type=%s,
    height=%s,
    longnm='%s',
    shortnm='%s',
    page=PageType('%s', %s),
''' % (struct.type, struct.height, struct.longnm, struct.shortnm,
       struct.page, struct.pageindex)

  if len(struct.inputs):
    ins = []
    for nm,t,loc in zip(struct.inputs,struct.inputtypes,struct.inputlocs):
      h, v = map(eval,loc.split(','))
      ins.append("      InputType(%-16sg2conncolors.%-14shoriz=%d,vert=%d)," %
          ("'%s'," % nm,'%s,' %t,h,v))
    s += '''    inputs=InputList([
%s
    ]),\n''' % (
      '\n'.join(ins),
      )
  else:
    s += '    inputs=InputList([]),\n'

  if len(struct.outputs):
    outs = []
    for nm,t,loc in zip(struct.outputs, struct.outputtypes, struct.outputlocs):
      h,v = map(eval,loc.split(','))
      outs.append("      OutputType(%-16sg2conncolors.%-14shoriz=%d,vert=%d),"
          % ("'%s'," % nm,'%s,' % t, h, v))
    s += '''    outputs=OutputList([
%s
    ]),\n''' % (
      '\n'.join(outs),
      )
  else:
    s += '    outputs=OutputList([]),\n'

  if len(struct.params):
    s += '    params=ParamList([\n'
    for p in range(len(struct.params)):
      nm, t = struct.params[p], struct.paramtypes[p]
      s += '      ParamType(%-16sparammap.%s' % ("'%s'," % nm, t)
      # add param labels
      if paramlabels.has_key(struct.type):
        if paramlabels[struct.type].has_key(p):
          labels = paramlabels[struct.type][p]
          s += ',\n        labels=[%s]\n      ' % ','.join(
              [ "'%s'" % label for label in labels ])
      s += '),\n'
    s += '    ]),\n'
  else:
    s += '    params=ParamList([]),\n'

  if len(struct.modes):
    s += '''    modes=ModeList([
%s
    ]),\n''' % (
      '\n'.join(["      ModeType(%-16sparammap.%s)," % ("'%s'," % nm,t) 
          for nm,t in zip(struct.modes, struct.modetypes) ]),
      )
  else:
    s += '    modes=ModeList([]),\n'

  s = '''  ModuleType(
%s  ),
''' % (s)
  printf('%s\n', s)
  f.write(s)

f.write(''']

__fromtype = {}
__fromname = {}
modulemap = ModuleMap()
for module in modules:
  __fromname[module.shortnm.lower()] = module
  __fromtype[module.type] = module
  name = module.shortnm.replace('-','_').replace('&','n')
  setattr(modulemap, name, module)

def fromname(name): return __fromname[name.lower()]
def fromtype(type): return __fromtype[type]

if __name__ == '__main__':

  __builtins__.printf = printf

  for module in modules:
    printf('%s.type: %d(0x%02x)\\n', module.shortnm, module.type, module.type)
    for i in range(len(module.inputs)):
      input = module.inputs[i]
      printf(' .inputs[%d] .%s\\n', i, input.name)
    for i in range(len(module.outputs)):
      output = module.outputs[i]
      printf(' .outputs[%d] .%s\\n', i, output.name)
    for i in range(len(module.params)):
      param = module.params[i]
      printf(' .params[%d] .%s\\n', i, param.name)
    for i in range(len(module.modes)):
      mode = module.modes[i]
      printf(' .modes[%d] .%s\\n', i, mode.name)
''')


fromtype = {}
fromname = {}

for struct in modulestructs:
  #printf('%s\\n', struct.longnm)
  fromname[struct.shortnm] = fromtype[struct.type] = Struct(
    inputs=[ Struct(name=nm,type=t)
            for nm,t in zip(struct.inputs, struct.inputtypes) ],
    outputs=[ Struct(name=nm, type=t)
            for nm,t in zip(struct.outputs, struct.outputtypes) ],
    modes=[ Struct(name=nm, type=t) for nm,t in zip(struct.modes,
            map(lambda a,p=parammap: getattr(p,a), struct.modetypes)) ],
    params=[ Struct(name=nm, type=t) for nm,t in zip(struct.params,
            map(lambda a,p=parammap: getattr(p,a), struct.paramtypes)) ],
    page=Struct(name=struct.page,index=struct.pageindex),
    height=struct.height,type=struct.type,
    longnm=struct.longnm,shortnm=struct.shortnm
  )

#del params
#del paramstructs
#del modules
#del modulestructs

# moduledef=moduledb.fromtype[x)
# input = moduledef.inputs[i]
#   input.name
#   input.type
# output = moduledef.outputs[i]
#   output.name
#   output.type
# mode = moduledef.modes[i]
#   mode.name
#   mode.type
# param = moduledef.params[i]
#   param.name
#   param.type
# page = moduledef.page
#   page.name
#   page.index
# moduledef.height
# moduledef.longnm
# moduledef.shortnm

