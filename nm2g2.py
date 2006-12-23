#!/usr/bin/env python
#
# Copyright: Matt Gerassimoff 2007
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

import sys
from glob import glob
sys.path.append('.')
from nord.g2.file import Pch2File
from nord.g2.modules import fromname as g2name
from nord.g2.colors import g2cablecolors, g2portcolors
from nord.nm1.file import PchFile
from nord.nm1.colors import nm1cablecolors, nm1portcolors
from nord.g2 import colors
from nord.convert import typetable

def convert(pch):
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
  pch2 = Pch2File('./nord/convert/initpatch.pch2')
  nmpatch = pch.patch
  g2patch = pch2.patch
  cablecolors = {
    nm1cablecolors.red:    g2cablecolors.red,
    nm1cablecolors.blue:   g2cablecolors.blue,
    nm1cablecolors.yellow: g2cablecolors.yellow,
    nm1cablecolors.grey:   g2cablecolors.blue,
    nm1cablecolors.green:  g2cablecolors.green,
    nm1cablecolors.purple: g2cablecolors.purple,
  }
  for areanm in 'voice','fx':
    nmarea = getattr(nmpatch,areanm)
    g2area = getattr(g2patch,areanm)
    print 'Area %s:' % areanm

    converters = []
    # do the modules
    for module in nmarea.modules:
      if module.type.type in typetable:
        print '%s: %d(0x%02x)' % (module.type.shortnm,
           module.type.type,module.type.type)
        conv = typetable[module.type.type](nmarea,g2area,module)
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
          source.module.type.shortnm,source.type.name, source.type.type,
          dest.module.type.shortnm,dest.type.name, dest.type.type),
      if dest.index >= len(dest.conv.inputs) or not g2source:
        print ' UNCONNECTED'
      else:
        print ' connected'
        g2dest = dest.conv.inputs[dest.index]
        #print source.index, dest.index
        #print source.module.type.shortnm, dest.module.type.shortnm
        #print source.module.type.shortnm, dest.module.type.shortnm
        if source.nets[0].output.type.type == nm1portcolors.slave:
          color = g2cablecolors.purple
        else:
          color = source.nets[0].output.type.type
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
          if len(input.nets) == 0:
            continue
          #print '',input.type.name, input.rate
          if (input.rate != g2portcolors.blue_red and
              input.rate != g2portcolors.yellow_orange):
            continue
          if not input.nets[0].output:
            continue
          if input.nets[0].output.rate == g2portcolors.red:
            #print module.name,input.type.name,input.nets[0].output.type.name
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
          #elif input.nets[0].output.rate == g2portcolors.blue:
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

  # handle Knobs
  # TBD
  
  # handle Midi CCs
  # TBD

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
  
prog = sys.argv.pop(0)
while len(sys.argv):
  patchlist = glob(sys.argv.pop(0))
  for fname in patchlist:
    print '"%s"' % fname
    # general algorithm for converter:
    convert(PchFile(fname))

