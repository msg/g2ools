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

import getopt, sys
from glob import glob
sys.path.append('.')
from nord.g2.file import Pch2File
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors, g2portcolors
from nord.nm1.file import PchFile
from nord.nm1.colors import nm1cablecolors, nm1portcolors
from nord.g2 import colors
from nord.convert import typetable,setv
from nord.net import printnet

nm2g2colors = {
  nm1cablecolors.red:    g2cablecolors.red,
  nm1cablecolors.blue:   g2cablecolors.blue,
  nm1cablecolors.yellow: g2cablecolors.yellow,
  nm1cablecolors.grey:   g2cablecolors.blue,
  nm1cablecolors.green:  g2cablecolors.green,
  nm1cablecolors.purple: g2cablecolors.purple,
}
port2cablecolors = {
  g2portcolors.red:           g2cablecolors.red,
  g2portcolors.blue:          g2cablecolors.blue,
  g2portcolors.yellow:        g2cablecolors.yellow,
  g2portcolors.orange:        g2cablecolors.orange,
  g2portcolors.blue_red:      g2cablecolors.blue,
  g2portcolors.yellow_orange: g2cablecolors.yellow,
}

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
  for color in ['red','blue','yellow','green','purple']:
    setattr(g2patch.description,color,getattr(nmpatch.header,color))
  if nmpatch.header.voices > 1:
    g2patch.description.monopoly = 0
    g2patch.description.voicecnt = nmpatch.header.voices
  setv(g2patch.settings.glide,nmpatch.header.porta)
  setv(g2patch.settings.glidetime,nmpatch.header.portatime)
  setv(g2patch.settings.octaveshift,nmpatch.header.octshift)

  for areanm in 'voice','fx':
    nmarea = getattr(nmpatch,areanm)
    g2area = getattr(g2patch,areanm)
    print 'Area %s:' % areanm

    # sort by mst/slv connections
    modules = []
    for module in nmarea.modules:
      if hasattr(module.outputs,'Slv'):
        modules.insert(0,module)
      else:
        modules.append(module)
    nmarea.modules = modules
    converters = []
    # do the modules
    for module in nmarea.modules:
      if module.type.type in typetable:
        print '%s: %d(0x%02x)' % (module.name,
           module.type.type,module.type.type)
        conv = typetable[module.type.type](nmarea,g2area,module,config)
        converters.append(conv)
        conv.domodule()
        #g2module = conv.g2module
        #print '%s (%d,%d)' % (g2module.type.shortnm,
        #    g2module.horiz, g2module.vert)
      else:
        print 'No converter for module "%s" type %d(0x%02x)' % (
            module.type.shortnm, module.type.type, module.type.type)

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

    # now do the cables
    print 'Cables:'
    for cable in nmarea.cables:
      source = cable.source
      g2source = None
      if source.direction:
        if source.index < len(source.conv.outputs):
          g2source = source.conv.outputs[source.index]
      elif source.index < len(source.conv.inputs):
        g2source = source.conv.inputs[source.index]
      dest = cable.dest
      print '%s:%s:%d -> %s:%s:%d :' % (
          source.module.name,source.type.name, source.type.type,
          dest.module.name,dest.type.name, dest.type.type),
      if dest.index >= len(dest.conv.inputs) or not g2source:
        print ' UNCONNECTED'
      else:
        print ' connected'
        g2dest = dest.conv.inputs[dest.index]
        if source.net.output.type.type == nm1portcolors.slave:
          color = g2cablecolors.purple
        else:
          color = source.net.output.type.type
        g2area.connect(g2source,g2dest,color)

    # now parse the entire netlist of the area and .uprate=1 all
    # modules with blue_red and yello_orange inputs connected to red outputs.
    # scan module list until we done change any modules
    print 'Uprate:'
    done = 0
    while not done:
      modified = 0
      for module in g2area.modules:
        #print module.name, module.type.shortnm
        for input in module.inputs:
	  if not input.net:
            continue
          #print '',input.type.name, input.rate
          if (input.rate != g2portcolors.blue_red and
              input.rate != g2portcolors.yellow_orange):
            continue
          if not input.net.output:
            continue
          if input.net.output.rate == g2portcolors.red:
            #print module.name,input.type.name,input.net.output.type.name
            modified = 1
            module.uprate = 1
            input.rate = g2portcolors.red
            # change all outputs to red for next iteration
            for output in module.outputs:
              if output.rate == g2portcolors.blue_red:
                output.rate = g2portcolors.red
              if output.rate == g2portcolors.yellow_orange:
                output.rate = g2portcolors.orange
            break
          #elif input.net.output.rate == g2portcolors.blue:
          #  modified = 1
          #  module.uprate = 0
          #  input.rate = g2portcolors.red
          #  # change all outputs to red for next iteration
          #  for output in module.outputs:
          #    if output.rate == g2portcolors.blue_red:
          #      output.rate = g2portcolors.blue
          #    if output.rate == g2portcolors.yellow_orange:
          #      output.rate = g2portcolors.yellow
          #  break
      if not modified:
        done = 1

    print 'Cable recolorize:'
    for cable in g2area.cables:
      #print '%s:%s -> %s:%s %d' % (
      #    cable.source.module.name,cable.source.type.name,
      #    cable.dest.module.name,cable.dest.type.name,
      #    cable.source.net.output.rate),
      cable.color = port2cablecolors[cable.source.net.output.rate]
      #print cable.color, cable.source.net.output.module.type.shortnm
      #printnet(cable.source.net)

  # handle Morphs
  # TBD

  # handle Knobs
  print 'Knobs:'
  for knob in nmpatch.knobs:
    if hasattr(knob.param,'module'): # module parameter
      if knob.knob < 18: # 19=pedal,20=afttch,22=on/off
        # Place parameters in A1(knobs 1-6),A2(knobs 7-12),A3(knobs 13-18)
        knobmap = [0,1,2,3,4,5,8,9,10,11,12,13,16,17,18,19,20,21]
        g2knob = knobmap[knob.knob]
        index = knob.param.index
        conv = knob.param.module.conv
        if conv.params[index]:
          g2patch.knobs[g2knob].param = conv.params[index]
          g2patch.knobs[g2knob].assigned = 1
          g2patch.knobs[g2knob].isled = 0
          print 'Knob%d: %s:%s -> %s' % (knob.knob,
              knob.param.module.name,knob.param.type.name,
              conv.params[index])
    else: # morph
      print ' Knob%d: Morph%d' % (knob.knob,knob.param.index)
  
  # handle Midi CCs
  print 'MIDI CCs:'
  reservedmidiccs = [ 0,1,7,11,17,18,19,32,64,70,80,96,97,121,123 ]
  from nord.g2.file import MIDIAssignment
  for ctrl in nmpatch.ctrls:
    if ctrl.midicc in reservedmidiccs:
      continue
    m = MIDIAssignment()
    m.midicc = ctrl.midicc
    if hasattr(ctrl.param,'module'): # module parameter
      m.param = ctrl.param.module.conv.params[ctrl.param.index]
      m.type = m.param.module.area.index
      g2patch.midiassignments.append(m)
    # NOTE: remove line above if uncommenting: g2patch.midiassignments.append(m)
    #else:
    #  m.param = g2patch.morphs[newindex]
    #  m.type = 2 # system
    #g2patch.midiassignments.append(m)

  # handle text pad
  pch2.patch.textpad = pch.patch.textpad

  message = '''
  nm2g2 patch converter Copyright 2007 Matt Gerassimoff
  '''
  lines = []
  words = message.split()
  line = words.pop(0)
  for word in words:
    if len(line) + len(word) + 1> 16:
      lines.append(line)
      line = word
    else:
      line += ' ' + word
  lines.append(line)
  #print '\n'.join(lines)

  vert = 0
  for module in pch2.patch.voice.modules:
    if module.horiz != 0:
      continue
    v = module.vert + module.type.height
    #print '',module.name, module.vert, module.type.height, v
    if v > vert:
      vert = v

  vert += 1
  for i in range(len(lines)):
    line = lines[i]
    m = pch2.patch.voice.addmodule(g2name['Name'])
    m.name = line
    m.horiz = 0
    m.vert = vert
    vert += 1

  print 'Writing patch "%s2"' % (pch.fname)
  pch2.write(pch.fname+'2')
  

class Config:
  def __init__(self, **kw):
    self.__dict__ = kw

def usage(prog):
  print 'usage: %s <flags> <.pch files>'
  print '\t<flags>'
  print '\t-h --help\tPrint this message'
  print '\t-d --debug\tDebug program'
  print '\t-l --low\tLower resource usage'
  
def main():
  prog = sys.argv.pop(0)
  try:
    opts, args = getopt.getopt(sys.argv,'hdl', ['help','debug','low'])
  except getopt.GetoptError:
    usage(prog)
    sys.exit(2)

  config = Config(debug=None,lowresource=None)
  for o, a in opts:
    if o in ('-h','--help'):
      usage(prog)
    if o in ('-d','--debug'):
      config.debug = True
    if o in ('-l','--low'):
      config.lowresource = True

  failedpatches = []
  while len(args):
    patchlist = glob(args.pop(0))
    for fname in patchlist:
      print '"%s"' % fname
      # general algorithm for converter:
      if config.debug:
        convert(PchFile(fname),config) # allow exception thru if debugging
      else:
        try:
          convert(PchFile(fname),config)
        except Exception, e:
          print '%r' % e
          failedpatches.append(fname)

  if len(failedpatches):
    print 'Failed patches: \n%s' % '\n '.join(failedpatches)

if __name__ == '__main__':
  main()
