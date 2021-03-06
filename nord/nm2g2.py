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

import os, sys
import nord.file
from nord.g2.file import Pch2File
from nord.g2.misc import handle_uprate, midicc_reserved
from nord.file import MorphMap
from nord.g2.colors import g2modulecolors, g2cablecolors, g2conncolors
from nord.nm1.file import PchFile
from nord.nm1.colors import nm1cablecolors, nm1conncolors
from nord.nm1.file import NM1Error
from nord.convert import id_table
from nord.convert.version import version as g2oolsversion
from nord.utils import setv, toascii
from nord.convert import osc
from nord import printf

#__builtins__.printf = printf

conn2cablecolors = {
  g2conncolors.red:           g2cablecolors.red,
  g2conncolors.blue:          g2cablecolors.blue,
  g2conncolors.yellow:        g2cablecolors.yellow,
  g2conncolors.orange:        g2cablecolors.orange,
  g2conncolors.blue_red:      g2cablecolors.blue,
  g2conncolors.yellow_orange: g2cablecolors.yellow,
}


class NM2G2Converter:
  def __init__(self, pchfilename, options, log):
    self.pch = PchFile(pchfilename)
    g2oolsdir = os.path.dirname(options.programpath)
    self.pch2 = Pch2File(os.path.join(g2oolsdir, 'initpatch.pch2'))
    self.nmpatch = self.pch.patch
    self.g2patch = self.pch2.patch
    self.g2patch.voice.keyboard = None
    self.g2patch.fx.keyboard = None
    self.options = options
    self.log = log
    osc.modindex.reset()

  def convert(self):
    # loop through each module
    #   determine and store separation from module above >= 0
    #   if mod in convertion table
    #     call convertion table module function
    # loop through each cable
    #   if source and dest in convertion table
    #     create new connection
    # update midi controller assignments
    # update knob assignments (on pags A1:1, A1:2 and A1:3)
    # update morph assignments
    # reorder modules top to bottom, left to right
    # relocate modules top to bottom, left to right based on separation
    # add name bar with my name and convertion info
    # add name bar with errors/comments etc.
    # save g2 file

    # other ideas:
    # create patch equal function
    # create patch merge function that updates variations
    #   of one patch from another.
    g2patch, nmpatch = self.g2patch, self.nmpatch

    setv(g2patch.settings.patchvol, 127)
    for color in ['red', 'blue', 'yellow', 'green', 'purple']:
      setattr(g2patch.description, color, getattr(nmpatch.header, color))
    if nmpatch.header.voices > 1:
      g2patch.description.monopoly = 0
      g2patch.description.voices = nmpatch.header.voices - 1
    setv(g2patch.settings.glide, nmpatch.header.porta)
    setv(g2patch.settings.glidetime, nmpatch.header.portatime)
    setv(g2patch.settings.octaveshift, nmpatch.header.octshift)

    self.log.info('--- area voice: ---')
    self.voiceconverters = self.doarea(nmpatch.voice, g2patch.voice)
    self.log.info('--- area fx: ---')
    self.fxconverters = self.doarea(nmpatch.fx, g2patch.fx)

    self.domorphs()
    self.doknobs()
    self.domidiccs()
    self.docurrentnotes()
    self.dofinalize()

    # handle text pad
    self.pch2.patch.textpad = self.pch.patch.textpad

    self.dotitleblock()

    self.log.info('Writing patch "%s2"' % (self.pch.filename))
    self.pch2.write(self.pch.filename+'2')


  def doarea(self, nmarea, g2area):
      # build converters for all NM1 modules
      converters = self.doconverters(nmarea, g2area)
      self.domodules(converters)        # do the modules
      self.docolorizemultis(converters) # colorize multi module setups
      self.dogroups(converters)         # handle groups of modules
      self.doreposition(converters)     # repostion all modules
      self.doprecables(converters)      # precable processing
      self.docables(nmarea, g2area)     # connect cables
      self.dologiccombine(g2area)       # combine logic modules
      self.docableshorten(g2area)       # shorten up cables
      self.douprate(g2area)             # uprate necessary modules
      self.cablerecolorize(g2area)      # recolor cables based on output
      return converters


  def doconverters(self, nmarea, g2area):
    converters = []
    log = self.log
    for module in nmarea.modules:
      converter = id_table.get(module.type.id)
      if converter:
        log.debug('%s: %s %d(0x%02x)' % (module.type.shortnm, module.name,
            module.type.id, module.type.id))
        conv = converter(nmarea, g2area, module, self.options)
        converters.append(conv)
        #g2m = conv.g2module
        #printf('%s (%d, %d)\n', g2m.type.shortnm, g2m.horiz, g2m.vert)
      else:
        log.warning('No converter for module "%s" type %d(0x%02x)' % (
            module.type.shortnm, module.type.id, module.type.id))
    return converters


  def domodules(self, converters):
    self.log.info('domodule:')
    for conv in converters:
      self.log.debug('%s: %s %d(0x%02x)' % (conv.nmmodule.type.shortnm,
          conv.nmmodule.name, conv.nmmodule.type.id, conv.nmmodule.type.id))
      conv.domodule()


  def docolorizemultis(self, converters):
    modcolors = [
      g2modulecolors.yellow2, g2modulecolors.green2,
      g2modulecolors.cyan2, g2modulecolors.blue2, g2modulecolors.magenta1
    ]
    # colorize multi-module convertions
    curr = 0
    for conv in converters:
      if len(conv.g2modules):
        conv.g2module.color = modcolors[curr]
        for mod in conv.g2modules:
          mod.color = modcolors[curr]
        curr = (curr+1)%len(modcolors)


  def dogroups(self, converters):
    self.log.info('groups:')
    groups = {}
    for conv in converters:
      nm = conv.nmmodule.type.shortnm
      if not nm in groups:
        groups[nm] = []
      groups[nm].append(conv)

    for key in groups:
      group = groups[key]
      group[0].dogroup(group)


  def doreposition(self, converters):
    self.log.info('reposition:')

    # location compare by horiz, then vert
    def locationcmp(a, b):
      if a.horiz == b.horiz:
        return cmp(a.nmmodule.vert, b.nmmodule.vert)
      return cmp(a.nmmodule.horiz, b.nmmodule.horiz)
    locsorted = converters[:]
    locsorted.sort(locationcmp)

    if len(locsorted):
      locsorted[0].reposition(None)
      for i in range(1, len(locsorted)):
        ca = locsorted[i-1]
        cb = locsorted[i]
        if ca.nmmodule.horiz == cb.nmmodule.horiz:
          cb.reposition(ca)
        else:
          cb.reposition(None)

    # remove gaps in horiz
    if self.options.compresscolumns:
      columns = []
      column = []
      last = None
      for conv in locsorted:
        if not last or last.g2module.horiz != conv.g2module.horiz:
          if len(column):
            columns.append(column)
          column = [ conv ]
        else:
          column.append(conv)
        last = conv
      if len(column):
        columns.append(column)

      col = 0
      for column in columns:
        dcol = column[0].g2module.horiz - col
        if dcol > 1:
          for conv in column:
            conv.g2module.horiz = col + 1
            for mod in conv.g2modules:
              mod.horiz = col + 1
        col = column[0].g2module.horiz


  def doprecables(self, converters):
    self.log.info('precables:')
    for conv in converters:
      self.log.debug('%s: %s %d(0x%02x)' % (conv.nmmodule.type.shortnm,
          conv.nmmodule.name, conv.nmmodule.type.id, conv.nmmodule.type.id))
      conv.precables()


  def docables(self, nmarea, g2area):
    # now do the cables
    self.log.info('cables:')
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
          source.module.name, source.type.name, source.type.type,
          dest.module.name, dest.type.name, dest.type.type)
      if dest.index >= len(dest.conv.inputs) or not g2source:
        self.log.warning(s + ' UNCONNECTED')
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
        self.log.debug(s)
        g2area.connect(g2source, g2dest, color)

  def douprate(self, g2area):

    self.log.info('uprate:')
    handle_uprate(g2area)


  def dologiccombine(self, g2area):
    # find all Gate modules
    # sort and create a 2d array gates[col][index]
    # group gates in pairs, ignore last one if odd numbered
    # for each pair:
    #   move upper gate connections to left
    #   move lower gate connections to right
    # find all Invert modules
    # sort and create a 2d array inverters[col][index]
    # group inverters in pairs, ignore last one if odd numbered
    # for each pair:
    #   move upper inverter connections to left
    #   move lower inverter connections to right
    # 'Gate', 'Invert'

    if not self.options.logiccombine:
      return

    def locationcmp(a, b):
      if a.horiz == b.horiz:
        return cmp(a.vert, b.vert)
      return cmp(a.horiz, b.horiz)

    def gateused(gate, num):
      if num == 1:
        return len(gate.inputs.In1_1.cables) != 0 or \
               len(gate.inputs.In1_2.cables) != 0 or \
               len(gate.outputs.Out1.cables) != 0
      elif num == 2:
        return len(gate.inputs.In2_1.cables) != 0 or \
               len(gate.inputs.In2_2.cables) != 0 or \
               len(gate.outputs.Out2.cables) != 0
      return False

    def freegate(gate):
      if not gateused(gate, 1):   return 1
      elif not gateused(gate, 2): return 2
      else:                       return 0

    def usedgate(gate):
      if gateused(gate, 1):   return 1
      elif gateused(gate, 2): return 2
      else:                   return 0

    def invertused(invert, num):
      if num == 1:
        return len(invert.inputs.In1.cables) != 0 or \
               len(invert.outputs.Out1.cables) != 0
      elif num == 2:
        return len(invert.inputs.In2.cables) != 0 or \
               len(invert.outputs.Out2.cables) != 0
      return 0

    def freeinvert(invert):
      if not invertused(invert, 1):   return 1
      elif not invertused(invert, 2): return 2
      else:                           return 0

    def usedinvert(invert):
      if invertused(invert, 1):   return 1
      elif invertused(invert, 2): return 2
      else:                       return 0

    def makepairs(shortnm, freelogic):
      mods = [ m for m in g2area.modules if m.type.shortnm == shortnm ]
      modcols = {}
      for mod in mods:
        if freelogic(mod) == 0:
          continue
        if not mod.horiz in modcols:
          modcols[mod.horiz] = []
        modcols[mod.horiz].append(mod)
      colpairs = []
      for col, mods in modcols.items():
        mods.sort(locationcmp)
        if len(mods) % 2:
          oddmod = mods[-1]
        else:
          oddmod = None
        colpairs.append([zip(mods[::2], mods[1::2]), oddmod])
      return colpairs

    def movecable(g2area, fromconn, toconn):
      if len(fromconn.cables) == 0:
        return
      minconn = g2area.removeconnector(fromconn)
      if minconn.direction:
        fromconn = minconn
      else:
        fromconn, toconn = toconn, minconn
      g2area.connect(fromconn, toconn, g2cablecolors.yellow)

    self.log.info('logic combine:')

    for gatecol, oddmod in makepairs('Gate', freegate):
      for odd, even in gatecol:
        self.log.debug('Gate combine: %s(%d,%d) and %s(%d,%d)' %
          (odd.name, odd.horiz, odd.vert, even.name, even.horiz, even.vert))
        odd.modes[0].value = odd.modes[1].value
        odd.modes[1].value = even.modes[1].value
        if freegate(odd) == 1:
          movecable(g2area, odd.inputs.In2_1, odd.inputs.In1_1)
          movecable(g2area, odd.inputs.In2_2, odd.inputs.In1_2)
          movecable(g2area, odd.outputs.Out2, odd.outputs.Out1)
        if usedgate(even) == 1:
          movecable(g2area, even.inputs.In1_1, odd.inputs.In1_1)
          movecable(g2area, even.inputs.In1_2, odd.inputs.In1_2)
          movecable(g2area, even.outputs.Out1, odd.outputs.Out1)
        elif usedgate(even) == 2:
          movecable(g2area, even.inputs.In2_1, odd.inputs.In2_1)
          movecable(g2area, even.inputs.In2_2, odd.inputs.In2_2)
          movecable(g2area, even.outputs.Out2, odd.outputs.Out2)
        g2area.del_module(even)

    for invertercol, oddmod in makepairs('Invert', freeinvert):
      for odd, even in invertercol:
        self.log.debug('Invert combine: %s(%d,%d) and %s(%d,%d)' %
          (odd.name, odd.horiz, odd.vert, even.name, even.horiz, even.vert))
        if freeinvert(odd) == 1:
          movecable(g2area, odd.inputs.In2, odd.inputs.In1)
          movecable(g2area, odd.outputs.Out2, odd.outputs.Out1)
        if usedinvert(even) == 1:
          movecable(g2area, even.inputs.In1, odd.inputs.In2)
          movecable(g2area, even.outputs.Out1, odd.outputs.Out2)
        elif usedinvert(even) == 2:
          movecable(g2area, even.inputs.In2, odd.inputs.In2)
          movecable(g2area, even.outputs.Out2, odd.outputs.Out2)
        g2area.del_module(even)


  def cablerecolorize(self, g2area):
    self.log.info('cable recolorize:')
    for cable in g2area.cables:
      if cable.source.net.output:
        cable.color = conn2cablecolors[cable.source.net.output.rate]


  def docableshorten(self, g2area):
    if not self.options.shorten:
      return
    self.log.info('cable shorten:')
    g2area.shorten_cables()


  def domorphs(self):
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
    g2patch, nmpatch = self.g2patch, self.nmpatch
    self.log.info('morphs:')
    nmmorphs = nmpatch.morphs
    g2morphs = g2patch.settings.morphs
    unused = g2morphs[:]
    morphmap = [None] * 4
    for morph in range(len(nmmorphs)):
      if nmmorphs[morph].ctrl:
        self.log.debug(' nm morph%d: midicc=%d' %
            (morph, nmmorphs[morph].ctrl.midicc))
        # ignore Volume cannot be assigned anyways
        if nmmorphs[morph].ctrl.midicc == 1:
          morphmap[morph] = g2morphs[0]
          unused[0] = None
          continue
        elif nmmorphs[morph].ctrl.midicc == 4:
          morphmap[morph] = g2morphs[5]
          unused[5] = None
          continue
      if nmmorphs[morph].keyassign:
        self.log.debug(' nm morph%d: keyassign=%d' %
            (morph, nmmorphs[morph].keyassign))
        g2morph = g2morphs[nmmorphs[morph].keyassign]
        unused[morph] = None
        morphmap[morph] = g2morph
        continue
      if nmmorphs[morph].knob:
        knob = nmmorphs[morph].knob
        self.log.debug(' nm morph%d: knob=%d' % (morph, knob.knob))
        if knob.knob > 18:                  #  v: 0 unused
          g2morph = g2morphs[[4, 3, 0, 6][knob.knob-19]]
          if hasattr(knob, 'dial'):
            setv(g2morph.dial, knob.dial)
          morphmap[morph] = g2morph
          unused[morph] = None

    def find_unused():
      for i, morph in enumerate(unused):
        if morph:
          unused[i] = None
          return morph
      return None
    # if morphmap[morph] empty assign unused morph and set it to knob
    for morph in range(len(morphmap)-1, -1, -1):
      if not morphmap[morph]:
        morphmap[morph] = find_unused()
        setv(morphmap[morph].mode, 0)
      else:
        setv(morphmap[morph].mode, 1)
      self.log.debug(' nm morph%d -> g2 morph%d' % \
          (morph, morphmap[morph].index))

    for morph in range(len(morphmap)):
      g2morph = morphmap[morph]
      self.log.debug(' Morph%d: dial=%d g2morph%d' % (morph+1,
              nmmorphs[morph].dial, g2morph.dial.index))
      setv(g2morph.dial, nmmorphs[morph].dial)
      for nmap in nmmorphs[morph].maps:
        s = '  %s:%s range=%d' % (nmap.param.module.name, nmap.param.type.name,
            nmap.range)
        conv = nmap.param.module.conv
        gmap = MorphMap()
        gmap.range = conv.domorphrange(nmap.param.index, nmap.range)
        index = nmap.param.index
        if nmap.range == 0: # ignore junk morphs (0 range)
          continue
        if index < len(conv.params) and conv.params[index]:
          gmap.param = conv.params[index]
          gmap.morph = g2morph
          morphmap[morph].maps[0].append(gmap)
          self.log.debug(s)
        else:
          self.log.warning(s + ' -- Parameter missing')
      for variation in range(1, 9):
        g2morph.maps[variation] = g2morph.maps[0][:]
    self.morphmap = morphmap

  def doknobs(self):
    g2patch, nmpatch = self.g2patch, self.nmpatch
    # handle Knobs
    self.log.info('knobs:')
    #knobmap = [0, 1,  2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21]
    knobmap = [0, 8, 16, 1, 9, 17, 2, 10, 18, 3, 11, 19, 4, 12, 20, 5, 13, 21]
    knoboffset = 24 * 4 # Effect knobs
    for knob in nmpatch.knobs:
      if knob.knob > 18: # 19=pedal, 20=afttch, 22=on/off
        continue
      g2knob = g2patch.knobs[knobmap[knob.knob]+knoboffset]
      index = knob.param.index
      if hasattr(knob.param, 'module'): # module parameter
        # Place parameters in A1(knobs 1-6), A2(knobs 7-12), A3(knobs 13-18)
        conv = knob.param.module.conv
        s = 'Knob%d: %s:%s ->' % (knob.knob,
            knob.param.module.name, knob.param.type.name)
        if index < len(conv.params) and conv.params[index]:
          param = conv.params[index]
          s += ' %s:%s' % (param.module.name, param.type.name)
          g2knob.param = param
          g2knob.assigned = 1
          g2knob.isled = 0
          self.log.debug(s)
        else:
          self.log.warning(s + ' Unknown param %d' % index)
      else: # morph
        self.log.debug(' Knob%d: Morph%d' % (knob.knob, knob.param.index))
        g2knob.param = self.morphmap[knob.param.index-1].dial
        self.log.debug('   G2Morph%d' % (g2knob.param.module.index))
        g2knob.assigned = 1
        g2knob.isled = 0

  def domidiccs(self):
    g2patch, nmpatch = self.g2patch, self.nmpatch
    # handle Midi CCs
    self.log.info('MIDI CCs:')
    from nord.g2.file import Ctrl
    for ctrl in nmpatch.ctrls:
      param = ctrl.param
      if hasattr(ctrl.param, 'module'): # module parameter
        s = ' CC%d %s.%s(%d,%d)' % (ctrl.midicc, param.module.name,
          param.type.name, param.module.horiz, param.module.vert)
      else:
        s = ' CC%d' % ctrl.midicc
      if midicc_reserved(ctrl.midicc):
        self.log.warning('%s cannot be used (reserved)' % s)
        continue
      new_ctrl = Ctrl()
      new_ctrl.midicc = ctrl.midicc
      if hasattr(ctrl.param,'module'): # module parameter
        index = param.index
        conv = param.module.conv
        if index < len(conv.params) and conv.params[index]:
          new_ctrl.param = conv.params[index]
          self.log.debug(s)
        else:
          self.log.warning(s + ' -- Parameter missing')
          continue
      else:
        new_ctrl.param = self.morphmap[ctrl.param.index-1].dial
      g2patch.ctrls.append(new_ctrl)

  def docurrentnotes(self):
    g2patch, nmpatch = self.g2patch, self.nmpatch
    # handle CurrentNotes
    self.log.info('currentnotes:')
    #g2patch.lastnote = nmpatch.lastnote
    g2patch.notes.append(nmpatch.lastnote)
    for note in nmpatch.notes:
      g2patch.notes.append(note)


  def dofinalize(self):
    self.log.info('Finalize:')
    for areanm in 'voice', 'fx':
      self.log.info('--- area %s: ---' % areanm)
      for conv in getattr(self, '%sconverters' % areanm):
        self.log.debug('%s: %s %d(0x%02x)' % (conv.nmmodule.type.shortnm,
            conv.nmmodule.name,
            conv.nmmodule.type.id, conv.nmmodule.type.id))
        conv.finalize()


  def dotitleblock(self):
    path = os.path.dirname(os.path.abspath(self.pch.filename))[-16:]
    lines = [path,
             'Converted by',
             'gtools-%s' % (g2oolsversion),
             'by',
             'Matt Gerassimoff',
             'models by',
             'Sven Roehrig',
             'All rights',
             'reserved']

    vert = 0
    if len(self.pch2.patch.voice.modules) <= nord.file.MAX_MODULES - len(lines):
      area = self.pch2.patch.voice
    elif len(self.pch2.patch.fx.modules) <= nord.file.MAX_MODULES - len(lines):
      area = self.pch2.patch.fx
    else:
      self.pch2.patch.textpad += '\n' + '\n'.join(lines)
      return
    for module in area.modules:
      if module.horiz != 0:
        continue
      v = module.vert + module.type.height
      if v > vert:
        vert = v

    def addnamebars(lines, horiz, vert):
      for line in lines:
        m = area.add_module('Name', name=toascii(line))
        m.horiz = horiz
        m.vert = vert
        vert += 1
      return vert

    vert = addnamebars(lines, 0, vert+2)
