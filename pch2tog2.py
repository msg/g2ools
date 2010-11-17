#!/usr/bin/env python2

import sys
import string
from nord.g2.file import Pch2File
from nord.g2.categories import G2Categories
from nord import printf, sprintf

def printdescription(patch):
  printf('# description\n')
  desc = patch.description
  printf('setting category %s\n', G2Categories[desc.category])
  printf('setting voices %d\n', desc.voices)
  printf('setting height %d\n', desc.height)
  printf('setting monopoly %d\n', desc.monopoly)
  printf('setting variation %d\n', desc.variation)
  x = [ desc.red, desc.blue, desc.yellow, desc.orange, desc.green,
      desc.purple, desc.white ]
  colors = ''.join(['RBYOGPW'[i] for i in range(len(x)) if x[i]])
  printf('setting colors %s\n', colors)
  #printf(' unk2=0x%02x\n', desc.unk2)
    
def printsettings(patch):
  settings = patch.settings
  printf('# settings\n')
  for group in patch.settings.groups:
    for attr in group:
      variations = getattr(settings, attr).variations[:]
      while len(variations) > 1 and variations[-2] == variations[-1]:
        variations.pop(-1)
      printf('setting %s %s\n', attr,
          ' '.join([ '%d' % v for v in variations]))

def module_loc(module):
  return '%s%d' % (string.ascii_lowercase[module.horiz],module.vert)

def printmodules(area):
  printf('  # modules\n')
  modules = area.modules[:]
  def byposition(a, b):
    x = cmp(a.horiz, b.horiz)
    if x: return x
    return cmp(a.vert, b.vert)
  modules.sort(byposition)
  lastvert = -1
  lasthoriz = -1
  lastcol = -1
  lastcolor = -1
  for module in modules:
    if module.horiz != lastcol:
      printf('  column %s\n' % chr(ord('a')+module.horiz))
      lastvert = 0
    lastcol = module.horiz
    sep = lastvert - module.vert
    if sep > module.type.height:
      printf('  separate %d\n', sep)
    if module.color != lastcolor:
      printf('  modulecolor %d\n', module.color)
    lastcolor = module.color
    loc = module_loc(module)
    module.loc = loc
    #moduleloc[loc] = module
    modulename = module.name.replace(' ', '\\ ')
    printf('  add %s %s %s\n', module.type.shortnm.lower(), loc, modulename)
    modulename = modulename.lower()
    lastvert = module.vert
    lasthoriz = module.horiz
    if hasattr(module, 'modes') and len(module.modes):
      for m in range(len(module.modes)):
        mode = module.modes[m]
        mtype = module.type.modes[m]
        printf('    set %s.%s %s\n', loc, mtype.name, mode.value)
    if hasattr(module, 'params') and len(module.params):
      for p in range(len(module.params)):
        param = module.params[p]
        ptype = module.type.params[p]
        variations = param.variations[:]
        while len(variations) > 1 and variations[-2] == variations[-1]:
          variations.pop(-1)
        printf('    set %s.%s %s\n', loc, ptype.name.lower(),
            ' '.join([ '%d' % v for v in variations]))
        if hasattr(param,'labels'):
          printf('    label %s.%s %s\n', loc, ptype.name.lower(),
              ' '.join(param.labels))

def printnetlist(area):
  printf('  # %s netlist\n', area.name)
  for net in area.netlist.nets:
    printf('%s\n', area.netlist.nettos(net))

def printcables(area):
  printf('  # cables\n')
  for cable in area.cables:
    source,dest = cable.source,cable.dest
    smod,dmod = source.module,dest.module
    stype,dtype = smod.type, dmod.type
    sname = source.type.name.lower()
    dname = dest.type.name.lower()
    sloc = module_loc(smod)
    dloc = module_loc(dmod)
    s=sprintf('connect %s.%s %s.%s', sloc, sname, dloc, dname)
    t=sprintf('# %s -%s %s', stype.shortnm,
        '->'[source.direction],dtype.shortnm)
    printf('  %-35s %s\n', s, t)

def printarea(area):
  printf('\n# area %s modules\n', area.name)
  printf('area %s\n', area.name)
  printmodules(area)
  #printnetlist(area)
  printcables(area)

def printknobs(patch):
  printf("\n# knobs\n")
  last_name = ''
  for i in range(len(patch.knobs)):
    knob = patch.knobs[i]
    if knob.assigned:
      if hasattr(knob.param,'module'):
        loc = module_loc(knob.param.module)
        s = sprintf('knob %s%d.%d %s.%s',
             'abcde'[i/24],((i/8)%3) + 1,(i&7) + 1, loc,
             knob.param.type.name.lower())
        t = ''
        if knob.param.module.name != last_name:
          t = '  # %s' % knob.param.module.name
        printf('%-35s %s\n', s, t)
        last_name = knob.param.module.name

def printmidicc(patch):
  printf('\n# midicc\n')
  for ctrl in patch.ctrls:
    param = ctrl.param.index
    if ctrl.type == 2:
      index = 1
    else:
      index = ctrl.param.module.index
    printf(' type=%s midicc=%d index=%d param=%d\n', 
        {0:'fx',1:'voice',2:'system'}[ctrl.type], ctrl.midicc,
        index, param)

def printmorphs(patch):
  settings = patch.settings
  printf('\n# morphs\n')
  printf(' dial settings:\n')
  for i in range(len(settings.morphs)):
    printf(' %s\n', settings.morphs[i].dials.variations)
  printf(' modes:\n')
  for i in range(len(settings.morphs)):
    printf(' %s\n', settings.morphs[i].modes.variations)
  printf(' names:\n')
  printf(' %s\n', ','.join(
      [ settings.morphs[i].label for i in range(len(settings.morphs))]))
  printf(' parameters:\n')
  for i in range(len(settings.morphs)):
    morph = settings.morphs[i]
    printf('  morph %d:\n', i)
    for j in range(len(morph.maps)):
      printf('   varation %d:\n', j)
      for k in range(len(morph.maps[j])):
        map = morph.maps[j][k]
        printf('    %s:%s range=%d\n', map.param.module.name,
            map.param.type.name, map.range)

def printpatch(patch):
  printdescription(patch)
  printsettings(patch)
  if len(patch.voice.modules):
    printarea(patch.voice)
  if len(patch.fx.modules):
    printarea(patch.fx)
  printknobs(patch)
  #printmidicc(patch)
  #printmorphs(patch)

prog = sys.argv.pop(0)
while len(sys.argv):
  filename = sys.argv.pop(0)
  pch = Pch2File(filename)
  printf('# %s\n', filename)
  printpatch(pch.patch)

