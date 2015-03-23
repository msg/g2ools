#!/usr/bin/env python2

import sys
import string
from nord.g2.file import Pch2File
import nord.g2.file
from nord.g2.categories import g2categories
from nord.g2.colors import g2cablecolors, g2conncolors, g2modulecolors
from nord.g2.file import Morph
from nord import printf, sprintf

def clean_variations(variations):
  v = variations[:]
  while len(v) > 1 and v[-2] == v[-1]:
    v.pop(-1)
  return v

def format_description(patch):
  s = sprintf('# description\n')
  description = patch.description
  s += sprintf('setting category %s\n', g2categories[description.category])
  s += sprintf('setting voices %d\n', description.voices)
  s += sprintf('setting height %d\n', description.height)
  s += sprintf('setting monopoly %d\n', description.monopoly)
  s += sprintf('setting variation %d\n', description.variation+1)
  x = [ description.red, description.blue, description.yellow,
        description.orange, description.green, description.purple,
        description.white ]
  colors = ''.join(['rbyogpw'[i] for i in range(len(x)) if x[i]])
  s += sprintf('setting cables %s\n', colors)
  return s

def format_settings(patch):
  settings = patch.settings
  s = sprintf('# settings\n')
  for group in settings.groups:
    for attr in group:
      variations = clean_variations(getattr(settings, attr).variations[:])
      variations = ' '.join([ '%d' % v for v in variations])
      s += sprintf('setting %s %s\n', attr, variations)
  return s

def module_loc(module):
  return '%s%d' % (string.ascii_lowercase[module.horiz], module.vert)

def format_modes(module, loc):
  s = ''
  if hasattr(module, 'modes') and len(module.modes):
    for m, mode in enumerate(module.modes):
      mtype = module.type.modes[m]
      name = mtype.name.lower()
      s += sprintf('    mode %s.%s %s\n', loc, name, mode.value)
  return s

def format_params(module, loc):
  s = ''
  if hasattr(module, 'params') and len(module.params):
    for p, param in enumerate(module.params):
      variations = param.variations[:]
      name = module.type.params[p].name.lower()
      while len(variations) > 1 and variations[-2] == variations[-1]:
        variations.pop(-1)
      variations = ' '.join([ '%d' % v for v in variations])
      s += sprintf('    set %s.%s %s\n', loc, name, variations)
      if hasattr(param, 'labels'):
        labels = ':'.join(param.labels)
        s += sprintf('    label %s.%s %s\n', loc, name, labels)
  return s

def format_modules(area):
  s = sprintf('  # modules\n')
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
      s += sprintf('  column %s\n' % chr(ord('a')+module.horiz))
      last_vert = 0
    last_col = module.horiz
    sep = module.vert - last_vert
    if sep > module.type.height:
      s += sprintf('  separate %d\n', sep - module.type.height)
    if module.color != last_color:
      s += sprintf('  modulecolor %s\n', g2modulecolors.name(module.color))
    last_color = module.color
    # print module
    loc = module_loc(module)
    module.loc = loc
    name = module.name
    s += sprintf('  add %s %s %s\n', module.type.shortnm.lower(), loc, name)
    name = name.lower()
    last_vert = module.vert
    last_horiz = module.horiz

    s += format_modes(module, loc)
    s += format_params(module, loc)
  return s

def format_netlist(area):
  s = sprintf('  # %s netlist\n', area.name)
  for net in area.netlist.nets:
    s += sprintf('# %s\n', area.netlist.nettos(net))
  return s

def format_cables(area):
  s = sprintf('  # cables\n')
  for cable in area.cables:
    source, dest = cable.source, cable.dest
    smod, dmod = source.module, dest.module
    stype, dtype = smod.type, dmod.type
    sname = source.type.name.lower()
    dname = dest.type.name.lower()
    sloc = module_loc(smod)
    dloc = module_loc(dmod)
    t = sprintf('connect %s.%s %s.%s', sloc, sname, dloc, dname)
    u = sprintf('# %s -%s %s', stype.shortnm,
        '->'[source.direction], dtype.shortnm)
    s += sprintf('  %-35s %s\n', t, u)
  return s

def format_area(area):
  s = sprintf('\n# area %s modules\n', area.name)
  s += sprintf('area %s\n', area.name)
  s += format_modules(area)
  #format_netlist(area)
  s += format_cables(area)
  return s

def format_settings_param(param):
  if param.module.index < 2: # morph
    return sprintf('morph.%d.%s', (param.index & 7) + 1, param.name.lower())
  else:
    return sprintf('setting.%s', param.name.lower())

def format_knob_location(location):
  row = location / 24
  col = ((location / 8 ) % 3) + 1
  knob = (location & 7) + 1
  names = ['osc', 'lfo', 'env', 'filter', 'effect']
  return sprintf('%s%d.%d', 'abcde'[row], col, knob), names[row]

def format_knobs(patch):
  s = sprintf("\n# knobs\n")
  last_name = ''
  for i in range(len(patch.knobs)):
    row = i / 24
    knob = patch.knobs[i]
    if not knob.assigned:
      continue

    module = knob.param.module
    knob_loc, name = format_knob_location(i)
    area = {0:'fx', 1:'voice', 2:'settings'}[module.area.index]
    if area == 'settings': # not hasattr(knob.param, 'module'):
      s += sprintf('knob %s %s\n', knob_loc, format_settings_param(knob.param))
      continue

    loc = module_loc(module)
    t = sprintf('knob %s %s.%s.%s', knob_loc, area, loc,
          knob.param.type.name.lower())
    u = sprintf('  # %s:', name)
    if module.name != last_name:
      u += ' ' + module.name + ' (' + module.type.shortnm.lower() + ')'
    s += sprintf('%-35s %s\n', t, u)
    last_name = module.name
  return s

def format_midicc(patch):
  s = sprintf('\n# midicc\n')
  for ctrl in patch.ctrls:
    index = ctrl.param.index
    area = {0:'fx', 1:'voice', 2:'settings'}[ctrl.param.module.area.index]
    if ctrl.param.module.area.index != 2:
      loc = module_loc(ctrl.param.module)
      t = sprintf('%s.%s', loc, ctrl.param.type.name.lower())
    else:
      t = format_settings_param(ctrl.param)
    s += sprintf('midicc %2d %s\n', ctrl.midicc, t)
  return s

def format_morphs(patch):
  settings = patch.settings
  s = sprintf('\n# morphs\n')
  s += '# morphs per variation: '
  for morphmap in settings.morphmaps:
    s += sprintf('%d ', len(morphmap))
  s += '\n'
  s += sprintf('# label morph.<morph> <label>\n')
  s += sprintf('# set morph.<morph>.dial <variations>\n')
  s += sprintf('# set morph.<morph>.mode <variations>\n')
  s += sprintf('#  add morph.<morph> <variation> <area>.<loc>.<param> <range>\n')
  morphs = settings.morphs
  for i, morph in enumerate(morphs, 1):
    s += sprintf('label morph.%d %s\n', i, morph.label)
  for i, morph in enumerate(morphs, 1):
    variations = clean_variations(morph.dial.variations)
    t = ' '.join(map(lambda a: '%d' % a, variations))
    s += sprintf('set morph.%d.dial %s\n', i, t)
    variations = clean_variations(morph.mode.variations)
    t = ' '.join(map(lambda a: '%d' % a, variations))
    s += sprintf('set morph.%d.mode %s\n', i, t)

  for i, morph in enumerate(morphs, 1):
    maps = morph.maps
    for variation in range(len(maps)):
      if not len(maps[variation]):
        continue
      for mmap in maps[variation]:
        param = mmap.param
        loc = module_loc(param.module)
        index = mmap.morph.dial.index
        area = ['fx', 'voice', 'settings'][param.module.area.index]
        t = sprintf('%s.%s.%s ', area, loc, param.type.name.lower())
        t += sprintf('%d ' % mmap.range)
        s += sprintf('  add morph.%d %d %s\n', index, variation, t)

  return s

def format_patch(patch):
  s = format_description(patch)
  s += format_settings(patch)
  if len(patch.voice.modules):
    s += format_area(patch.voice)
  if len(patch.fx.modules):
    s += format_area(patch.fx)
  s += format_knobs(patch)
  s += format_midicc(patch)
  s += format_morphs(patch)
  return s

if __name__ == '__main__':
  prog = sys.argv.pop(0)
  while len(sys.argv):
    filename = sys.argv.pop(0)
    pch = Pch2File(filename)
    s = sprintf('# %s\n', filename) + format_patch(pch.patch)
    printf("%s\n", s)

