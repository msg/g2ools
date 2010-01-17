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

import string, struct, sys
from array import array

from nord.net import addnet
from nord.module import Module
from nord.g2.modules import fromname
from nord.file import *
from nord.g2 import modules
from nord.g2.crc import crc
from nord.g2.bits import setbits, getbits

sectiondebug = 0 # outputs section debug 
titlesection = 0 # replace end of section with section title

NVARIATIONS = 9 # 1-8, init
NMORPHS = 8     # 8 morphs
NKNOBS = 120    # 120 knob settings

class G2Error(Exception):
  '''G2Error - exception for throwing an unrecoverable error.'''
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Struct(object):
  '''Struct - generic class for creating named variables in objects
  i.e. s = Struct(one=1,two=2,three=3,...)
     contains: s.one, s.two, s.three
'''
  def __init__(self, **kw):
    self.__dict__ = kw

zeros = array('B', [0] * (64<<10))
class Section(Struct):
  '''Section abstract class that represents a section of .pch2 file.
  all sections objects have parse() and format() methods.
'''
  def __init__(self, **kw):
    super(Section,self).__init__(**kw)
    self.data = zeros[:]

class Description(object):
  '''Description class for patch/performance description.'''
  pass

class PatchDescription(Section):
  '''PatchDescription Section subclass'''
  def parse(self, patch, data):
    desc = patch.description = Description()

    bit,desc.reserved  = getbits(7*8,5,data)
    bit,desc.nvoices   = getbits(bit,5,data)
    bit,desc.height    = getbits(bit,14,data)
    bit,desc.unk2      = getbits(bit,3,data) # range 0 to 4
    bit,desc.red       = getbits(bit,1,data)
    bit,desc.blue      = getbits(bit,1,data)
    bit,desc.yellow    = getbits(bit,1,data)
    bit,desc.orange    = getbits(bit,1,data)
    bit,desc.green     = getbits(bit,1,data)
    bit,desc.purple    = getbits(bit,1,data)
    bit,desc.white     = getbits(bit,1,data)
    bit,desc.monopoly  = getbits(bit,2,data)
    bit,desc.variation = getbits(bit,8,data)
    bit,desc.category  = getbits(bit,8,data)

  def format(self, patch):
    data = self.data
    desc = patch.description

    bit = setbits(7*8,5,data,desc.reserved)
    bit = setbits(bit,5,data,desc.nvoices)
    bit = setbits(bit,14,data,desc.height)
    bit = setbits(bit,3,data,desc.unk2)
    bit = setbits(bit,1,data,desc.red)
    bit = setbits(bit,1,data,desc.blue)
    bit = setbits(bit,1,data,desc.yellow)
    bit = setbits(bit,1,data,desc.orange)
    bit = setbits(bit,1,data,desc.green)
    bit = setbits(bit,1,data,desc.purple)
    bit = setbits(bit,1,data,desc.white)
    bit = setbits(bit,2,data,desc.monopoly)
    bit = setbits(bit,8,data,desc.variation)
    bit = setbits(bit,8,data,desc.category)
    bit = setbits(bit,8,data,0)

    last = (bit+7)>>3
    return data[:last].tostring()

class ModuleList(Section):
  '''ModuleList Section subclass'''
  def parse(self, patch, data):
    bit,self.area = getbits(0,2,data)
    bit,nmodules = getbits(bit,8,data)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    area.modules = [ None ] * nmodules
    for i in range(nmodules):
      #m = area.modules[i]
      bit,type       = getbits(bit,8,data)
      m = Module(modules.fromtype(type),area)
      area.modules[i] = m
      #m.type = modules.fromtype(type) # use type object instead of number
      bit,m.index    = getbits(bit,8,data)
      bit,m.horiz    = getbits(bit,7,data)
      bit,m.vert     = getbits(bit,7,data)
      bit,m.color    = getbits(bit,8,data)
      bit,m.uprate   = getbits(bit,1,data)
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property but added to the module types that
      #       set it.
      bit,m.leds     = getbits(bit,1,data)
      self.fixleds(m)
      bit,m.reserved = getbits(bit,6,data)
      bit, nmodes = getbits(bit,4,data)

      #printf('modules %-10s t=%03d i=%02x h=%d v=%02d c=%02d r=%x l=%x s=%02x m=%x\n',
      #    modules.fromtype(m.type).shortnm, m.type, m.ndex,
      #    m.horiz, m.vert, m.color, m.uprate, m.leds, m.reserved, nmodes)

      # mode data for module (if there is any)
      for mode in range(nmodes):
        bit,val = getbits(bit,6,data)
        m.modes[mode].value = val

      # add missing mode data. some .pch2 versions didn't contain
      #   the all the modes in version 23 BUILD 266
      mt = m.type
      if len(m.modes) < len(mt.modes):
        for i in range(len(m.modes),len(mt.modes)):
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
    if module.type.type in ModuleList.ledtypes:
      module.leds = 1
    else:
      module.leds = 0

  def format(self, patch):
    data = self.data

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    bit  = setbits(0,2,data,self.area)
    bit  = setbits(bit,8,data,len(area.modules))

    for i in range(len(area.modules)):
      m = area.modules[i]
      bit = setbits(bit,8,data,m.type.type)
      bit = setbits(bit,8,data,m.index)
      bit = setbits(bit,7,data,m.horiz)
      bit = setbits(bit,7,data,m.vert)
      bit = setbits(bit,8,data,m.color)
      bit = setbits(bit,1,data,m.uprate)
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property.
      self.fixleds(m)
      bit = setbits(bit,1,data,m.leds)
      bit = setbits(bit,6,data,0) # m.reserved

      nmodes = len(area.modules[i].modes)
      bit = setbits(bit,4,data,nmodes)
      for mode in range(nmodes):
        bit = setbits(bit,6,data,area.modules[i].modes[mode].value)

    return data[:(bit+7)>>3].tostring()

class CurrentNote(Section):
  '''CurrentNote Section subclass'''
  def parse(self, patch, data):
    lastnote = patch.lastnote = Note()
    bit, lastnote.note    = getbits(0,7,data)
    bit, lastnote.attack  = getbits(bit,7,data)
    bit, lastnote.release = getbits(bit,7,data)
    bit, nnotes           = getbits(bit,5,data)
    notes = patch.notes = [ Note() for i in range(nnotes +1) ]
    for i in range(len(notes)):
      bit, notes[i].note    = getbits(bit,7,data)
      bit, notes[i].attack  = getbits(bit,7,data)
      bit, notes[i].release = getbits(bit,7,data)

  def format(self, patch):
    data = self.data
    if len(patch.notes):
      if not patch.lastnote:
        bit = setbits(0,7,data,64)
        bit = setbits(bit,7,data,0)
        bit = setbits(bit,7,data,0)
      else:
        bit = setbits(0,7,data,patch.lastnote.note)
        bit = setbits(bit,7,data,patch.lastnote.attack)
        bit = setbits(bit,7,data,patch.lastnote.release)
      bit = setbits(bit,5,data,len(patch.notes)-1)
      for note in patch.notes:
        bit = setbits(bit,7,data,note.note)
        bit = setbits(bit,7,data,note.attack)
        bit = setbits(bit,7,data,note.release)
      return data[:(bit+7)>>3].tostring()
    else:
      return '\x80\x00\x00\x20\x00\x00'  # normal default


def validcable(area, smodule, sconn, direction, dmodule, dconn):
  '''validatecable(area, smodule, sconn, direction, dmodule, dconn)
 if connection valid return 0, otherwise error.
'''

  # verify from
  # out -> in
  if direction == 1:
    if sconn >= len(smodule.outputs):
      return 1
  # in -> in
  elif sconn >= len(smodule.inputs):
    return 2

  # verify to
  if dconn >= len(dmodule.inputs):
    return 3

  # if we got here, everything's cool.
  return 0

class CableList(Section):
  '''CableList Section subclass'''
  def parse(self, patch, data):

    bit,self.area = getbits(0,2,data)
    bit,ncables   = getbits(8,16,data)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    area.cables = [ None ] * ncables 
    for i in range(ncables ):
      c = Cable(area)
      bit,c.color = getbits(bit,3,data)
      bit,smod    = getbits(bit,8,data)
      bit,sconn   = getbits(bit,6,data)
      bit,dir     = getbits(bit,1,data)
      bit,dmod    = getbits(bit,8,data)
      bit,dconn   = getbits(bit,6,data)

      smodule     = area.findmodule(smod)
      dmodule     = area.findmodule(dmod)

      invalid = validcable(area, smodule, sconn, dir, dmodule, dconn)
      if invalid:
        printf('Invalid cable %d: "%s"(%d,%d) -%d-> "%s"(%d,%d)\n',
            invalid, smodule.type.shortnm, smodule.index, sconn, dir,
            dmodule.type.shortnm, dmodule.index, dconn)
      else:
        area.cables[i] = c

        if dir == 1:
          c.source = smodule.outputs[sconn]
        else:
          c.source = smodule.inputs[sconn]
        c.dest = dmodule.inputs[dconn]

        c.source.cables.append(c)
        c.dest.cables.append(c)

        addnet(area.netlist, c.source, c.dest)

  def format(self, patch):
    data = self.data
    bit  = setbits(0,2,data,self.area)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    bit = setbits(8,16,data,len(area.cables))

    for i in range(len(area.cables)):
      c = area.cables[i]
      #printf('%d %02d %d -%d- %02d %d\n', c.color, c.source.module.index,
      #    c.source.index, c.source.direction, c.dest.module.index,
      #    c.dest.index)
      bit = setbits(bit,3,data,c.color)
      bit = setbits(bit,8,data,c.source.module.index)
      bit = setbits(bit,6,data,c.source.index)
      bit = setbits(bit,1,data,c.source.direction)
      bit = setbits(bit,8,data,c.dest.module.index)
      bit = setbits(bit,6,data,c.dest.index)

    return data[:(bit+7)>>3].tostring()

class Parameter(object):
  '''Parameter class for module parameters/settings.'''
  def __init__(self,default=0):
    self.variations = [default]*NVARIATIONS
    self.knob = None
    self.mmap = None
    self.ctrl = None

class Morph(object):
  '''Morph class for morph settings.'''
  def __init__(self,index):
    self.dials = Parameter(0)
    self.modes = Parameter(1)
    self.params = []
    self.maps = [[] for variation in range(NVARIATIONS) ]
    self.index = index
    self.ctrl = None

class Settings(object):
  '''Settings class for patch settings.'''
  def __init__(self):
    self.patchvol    = Parameter()
    self.activemuted = Parameter()
    self.glide       = Parameter()
    self.glidetime   = Parameter()
    self.bend        = Parameter()
    self.semi        = Parameter()
    self.vibrato     = Parameter()
    self.cents       = Parameter()
    self.rate        = Parameter()
    self.arpeggiator = Parameter()
    self.arptime     = Parameter()
    self.arptype     = Parameter()
    self.octaves     = Parameter()
    self.octaveshift = Parameter()
    self.sustain     = Parameter()
    self.morphs = [ Morph(morph) for morph in range(NMORPHS) ]

class PatchSettings(Section):
  '''PatchSettings Section subclass'''
  def parse(self, patch, data):
    settings = patch.settings = Settings()

    bit,self.area   = getbits(0,2,data)   # always 2 (0=fx,1=voice,2=settings)
    bit,nsections   = getbits(bit,8,data) # usually 7
    bit,nvariations = getbits(bit,8,data) # usually 9

    bit,section  = getbits(bit,8,data) # 1 for morph settings
    bit,nentries = getbits(bit,7,data) # 16 parameters per variation

    for i in range(nvariations): # morph groups
      bit,variation = getbits(bit,8,data) # variation number
      for morph in range(NMORPHS):
        bit,dial = getbits(bit,7,data)
	#print 'var %d: morph dial=%d' % (i, dial)
	if variation >= NVARIATIONS:
	  continue
        settings.morphs[morph].dials.variations[variation] = dial
      for morph in range(NMORPHS):
        bit,mode = getbits(bit,7,data)
	#print 'var %d: morph mode=%d' % (i, mode)
	if variation >= NVARIATIONS:
	  continue
        settings.morphs[morph].modes.variations[variation] = mode

    settinggroups = [
      [ 'patchvol', 'activemuted' ],
      [ 'glide', 'glidetime' ],
      [ 'bend', 'semi' ],
      [ 'vibrato', 'cents', 'rate' ],
      [ 'arpeggiator', 'arptime', 'arptype', 'octaves' ],
      [ 'octaveshift', 'sustain' ],
    ]
    for group in settinggroups:
      bit,section  = getbits(bit,8,data)
      bit,nentries = getbits(bit,7,data)
      for i in range(nvariations):
        bit, variation = getbits(bit, 8, data)
	for j in range(nentries):
          bit, value = getbits(bit, 7, data)
	  #print 'var %d: %s=%d' % (i, group[j], value)
	  if variation >= NVARIATIONS:
	    continue
	  getattr(settings, group[j]).variations[variation] = value
      
    return

    bit,section  = getbits(bit,8,data) # 2 for volume/active settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation

    for i in range(nvariations): # variation volume/active
      bit,variation = getbits(bit,8,data)
      bit,patchvol = getbits(bit,7,data)
      bit,activemuted = getbits(bit,7,data)
      if variation >= NVARIATIONS:
        continue
      settings.patchvol.variations[variation] = patchvol
      settings.activemuted.variations[variation] = activemuted

    bit,section  = getbits(bit,8,data) # 3 for glide/time settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation

    for i in range(nvariations): # variation glide
      bit,variation = getbits(bit,8,data)
      bit,settings.glide.variations[variation]     = getbits(bit,7,data)
      bit,settings.glidetime.variations[variation] = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 4 for bend/semi settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation

    for i in range(nvariations): # variation bend
      bit,variation = getbits(bit,8,data)
      bit,settings.bend.variations[variation] = getbits(bit,7,data)
      bit,settings.semi.variations[variation] = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 5 for vibrato/cents/rate settings
    bit,nentries = getbits(bit,7,data) # 3 parameters per variation

    for i in range(nvariations): # variation vibrato
      bit,variation = getbits(bit,8,data)
      bit,settings.vibrato.variations[variation] = getbits(bit,7,data)
      bit,settings.cents.variations[variation]   = getbits(bit,7,data)
      bit,settings.rate.variations[variation]    = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 6 for arp/time/type/octaves settings
    bit,nentries = getbits(bit,7,data) # 4 parameters per variation

    for i in range(nvariations): # variation arpeggiator
      bit,variation = getbits(bit,8,data)
      bit,settings.arpeggiator.variations[variation] = getbits(bit,7,data)
      bit,settings.arptime.variations[variation]     = getbits(bit,7,data)
      bit,settings.arptype.variations[variation]     = getbits(bit,7,data)
      bit,settings.octaves.variations[variation]     = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 7 for shift/sustain settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation
      
    for i in range(nvariations): # variation octave shift
      bit,variation = getbits(bit,8,data)
      bit,settings.octaveshift.variations[variation] = getbits(bit,7,data)
      bit,settings.sustain.variations[variation]     = getbits(bit,7,data)

  def format(self, patch):
    data = self.data
    settings   = patch.settings

    bit = setbits(0,2,data,self.area)
    bit = setbits(bit,8,data,7) # always 7
    bit = setbits(bit,8,data,NVARIATIONS)
    
    bit = setbits(bit,8,data,1)  # 1 for morph settings
    bit = setbits(bit,7,data,16) # 16 parameters per variation

    for variation in range(NVARIATIONS): # morph groups
      bit = setbits(bit,8,data,variation) # variation
      for morph in range(NMORPHS):
        bit = setbits(bit,7,data,settings.morphs[morph].dials.variations[variation])
      for morph in range(NMORPHS):
        bit = setbits(bit,7,data,settings.morphs[morph].modes.variations[variation])

    bit = setbits(bit,8,data,2) # 2 for volume/active settings
    bit = setbits(bit,7,data,2) # 2 parameters per variation

    for variation in range(NVARIATIONS):
      bit = setbits(bit,8,data,variation)
      bit = setbits(bit,7,data,settings.patchvol.variations[variation])
      bit = setbits(bit,7,data,settings.activemuted.variations[variation])

    bit = setbits(bit,8,data,3) # 3 for glide/time settings
    bit = setbits(bit,7,data,2) # 2 parameters per variation

    for variation in range(NVARIATIONS): # variation glide
      bit = setbits(bit,8,data,variation)
      bit = setbits(bit,7,data,settings.glide.variations[variation])
      bit = setbits(bit,7,data,settings.glidetime.variations[variation])

    bit = setbits(bit,8,data,4) # 4 for bend/semi settings
    bit = setbits(bit,7,data,2) # 2 parameters per variation

    for variation in range(NVARIATIONS): # variation bend
      bit = setbits(bit,8,data,variation)
      bit = setbits(bit,7,data,settings.bend.variations[variation])
      bit = setbits(bit,7,data,settings.semi.variations[variation])

    bit = setbits(bit,8,data,5) # 5 for vibrato/cents/rate settings
    bit = setbits(bit,7,data,3) # 3 parameters per variation

    for variation in range(NVARIATIONS): # variation vibrato
      bit = setbits(bit,8,data,variation)
      bit = setbits(bit,7,data,settings.vibrato.variations[variation])
      bit = setbits(bit,7,data,settings.cents.variations[variation])
      bit = setbits(bit,7,data,settings.rate.variations[variation])

    bit = setbits(bit,8,data,6) # 6 for arp/time/type/octaves settings
    bit = setbits(bit,7,data,4) # 4 parameters per variation

    for variation in range(NVARIATIONS): # variation arpeggiator
      bit = setbits(bit,8,data,variation)
      bit = setbits(bit,7,data,settings.arpeggiator.variations[variation])
      bit = setbits(bit,7,data,settings.arptime.variations[variation])
      bit = setbits(bit,7,data,settings.arptype.variations[variation])
      bit = setbits(bit,7,data,settings.octaves.variations[variation])

    bit = setbits(bit,8,data,7) # 7 for shift/sustain settings
    bit = setbits(bit,7,data,2) # 2 parameters per variation

    for variation in range(NVARIATIONS): # variation octave shift
      bit = setbits(bit,8,data,variation)
      bit = setbits(bit,7,data,settings.octaveshift.variations[variation])
      bit = setbits(bit,7,data,settings.sustain.variations[variation])

    return data[:(bit+7)>>3].tostring()

class ModuleParameters(Section):
  '''ModuleParameters Section subclass'''
  def parse(self, patch, data):
    bit,self.area   = getbits(0,2,data) # (0=fx,1=voice)
    bit,nmodules    = getbits(bit,8,data)
    bit,nvariations = getbits(bit,8,data) # if any modules=9, otherwise=0

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    for i in range(nmodules):
      bit,index = getbits(bit,8,data)
      m = area.findmodule(index)

      bit,nparams = getbits(bit,7,data)

      params = m.params
      mt = m.type
      for i in range(nvariations):
        bit,variation = getbits(bit,8,data)
        for param in range(nparams):
          if param < len(m.params):
            bit,params[param].variations[variation] = getbits(bit,7,data)
          else:
            bit,junk = getbits(bit,7,data)
            
  def format(self, patch):
    data = self.data

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    modules = []
    for i in range(len(area.modules)):
      if not hasattr(area.modules[i],'params'):
        continue
      elif not len(area.modules[i].params):
        continue
      modules.append(area.modules[i])
    modules.sort(lambda a,b: cmp(a.index,b.index))

    bit = setbits(0,2,data,self.area)
    bit = setbits(bit,8,data,len(modules))
    if not len(modules):
      bit = setbits(bit,8,data,0) # 0 variations
      return data[:(bit+7)>>3].tostring()
    bit = setbits(bit,8,data,NVARIATIONS)

    for i in range(len(modules)):
      m = modules[i]

      bit = setbits(bit,8,data,m.index)

      params = m.params
      bit = setbits(bit,7,data,len(params))
      for variation in range(NVARIATIONS):
        bit = setbits(bit,8,data,variation)
        for param in range(len(params)):
          bit = setbits(bit,7,data,params[param].variations[variation])

    return data[:(bit+7)>>3].tostring()

class MorphParameters(Section):
  '''MorphParameters Section subclass'''
  def parse(self, patch, data):
    bit,nvariations = getbits(0,8,data)
    bit,nmorphs     = getbits(bit,4,data)
    bit,reserved    = getbits(bit,10,data) # always 0
    bit,reserved    = getbits(bit,10,data) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs

    for i in range(nvariations):
      bit,variation = getbits(bit,4,data)
      bit += 4+(6*8)+4 # zeros

      bit, nmorphs = getbits(bit,8,data)
      for i in range(nmorphs):
        mmap = MorphMap()
        bit,area       = getbits(bit,2,data)
        bit,index      = getbits(bit,8,data)
        bit,param      = getbits(bit,7,data)
        bit,morph      = getbits(bit,4,data)
        bit,mmap.range = getbits(bit,8,data,1)
        if area:
          mmap.param = patch.voice.findmodule(index).params[param]
        else:
          mmap.param = patch.fx.findmodule(index).params[param]
        mmap.param.mmap = mmap
        mmap.morph = morphs[morph]
        morphs[morph].maps[variation].append(mmap)

      bit,reserved = getbits(bit,4,data) # always 0

  def format(self, patch):
    data = self.data

    bit = setbits(0,8,data,NVARIATIONS)
    bit = setbits(bit,4,data,NMORPHS)
    bit = setbits(bit,10,data,0) # always 0
    bit = setbits(bit,10,data,0) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs

    for variation in range(NVARIATIONS):
      bit = setbits(bit,4,data,variation)
      bit += 4+(6*8)+4 # zeros

      # collect all params of this variation into 1 array
      mparams = []
      for morph in range(len(morphs)):
        mparams.extend(morphs[morph].maps[variation])
      mparams.sort(lambda a,b: cmp(a.param.module.index,b.param.module.index))

      bit = setbits(bit,8,data,len(mparams))
      for i in range(len(mparams)):
        mparam = mparams[i]
        bit = setbits(bit,2,data,mparam.param.module.area.index)
        bit = setbits(bit,8,data,mparam.param.module.index)
        bit = setbits(bit,7,data,mparam.param.index)
        bit = setbits(bit,4,data,mparam.morph.index)
        bit = setbits(bit,8,data,mparam.range)

      bit = setbits(bit,4,data,0) # always 0

    bit -= 4
    return data[:(bit+7)>>3].tostring()

class KnobAssignments(Section):
  '''KnobAssignments Section subclass'''
  def parse(self, patch, data):
    bit,nknobs = getbits(0,16,data)
    patch.knobs = [ Knob() for i in range(nknobs)]
    perf = patch

    for i in range(nknobs):
      k = perf.knobs[i]
      bit,k.assigned = getbits(bit,1,data)
      if k.assigned:
        bit,area = getbits(bit,2,data)
        bit,index = getbits(bit,8,data)
        bit,k.isled = getbits(bit,2,data)
        bit,param = getbits(bit,7,data)
        if type(perf) == Performance:
          bit,k.slot = getbits(bit,2,data)
          patch = perf.patches[k.slot]
        else:
          k.slot = 0
        if area == 0:
          m = patch.fx.findmodule(index)
          if m:
            k.param = m.params[param]
          else:
            k.assigned = 0
            continue
        elif area == 1:
          m = patch.voice.findmodule(index)
          if m:
            k.param = m.params[param]
          else:
            k.assigned = 0
            continue
        elif area == 2:
          #printf('%d %d %d %d\n', area,index,k.isled,param)
          k.param = patch.settings.morphs[param]
        #printf('  %s%d-%d: %d %d\n', 'ABCDE'[i/24],(i%24)>>3,(i%24)&7, index,param)
        k.param.knob = k

  def format(self, patch):
    data = self.data
    perf = patch

    bit = setbits(0,16,data,NKNOBS)

    for i in range(NKNOBS):
      k = perf.knobs[i]
      bit = setbits(bit,1,data,k.assigned)
      if k.assigned:
        if hasattr(k.param,'module'):
          mod = k.param.module
          area,index,param=mod.area.index,mod.index,k.param.index
        else:
          area,index,param=2,1,k.param.index
        bit = setbits(bit,2,data,area)
        bit = setbits(bit,8,data,index)
        bit = setbits(bit,2,data,k.isled)
        bit = setbits(bit,7,data,param)
        if type(perf) == Performance:
          bit = setbits(bit,2,data,k.slot)

    return data[:(bit+7)>>3].tostring()

class CtrlAssignments(Section):
  '''CtrlAssignments Section subclass'''
  def parse(self, patch, data):
    bit,nctrls  = getbits(0,7,data)
    patch.ctrls = [ Ctrl() for i in range(nctrls)]

    for i in range(nctrls):
      m = patch.ctrls[i]
      bit,m.midicc = getbits(bit,7,data)
      bit,m.type = getbits(bit,2,data) # 0:FX, 1:Voice, 2:System/Morph
      bit,index = getbits(bit,8,data)
      bit,param = getbits(bit,7,data)
      if m.type == 0:
        m.param = patch.fx.findmodule(index).params[param]
      elif m.type == 1:
        m.param = patch.voice.findmodule(index).params[param]
      elif m.type == 2:
        m.param = patch.settings.morphs[index]
      m.param.ctrl = m

  def format(self, patch):
    data = self.data

    bit = setbits(0,7,data,len(patch.ctrls))

    for i in range(len(patch.ctrls)):
      m = patch.ctrls[i]
      bit = setbits(bit,7,data,m.midicc)
      bit = setbits(bit,2,data,m.type)
      if m.type < 2:
        index,param = m.param.module.index,m.param.index
      else:
        index,param = m.param.index,0
      bit = setbits(bit,8,data,index)
      bit = setbits(bit,7,data,param)

    return data[:(bit+7)>>3].tostring()

class MorphLabels(Section):
  '''MorphLabels Section subclass'''
  def parse(self, patch, data):
    bit,self.area = getbits(0,2,data)   # 0=fx,1=voice,2=morph

    #b = bit
    #s = ''
    #while b/8 < len(data):
    #  b,c = getbits(b,8,data)
    #  s += chr(c)
    #printf('morphlabels:\n')
    #printf('%s\n',hexdump(s))

    bit,nentries  = getbits(bit,8,data) # 1
    bit,entry     = getbits(bit,8,data) # 1
    bit,length    = getbits(bit,8,data) # 0x50

    for i in range(NMORPHS):
      bit,morph    = getbits(bit,8,data)
      bit,morphlen = getbits(bit,8,data)
      bit,entry    = getbits(bit,8,data)
      morphlen -= 1
      s = ''
      for l in range(morphlen):
        bit, c = getbits(bit,8,data)
        if c != 0:
          s += chr(c&0xff)
      patch.settings.morphs[i].label = s

  def format(self, patch):
    data = self.data

    bit = setbits(  0,2,data,2)    # 0=fx,1=voice,2=morph

    t = '\1\1\x50'
    for morph in range(NMORPHS):
      t += ''.join(map(chr, [1,8,8+morph]))
      s = patch.settings.morphs[morph].label[:7]
      s += '\0' * (7-len(s))
      for i in range(len(s)):
        t += s[i]
        #bit = setbits(bit,8,data,ord(s[i]))

    #printf('morphlabels:\n')
    #printf('%s\n', hexdump(t))

    for c in t:
      bit = setbits(bit,8,data,ord(c))

    return data[:(bit+7)>>3].tostring()

class ParameterLabels(Section):
  '''ParameterLabels Section subclass'''
  def parse(self, patch, data):

    bit, self.area = getbits(0,2,data) # 0=fx,1=voice,2=morph
    bit, nmodules = getbits(bit,8,data)

    if sectiondebug:
      b = bit
      s = chr(nmodules)
      while b/8 < len(data):
	b,c = getbits(b,8,data)
	s += chr(c)
      printf('paramlabels:\n')
      printf('%s\n', hexdump(s))

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    for mod in range(nmodules):

      bit,index = getbits(bit,8,data)
      m = area.findmodule(index)

      bit,modlen   = getbits(bit,8,data)
      if m.type.type == 121: # SeqNote
        # extra editor parameters 
        # [0, 1, mag, 0, 1, octave]
        # view: 0=3-octaves,1=2-octaves,2=1-octave
        # octave: 0-9 (c0-c9)
        m.editmodes = []
        for i in range(modlen):
          bit,c = getbits(bit,8,data)
          m.editmodes.append(c)
        continue
      while modlen > 0:
        bit,str      = getbits(bit,8,data) 
        bit,paramlen = getbits(bit,8,data)
        bit,param    = getbits(bit,8,data)
        modlen -= 3

        p = m.params[param]
        p.labels = []

        paramlen -= 1 # decrease because we got param index
        if paramlen:
          for i in range(paramlen/7):
            s = ''
            for i in range(7):
              bit,c = getbits(bit,8,data) # grab 3 chars
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

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    modules = []
    # collect all modules with parameters that have labels
    for i in range(len(area.modules)):
      m = area.modules[i]
      if hasattr(m,'params'):
        for j in range(len(m.params)):
          if hasattr(m.params[j],'labels'):
            modules.append(m)
            break
      if hasattr(m,'editmodes'):
        modules.append(m)

    bit = setbits(0,2,data, self.area) # 0=fx,1=voice,2=morph

    t = chr(len(modules))
    for mod in range(len(modules)):

      m = modules[mod]

      s = ''
      if m.type.type == 121: # SeqNote
        for ep in m.editmodes:
          s += chr(ep)
      else:
        # build up the labels and then write them
        pc = 0
        for i in range(len(m.params)):
          param = m.params[i]
          if not hasattr(param,'labels'):
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
      bit = setbits(bit,8,data,ord(c))

    return data[:(bit+7)>>3].tostring()

class ModuleNames(Section):
  '''ModuleNames Section subclass'''
  def parse(self, patch, data):
    bit,self.area = getbits(0,2,data)
    bit,self.unk1 = getbits(bit,6,data)
    bit,nmodules = getbits(bit,8,data)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

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

    bit = setbits(0,2,data,self.area)
    bit = setbits(bit,6,data,self.area) # seems to be duplicate of area
    # finish paring
    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    bit = setbits(bit,8,data,len(area.modules)) # unknown, see if zero works
    for i in range(len(area.modules)):
      bit = setbits(bit,8,data,area.modules[i].index)
      nm = area.modules[i].name[:16]
      #printf('%d "%s"\n', area.modules[i].index, nm)
      if len(nm) < 16:
        nm += '\0'
      for c in nm:
        bit = setbits(bit,8,data,ord(c))

    return data[:(bit+7)>>3].tostring()

class TextPad(Section):
  '''TextPad Section subclass'''
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
    PatchDescription(type=0x21),
    ModuleList(type=0x4a,area=1),
    ModuleList(type=0x4a,area=0),
    CurrentNote(type=0x69),
    CableList(type=0x52,area=1),
    CableList(type=0x52,area=0),
    PatchSettings(type=0x4d,area=2),
    ModuleParameters(type=0x4d,area=1),
    ModuleParameters(type=0x4d,area=0),
    MorphParameters(type=0x65),
    KnobAssignments(type=0x62),
    CtrlAssignments(type=0x60),
    MorphLabels(type=0x5b,area=2),
    ParameterLabels(type=0x5b,area=1),
    ParameterLabels(type=0x5b,area=0),
    ModuleNames(type=0x5a,area=1),
    ModuleNames(type=0x5a,area=0),
    TextPad(type=0x6f),
  ]
  standardtxthdr = '''Version=Nord Modular G2 File Format 1\r
Type=%s\r
Version=%d\r
Info=BUILD %d\r
\0'''
  standardbinhdr = 23
  standardbuild = 266
  def __init__(self, fname=None):
    self.type = 'Patch'
    self.binrev = 0
    self.patch = Patch(fromname)
    if fname:
      self.read(fname)

  def parsepatch(self, patch, data, off):
    for section in Pch2File.patchsections:
      sectiontype,l = struct.unpack('>BH',data[off:off+3])
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
  def read(self, fname):
    self.fname = fname
    data = open(fname,'rb').read()
    null = data.find('\0')
    if null < 0:
      raise G2Error('Invalid G2File "%s" missing null terminator.' % fname)
    self.txthdr = data[:null]
    off = null+1
    self.binhdr = struct.unpack('BB',data[off:off+2])
    if self.binhdr[0] != self.standardbinhdr:
      printf('Warning: %s version %d\n', fname, self.binhdr[0])
      printf('         version %d supported. it may fail to load.\n',
          self.standardbinhdr)
    off += 2
    off = self.parse(data, off)

    ecrc = struct.unpack('>H',data[-2:])[0]
    acrc = crc(data[null+1:-2])
    if ecrc != acrc:
      printf('Bad CRC\n')

  def formatpatch(self, patch):
    s = ''
    for section in Pch2File.patchsections:
      section.data[:] = zeros[:]
      f = section.format(patch)
      if sectiondebug:
        nm = section.__class__.__name__
        printf('0x%02x %-25s len:0x%04x total: 0x%04x\n',
            section.type,nm,len(f),self.off+len(s))
        tbl = string.maketrans(string.ascii_lowercase,' '*26)
        nm = nm.translate(tbl).replace(' ','')
        printf('%s\n', nm)
        if titlesection:
          l = len(nm)
          if l < len(f):
            #f = f[:-len(nm)]+nm # debug for front of section or back
            f = nm+f[len(nm):]
      s += struct.pack('>BH',section.type,len(f)) + f
    return s

  def format(self):
    return self.formatpatch(self.patch)

  # write - this looks a lot easier then read ehhhh???
  def write(self, fname=None):
    out = open(fname,'wb')
    hdr = Pch2File.standardtxthdr % (self.type,
        self.standardbinhdr, self.standardbuild)
    self.off = len(hdr)
    s = struct.pack('BB',Pch2File.standardbinhdr,self.binrev)
    self.off += len(s)
    s += self.format()
    out.write(hdr + s)
    out.write(struct.pack('>H',crc(s)))

class PerformanceDescription(Section):
  '''PerformanceDescription Section subclass'''
  def parse(self, perf, data):
    desc = perf.description = Description()

    bit,desc.unk1     = getbits(0,8,data)
    bit,desc.hold     = getbits(bit,1,data)
    bit,desc.unk2     = getbits(bit,7,data)
    bit,desc.rangesel = getbits(bit,8,data)
    bit,desc.rate     = getbits(bit,8,data)
    bit,desc.unk3     = getbits(bit,8,data)
    bit,desc.clock    = getbits(bit,8,data)
    bit,desc.unk4     = getbits(bit,8,data)
    bit,desc.unk5     = getbits(bit,8,data)

    patches = desc.patches = [ Description() for i in range(4) ] 
    for i in range(4):
      patch = patches[i]
      pdata = data[bit/8:]
      null = pdata.find('\0')
      if null < 0 or null > 16:
        null = 16
      else:
        null += 1
      patch.name = pdata[:null].replace('\0','')
      bit += null*8
      bit,patch.unk1     = getbits(bit,8,data)
      bit,patch.active   = getbits(bit,8,data)
      bit,patch.keyboard = getbits(bit,8,data)
      bit,patch.keyhold  = getbits(bit,8,data)
      bit,patch.unk2     = getbits(bit,16,data)
      bit,patch.keylow   = getbits(bit,8,data)
      bit,patch.keyhigh  = getbits(bit,8,data)
      bit,patch.unk3     = getbits(bit,8,data)
      bit,patch.unk4     = getbits(bit,8,data)

  def format(self, perf):
    data = self.data
    desc = perf.description

    bit = setbits(0,8,data,desc.unk1)
    bit = setbits(bit,1,data,desc.hold)
    bit = setbits(bit,7,data,desc.unk2)
    bit = setbits(bit,8,data,desc.rangesel)
    bit = setbits(bit,8,data,desc.rate)
    bit = setbits(bit,8,data,desc.unk3)
    bit = setbits(bit,8,data,desc.clock)
    bit = setbits(bit,8,data,desc.unk4)
    bit = setbits(bit,8,data,desc.unk5)

    patches = desc.patches
    for i in range(4):
      patch = patches[i]
      nm = patch.name
      if len(nm) < 16:
        nm += '\0'
      for c in nm[:16]:
        bit = setbits(bit,8,data,ord(c))
      bit = setbits(bit,8,data,patch.unk1)
      bit = setbits(bit,8,data,patch.active)
      bit = setbits(bit,8,data,patch.keyboard)
      bit = setbits(bit,8,data,patch.keyhold)
      bit = setbits(bit,16,data,patch.unk2)
      bit = setbits(bit,8,data,patch.keylow)
      bit = setbits(bit,8,data,patch.keyhigh)
      bit = setbits(bit,8,data,patch.unk3)
      bit = setbits(bit,8,data,patch.unk4)

    last = (bit+7)>>3
    return data[:last].tostring()

class Prf2File(Pch2File):
  '''Prf2File(filename) -> load a nord modular g2 performance.'''
  def __init__(self, fname=None):
    self.type = 'Performance'
    self.binrev = 1
    self.performance = Performance(fromname)
    self.perfsection = PerformanceDescription(type=0x11)
    self.globalsection = KnobAssignments(type=0x5f)
    if fname:
      self.read(fname)

  def parsesection(self, section, data, off):
    id,l = struct.unpack('>BH',data[off:off+3])
    off += 3
    if sectiondebug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s addr:0x%04x len:0x%04x\n', id,nm,off,l)

    section.parse(self.performance, data[off:off+l])
    off += l
    return off

  def parse(self, data, off):
    off = self.parsesection(self.perfsection, data, off)
    for i in range(4):
      off = self.parsepatch(self.performance.patches[i], data, off)
    off = self.parsesection(self.globalsection, data, off)
    return off

  def formatsection(self, section, total=0):
    section.data[:] = zeros[:]
    f = section.format(self.performance)
    if sectiondebug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s             len:0x%04x total: 0x%04x\n',
          section.type,nm,len(f),total)
      if titlesection:
        tbl = string.maketrans(string.ascii_lowercase,' '*26)
        nm = nm.translate(tbl).replace(' ','')
        l = len(nm)
        if l < len(f):
          f = f[:-len(nm)]+nm
    return struct.pack('>BH',section.type,len(f)) + f

  def format(self):
    s = self.formatsection(self.perfsection)
    for i in range(4):
      s += self.formatpatch(self.performance.patches[i])
    s += self.formatsection(self.globalsection,len(s))
    return s

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
  fname = sys.argv.pop(0)
  printf('"%s"\n', fname)
  pch2 = Pch2File(fname)
  #pch2.write(sys.argv.pop(0))

