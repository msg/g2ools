#!/usr/bin/env python

import sys
import string
from nord.g2.file import Pch2File
from nord.g2.categories import G2Categories
from nord.net import printnet
from nord import printf

def printdescription(patch):
  printf('# description\n')
  desc = patch.description
  printf('setting category, %s\n', G2Categories[desc.category])
  printf('setting voices, %d\n', desc.nvoices)
  printf('# height %d\n', desc.height)
  printf('setting monopoly, %d\n', desc.monopoly)
  printf('setting variation, %d\n', desc.variation)
  x = [ desc.red, desc.blue, desc.yellow, desc.orange, desc.green,
      desc.purple, desc.white ]
  colors = ''.join(['RBYOGPW'[i] for i in range(len(x)) if x[i]])
  printf('setting colors, %s\n', colors)
  #printf(' unk2=0x%02x\n', desc.unk2)
    
def printsettings(patch):
  settings = patch.settings
  printf('# settings\n')
  for attr in [ 'activemuted','patchvol','glide','glidetime','bend', 'semi',
                'vibrato','cents','rate',
                'arpeggiator','arptime','arptype','octaves',
                'octaveshift','sustain' ]:
    printf('setting %s, %s\n', attr,
        ', '.join([ '%d' % v for v in getattr(settings,attr).variations]))

def printmodules(area):
  printf('# %s modules\n', area.name)
  modules = area.modules[:]
  def byposition(a, b):
    x = cmp(a.horiz, b.horiz)
    if x: return x
    return cmp(a.vert, b.vert)
  modules.sort(byposition)
  lastvert = -1
  lasthoriz = -1
  modcolindex = 0
  for module in modules:
    sep = module.vert - lastvert
    if sep > module.type.height:
      sep = ', sep=%d' % sep
    else:
      sep = ''
    if module.color != 0:
      color = ', color=%d' % module.color
    else:
      color = ''
    loc = '%s%d' % (string.ascii_lowercase[module.horiz],modcolindex)
    module.loc = loc
    #moduleloc[loc] = module
    printf('add %s, %s, %s%s%s\n',
        module.type.shortnm.lower(), loc, module.name, color, sep)
    lastvert = module.vert
    modcolindex += 1
    if lasthoriz != module.horiz:
      lastvert = -1
      modcolindex = 0
    lasthoriz = module.horiz
    if hasattr(module, 'modes') and len(module.modes):
      printf('  # modes\n')
      for m in range(len(module.modes)):
        mode = module.modes[m]
        mtype = module.type.modes[m]
        printf('  set %s.%s, %s\n', loc, mtype.name, mode.value)
    if hasattr(module, 'params') and len(module.params):
      printf('  # params\n')
      for p in range(len(module.params)):
        param = module.params[p]
        ptype = module.type.params[p]
        printf('  set %s.%s, %s\n', loc, ptype.name.lower(),
	    ', '.join([ '%d' % v for v in param.variations]))
        if hasattr(param,'labels'):
          printf('  label %s.%s, %s\n', loc, ptype.name.lower(),
	      ', '.join(param.labels))

def printnetlist(area):
  printf('# %s netlist\n', area.name)
  for net in area.netlist:
    printnet(net)

def printcables(patch):
  printf('# cables\n')
  for cable in patch.voice.cables:
    source,dest = cable.source,cable.dest
    smod,dmod = source.module,dest.module
    stype,dtype = smod.type, dmod.type
    snm = source.type.name
    dnm = dest.type.name
    printf(' %s.%s -%s %s.%s: c=%d\n', stype.shortnm, snm,
        '->'[source.direction], dtype.shortnm, dnm, cable.color)

def printknobs(patch):
  printf('# knobs\n')
  for i in range(len(patch.knobs)):
    knob = patch.knobs[i]
    if knob.assigned:
      if hasattr(knob.param,'module'):
        printf(' %s%d:%d %s:"%s":%s isled=0x%02x\n',
            'ABCDE'[i/24],(i/8)%3,i&7,
            ['fx','voice'][knob.param.module.area.index],
            knob.param.module.name, knob.param.type.name,
            knob.isled)

def printmidicc(patch):
  printf('midicc:\n')
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
  printf('morphs:\n')
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
    printf("area voice\n")
    printmodules(patch.voice)
    printnetlist(patch.voice)
  if len(patch.fx.modules):
    printf("area fx\n")
    printmodules(patch.fx)
    printnetlist(patch.fx)
  #printcables(patch)
  #printknobs(patch)
  #printmidicc(patch)
  #printmorphs(patch)

  #printf('Unknown0x69:\n')
  #printf('%s\n','\n '.join(hexdump(patch.unknown0x69.data).split('\n')))
  #printf('ParamNames fx:\n')
  #printf('%s\n','\n '.join(hexdump(patch.fx.paramnames).split('\n')))

prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  pch = Pch2File(fname)
  patch = pch.patch
  printf('# %s\n', fname)
  printpatch(patch)

