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

import logging
import getopt, os, sys
from glob import glob
from exceptions import KeyboardInterrupt
sys.path.append('.')
from nord.g2.file import Pch2File
from nord.file import MorphMap
from nord.g2.colors import g2modulecolors, g2cablecolors, g2conncolors
from nord.nm1.file import PchFile
from nord.nm1.colors import nm1cablecolors, nm1conncolors
from nord.nm1.file import NM1Error
from nord.convert import typetable,setv
from nord.net import printnet
from nord.convert.version import version as g2oolsversion
from nord.utils import toascii

nm2g2colors = {
  nm1cablecolors.red:    g2cablecolors.red,
  nm1cablecolors.blue:   g2cablecolors.blue,
  nm1cablecolors.yellow: g2cablecolors.yellow,
  nm1cablecolors.grey:   g2cablecolors.blue,
  nm1cablecolors.green:  g2cablecolors.green,
  nm1cablecolors.purple: g2cablecolors.purple,
}
conn2cablecolors = {
  g2conncolors.red:           g2cablecolors.red,
  g2conncolors.blue:          g2cablecolors.blue,
  g2conncolors.yellow:        g2cablecolors.yellow,
  g2conncolors.orange:        g2cablecolors.orange,
  g2conncolors.blue_red:      g2cablecolors.blue,
  g2conncolors.yellow_orange: g2cablecolors.yellow,
}

def doconverters(nmarea,g2area,config):
  converters = []
  for module in nmarea.modules:
    if module.type.type in typetable:
      logging.debug('%s: %s %d(0x%02x)' % (module.type.shortnm, module.name,
          module.type.type,module.type.type))
      conv = typetable[module.type.type](nmarea,g2area,module,config)
      converters.append(conv)
      #g2module = conv.g2module
      #print '%s (%d,%d)' % (g2module.type.shortnm,
      #    g2module.horiz, g2module.vert)
    else:
      logging.warning('No converter for module "%s" type %d(0x%02x)' % (
          module.type.shortnm, module.type.type, module.type.type))
  return converters

def domodules(converters, config):
  logging.info('domodule:')
  for conv in converters:
    logging.debug('%s: %s %d(0x%02x)' % (conv.nmmodule.type.shortnm,
        conv.nmmodule.name, conv.nmmodule.type.type,conv.nmmodule.type.type))
    conv.domodule()


def docolorizemultis(converters, config):
  modcolors = [
      g2modulecolors.yellow2,g2modulecolors.green2,
      g2modulecolors.cyan2,g2modulecolors.blue2,g2modulecolors.magenta1]
  # colorize multi-module convertions
  curr = 0
  for conv in converters:
    if len(conv.g2modules):
      conv.g2module.color = modcolors[curr]
      for mod in conv.g2modules:
        mod.color = modcolors[curr]
      curr = (curr+1)%len(modcolors)

def doreposition(converters, config):
  logging.info('reposition:')
  # reposition modules
  locsorted = converters[:]
  def loccmp(a, b):
    if a.horiz == b.horiz:
      return cmp(a.nmmodule.vert, b.nmmodule.vert)
    return cmp(a.nmmodule.horiz,b.nmmodule.horiz)
  locsorted.sort(loccmp)

  if len(locsorted):
    locsorted[0].reposition(None)
    for i in range(1,len(locsorted)):
      ca = locsorted[i-1]
      cb = locsorted[i]
      if ca.nmmodule.horiz == cb.nmmodule.horiz:
        cb.reposition(ca)
      else:
        cb.reposition(None)

def doprecables(converters, config):
  logging.info('precables:')
  for conv in converters:
    logging.debug('%s: %s %d(0x%02x)' % (conv.nmmodule.type.shortnm,
        conv.nmmodule.name, conv.nmmodule.type.type,conv.nmmodule.type.type))
    conv.precables()

def docables(nmarea, g2area, converters, config):
  # now do the cables
  logging.info('cables:')
  for cable in nmarea.cables:
    source = cable.source
    g2source = None
    if source.direction:
      if source.index < len(source.conv.outputs):
        g2source = source.conv.outputs[source.index]
    elif source.index < len(source.conv.inputs):
      g2source = source.conv.inputs[source.index]
    dest = cable.dest
    s = '%s:%s:%d -> %s:%s:%d :' % (
        source.module.name,source.type.name, source.type.type,
        dest.module.name,dest.type.name, dest.type.type)
    if dest.index >= len(dest.conv.inputs) or not g2source:
      logging.warning(s + ' UNCONNECTED')
    else:
      s += ' connected'
      g2dest = dest.conv.inputs[dest.index]
      if not source.net.output:
        s += ' No source connection'
        color = g2cablecolors.white
      elif source.net.output.type.type == nm1conncolors.slave:
        color = g2cablecolors.purple
      else:
        color = source.net.output.type.type
      g2area.connect(g2source,g2dest,color)
      logging.debug(s)

def douprate(g2area,config):
  # now parse the entire netlist of the area and .uprate=1 all
  # modules with blue_red and yello_orange inputs connected to red outputs.
  # scan module list until we done change any modules
  logging.info('uprate:')
  done = 0
  while not done:
    modified = 0
    for module in g2area.modules:
      #logging.debug('%s:%s' % (module.name, module.type.shortnm))
      for input in module.inputs:
        if not input.net:
          continue
        #logging.debug(' %s:%d' % (input.type.name, input.rate))
        # try and make all logic run at control rate.
        if input.rate == g2conncolors.yellow_orange:
          input.rate = g2conncolors.yellow
          continue
        if input.rate != g2conncolors.blue_red:
          continue
        if not input.net.output:
          continue
        if input.net.output.rate == g2conncolors.red:
          #logging.debug('%s:%s %s' % (
          #     module.name,input.type.name,input.net.output.type.name))
          modified = 1
          module.uprate = 1
          input.rate = g2conncolors.red
          # change all outputs to red for next iteration
          for output in module.outputs:
            if output.rate == g2conncolors.blue_red:
              output.rate = g2conncolors.red
            if output.rate == g2conncolors.yellow_orange:
              output.rate = g2conncolors.orange
          break
        #elif input.net.output.rate == g2conncolors.blue:
        #  modified = 1
        #  module.uprate = 0
        #  input.rate = g2conncolors.red
        #  # change all outputs to red for next iteration
        #  for output in module.outputs:
        #    if output.rate == g2conncolors.blue_red:
        #      output.rate = g2conncolors.blue
        #    if output.rate == g2conncolors.yellow_orange:
        #      output.rate = g2conncolors.yellow
        #  break
    if not modified:
      done = 1

def cablerecolorize(g2area,config):
  logging.info('cable recolorize:')
  for cable in g2area.cables:
    if cable.source.net.output:
      cable.color = conn2cablecolors[cable.source.net.output.rate]

def docableshorten(g2area,config):
  if not config.shorten:
    return
  logging.info('cable shorten:')
  g2area.shortencables()

def dofinalize(areaconverters,config):
  logging.info('Finalize:')
  for areanm in 'voice','fx':
    logging.info('--- area %s: ---' % areanm)
    for conv in areaconverters[areanm]:
      logging.debug('%s: %s %d(0x%02x)' % (conv.nmmodule.type.shortnm,
          conv.nmmodule.name, conv.nmmodule.type.type,conv.nmmodule.type.type))
      conv.finalize()

def domorphsknobsmidiccs(nmpatch,g2patch,config):
  # handle Morphs
  #  morphs[x].ctrl.midicc
  #    1: Wheel -> Wheel (morph 0)
  #    7: Volume -> ?
  #    4: Foot -> Ctrl.Pd (morph 5)
  #  morphs[x].keyassign
  #    0: None -> ignored
  #    1: Velocity -> Vel (morph 1)
  #    2: Note -> Keyb (morph 2)
  #  morphs[x].knob.knob
  #    19: Pedal -> Sust Pd. (morph 4)
  #    20: After Touch -> Aft. Tch. (morph 3)
  #    22: On/Off -> P.Stick (morph 6) set to knob
  #
  #  Priority:
  #    keyassign (highest)
  #    ctrl
  #    knob (lowest)
  #    This means if keyassign is found it's will ignore the other two
  #
  # build a morphmap[x] that maps x to g2 morph
  logging.info('morphs:')
  nmmorphs = nmpatch.morphs
  g2morphs = g2patch.settings.morphs
  unused = g2morphs[:]
  morphmap = [None] * 4
  for morph in range(len(nmmorphs)):
    if nmmorphs[morph].ctrl:
      logging.debug(' nm morph%d: midicc=%d' %
          (morph,nmmorphs[morph].ctrl.midicc))
      # ignore Volume cannot be assigned anyways
      if nmmorphs[morph].ctrl.midicc == 1:
        morphmap[morph] = g2morphs[0]
        unused.remove(g2morphs[0])
        continue
      elif nmmorphs[morph].ctrl.midicc == 4:
        morphmap[morph] = g2morphs[5]
        unused.remove(g2morphs[5])
        continue
    if nmmorphs[morph].keyassign:
      logging.debug(' nm morph%d: keyassign=%d' %
          (morph,nmmorphs[morph].keyassign))
      m = g2morphs[nmmorphs[morph].keyassign]
      unused.remove(m)
      morphmap[morph] = m
      continue
    if nmmorphs[morph].knob:
      knob = nmmorphs[morph].knob
      logging.debug(' nm morph%d: knob=%d' % (morph,knob.knob))
      if knob.knob > 18:                  #  v: 0 unused
        m = g2morphs[[4,3,0,6][knob.knob-19]]
        morphmap[morph] = m
        unused.remove(m)

  # if morphmap[morph] empty assign unused morph and set it to knob
  for morph in range(len(morphmap)-1,-1,-1):
    if not morphmap[morph]:
      morphmap[morph] = unused.pop()
      setv(morphmap[morph].modes,0)
    else:
      setv(morphmap[morph].modes,1)
    logging.debug(' nm morph%d -> g2 morph%d' % (morph,morphmap[morph].index))

  for morph in range(len(morphmap)):
    g2morph = morphmap[morph]
    setv(g2morph.dials,nmmorphs[morph].dial)
    logging.debug(' Morph%d: dial=%d' % (morph+1,nmmorphs[morph].dial))
    for map in nmmorphs[morph].maps:
      s = '  %s:%s range=%d' % (map.param.module.name,map.param.type.name,
          map.range)
      mmap = MorphMap()
      conv = map.param.module.conv
      mmap.range = conv.domorphrange(map.param.index,map.range)
      index = map.param.index
      if index < len(conv.params) and conv.params[index]:
        mmap.param = conv.params[index]
        mmap.morph = g2morph
        morphmap[morph].maps[0].append(mmap)
        logging.debug(s)
      else:
        logging.warning(s + ' -- Parameter missing')
    for variation in range(1,9):
      g2morph.maps[variation]=g2morph.maps[0][:]
      
  # handle Knobs
  logging.info('knobs:')
  knobmap = [0,1,2,3,4,5,8,9,10,11,12,13,16,17,18,19,20,21]
  for knob in nmpatch.knobs:
    if knob.knob > 18: # 19=pedal,20=afttch,22=on/off
      continue
    g2knob = g2patch.knobs[knobmap[knob.knob]]
    index = knob.param.index
    if hasattr(knob.param,'module'): # module parameter
      # Place parameters in A1(knobs 1-6),A2(knobs 7-12),A3(knobs 13-18)
      conv = knob.param.module.conv
      s = 'Knob%d: %s:%s ->' % (knob.knob,
          knob.param.module.name,knob.param.type.name)
      if index < len(conv.params) and conv.params[index]:
        s += ' %s' % conv.params[index]
        g2knob.param = conv.params[index]
        g2knob.assigned = 1
        g2knob.isled = 0
        logging.debug(s)
      else:
        logging.warning(s + ' Unknown param %d' % index)
    else: # morph
      #logging.debug(' Knob%d: Morph%d' % (knob.knob,knob.param.index))
      g2knob.param = morphmap[knob.param.index-1]
      g2knob.assigned = 1
      g2knob.isled = 0
  
  # handle Midi CCs
  logging.info('MIDI CCs:')
  reservedmidiccs = [ 0,1,7,11,17,18,19,32,64,70,80,96,97,121,123 ]
  from nord.g2.file import Ctrl
  for ctrl in nmpatch.ctrls:
    if ctrl.midicc in reservedmidiccs:
      continue
    m = Ctrl()
    m.midicc = ctrl.midicc
    if hasattr(ctrl.param,'module'): # module parameter
      s = ' CC%d: %s:%s' % (ctrl.midicc,ctrl.param.module.name,
        ctrl.param.type.name)
      index = ctrl.param.index
      conv = ctrl.param.module.conv
      if index < len(conv.params) and conv.params[index]:
        m.param = conv.params[index]
        m.type = conv.g2module.area.index
        logging.debug(s)
      else:
        logging.warning(s + ' -- Parameter missing')
        continue
    else:
      m.param = morphmap[ctrl.param.index-1]
      m.type = 2 # system
    g2patch.ctrls.append(m)

def docurrentnotes(nmpatch,g2patch,config):
  # handle CurrentNotes
  logging.info('currentnotes:')
  #g2patch.lastnote = nmpatch.lastnote
  g2patch.notes.append(nmpatch.lastnote)
  for note in nmpatch.notes:
    g2patch.notes.append(note)

def dotitleblock(pch,pch2,config):
  lines = ['Converted by',
           'gtools-%s' % (g2oolsversion),
           'by',
           'Matt Gerassimoff',
           'models by',
           'Sven Roehrig']

  vert = 0
  for module in pch2.patch.voice.modules:
    if module.horiz != 0:
      continue
    v = module.vert + module.type.height
    if v > vert:
      vert = v

  def addnamebars(lines, horiz, vert):
    for line in lines:
      m = pch2.patch.voice.addmodule('Name',name=toascii(line))
      m.horiz = horiz
      m.vert = vert
      vert += 1
    return vert

  path = os.path.dirname(os.path.abspath(pch.fname))[-16:]
  vert = addnamebars([path],0,vert+2)
  vert = addnamebars(lines,0,vert+1)
  vert = addnamebars(['All rights','reserved'],0,vert+1)

def convert(pch,config):
  #   loop through each module
  #     determine and store separation from module above >= 0
  #     if mod in convertion table
  #       call convertion table module function
  #   loop through each cable
  #     if source and dest in convertion table
  #       create new connection
  #   update midi controller assignments
  #   update knob assignments (on pags A1:1, A1:2 and A1:3)
  #   update morph assignments
  #   reorder modules top to bottom, left to right
  #   relocate modules top to bottom, left to right based on separation
  #   add name bar with my name and convertion info
  #   add name bar with errors/comments etc.
  #   save g2 file

  # other ideas:
  # create patch equal function
  # create patch merge function that updates variations
  #   of one patch from another.
  pch2 = Pch2File('initpatch.pch2')
  nmpatch = pch.patch
  g2patch = pch2.patch
  g2patch.voice.keyboard = None
  g2patch.fx.keyboard = None

  setv(g2patch.settings.patchvol,127)
  for color in ['red','blue','yellow','green','purple']:
    setattr(g2patch.description,color,getattr(nmpatch.header,color))
  if nmpatch.header.voices > 1:
    g2patch.description.monopoly = 0
    g2patch.description.voicecnt = nmpatch.header.voices - 1
  setv(g2patch.settings.glide,nmpatch.header.porta)
  setv(g2patch.settings.glidetime,nmpatch.header.portatime)
  setv(g2patch.settings.octaveshift,nmpatch.header.octshift)

  areaconverters = { }
  for areanm in 'voice','fx':
    nmarea = getattr(nmpatch,areanm)
    g2area = getattr(g2patch,areanm)
    logging.info('--- area %s: ---' % areanm)

    # build converters for all NM1 modules
    converters = areaconverters[areanm] = doconverters(nmarea,g2area,config)
    domodules(converters,config)              # do the modules
    docolorizemultis(converters,config)       # colorize multi module setups
    doreposition(converters,config)           # repostion all modules
    doprecables(converters,config)            # precable processing
    docables(nmarea,g2area,converters,config) # connect cables
    douprate(g2area,config)                   # uprate necessary modules
    docableshorten(g2area,config)             # shorten up cables
    cablerecolorize(g2area,config)            # recolor cables based on output

  domorphsknobsmidiccs(nmpatch,g2patch,config)
  docurrentnotes(nmpatch,g2patch,config)
  dofinalize(areaconverters,config)


  # handle text pad
  pch2.patch.textpad = pch.patch.textpad

  dotitleblock(pch,pch2,config)

  logging.info('Writing patch "%s2"' % (pch.fname))
  pch2.write(pch.fname+'2')
  

class Config:
  def __init__(self, **kw):
    self.__dict__ = kw

def usage(prog):
  print 'usage: nm2g2 <flags> <.pch files>'
  print '\t<flags>'
  print '\t-a --allfiles\tProcess all files (not just extension .pch)'
  print '\t-d --debug\tDo not catch exceptions to debug.'
  print '\t-h --help\tPrint this message'
  print '\t-k --keepold\tDo not replace existing .pch2 files'
  print '\t-l --low\tLower resource usage'
  print '\t-r --recursive\tOn directory arguments convert all .pch files'
  print '\t-s --shorten\tShorten cable connections'
  print '\t-v --verbosity\tSet converter verbosity level 0-4'
  
def main(argv):
  prog = argv.pop(0)
  try:
    opts, args = getopt.getopt(argv,'adhlkrsv:',
        ['all','debug','help','keepold','low','recursive','shorten','verbosity='])
  except getopt.GetoptError:
    usage(prog)
    sys.exit(2)

  config = Config(debug=False,lowresource=False,recursive=False,
      keepold=False,allfiles=False,shorten=False,verbosity=logging.INFO)
  for o, a in opts:
    if o in ('-h','--help'):
      usage(prog)
    if o in ('-a','--all-files'):
      config.allfiles = True
    if o in ('-d','--debug'):
      config.debug = True
    if o in ('-l','--low'):
      config.lowresource = True
    if o in ('-r','--recursive'):
      config.recursive = True
    if o in ('-k','--keepold'):
      config.keepold = True
    if o in ('-s','--shorten'):
      config.shorten = True
    if o in ('-v','--verbosity'):
      print o,a
      config.verbosity = [
          logging.DEBUG,logging.INFO,logging.WARNING,
          logging.ERROR,logging.CRITICAL ][int(a)]

  logging.basicConfig(level=config.verbosity,format='%(message)s')
  #console = logging.StreamHandler()
  #console.setLevel(logging.DEBUG)
  #logging.getLogger('').addHandler(console)

  def doconvert(fname,config):
    # general algorithm for converter:
    if config.debug:
      try:
        convert(PchFile(fname),config) # allow exception thru if debugging
      except NM1Error, s:
        logging.error(s)
    else:
      try:
        convert(PchFile(fname),config)
      except KeyboardInterrupt:
        sys.exit(1)
      except Exception, e:
        print '%r' % e
        return fname
    return ''

  failedpatches = []
  while len(args):
    arg = args.pop(0)
    patchlist = glob(arg)
    if len(patchlist) == 0:
      failedpatches.append(arg)
      continue
    for fname in patchlist:
      if os.path.isdir(fname) and config.recursive:
        for root,dirs,files in os.walk(fname):
          for f in files:
            fname = os.path.join(root,f)
            if fname[-5:].lower() == '.pch2':
              continue
            if fname[-4:].lower() == '.pch' or config.allfiles:
              logging.info('"%s"' % fname)
              testname = fname
              if fname[-4:].lower() != '.pch':
                testname = fname+'.pch'
              if config.keepold and os.path.exists(testname+'2'):
                continue
              failed = doconvert(fname,config)
              if failed:
                failedpatches.append(failed)
              logging.info('-' * 20)
      else:
        logging.info('"%s"' % fname)
        failed = doconvert(fname,config)
        if failed:
          failedpatches.append(failed)
        logging.info('-' * 20)

  if len(failedpatches):
    f=open('failedpatches.txt','w')
    s = 'Failed patches: \n %s\n' % '\n '.join(failedpatches)
    f.write(s)
    logging.warning(s)

if __name__ == '__main__':
  try:
    import psyco
    psyco.full()
  except ImportError:
    pass
  main(sys.argv)
