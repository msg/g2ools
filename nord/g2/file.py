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
from array import array

from nord import printf
from nord.module import Module
from nord.file import hexdump, binhexdump
from nord.g2.modules import fromname
from nord.file import Patch, Performance, Note, Cable, Knob, Ctrl, MorphMap
from nord.g2 import modules
from nord.g2.crc import crc
from nord.g2.bits import setbits, getbits

sectiondebug = 0 # outputs section debug 
titlesection = 0 # replace end of section with section title

NVARIATIONS = 9 # 1-8, init
NMORPHS = 8     # 8 morphs
NKNOBS = 120    # 120 knob settings

FX, VOICE, SETTINGS = 0, 1, 2

zeros = '\0' * (16<<10) # [0] * (8<<10)

class G2Error(Exception):
  '''G2Error - exception for throwing an unrecoverable error.'''
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def getbitsa(bit, sizes, data):
  '''getbitsa(bit, sizes, data) -> bit, [values]'''
  values = []
  for size in sizes:
    bit, value = getbits(bit, size, data)
    values.append(value)
  return [bit] + values

def setbitsa(bit, sizes, data, values):
  '''setbitsa(bit, sizes, data, values) -> bit'''
  for size, value in zip(sizes, values):
    bit = setbits(bit, size, data, value)
  return bit

class Section(object):
  '''Section abstract class that represents a section of .pch2 file.
  all sections objects have parse() and format() methods.
'''
  def __init__(self, **kw):
    self.__dict__ = kw
    self.data = array('B', [0] * (64<<10)) # max 64k section size

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

    bit = 7*8
    for name, nbits in self.description_attrs:
      bit, val = getbits(bit, nbits, data)
      setattr(description, name, val)

  def format(self, patch):
    data = self.data
    description = patch.description

    bit = 7*8
    for name, nbits in self.description_attrs:
      bit = setbits(bit, nbits, data, getattr(description, name))
    bit = setbits(bit, 8, data, 0)

    last = (bit+7)>>3
    return data[:last].tostring()

class ModuleList(Section):
  '''ModuleList Section subclass'''
  type = 0x4a
  module_bit_sizes = [8, 7, 7, 8, 1, 1, 6]
  def parse(self, patch, data):
    bit, self.area = getbits(0, 2, data)
    bit, nmodules = getbits(bit, 8, data)

    area = [patch.fx, patch.voice][self.area]

    area.modules = [ None ] * nmodules
    for i in range(nmodules):
      bit, id = getbits(bit, 8, data)
      m = Module(modules.fromid(id), area)
      area.modules[i] = m

      bit, m.index, m.horiz, m.vert, m.color, m.uprate, m.leds, m.reserved = \
          getbitsa(bit, self.module_bit_sizes, data)
      bit, nmodes = getbits(bit, 4, data)
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property but added to the module types that
      #       set it.
      self.fixleds(m)

      # mode data for module (if there is any)
      for mode in range(nmodes):
        bit, m.modes[mode].value = getbits(bit, 6, data)

      # add missing mode data. some .pch2 versions didn't contain
      #   all the modes in version 23 BUILD 266
      mt = m.type
      if len(m.modes) < len(mt.modes):
        for i in range(len(m.modes), len(mt.modes)):
          m.modes[i].value = mt.modes[i].type.default

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

  def format(self, patch):
    data = self.data

    area = [patch.fx, patch.voice][self.area]

    bit  = setbits(0, 2, data, self.area)
    bit  = setbits(bit, 8, data, len(area.modules))

    for i in range(len(area.modules)):
      m = area.modules[i]
      bit = setbits(bit, 8, data, m.type.id)
      values = [m.index, m.horiz, m.vert, m.color, m.uprate, m.leds, 0]
      bit = setbitsa(bit, self.module_bit_sizes, data, values)
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property.
      self.fixleds(m)

      nmodes = len(area.modules[i].modes)
      bit = setbits(bit, 4, data, nmodes)
      for mode in range(nmodes):
        bit = setbits(bit, 6, data, area.modules[i].modes[mode].value)

    return data[:(bit+7)>>3].tostring()

class CurrentNote(Section):
  '''CurrentNote Section subclass'''
  type = 0x69
  def parse(self, patch, data):
    lastnote = patch.lastnote = Note()
    values = getbitsa(0, [7, 7, 7], data)
    bit, lastnote.note, lastnote.attack, lastnote.release = values
    bit, nnotes = getbits(bit, 5, data)
    notes = patch.notes = [ Note() for i in range(nnotes +1) ]
    for i in range(len(notes)):
      bit, notes[i].note    = getbits(bit, 7, data)
      bit, notes[i].attack  = getbits(bit, 7, data)
      bit, notes[i].release = getbits(bit, 7, data)

  def format(self, patch):
    data = self.data
    if len(patch.notes):
      bit = 0
      lastnote = patch.lastnote
      if not lastnote:
        values = [ 64, 0, 0 ]
      else:
        values = [ lastnote.note, lastnote.attack, lastnote.release ]
      bit = setbitsa(bit, [7, 7, 7], data, values)
      bit = setbits(bit, 5, data, len(patch.notes)-1)
      for note in patch.notes:
        bit = setbits(bit, 7, data, note.note)
        bit = setbits(bit, 7, data, note.attack)
        bit = setbits(bit, 7, data, note.release)
      return data[:(bit+7)>>3].tostring()
    else:
      return '\x80\x00\x00\x20\x00\x00'  # normal default

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

    bit, self.area = getbits(0, 2, data)
    bit, ncables   = getbits(8, 16, data)

    area = [patch.fx, patch.voice][self.area]

    area.cables = [ None ] * ncables 
    for i in range(ncables ):
      c = Cable(area)
      bit, c.color = getbits(bit, 3, data)
      bit, smod    = getbits(bit, 8, data)
      bit, sconn   = getbits(bit, 6, data)
      bit, dir     = getbits(bit, 1, data)
      bit, dmod    = getbits(bit, 8, data)
      bit, dconn   = getbits(bit, 6, data)

      smodule     = area.findmodule(smod)
      dmodule     = area.findmodule(dmod)

      if invalidcable(smodule, sconn, dir, dmodule, dconn):
        printf('Invalid cable %d: "%s"(%d,%d) -%d-> "%s"(%d,%d)\n',
            i, smodule.type.shortnm, smodule.index, sconn, dir,
            dmodule.type.shortnm, dmodule.index, dconn)
        continue

      if dir == 1:
        c.source = smodule.outputs[sconn]
      else:
        c.source = smodule.inputs[sconn]
      c.dest = dmodule.inputs[dconn]

      area.cables[i] = c
      c.source.cables.append(c)
      c.dest.cables.append(c)

      area.netlist.add(c.source, c.dest)

  def format(self, patch):
    data = self.data
    bit  = setbits(0, 2, data, self.area)

    area = [patch.fx, patch.voice][self.area]

    bit = setbits(8, 16, data, len(area.cables))

    for i in range(len(area.cables)):
      c = area.cables[i]
      bit = setbits(bit, 3, data, c.color)
      bit = setbits(bit, 8, data, c.source.module.index)
      bit = setbits(bit, 6, data, c.source.index)
      bit = setbits(bit, 1, data, c.source.direction)
      bit = setbits(bit, 8, data, c.dest.module.index)
      bit = setbits(bit, 6, data, c.dest.index)

    return data[:(bit+7)>>3].tostring()

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
  def __init__(self, param):
    self.dials = Parameter(0, 0, 0)
    self.modes = Parameter(0, 0, 1)
    self.params = []
    self.maps = [[] for variation in range(NVARIATIONS) ]
    self.index = 1
    self.param = param
    self.ctrl = None
    self.name = 'morph%d' % (param+1)

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
    for i in range(len(self.groups)):
      group = self.groups[i]
      for j in range(len(group)):
        name = group[j]
        setattr(self, name, Parameter(i+2, j, name=name))
    self.morphs = [ Morph(morph) for morph in range(NMORPHS) ]

class PatchSettings(Section):
  '''PatchSettings Section subclass'''
  type = 0x4d
  def parse(self, patch, data):
    settings = patch.settings = Settings()

    bit, self.area   = getbits(0, 2, data)
    bit, nsections   = getbits(bit, 8, data) # usually 7
    bit, nvariations = getbits(bit, 8, data) # usually 9

    bit, section  = getbits(bit, 8, data) # 1 for morph settings
    bit, nentries = getbits(bit, 7, data) # 16 parameters per variation
                                          # 8 dials, 8 modes 
    for i in range(nvariations): # morph groups
      bit, variation = getbits(bit, 8, data) # variation number
      for morph in range(NMORPHS):
        bit, dial = getbits(bit, 7, data)
        if variation >= NVARIATIONS:
          continue
        settings.morphs[morph].dials.variations[variation] = dial

      for morph in range(NMORPHS):
        bit, mode = getbits(bit, 7, data)
        if variation >= NVARIATIONS:
          continue
        settings.morphs[morph].modes.variations[variation] = mode

    for group in settings.groups:
      bit, section  = getbits(bit, 8, data)
      bit, nentries = getbits(bit, 7, data)
      for i in range(nvariations):
        bit, variation = getbits(bit, 8, data)
        for entry in range(nentries):
          bit, value = getbits(bit, 7, data)
          if variation >= NVARIATIONS:
            continue
          getattr(settings, group[entry]).variations[variation] = value

  def format(self, patch):
    data     = self.data
    settings = patch.settings

    bit = setbits(0, 2, data, self.area)
    bit = setbits(bit, 8, data, 7) # always 7 (number of sections?)
    bit = setbits(bit, 8, data, NVARIATIONS)
    
    bit = setbits(bit, 8, data, 1)  # 1 for morph settings
    bit = setbits(bit, 7, data, 16) # 16 parameters per variation

    for variation in range(NVARIATIONS): # morph groups
      bit = setbits(bit, 8, data, variation) # variation
      for morph in range(NMORPHS):
        dial = settings.morphs[morph].dials
        bit = setbits(bit, 7, data, dial.variations[variation])
      for morph in range(NMORPHS):
        mode = settings.morphs[morph].modes
        bit = setbits(bit, 7, data, mode.variations[variation])

    section = 2 # starts at 2 (above: morph is section 1)
    for group in settings.groups:
      nentries = len(group)
      bit = setbits(bit, 8, data, section)
      bit = setbits(bit, 7, data, nentries)
      for variation in range(NVARIATIONS):
        bit = setbits(bit, 8, data, variation)
        for entry in range(nentries):
          value = getattr(settings, group[entry]).variations[variation]
          bit = setbits(bit, 7, data, value)
      section += 1

    return data[:(bit+7)>>3].tostring()

class ModuleParameters(Section):
  '''ModuleParameters Section subclass'''
  type = 0x4d
  def parse(self, patch, data):
    bit, self.area   = getbits(0, 2, data)
    bit, nmodules    = getbits(bit, 8, data)
    bit, nvariations = getbits(bit, 8, data) # if any modules=9, otherwise=0

    area = [patch.fx, patch.voice][self.area]

    for i in range(nmodules):
      bit, index = getbits(bit, 8, data)
      m = area.findmodule(index)

      bit, nparams = getbits(bit, 7, data)

      params = m.params
      for i in range(nvariations):
        bit, variation = getbits(bit, 8, data)
        for param in range(nparams):
          if param < len(m.params):
            bit, params[param].variations[variation] = getbits(bit, 7, data)
          else:
            bit, junk = getbits(bit, 7, data)
            
  def format(self, patch):
    data = self.data

    area = [patch.fx, patch.voice][self.area]

    modules = []
    for i in range(len(area.modules)):
      if not hasattr(area.modules[i], 'params'):
        continue
      elif not len(area.modules[i].params):
        continue
      modules.append(area.modules[i])
    modules.sort(lambda a, b: cmp(a.index, b.index))

    bit = setbits(0, 2, data, self.area)
    bit = setbits(bit, 8, data, len(modules))
    if not len(modules):
      bit = setbits(bit, 8, data, 0) # 0 variations
      return data[:(bit+7)>>3].tostring()
    bit = setbits(bit, 8, data, NVARIATIONS)

    for i in range(len(modules)):
      m = modules[i]

      bit = setbits(bit, 8, data, m.index)

      params = m.params
      bit = setbits(bit, 7, data, len(params))
      for variation in range(NVARIATIONS):
        bit = setbits(bit, 8, data, variation)
        for param in range(len(params)):
          bit = setbits(bit, 7, data, params[param].variations[variation])

    return data[:(bit+7)>>3].tostring()

class MorphParameters(Section):
  '''MorphParameters Section subclass'''
  type = 0x65
  def parse(self, patch, data):
    bit, nvariations = getbits(0, 8, data)
    bit, nmorphs     = getbits(bit, 4, data)
    bit, reserved    = getbits(bit, 10, data) # always 0
    bit, reserved    = getbits(bit, 10, data) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs

    for i in range(nvariations):
      bit, variation = getbits(bit, 4, data)
      bit += 4+(6*8)+4 # zeros

      bit, nmorphs = getbits(bit, 8, data)
      for i in range(nmorphs):
        mmap = MorphMap()
        bit, area       = getbits(bit, 2, data)
        bit, index      = getbits(bit, 8, data)
        bit, param      = getbits(bit, 7, data)
        bit, morph      = getbits(bit, 4, data)
        bit, mmap.range = getbits(bit, 8, data, 1)
        if area:
          mmap.param = patch.voice.findmodule(index).params[param]
        else:
          mmap.param = patch.fx.findmodule(index).params[param]
        mmap.morph = morphs[morph]
        morphs[morph].maps[variation].append(mmap)

      bit, reserved = getbits(bit, 4, data) # always 0

  def format(self, patch):
    data = self.data

    bit = setbits(0, 8, data, NVARIATIONS)
    bit = setbits(bit, 4, data, NMORPHS)
    bit = setbits(bit, 10, data, 0) # always 0
    bit = setbits(bit, 10, data, 0) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs

    for variation in range(NVARIATIONS):
      bit = setbits(bit, 4, data, variation)
      bit += 4+(6*8)+4 # zeros

      # collect all params of this variation into 1 array
      mparams = []
      for morph in range(len(morphs)):
        mparams.extend(morphs[morph].maps[variation])
      mparams.sort(lambda a, b: cmp(a.param.module.index, b.param.module.index))

      bit = setbits(bit, 8, data, len(mparams))
      for i in range(len(mparams)):
        mparam = mparams[i]
        bit = setbits(bit, 2, data, mparam.param.module.area.index)
        bit = setbits(bit, 8, data, mparam.param.module.index)
        bit = setbits(bit, 7, data, mparam.param.index)
        bit = setbits(bit, 4, data, mparam.morph.index)
        bit = setbits(bit, 8, data, mparam.range)

      bit = setbits(bit, 4, data, 0) # always 0

    bit -= 4
    return data[:(bit+7)>>3].tostring()

class KnobAssignments(Section):
  '''KnobAssignments Section subclass'''
  type = 0x62
  def parse(self, patch, data):
    bit, nknobs = getbits(0, 16, data)
    patch.knobs = [ Knob() for i in range(nknobs)]
    perf = patch

    for i in range(nknobs):
      k = perf.knobs[i]
      bit, k.assigned = getbits(bit, 1, data)
      if k.assigned:
        bit, area = getbits(bit, 2, data)
        bit, index = getbits(bit, 8, data)
        bit, k.isled = getbits(bit, 2, data)
        bit, param = getbits(bit, 7, data)
        if type(perf) == Performance:
          bit, k.slot = getbits(bit, 2, data)
          patch = perf.patches[k.slot]
        else:
          k.slot = 0

        if area == FX or area == VOICE:
          m = [patch.fx, patch.voice][area].findmodule(index)
          if m:
            k.param = m.params[param]
          else:
            k.assigned = 0
            continue
        elif area == SETTINGS:
          k.param = patch.settings.morphs[param]
        k.param.knob = k

  def format(self, patch):
    data = self.data
    perf = patch

    bit = setbits(0, 16, data, NKNOBS)
    for i in range(NKNOBS):
      k = perf.knobs[i]
      bit = setbits(bit, 1, data, k.assigned)
      if k.assigned:
        if hasattr(k.param, 'module'):
          mod = k.param.module
          area, index, param = mod.area.index, mod.index, k.param.index
        else:
          area, index, param = 2, 1, k.param.index
        bit = setbits(bit, 2, data, area)
        bit = setbits(bit, 8, data, index)
        bit = setbits(bit, 2, data, k.isled)
        bit = setbits(bit, 7, data, param)
        if type(perf) == Performance:
          bit = setbits(bit, 2, data, k.slot)

    return data[:(bit+7)>>3].tostring()

class CtrlAssignments(Section):
  '''CtrlAssignments Section subclass'''
  type = 0x60
  def parse(self, patch, data):
    bit, nctrls  = getbits(0, 7, data)
    patch.ctrls = [ Ctrl() for i in range(nctrls)]
    settings = patch.settings

    for i in range(nctrls):
      m = patch.ctrls[i]
      bit, m.midicc = getbits(bit, 7, data)
      bit, m.type = getbits(bit, 2, data) # FX, VOICE, SETTINGS
      bit, index = getbits(bit, 8, data)
      bit, param = getbits(bit, 7, data)
      m.index = index
      m.param_index = param
      if m.type == FX:
        m.param = patch.fx.findmodule(index).params[param]
      elif m.type == VOICE:
        m.param = patch.voice.findmodule(index).params[param]
      elif m.type == SETTINGS:
        if index < 2:
          m.param = settings.morphs[param]
        else:
          m.param = getattr(settings, settings.groups[index-2][param])
      m.param.ctrl = m

  def format(self, patch):
    data = self.data

    bit = setbits(0, 7, data, len(patch.ctrls))

    for i in range(len(patch.ctrls)):
      m = patch.ctrls[i]
      bit = setbits(bit, 7, data, m.midicc)
      bit = setbits(bit, 2, data, m.type)
      if m.type < SETTINGS:
        index, param = m.param.module.index, m.param.index
      else:
        index, param = m.param.index, m.param.param
      bit = setbits(bit, 8, data, index)
      bit = setbits(bit, 7, data, param)

    return data[:(bit+7)>>3].tostring()

class MorphLabels(Section):
  '''MorphLabels Section subclass'''
  type = 0x5b
  def parse(self, patch, data):
    bit, self.area = getbits(0, 2, data)

    bit, nentries, entry, length = getbitsa(bit, [8, 8, 8], data) # 1, 1, 0x50
    for i in range(NMORPHS):
      bit, morph, morphlen, entry = getbitsa(bit, [8, 8, 8], data)
      morphlen -= 1
      s = ''
      for l in range(morphlen):
        bit, c = getbits(bit, 8, data)
        if c != 0:
          s += chr(c&0xff)
      patch.settings.morphs[i].label = s

  def format(self, patch):
    data = self.data

    bit = setbits(  0, 2, data, self.area)

    t = '\1\1\x50'
    for morph in range(NMORPHS):
      t += ''.join(map(chr, [1, 8, 8+morph]))
      s = patch.settings.morphs[morph].label[:7]
      s += '\0' * (7-len(s))
      for i in range(len(s)):
        t += s[i]

    for c in t:
      bit = setbits(bit, 8, data, ord(c))

    return data[:(bit+7)>>3].tostring()

class ParameterLabels(Section):
  '''ParameterLabels Section subclass'''
  type = 0x5b
  def parse(self, patch, data):

    bit, self.area = getbits(0, 2, data)
    bit, nmodules = getbits(bit, 8, data)

    if sectiondebug:
      b = bit
      s = chr(nmodules)
      while b/8 < len(data):
        b, c = getbits(b, 8, data)
        s += chr(c)
      printf('paramlabels:\n')
      printf('%s\n', hexdump(s))

    area = [patch.fx, patch.voice][self.area]

    for mod in range(nmodules):

      bit, index = getbits(bit, 8, data)
      m = area.findmodule(index)

      bit, modlen   = getbits(bit, 8, data)
      if m.type.id == 121: # SeqNote
        # extra editor parameters 
        # [0, 1, mag, 0, 1, octave]
        # mag: 0=3-octaves, 1=2-octaves, 2=1-octave
        # octave: 0-9 (c0-c9)
        m.editmodes = []
        for i in range(modlen):
          bit, c = getbits(bit, 8, data)
          m.editmodes.append(c)
        continue
      while modlen > 0:
        bit, stri, paramlen, param = getbitsa(bit, [8, 8, 8], data) 
        modlen -= 3

        p = m.params[param]
        p.labels = []

        paramlen -= 1 # decrease because we got param index
        if paramlen:
          for i in range(paramlen/7):
            s = ''
            for i in range(7):
              bit, c = getbits(bit, 8, data)
              s += chr(c)
            modlen -= 7
            null = s.find('\0')
            if null > -1:
              s = s[:null]
            p.labels.append(s)
        else:
          p.labels.append('')
        if sectiondebug:
          printf('%d %s %d %d %s\n', index, m.type.shortnm,
              paramlen, param, p.labels)

  def format(self, patch):
    data = self.data

    area = [patch.fx, patch.voice][self.area]

    modules = []
    # collect all modules with parameters that have labels
    for i in range(len(area.modules)):
      m = area.modules[i]
      if hasattr(m, 'params'):
        for j in range(len(m.params)):
          if hasattr(m.params[j], 'labels'):
            modules.append(m)
            break
      if hasattr(m, 'editmodes'):
        modules.append(m)

    bit = setbits(0, 2, data, self.area)

    t = chr(len(modules))
    for mod in range(len(modules)):
      m = modules[mod]

      s = ''
      if m.type.id == 121: # SeqNote
        for ep in m.editmodes:
          s += chr(ep)
      else:
        # build up the labels and then write them
        for i in range(len(m.params)):
          param = m.params[i]
          if not hasattr(param, 'labels'):
            continue
          if sectiondebug:
            printf('%d %s %d %d %s\n', m.index, m.type.shortnm,
                7*len(param.labels), i, param.labels)
          ps = ''
          for nm in param.labels:
            ps += (nm+'\0'*7)[:7]
          ps = chr(i)+ps
          ps = chr(1)+chr(len(ps))+ps
          s += ps

      t += chr(m.index) + chr(len(s)) + s

    if sectiondebug:
      printf('paramlabels:\n')
      printf('%s\n', hexdump(t))

    for c in t:
      bit = setbits(bit, 8, data, ord(c))

    return data[:(bit+7)>>3].tostring()

class ModuleNames(Section):
  '''ModuleNames Section subclass'''
  type = 0x5a
  def parse(self, patch, data):
    bit, self.area = getbits(0, 2, data)
    bit, self.unk1 = getbits(bit, 6, data)
    bit, nmodules = getbits(bit, 8, data)

    area = [patch.fx, patch.voice][self.area]

    names = data[bit/8:]
    for i in range(nmodules):
      null = names.find('\0')
      index = ord(names[0])
      if null < 0 or null > 17:
        name = names[1:17]
        null = 16
      else:
        name = names[1:null]
      m = area.findmodule(index)
      m.name = name
      names = names[null+1:]

  def format(self, patch):
    data = self.data

    bit = setbits(0, 2, data, self.area)
    bit = setbits(bit, 6, data, self.area) # seems to be duplicate of area
    area = [patch.fx, patch.voice][self.area]

    bit = setbits(bit, 8, data, len(area.modules)) # unknown, see if zero works
    for i in range(len(area.modules)):
      bit = setbits(bit, 8, data, area.modules[i].index)
      nm = area.modules[i].name[:16]
      if len(nm) < 16:
        nm += '\0'
      for c in nm:
        bit = setbits(bit, 8, data, ord(c))

    return data[:(bit+7)>>3].tostring()

class TextPad(Section):
  '''TextPad Section subclass'''
  type = 0x6f
  def parse(self, patch, data):
    patch.textpad = data

  def format(self, patch):
    return patch.textpad

class Pch2File(object):
  '''Pch2File(filename) - main reading/writing object for .pch2 files
   this may become generic G2 file for .pch2 and .prf2 files
   just by handling the performance sections (and perhaps others)
   and parsing all 4 patches within the .prf2 file.
'''
  patchsections = [
    PatchDescription(),
    ModuleList(area=1), ModuleList(area=0),
    CurrentNote(),
    CableList(area=1), CableList(area=0),
    PatchSettings(area=2),
    ModuleParameters(area=1), ModuleParameters(area=0),
    MorphParameters(),
    KnobAssignments(),
    CtrlAssignments(),
    MorphLabels(area=2),
    ParameterLabels(area=1), ParameterLabels(area=0),
    ModuleNames(area=1), ModuleNames(area=0),
    TextPad(),
  ]
  standardtxthdr = '''Version=Nord Modular G2 File Format 1\r
Type=%s\r
Version=%d\r
Info=BUILD %d\r
\0'''
  standardbinhdr = 23
  standardbuild = 266
  def __init__(self, filename=None):
    self.type = 'Patch'
    self.binrev = 0
    self.patch = Patch(fromname)
    if filename:
      self.read(filename)

  def parsepatch(self, patch, data, off):
    for section in Pch2File.patchsections:
      sectiontype, l = struct.unpack('>BH', data[off:off+3])
      off += 3
      if sectiondebug:
        nm = section.__class__.__name__
        printf('0x%02x %-25s addr:0x%04x len:0x%04x\n', sectiontype, nm, off, l)
        printf('%s\n', binhexdump(data[off:off+l]))
      section.parse(patch, data[off:off+l])
      off += l
    return off

  def parse(self, data, off):
    return self.parsepatch(self.patch, data, off)

  # read - this is where the rubber meets the road.  it start here....
  def read(self, filename):
    self.filename = filename
    data = open(filename, 'rb').read()
    null = data.find('\0')
    if null < 0:
      raise G2Error('Invalid G2File "%s" missing null terminator.' % filename)
    self.txthdr = data[:null]
    off = null+1
    self.binhdr = struct.unpack('BB', data[off:off+2])
    if self.binhdr[0] != self.standardbinhdr:
      printf('Warning: %s version %d\n', filename, self.binhdr[0])
      printf('         version %d supported. it may fail to load.\n',
          self.standardbinhdr)
    off += 2
    off = self.parse(data, off)

    ecrc = struct.unpack('>H', data[-2:])[0]
    acrc = crc(data[null+1:-2])
    if ecrc != acrc:
      printf('Bad CRC\n')

  def formatpatch(self, patch):
    s = ''
    for section in Pch2File.patchsections:
      section.data = array('B', zeros) # max 64k section size
      f = section.format(patch)

      if sectiondebug:
        nm = section.__class__.__name__
        printf('0x%02x %-25s len:0x%04x total: 0x%04x\n',
            section.type, nm, len(f), self.off+len(s))
        tbl = string.maketrans(string.ascii_lowercase, ' '*26)
        nm = nm.translate(tbl).replace(' ', '')
        printf('%s\n', nm)
        if titlesection and len(nm) < len(f):
          f = nm+f[len(nm):]

      s += struct.pack('>BH', section.type, len(f)) + f
    return s

  def format(self):
    return self.formatpatch(self.patch)

  # write - this looks a lot easier then read ehhhh???
  def write(self, filename=None):
    out = open(filename, 'wb')
    hdr = Pch2File.standardtxthdr % (self.type,
        self.standardbinhdr, self.standardbuild)
    self.off = len(hdr)
    s = struct.pack('BB', Pch2File.standardbinhdr, self.binrev)
    self.off += len(s)
    s += self.format()
    out.write(hdr + s)
    out.write(struct.pack('>H', crc(s)))

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
  def parse(self, perf, data):
    description = perf.description = Description()

    bit = 0
    for name, nbits in self.description_attrs:
      bit, value = getbits(bit, nbits, data)
      setattr(description, name, value)

    patches = description.patches = [ Description() for i in range(4) ] 
    for i in range(4):
      patch = patches[i]
      pdata = data[bit/8:]
      null = pdata.find('\0')
      if null < 0 or null > 16:
        null = 16
      else:
        null += 1
      patch.name = pdata[:null].replace('\0', '')
      bit += null*8

      for name, nbits in self.patch_attrs:
        bit, value = getbits(bit, nbits, data)
        setattr(patch, name, value)

  def format(self, perf):
    data = self.data
    description = perf.description

    bit = 0
    for name, nbits in self.description_attrs:
      bit = setbits(bit, nbits, data, getattr(description, name))

    patches = description.patches
    for i in range(4):
      patch = patches[i]
      nm = patch.name
      if len(nm) < 16:
        nm += '\0'
      for c in nm[:16]:
        bit = setbits(bit, 8, data, ord(c))

      for name, nbits in self.patch_attrs:
        bit = setbits(bit, nbits, data, getattr(patch, name))

    last = (bit+7)>>3
    return data[:last].tostring()

class GlobalKnobAssignments(KnobAssignments):
  '''GlobalKnobAssignments Section subclasss'''
  type = 0x5f

class Prf2File(Pch2File):
  '''Prf2File(filename) -> load a nord modular g2 performance.'''
  def __init__(self, filename=None):
    self.type = 'Performance'
    self.binrev = 1
    self.performance = Performance(fromname)
    self.perfsection = PerformanceDescription()
    self.globalsection = GlobalKnobAssignments()
    if filename:
      self.read(filename)

  def parsesection(self, section, data, off):
    sid, l = struct.unpack('>BH', data[off:off+3])
    off += 3
    if sectiondebug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s addr:0x%04x len:0x%04x\n', sid, nm, off, l)

    section.parse(self.performance, data[off:off+l])
    return off + l

  def parse(self, data, off):
    off = self.parsesection(self.perfsection, data, off)
    for i in range(4):
      off = self.parsepatch(self.performance.patches[i], data, off)
    return self.parsesection(self.globalsection, data, off)

  def formatsection(self, section, total=0):
    section.data = array('B', [0] * (64<<10)) # max 64k section size
    f = section.format(self.performance)
    if sectiondebug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s             len:0x%04x total: 0x%04x\n',
          section.type, nm, len(f), total)
      if titlesection:
        tbl = string.maketrans(string.ascii_lowercase, ' '*26)
        nm = nm.translate(tbl).replace(' ', '')
        l = len(nm)
        if l < len(f):
          f = f[:-len(nm)]+nm
    return struct.pack('>BH', section.type, len(f)) + f

  def format(self):
    s = self.formatsection(self.perfsection)
    for i in range(4):
      s += self.formatpatch(self.performance.patches[i])
    return s + self.formatsection(self.globalsection, len(s))

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

