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

import string, struct, sys

from nord import printf
from nord.module import Module
from nord.file import hexdump, binhexdump
from nord.g2.modules import fromname
from nord.file import Patch, Performance, Note, Cable, Knob, Ctrl, MorphMap
from nord.g2 import modules
from nord.g2.crc import crc
from nord.g2.bits import setbits, getbits, BitStream

section_debug = 0 # outputs section debug 
title_section = 0 # replace end of section with section title

NVARIATIONS = 9 # 1-8, init
NMORPHS = 8     # 8 morphs
NKNOBS = 120    # 120 knob settings
NMORPHMAPS = 25 # max morphmaps per variation

FX, VOICE, SETTINGS = 0, 1, 2

class G2Error(Exception):
  '''G2Error - exception for throwing an unrecoverable error.'''
  def __init__(self, value):
    Exception.__init__(self)
    self.value = value
  def __str__(self):
    return repr(self.value)

def getbitsa(bit, sizes, data):
  '''getbitsa(bit, sizes, data) -> bit, [values]'''
  values = []
  for size in sizes:
    bit, value = getbits(bit, size, data)
    values.append(value)
  return bit, values

def setbitsa(bit, sizes, data, values):
  '''setbitsa(bit, sizes, data, values) -> bit'''
  for size, value in zip(sizes, values):
    bit = setbits(bit, size, data, value)
  return bit

class Section(object):
  '''Section abstract class that represents a section of .pch2 file.
  all sections objects have parse() and format() methods.
'''
  default = [0] * (2 << 10) # max 64k section size
  def __init__(self, **kw):
    self.__dict__ = kw
    self.data = bytearray(64<<10)

class Description(object):
  '''Description class for patch/performance description.'''
  pass

class PatchDescription(Section):
  '''PatchDescription Section subclass'''
  type = 0x21
  description_attrs = [
    ['reserved', 5], ['voices', 5], ['height', 14], ['unk2', 3],
    ['red', 1], ['blue', 1], ['yellow', 1], ['orange', 1],
    ['green', 1], ['purple', 1], ['white', 1],
    ['monopoly', 2], ['variation', 8], ['category', 8],
  ]
  def parse(self, patch, data):
    description = patch.description = Description()

    bitstream = BitStream(data, 7*8)
    for name, nbits in self.description_attrs:
      setattr(description, name, bitstream.read_bits(nbits))

  def format(self, patch, data):
    description = patch.description

    bitstream = BitStream(data, 7*8)
    for name, nbits in self.description_attrs:
      bitstream.write_bits(nbits, getattr(description, name))
    bitstream.write_bits(8, 0)

    return bitstream.tell_bit()

class ModuleList(Section):
  '''ModuleList Section subclass'''
  type = 0x4a
  module_params = [
    ['index', 8 ], ['horiz', 7], ['vert', 7], ['color', 8],
    ['uprate', 1 ], ['leds', 1], ['reserved', 6],
  ]
  def parse(self, patch, data):
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits

    self.area = read_bits(2)
    nmodules  = read_bits(8)

    area = [patch.fx, patch.voice][self.area]

    area.modules = [ None ] * nmodules
    for i in xrange(nmodules):
      id = read_bits(8)
      module = Module(modules.fromid(id), area)
      area.modules[i] = module

      for attr, nbits in self.module_params:
        setattr(module, attr, bitstream.read_bits(nbits))
      nmodes = read_bits(4)
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property but added to the module types that
      #       set it.
      self.fixleds(module)

      # mode data for module (if there is any)
      for mode in module.modes:
        mode.value = read_bits(6)

      # add missing mode data. some .pch2 versions didn't contain
      #   all the modes in version 23 BUILD 266
      module_type = module.type
      if len(module.modes) < len(module_type.modes):
        for mode in xrange(len(module.modes), len(module_type.modes)):
          module.modes[mode].value = module_type.modes[mode].type.default

  # make sure leds bit is set for specific modules
  # - some earlier generated .pch2 files where different
  #   these were emperically determined.
  ledtypes = [
    3, 4, 17, 38, 42, 48, 50, 57, 59, 60, 68, 69,
    71, 75, 76, 81, 82, 83, 85,
    105, 108, 112, 115, 141, 142, 143, 147, 148, 149, 150,
    156, 157, 170, 171, 178, 188, 189, 198, 199, 208,
  ]
  def fixleds(self, module):
    module.leds = 0
    return
    #if module.type.id in ModuleList.ledtypes:
    #  module.leds = 1
    #else:
    #  module.leds = 0

  def format(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    area = [patch.fx, patch.voice][self.area]

    write_bits(2, self.area)
    write_bits(8, len(area.modules))

    for module in area.modules:
      write_bits(8, module.type.id)
      module.reserved = 0 # just in case is wasn't set
      for attr, nbits in self.module_params:
        bitstream.write_bits(nbits, getattr(module, attr))
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property.
      self.fixleds(module)

      nmodes = len(module.modes)
      write_bits(4, nmodes)
      for mode in module.modes:
        write_bits(6, mode.value)

    return bitstream.tell_bit()

class CurrentNote(Section):
  '''CurrentNote Section subclass'''
  type = 0x69
  def parse(self, patch, data):
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits

    lastnote = patch.lastnote = Note()
    values = bitstream.read_bitsa([7] * 3)
    lastnote.note, lastnote.attack, lastnote.release = values
    nnotes = read_bits(5)
    notes = patch.notes = [ Note() for i in xrange(nnotes + 1) ]
    for i, note in enumerate(notes):
      note.note    = read_bits(7)
      note.attack  = read_bits(7)
      note.release = read_bits(7)

  def format(self, patch, data):
    if len(patch.notes):
      bitstream = BitStream(data)
      write_bits = bitstream.write_bits

      lastnote = patch.lastnote
      if not lastnote:
        values = [ 64, 0, 0 ]
      else:
        values = [ lastnote.note, lastnote.attack, lastnote.release ]
      bitstream.write_bitsa([7, 7, 7], values)
      write_bits(5, len(patch.notes)-1)
      for note in patch.notes:
        write_bits(7, note.note)
        write_bits(7, note.attack)
        write_bits(7, note.release)
    else:
      bitstream.write_bits(24, 0x800000)
      bitstream.write_bits(24, 0x200000)
    return bitstream.tell_bit()

def invalidcable(smodule, sconn, direction, dmodule, dconn):
  '''invalidcable(area, smodule, sconn, direction, dmodule, dconn) -> bool
 if connection valid return 0, otherwise error.
'''
  if direction == 1:                  # verify from
    if sconn >= len(smodule.outputs): # out -> in
      return 1
  elif sconn >= len(smodule.inputs):  # in -> in
    return 2
  if dconn >= len(dmodule.inputs):    # verify to
    return 3

  return 0 # if we got here, everything's cool.

class CableList(Section):
  '''CableList Section subclass'''
  type = 0x52
  def parse(self, patch, data):
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits

    self.area = read_bits(2)
    bitstream.seek_bit(8)
    ncables   = read_bits(16)

    area = [patch.fx, patch.voice][self.area]

    area.cables = [ None ] * ncables 
    for i in xrange(ncables):
      cable       = Cable(area)
      cable.color = read_bits(3)

      source      = read_bits(8)
      src_conn    = read_bits(6)
      direction   = read_bits(1)
      dest        = read_bits(8)
      dest_conn   = read_bits(6)

      src_module  = area.find_module(source)
      dest_module = area.find_module(dest)

      if invalidcable(src_module, src_conn, direction, dest_module, dest_conn):
        printf('Invalid cable %d: "%s"(%d,%d) -%d-> "%s"(%d,%d)\n',
            i, src_module.type.shortnm, src_module.index, src_conn, direction,
            dest_module.type.shortnm, dest_module.index, dest_conn)
        continue

      if direction == 1:
        cable.source = src_module.outputs[src_conn]
      else:
        cable.source = src_module.inputs[src_conn]
      cable.dest = dest_module.inputs[dest_conn]

      area.cables[i] = cable
      cable.source.cables.append(cable)
      cable.dest.cables.append(cable)

      area.netlist.add(cable.source, cable.dest)

  def format(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    write_bits(2, self.area)

    area = [patch.fx, patch.voice][self.area]

    bitstream.seek_bit(8)
    write_bits(16, len(area.cables))

    for i, cable in enumerate(area.cables):
      write_bits(3, cable.color)
      write_bits(8, cable.source.module.index)
      write_bits(6, cable.source.index)
      write_bits(1, cable.source.direction)
      write_bits(8, cable.dest.module.index)
      write_bits(6, cable.dest.index)

    return bitstream.tell_bit()

class Parameter(object):
  '''Parameter class for module parameters/settings.'''
  def __init__(self, index, param, default=0, name=''):
    self.index = index
    self.param = param
    self.variations = [default]*NVARIATIONS
    self.name = name
    self.knob = None
    self.mmap = None
    self.ctrl = None

class Morph(object):
  '''Morph class for morph settings.'''
  def __init__(self, index):
    self.name  = 'morph%d' % (index+1)
    self.maps  = [[] for variation in xrange(NVARIATIONS) ]
    self.index = index
    self.ctrl  = None
    self.param = 1
    self.area  = SETTINGS

    # morph "module" has 2 parameters dial and mode
    self.dial = Parameter(1, index, 0)
    self.mode = Parameter(1, index+NMORPHS, 1)
    self.dial.module = self
    self.mode.module = self


class Settings(object):
  '''Settings class for patch settings.'''
  groups = [
    [ 'patchvol', 'activemuted' ],
    [ 'glide', 'glidetime' ],
    [ 'bend', 'semi' ],
    [ 'vibrato', 'cents', 'rate' ],
    [ 'arpeggiator', 'arptime', 'arptype', 'octaves' ],
    [ 'octaveshift', 'sustain' ],
  ]

  def __init__(self):
    for i, group in enumerate(self.groups):
      for j, name in enumerate(group):
        setattr(self, name, Parameter(i+2, j, name=name))
    self.morphs = [ Morph(morph) for morph in xrange(NMORPHS) ]
    self.morphmaps = [ [] for variation in xrange(NVARIATIONS) ]

class Parameters(Section):
  '''Parameters Section subclass'''
  type = 0x4d
  def parse_patch(self, patch, bitstream):
    settings = patch.settings = Settings()
    read_bits = bitstream.read_bits

    nsections   = read_bits(8) # usually 7
    nvariations = read_bits(8) # usually 9

    section     = read_bits(8) # 1 for morph settings
    nentries    = read_bits(7) # 16 parameters per variation
                                         # 8 dials, 8 modes 
    for i in xrange(nvariations): # morph groups
      variation = read_bits(8)
      for morph in xrange(NMORPHS):
        dial = read_bits(7)
        if variation < NVARIATIONS:
          settings.morphs[morph].dial.variations[variation] = dial

      for morph in xrange(NMORPHS):
        mode = read_bits(7)
        if variation < NVARIATIONS:
          settings.morphs[morph].mode.variations[variation] = mode

    for group in settings.groups:
      section   = read_bits(8)
      nentries  = read_bits(7)
      for i in xrange(nvariations):
        variation = read_bits(8)
        for entry in xrange(nentries):
          value = read_bits(7)
          if variation < NVARIATIONS:
            getattr(settings, group[entry]).variations[variation] = value

  def format_patch(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    settings = patch.settings

    write_bits(2, self.area)
    write_bits(8, 7) # always 7 (number of sections?)
    write_bits(8, NVARIATIONS)
    
    write_bits(8, 1)  # 1 for morph settings
    write_bits(7, 16) # 16 parameters per variation

    for variation in xrange(NVARIATIONS): # morph groups
      write_bits(8, variation)
      for morph in xrange(NMORPHS):
        dial = settings.morphs[morph].dial
        write_bits(7, dial.variations[variation])
      for morph in xrange(NMORPHS):
        mode = settings.morphs[morph].mode
        write_bits(7, mode.variations[variation])

    section = 2 # starts at 2 (above: morph is section 1)
    for group in settings.groups:
      nentries = len(group)
      write_bits(8, section)
      write_bits(7, nentries)
      for variation in xrange(NVARIATIONS):
        write_bits(8, variation)
        for entry in xrange(nentries):
          value = getattr(settings, group[entry]).variations[variation]
          write_bits(7, value)
      section += 1

    return bitstream.tell_bit()

  def parse_module(self, patch, bitstream):
    read_bits = bitstream.read_bits

    nmodules    = read_bits(8)
    nvariations = read_bits(8) # if any modules=9, otherwise=0

    area = [patch.fx, patch.voice][self.area]

    for i in xrange(nmodules):
      index   = read_bits(8)
      nparams = read_bits(7)

      module = area.find_module(index)
      params = module.params
      for i in xrange(nvariations):
        variation = read_bits(8)
        for param in xrange(nparams):
          value = read_bits(7)
          if param < len(params) and variation < NVARIATIONS:
            params[param].variations[variation] = value

  def format_module(self, patch, data):
    area = [patch.fx, patch.voice][self.area]

    modules = []
    for module in area.modules:
      try:
        if not len(module.params):
          continue
        modules.append(module)
      except:
        pass
    modules.sort(lambda a, b: cmp(a.index, b.index))

    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    mlen = len(modules)
    write_bits(2, self.area)
    write_bits(8, mlen)
    if mlen == 0:
      write_bits(8, 0)
      return bitstream.tell_bit()
    write_bits(8, NVARIATIONS)

    for module in modules:
      write_bits(8, module.index)

      params = module.params
      write_bits(7, len(params))
      for variation in xrange(NVARIATIONS):
        write_bits(8, variation)
        for param in params:
          write_bits(7, param.variations[variation])

    return bitstream.tell_bit()

  def parse(self, patch, data):
    bitstream = BitStream(data)
    self.area = bitstream.read_bits(2)
    if self.area < 2:
      self.parse_module(patch, bitstream)
    else:
      self.parse_patch(patch, bitstream)

  def format(self, patch, data):
    if self.area < 2:
      return self.format_module(patch, data)
    else:
      return self.format_patch(patch, data)

class MorphParameters(Section):
  '''MorphParameters Section subclass'''
  type = 0x65
  def parse(self, patch, data):
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits

    nvariations = read_bits(8)
    nmorphs     = read_bits(4)
    reserved    = read_bits(10) # always 0
    reserved    = read_bits(10) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs
    morphmaps = patch.settings.morphmaps

    for i in xrange(nvariations):
      variation = read_bits(4)
      bitstream.seek_bit(4 + (6*8) + 4, 1) # zeros

      nmorphs = read_bits(8)
      for j in xrange(nmorphs):
        morph_map       = MorphMap()
        area            = read_bits(2)
        index           = read_bits(8)
        param           = read_bits(7)
        morph           = read_bits(4)
        morph_map.range = read_bits(8, 1)

        module = [patch.fx, patch.voice][area].find_module(index)
        morph_map.param = module.params[param]
        morph_map.variation = variation
        morph_map.morph = morphs[morph]
        morph_map.morph.maps[variation].append(morph_map)
        morphmaps[variation].append(morph_map)

      reserved = read_bits(4) # always 0

  def format(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    write_bits(8, NVARIATIONS)
    write_bits(4, NMORPHS)
    write_bits(10, 0) # always 0
    write_bits(10, 0) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs

    for variation in xrange(NVARIATIONS):
      write_bits(4, variation)
      bitstream.seek_bit(4 + (6 * 8) + 4, 1)

      # collect all params of this variation into 1 array
      morph_params = []
      for morph in morphs:
        morph_params.extend(morph.maps[variation])
      def mod_param_index_cmp(a, b):
        return cmp(a.param.module.index, b.param.module.index)
      morph_params.sort(lambda a, b: mod_param_index_cmp)

      write_bits(8, len(morph_params))
      for morph_param in morph_params:
        write_bits(2, morph_param.param.module.area.index)
        write_bits(8, morph_param.param.module.index)
        write_bits(7, morph_param.param.index)
        write_bits(4, morph_param.morph.index)
        write_bits(8, morph_param.range)

      write_bits(4, 0) # always 0

    bitstream.seek_bit(-4, 1)
    return bitstream.tell_bit()

class KnobAssignments(Section):
  '''KnobAssignments Section subclass'''
  type = 0x62
  def parse(self, patch, data):
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits

    nknobs = read_bits(16)
    patch.knobs = [ Knob() for i in xrange(nknobs)]

    for knob in patch.knobs:
      knob.assigned = read_bits(1)
      if knob.assigned:
        area       = read_bits(2)
        index      = read_bits(8)
        knob.isled = read_bits(2)
        param      = read_bits(7)
        if type(patch) == Performance:
          perf = patch
          knob.slot = read_bits(2)
          patch = perf.patches[knob.slot]
        else:
          knob.slot = 0

        if area == SETTINGS:
          # TODO: handle morph dial and mode params
          knob.param = patch.settings.morphs[param]
        else:
          module = [patch.fx, patch.voice][area].find_module(index)
          if module:
            knob.param = module.params[param]
          else:
            knob.assigned = 0
            continue
        knob.param.knob = knob

  def format(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    write_bits(16, NKNOBS)
    for knob in patch.knobs:
      write_bits(1, knob.assigned)
      if knob.assigned:
        if hasattr(knob.param, 'module'):
          module = knob.param.module
          area, index, param = module.area.index, module.index, knob.param.index
        else:
          area, index, param = 2, 1, knob.param.index
        write_bits(2, area)
        write_bits(8, index)
        write_bits(2, knob.isled)
        write_bits(7, param)
        if type(patch) == Performance:
          write_bits(2, knob.slot)

    return bitstream.tell_bit()

class CtrlAssignments(Section):
  '''CtrlAssignments Section subclass'''
  type = 0x60
  def parse(self, patch, data):
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits

    nctrls = read_bits(7)
    patch.ctrls = [ Ctrl() for i in xrange(nctrls)]
    settings = patch.settings

    for ctrl in patch.ctrls:
      ctrl.midicc = read_bits(7)
      ctrl.type   = read_bits(2) # FX, VOICE, SETTINGS
      index       = read_bits(8)
      param       = read_bits(7)
      ctrl.index  = index
      if ctrl.type == SETTINGS:
        # TODO: handle dial and mode morphs params
        if index < 2:
          ctrl.param = settings.morphs[param]
        else:
          ctrl.param = getattr(settings, settings.groups[index-2][param])
      else:
        module = [patch.fx, patch.voice][ctrl.type].find_module(index)
        ctrl.param = module.params[param]
      ctrl.param.ctrl = ctrl

  def format(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    write_bits(7, len(patch.ctrls))

    for ctrl in patch.ctrls:
      write_bits(7, ctrl.midicc)
      write_bits(2, ctrl.type)
      if ctrl.type < SETTINGS:
        index, param = ctrl.param.module.index, ctrl.param.index
      else:
        index, param = 1, ctrl.param.index
      write_bits(8, index)
      write_bits(7, param)

    return bitstream.tell_bit()

class Labels(Section):
  '''Labels Section subclass'''
  type = 0x5b
  def parse_morph(self, patch, bitstream):
    read_bits = bitstream.read_bits

    nentries = read_bits(8)

    entry, length = bitstream.read_bitsa([8, 8]) # 1, 1, 0x50

    for i in xrange(NMORPHS):
      morph, morphlen, entry = bitstream.read_bitsa([8, 8, 8])
      morphlen -= 1
      s = ''
      for l in xrange(7):
        c = read_bits(8)
        if c != 0:
          s += chr(c&0xff)
      patch.settings.morphs[i].label = s

  def format_morph(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    write_bits(2, self.area)

    t = '\1\1\x50'
    for morph in xrange(NMORPHS):
      s = patch.settings.morphs[morph].label[:7]
      t += '\1\1' + chr(8+morph) + s.ljust(7,'\0')

    for c in map(ord, t):
      write_bits(8, c)

    return bitstream.tell_bit()

  def parse_parameter(self, patch, bitstream):
    read_bits = bitstream.read_bits

    nmodules = read_bits(8)
    area = [patch.fx, patch.voice][self.area]

    for i in xrange(nmodules):
      index  = read_bits(8)
      modlen = read_bits(8)

      module = area.find_module(index)
      if module.type.id == 121: # SeqNote
        # extra editor parameters 
        # [0, 1, mag, 0, 1, octave]
        # mag: 0=3-octaves, 1=2-octaves, 2=1-octave
        # octave: 0-9 (c0-c9)
        module.editmodes = []
        for i in xrange(modlen):
          c = read_bits(8)
          module.editmodes.append(c)
        continue
      while modlen > 0:
        stri, paramlen, param = bitstream.read_bitsa([8, 8, 8]) 
        modlen -= 3

        p = module.params[param]
        p.labels = []

        paramlen -= 1 # decrease because we got param index
        if paramlen:
          for i in xrange(paramlen/7):
            s = ''.join([chr(read_bits(8)) for i in xrange(7)])
            modlen -= 7
            p.labels.append(s.strip('\0'))
        else:
          p.labels.append('')
        if section_debug:
          printf('%d %s %d %d %s\n', index, module.type.shortnm,
              paramlen, param, p.labels)

  def write_str_bits(self, bitstream, s):
    write_bits = bitstream.write_bits
    for char in s:
      write_bits(8, ord(char))

  def format_parameter(self, patch, data):
    area = [patch.fx, patch.voice][self.area]

    modules = []
    # collect all modules with parameters that have labels
    for module in area.modules:
      if hasattr(module, 'params'):
        for param in module.params:
          if hasattr(param, 'labels'):
            modules.append(module)
            break
      if hasattr(module, 'editmodes'):
        modules.append(module)

    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    write_bits(2, self.area)

    write_bits(8, len(modules))
    for module in modules:
      s = ''
      if module.type.id == 121: # SeqNote
        for ep in module.editmodes:
          s += chr(ep)
      else:
        # build up the labels and then write them
        for i, param in enumerate(module.params):
          if not hasattr(param, 'labels'):
            continue
          if section_debug:
            printf('%d %s %d %d %s\n', module.index, module.type.shortnm,
                7*len(param.labels), i, param.labels)
          ps = chr(i)
          for nm in param.labels:
            ps += nm.ljust(7,'\0')[:7]
          s += chr(1)+chr(len(ps))+ps

      write_bits(8, module.index)
      write_bits(8, len(s))
      self.write_str_bits(bitstream, s)

    if section_debug:
      printf('paramlabels:\n')
      printf('%s\n', hexdump(t))

    return bitstream.tell_bit()

  def parse(self, patch, data):
    bitstream = BitStream(data)
    self.area = bitstream.read_bits(2)
    if self.area < 2:
      self.parse_parameter(patch, bitstream)
    else:
      self.parse_morph(patch, bitstream)

  def format(self, patch, data):
    if self.area < 2:
      return self.format_parameter(patch, data)
    else:
      return self.format_morph(patch, data)

class ModuleNames(Section):
  '''ModuleNames Section subclass'''
  type = 0x5a
  def parse(self, patch, data):
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits

    self.area = read_bits(2)
    self.unk1 = read_bits(6)
    nmodules  = read_bits(8)

    area = [patch.fx, patch.voice][self.area]

    names = data[bitstream.tell_bit()>>3:].tobytes()
    for i in xrange(nmodules):
      null = names[1:].find('\0') + 1
      if 0 < null < 17:
        name = names[1:null]
      else:
        name = names[1:17]
        null = 16
      index = ord(names[0])
      module = area.find_module(index)
      module.name = name
      names = names[null+1:]

  def format(self, patch, data):
    bitstream = BitStream(data)
    write_bits = bitstream.write_bits

    write_bits(2, self.area)
    write_bits(6, self.area) # seems to be duplicate of area
    area = [patch.fx, patch.voice][self.area]

    write_bits(8, len(area.modules)) # unknown, see if zero works
    for module in area.modules:
      write_bits(8, module.index)
      nm = module.name[:16]
      if len(nm) < 16:
        nm += '\0'
      for c in nm:
        write_bits(8, ord(c))

    return bitstream.tell_bit()

class TextPad(Section):
  '''TextPad Section subclass'''
  type = 0x6f
  def parse(self, patch, data):
    patch.textpad = data

  def format(self, patch, data):
    bitstream = BitStream(data)
    for c in map(ord, patch.textpad):
      bitstream.write_bits(8, c)
    return bitstream.tell_bit()

class Pch2File(object):
  '''Pch2File(filename) - main reading/writing object for .pch2 files
   this may become generic G2 file for .pch2 and .prf2 files
   just by handling the performance sections (and perhaps others)
   and parsing all 4 patches within the .prf2 file.
'''
  section_map = {
      PatchDescription.type: PatchDescription,
      ModuleList.type:       ModuleList,
      CurrentNote.type:      CurrentNote,
      CableList.type:        CableList,
      Parameters.type:       Parameters,
      MorphParameters.type:  MorphParameters,
      KnobAssignments.type:  KnobAssignments,
      CtrlAssignments.type:  CtrlAssignments,
      Labels.type:           Labels,
      ModuleNames.type:      ModuleNames,
      TextPad.type:          TextPad,
  }
  patch_sections = [
    PatchDescription(),
    ModuleList(area=1),
    ModuleList(area=0),
    CurrentNote(),
    CableList(area=1),
    CableList(area=0),
    Parameters(area=2),
    Parameters(area=1),
    Parameters(area=0),
    MorphParameters(area=2),
    KnobAssignments(),
    CtrlAssignments(),
    Labels(area=2),
    Labels(area=1),
    Labels(area=0),
    ModuleNames(area=1),
    ModuleNames(area=0),
    TextPad(),
  ]
  standard_text_header = '''Version=Nord Modular G2 File Format 1\r
Type=%s\r
Version=%d\r
Info=BUILD %d\r
\0'''  # needs the null byte
  standard_binary_header = 23
  standard_build = 266
  def __init__(self, filename=None):
    self.type = 'Patch'
    self.binary_revision = 0
    self.patch = Patch(fromname)
    if filename:
      self.read(filename)

  def parse_section(self, section, patch_or_perf, memview):
    x = memview[:3].tolist()
    type, l = x[0], 3+((x[1]<<8)|x[2])
    if section_debug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s len:0x%04x\n', type, nm, l)
      printf('%s\n', binhexdump(memview[:l].tobytes()))
    section.parse(patch_or_perf, memview[3:l])
    return l

  def parse_patch(self, patch, memview):
    size = len(memview)
    for section in Pch2File.patch_sections:
      bytes = self.parse_section(section, patch, memview)
      memview = memview[bytes:]
    return size - len(memview)

  def parse(self, memview):
    return self.parse_patch(self.patch, memview)

  # read - this is where the rubber meets the road.  it start here....
  def read(self, filename):
    self.filename = filename
    data = bytearray(open(filename, 'rb').read())
    null = data.find('\0')
    if null < 0:
      raise G2Error('Invalid G2File "%s" missing null terminator.' % filename)
    self.txthdr = data[:null]
    self.binhdr = data[null+1], data[null+2]
    if self.binhdr[0] != self.standard_binary_header:
      printf('Warning: %s version %d\n', filename, self.binhdr[0])
      printf('         version %d supported. it may fail to load.\n',
          self.standard_binary_header)
    memview = memoryview(data)[null+1:]
    bytes = self.parse(memview[2:-2])

    ecrc = (data[-2]<<8)|data[-1]
    acrc = crc(memview[:-2])
    if ecrc != acrc:
      printf('Bad CRC 0x%x 0x%x\n' % (ecrc, acrc))

  def format_section(self, section, patch_or_perf, memview):
    #print section.__class__.__name__
    bits = section.format(patch_or_perf, memview[3:]) # skip type, size 
    bytes = (bits + 7) >> 3
    # write type, size
    memview[0] = chr(section.type)
    memview[1] = chr((bytes >> 8) & 0xff)
    memview[2] = chr(bytes & 0xff)

    if section_debug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s len:0x%04x\n', section.type, nm, bytes)
      tbl = string.maketrans(string.ascii_lowercase, ' '*26)
      nm = nm.translate(tbl).replace(' ', '')
      printf('%s\n', nm)
      #if title_section and len(nm) < len(f):
      #  f = nm+f[len(nm):]

    return bytes + 3

  def format_patch(self, patch, memview):
    size = len(memview)
    for section in Pch2File.patch_sections:
      bytes = self.format_section(section, patch, memview)
      memview = memview[bytes:]
    return size - len(memview)

  def format(self, memview):
    return self.format_patch(self.patch, memview)

  # write - this looks a lot easier then read ehhhh???
  def write(self, filename=None):
    out = open(filename, 'wb')
    hdr = Pch2File.standard_text_header % (self.type,
        self.standard_binary_header, self.standard_build)
    out.write(hdr)
    data = bytearray(64<<10)
    memview = memoryview(data)
    data[:2] = self.standard_binary_header, self.binary_revision
    bytes = self.format(memview[2:]) + 2
    data_crc = crc(data[:bytes])
    data[bytes:bytes+2] = (data_crc >> 8) & 0xff, data_crc & 0xff
    out.write(data[:bytes+2])

class PerformanceDescription(Section):
  '''PerformanceDescription Section subclass'''
  type = 0x11
  description_attrs = [
    ['unk1', 8], ['hold', 1], ['unk2', 7], ['rangesel', 8], ['rate', 8],
    ['unk3', 8], ['clock', 8], ['unk4', 8], ['unk5', 8],
  ]
  patch_attrs = [
    ['unk1', 8], ['active', 8], ['keyboard', 8], ['keyhold', 8],
    ['unk2', 16], ['keylow', 8], ['keyhigh', 8], ['unk3', 8], ['unk4', 8],
  ]
  def parse(self, performance, data):
    description = performance.description = Description()
    bitstream = BitStream(data)
    read_bits = bitstream.read_bits
    for name, nbits in self.description_attrs:
      value = read_bits(nbits)
      setattr(description, name, value)

    patches = description.patches = [ Description() for i in xrange(4) ] 
    bit = bitstream.tell_bit()
    if bit & 7:  # align to next byte
      read_bits(bit & 7)
    for patch in patches:
      name = ''
      for i in range(16):
        c = chr(read_bits(8))
        if c == '\0':
          break
        name += c
      patch.name = name

      for name, nbits in self.patch_attrs:
        value = read_bits(nbits)
        setattr(patch, name, value)

  def format(self, performance, data):
    bitstream = BitStream(data)
    description = performance.description

    for name, nbits in self.description_attrs:
      write_bits(nbits, getattr(description, name))

    patches = description.patches
    for patch in patches:
      for c in patch.name:
        write_bits(8, ord(c))
      if len(patch.name) < 16:
        write_bits(8, 0)

      for name, nbits in self.patch_attrs:
        write_bits(nbits, getattr(patch, name))

    return bitstream.tell_bit()

class GlobalKnobAssignments(KnobAssignments):
  '''GlobalKnobAssignments Section subclasss'''
  type = 0x5f

class Prf2File(Pch2File):
  '''Prf2File(filename) -> load a nord modular g2 performance.'''
  def __init__(self, filename=None):
    self.type = 'Performance'
    self.binary_revision = 1
    self.performance = Performance(fromname)
    self.performance_section = PerformanceDescription()
    self.globalknobs_section = GlobalKnobAssignments()
    if filename:
      self.read(filename)

  def parse(self, memview):
    performance = self.performance
    size = len(memview)
    bytes = self.parse_section(self.performance_section, performance, memview)
    memview = memview[bytes:]
    for patch in performance.patches:
      bytes = self.parse_patch(patch, memview)
      memview = memview[bytes:]
    bytes = self.parse_section(self.globalknobs_section, performance, memview)
    memview = memview[bytes:]
    return size - len(memview)

  def format_performance(self, memview):
    performance = self.performance
    size = len(memview)
    bytes = self.format_section(self.performance_section, performance, memview)
    memview = memview[bytes:]
    for patch in self.performance.patches:
      bytes = self.format_patch(patch, memview)
      memview = memview[bytes:]
    bytes = self.format_section(self.globalknobs_section, performance, memview)
    memview = memview[bytes:]
    return size - len(memview)

  def format(self, memview):
    return self.format_performace(memview)

# this is what comes out the other end:
#   pch2 = Pch2File('test.pch2')
#   patch = pch2.patch
#
#   textpad = patch.textpad
#
#   desc = patch.description
#     desc.nvoices
#     desc.height
#     desc.unk2
#     desc.monopoly
#     desc.variation
#     desc.category
#     desc.red
#     desc.blue
#     desc.yellow
#     desc.orange
#     desc.green
#     desc.purple
#     desc.white
#
#   knob = patch.knobs[i] (i=0~119)
#     page = (i/8)%3 (1,2,3)
#     group = i/24   (A,B,C,D,E)
#     knobnum = i&7  (0 ~ 7)
#     knob.index
#     knob.paramindex
#     knob.area
#     knob.isled
#
#   ctrl = patch.ctrls[i]
#     ctrl.type (1=User,2=System)
#     ctrl.midicc
#     ctrl.index
#     ctrl.paramindex
#
#   settings = patch.settings
#     settings.morphdial[var][dial] (var=0~8, dial=0~7)
#   morphgroup = settings.morphgroup[var][group] (var=0~8, group=0~7)
#     - i may invert the composition so all variations just become arrays
#   variation = settings.variation[var]
#     - i may invert the composition so all variations just become arrays
#     - instead of settings.variation[var].activemuted, it would become
#       settings.activemuted which is a sequence of 9 integers.
#     variation.activemuted
#     variation.arpeggiator
#     variation.arptype
#     variation.bend
#     variation.cents
#     variation.glide
#     variation.octaves
#     variation.octaveshift
#     variation.patchvol
#     variation.rate
#     variation.semi
#     variation.sustain
#     variation.time
#     variation.vibrato
#
#   area = patch.voice
#   area = patch.fx
#
#   module = area.modules[i]
#     module.name
#     module.index
#     module.horiz
#     module.vert
#     module.color
#     module.uprate # increase rate of module i.e. control -> audio
#     module.led    # special parameter seems set for a group of modules
#                   # mostly led outputs for knobs but not always
#                   # i may handle it on a module type basis and remove it
#     module.modes[i]
#     module.params[i]
#     module.inputs[i]
#     module.outputs[i]
#   param = module.params[i]
#     param.variations
#     param.labels
#   type = module.type
#     type.longnm
#     type.shortnm
#     type.height
#     type.page
#     type.modes[i]
#     type.params[i]
#     type.inputs[i]
#     type.outputs[i]
#   page = type.page
#     page.name
#     page.index
#   input = module.inputs[i]
#     input.module
#     input.index
#     input.type
#     input.rate
#     input.cables[i]
#     input.net
#   output = module.outputs[i] # same members as input
#   param = module.params[i]
#     param.module
#     param.index
#     param.type
#     param.variations[i]
#     param.labels[i]
#   ptype = param.type
#     ptype.type
#     ptype.name
#     ptype.low
#     ptype.high
#     ptype.default
#     ptype.definitions
#     ptype.comments
#   mode = module.modes[i]
#     mode.module
#     mode.index
#     mode.type
#     mode.value
#   mtype = mode.type
#     mtype.name
#     mtype.low
#     mtype.high
#     mtype.default
#     mtype.definitions
#     mtype.comments
#
#   cable = area.cables[i]
#     cable.color
#     cable.source
#     cable.dest
#
#   source = cable.source # same as module.inputs[i] or module.outputs[i]
#   dest = cable.dest # same as module.inputs[i] only
#
#   morph = patch.morphs[i]
#     morph.label
#     morph.dial[variation]
#     morph.mode[variation] (0=knob,1=morph,2=wheel2)
#
#   param = morph.params[i]
#     param.area
#     param.index
#     param.paramindex
#     param.range
#   

if __name__ == '__main__':
  prog = sys.argv.pop(0)
  filename = sys.argv.pop(0)
  printf('"%s"\n', filename)
  pch2 = Pch2File(filename)
  #pch2.write(sys.argv.pop(0))

