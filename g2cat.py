#!/usr/bin/env python

import sys
sys.path.append('.')
from nord.g2.file import Pch2File

def printpatch(patch):
  print 'patchdescription:'
  desc = patch.description
  #print ' header:', hexdump(desc.header)
  print ' voicecnt=%d height=%d unk2=0x%02x mono=%d var=%d cat=%d' % (
      desc.voicecnt, desc.height, desc.unk2, desc.monopoly,
      desc.variation, desc.category)
  print '  red=%d blue=%d yellow=%d orange=%d green=%d purple=%d white=%d' % (
      desc.red, desc.blue, desc.yellow, desc.orange, desc.green,
      desc.purple, desc.white)
  print 'knobs:'
  for i in range(len(patch.knobs)):
    knob = patch.knobs[i]
    if knob.assigned:
      print ' %s%d:%d %s:"%s":%s isled=0x%02x' % (
          'ABCDE'[i/24],(i/8)%3,i&7,
          ['fx','voice'][knob.param.module.area.index],
          knob.param.module.name, knob.param.type.name,
          knob.isled)
  print 'MIDIAssignments:'
  for midiassignment in patch.midiassignments:
    if midiassignment.type == 2:
      index,param = midiassignment.param
    else:
      index,param = midiassignment.param.module.index,midiassignment.param.index
    print ' type=%s midicc=%d index=%d param=%d' % (
        {0:'fx',1:'voice',2:'system'}[midiassignment.type], midiassignment.midicc,
        index,param)
  settings = patch.settings
  print 'morphs:'
  print ' dial settings:'
  for i in range(len(settings.morphs)):
    print ' ',settings.morphs[i].dials
  print ' modes:'
  for i in range(len(settings.morphs)):
    print ' ',settings.morphs[i].modes
  print ' names:'
  print ' ',','.join(
      [ settings.morphs[i].label for i in range(len(settings.morphs))])
  print 'variations:'
  for attr in [ 'activemuted','patchvol','glide','glidetime','bend', 'semi',
                'vibrato','cents','rate',
                'arpeggiator','arptime','arptype','octaves',
                'octaveshift','sustain' ]:
    print ' %-16s' % (attr+':'), [ getattr(var,attr) for var in settings.variations ]
  print 'modules:'
  for module in patch.voice.modules:
    print ' %-18s %-16s %2d:(%d,%2d)%3d type=%3d uprate=%d leds=%d' % (
        '"%s"' % module.name, module.type.shortnm,
        module.index, module.horiz, module.vert, module.color,
        module.type.type, module.uprate, module.leds)
    if hasattr(module, 'modes') and len(module.modes):
      print '  modes:'
      for m in range(len(module.modes)):
        mode = module.modes[m]
        mtype = module.type.modes[m]
        print '  %-16s %r' % (mtype.name+':', mode)
    if hasattr(module, 'params') and len(module.params):
      print '  params:'
      for p in range(len(module.params)):
        param = module.params[p]
        ptype = module.type.params[p]
        print '  %-16s %r' % (ptype.name+':', param.variations)
        if hasattr(param,'labels'):
          print '   %r' % param.labels
  print 'cables:'
  for cable in patch.voice.cables:
    source,dest = cable.source,cable.dest
    smod,dmod = source.module,dest.module
    stype,dtype = smod.type, dmod.type
    snm = source.type.name
    dnm = dest.type.name
    print ' %s.%s -%s %s.%s: c=%d' % (
      stype.shortnm,snm,'->'[source.direction],dtype.shortnm,dnm,cable.color)
  #print 'Unknown0x69:'
  #print '','\n '.join(hexdump(patch.unknown0x69.data).split('\n'))
  #print 'ParamNames fx:'
  #print '','\n '.join(hexdump(patch.fx.paramnames).split('\n'))

prog = sys.argv.pop(0)
while len(sys.argv):
  fname = sys.argv.pop(0)
  print '"%s"' % fname
  pch2 = Pch2File(fname)
  printpatch(pch2.patch)
