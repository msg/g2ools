#!/usr/bin/env python2

import sys
import string
from nord.g2.file import Pch2File
from nord.g2.categories import g2categories
from nord import printf, sprintf

def print_description(patch):
  printf('# description\n')
  description = patch.description
  printf('setting category %s\n', g2categories[description.category])
  printf('setting voices %d\n', description.voices)
  printf('setting height %d\n', description.height)
  printf('setting monopoly %d\n', description.monopoly)
  printf('setting variation %d\n', description.variation)
  x = [ description.red, description.blue, description.yellow,
        description.orange, description.green, description.purple,
        description.white ]
  colors = ''.join(['rbyogpw'[i] for i in range(len(x)) if x[i]])
  printf('setting cables %s\n', colors)
    
def print_settings(patch):
  settings = patch.settings
  printf('# settings\n')
  for group in settings.groups:
    for attr in group:
      variations = getattr(settings, attr).variations[:]
      while len(variations) > 1 and variations[-2] == variations[-1]:
        variations.pop(-1)
      variations = ' '.join([ '%d' % v for v in variations])
      printf('setting %s %s\n', attr, variations)

def module_loc(module):
  return '%s%d' % (string.ascii_lowercase[module.horiz], module.vert)

def print_modes(module, loc):
  if hasattr(module, 'modes') and len(module.modes):
    for m, mode in enumerate(module.modes):
      mtype = module.type.modes[m]
      printf('    set %s.%s %s\n', loc, mtype.name, mode.value)

def print_params(module, loc):
  if hasattr(module, 'params') and len(module.params):
    for p, param in enumerate(module.params):
      variations = param.variations[:]
      name = module.type.params[p].name.lower()
      while len(variations) > 1 and variations[-2] == variations[-1]:
        variations.pop(-1)
      variations = ' '.join([ '%d' % v for v in variations])
      printf('    set %s.%s %s\n', loc, name, variations)
      if hasattr(param, 'labels'):
        labels = ' '.join(param.labels)
        printf('    label %s.%s %s\n', loc, name, labels)

def print_modules(area):
  printf('  # modules\n')
  modules = area.modules[:]
  def by_position(a, b):
    x = cmp(a.horiz, b.horiz)
    if x:
      return x
    return cmp(a.vert, b.vert)
  modules.sort(by_position)
  last_vert = -1
  last_horiz = -1
  last_col = -1
  last_color = -1
  for module in modules:
    # handle location/color
    if module.horiz != last_col:
      printf('  column %s\n' % chr(ord('a')+module.horiz))
      last_vert = 0
    last_col = module.horiz
    sep = last_vert - module.vert
    if sep > module.type.height:
      printf('  separate %d\n', sep)
    if module.color != last_color:
      printf('  modulecolor %d\n', module.color)
    last_color = module.color
    # print module
    loc = module_loc(module)
    module.loc = loc
    name = module.name.replace(' ', '\\ ')
    printf('  add %s %s %s\n', module.type.shortnm.lower(), loc, name)
    name = name.lower()
    last_vert = module.vert
    last_horiz = module.horiz

    print_modes(module, loc)

    print_params(module, loc)

def print_netlist(area):
  printf('  # %s netlist\n', area.name)
  for net in area.netlist.nets:
    printf('%s\n', area.netlist.nettos(net))

def print_cables(area):
  printf('  # cables\n')
  for cable in area.cables:
    source, dest = cable.source, cable.dest
    smod, dmod = source.module, dest.module
    stype, dtype = smod.type, dmod.type
    sname = source.type.name.lower()
    dname = dest.type.name.lower()
    sloc = module_loc(smod)
    dloc = module_loc(dmod)
    s = sprintf('connect %s.%s %s.%s', sloc, sname, dloc, dname)
    t = sprintf('# %s -%s %s', stype.shortnm,
        '->'[source.direction], dtype.shortnm)
    printf('  %-35s %s\n', s, t)

def print_area(area):
  printf('\n# area %s modules\n', area.name)
  printf('area %s\n', area.name)
  print_modules(area)
  #print_netlist(area)
  print_cables(area)

def print_knobs(patch):
  printf("\n# knobs\n")
  last_name = ''
  for i in range(len(patch.knobs)):
    knob = patch.knobs[i]
    if knob.assigned:
      if hasattr(knob.param, 'module'):
        loc = module_loc(knob.param.module)
        s = sprintf('knob %s%d.%d %s.%s',
             'abcde'[i/24], ((i/8)%3) + 1, (i&7) + 1, loc,
             knob.param.type.name.lower())
        t = ''
        if knob.param.module.name != last_name:
          t = '  # %s' % knob.param.module.name
        printf('%-35s %s\n', s, t)
        last_name = knob.param.module.name

def print_midicc(patch):
  printf('\n# midicc\n')
  for ctrl in patch.ctrls:
    param = ctrl.param.index
    if ctrl.type == 2:
      index = 1
    else:
      index = ctrl.param.module.index
    area = {0:'fx', 1:'voice', 2:'system'}[ctrl.type]
    printf(' area=%s midicc=%d index=%d param=%d\n',
        area, ctrl.midicc, index, param)

def print_morphs(patch):
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

def print_patch(patch):
  print_description(patch)
  print_settings(patch)
  if len(patch.voice.modules):
    print_area(patch.voice)
  if len(patch.fx.modules):
    print_area(patch.fx)
  print_knobs(patch)
  #print_midicc(patch)
  #print_morphs(patch)

prog = sys.argv.pop(0)
while len(sys.argv):
  filename = sys.argv.pop(0)
  pch = Pch2File(filename)
  printf('# %s\n', filename)
  print_patch(pch.patch)

