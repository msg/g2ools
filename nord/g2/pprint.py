#!/usr/bin/env python2
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

from nord.g2.categories import g2categories
from nord import printf

def printdescription(patch):
  printf('patchdescription:\n')
  desc = patch.description
  printf(' category: %s\n', g2categories[desc.category])
  printf(' voices: %d\n', desc.voices)
  printf(' height: %d\n', desc.height)
  printf(' monopoly: %d\n', desc.monopoly)
  printf(' variation: %d\n', desc.variation)
  x = [ desc.red, desc.blue, desc.yellow, desc.orange, desc.green,
      desc.purple, desc.white ]
  colors = ''.join(['RBYOGPW'[i] for i in xrange(len(x)) if x[i]])
  printf(' colors: %s\n', colors)
  #printf(' unk2=0x%02x\n', desc.unk2)
    
def printvariations(patch):
  settings = patch.settings
  printf('variations:\n')
  for attr in [ 'activemuted', 'patchvol', 'glide', 'glidetime', 'bend', 'semi',
                'vibrato', 'cents', 'rate',
                'arpeggiator', 'arptime', 'arptype', 'octaves',
                'octaveshift', 'sustain' ]:
    printf(' %-16s %s\n', (attr+':'), getattr(settings, attr).variations)

def printmodules(patch):
  printf('modules:\n')
  for module in patch.voice.modules:
    printf(' %-18s %-16s %2d:(%d,%2d)%3d type=%3d uprate=%d leds=%d\n', 
        '"%s"' % module.name, module.type.shortnm,
        module.index, module.horiz, module.vert, module.color,
        module.type.id, module.uprate, module.leds)
    if hasattr(module, 'modes') and len(module.modes):
      printf('  modes:\n')
      for m, mode in enumerate(module.modes):
        mtype = module.type.modes[m]
        printf('  %-16s %r\n', mtype.name+':', mode)
    if hasattr(module, 'params') and len(module.params):
      printf('  params:\n')
      for p, param in enumerate(module.params):
        ptype = module.type.params[p]
        printf('  %-16s %r\n', ptype.name+':', param.variations)
        if hasattr(param, 'labels'):
          printf('   %r\n', param.labels)

def printcables(patch):
  printf('cables:\n')
  for cable in patch.voice.cables:
    source, dest = cable.source, cable.dest
    smod, dmod = source.module, dest.module
    stype, dtype = smod.type, dmod.type
    snm = source.type.name
    dnm = dest.type.name
    printf(' %s.%s -%s %s.%s: c=%d\n', stype.shortnm, snm,
        '->'[source.direction], dtype.shortnm, dnm, cable.color)

def printknobs(patch):
  printf('knobs:\n')
  for i, knob in enumerate(patch.knobs):
    if knob.assigned:
      printf(' %s%d:%d ', 'ABCDE'[i/24], (i/8)%3, i&7)
      if hasattr(knob.param, 'module'):
        printf('%s:"%s":%s isled=0x%02x\n',
            ['fx', 'voice'][knob.param.module.area.index],
            knob.param.module.name, knob.param.type.name,
            knob.isled)
      else:
        printf('morph:%d:"%s"\n', knob.param.index, knob.param.label)

midicctable = {
    0: 'Bank Select MSB',
    1: 'Modwheel',
    2: 'Breath',
    4: 'Foot ctrl',
    5: 'Port time',
    6: 'Data MSB',
    8: 'Balance',
   10: 'Pan',
   38: 'Data LSB',
   65: 'Portamento On/Off',
   66: 'Sustenuto On/Off',
   67: 'Soft Pedal On/Off',
   68: 'Legato Pedal On/Off',
   69: 'Hold 2',
   84: 'Port control',
   91: 'Effect 1 Depth',
   92: 'Effect 2 Depth',
   93: 'Effect 3 Depth',
   94: 'Effect 4 Depth',
   95: 'Effect 5 Depth',
   96: 'G2 Global Modwheel 1',
   97: 'G2 Global Modwheel 2',
   98: 'NRPN LSB',
   99: 'NPRN MSB',
  100: 'RPN LSB',
  101: 'RPN MSB',
  121: 'Reset all controllers',
  123: 'All notes off',
}

def printmidicc(patch):
  printf('midicc:\n')
  for ctrl in patch.ctrls:
    if ctrl.param.module.area.index == 2:
      name = ctrl.param.name
      index, param = ctrl.param.index, ctrl.param.param
    else:
      name = ctrl.param.module.name + ':' + ctrl.param.type.name
      index = ctrl.param.module.index
      param = ctrl.param.index
    if midicctable.has_key(ctrl.midicc):
      s = '"' + midicctable[ctrl.midicc] + '"'
    else:
      s = ''
    area = param.module.area.index
    printf(' %-8s midicc=%2d %s(%d, %d) %s\n',
        {0:'fx', 1:'voice', 2:'settings'}[area], ctrl.midicc,
        name, index, param, s)

def printmorphs(patch):
  settings = patch.settings
  printf('morphs:\n')
  printf(' dial settings:\n')
  for i in range(len(settings.morphs)):
    printf(' %s\n', settings.morphs[i].dial.variations)
  printf(' modes:\n')
  for i in range(len(settings.morphs)):
    printf(' %s\n', settings.morphs[i].mode.variations)
  printf(' names:\n')
  printf(' %s\n', ', '.join(
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
  printvariations(patch)
  printmodules(patch)
  printcables(patch)
  printknobs(patch)
  printmidicc(patch)
  printmorphs(patch)

  #printf('Unknown0x69:\n')
  #printf('%s\n', '\n '.join(hexdump(patch.unknown0x69.data).split('\n')))
  #printf('ParamNames fx:\n')
  #printf('%s\n', '\n '.join(hexdump(patch.fx.paramnames).split('\n')))

