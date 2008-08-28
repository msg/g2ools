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
from modules import fromname
from nord.file import *
import modules

sectiondebug = 0 # outputs section debug 
titlesection = 0 # replace end of section with section title

# calculate crc of 1 char
def crc16(val, icrc):
  k = (((icrc>>8)^val)&0xff)<<8
  crc = 0
  for bits in range(8):
    if (crc^k)&0x8000 != 0:
      crc = (crc<<1)^0x1021
    else:
      crc <<= 1
    k <<= 1
  return (icrc<<8)^crc

# calculate crc of whole string
def crc(s):
  return  reduce(lambda a,b: crc16(ord(b),a),s,0) & 0xffff

# calculated via:
# ./pycrc.py --model zmodem --algorithm table-driven --table-idx-width 8 \
#     --generate c -o crc.c
crctab = [
  0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
  0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
  0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
  0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
  0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
  0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
  0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
  0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
  0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
  0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
  0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
  0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
  0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
  0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
  0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
  0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
  0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
  0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
  0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
  0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
  0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
  0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
  0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
  0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
  0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
  0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
  0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
  0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
  0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
  0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
  0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
  0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]

def crc(s):
  #crc = 0
  #for c in s:
  #  crc = (crctab[((crc>>8)^c)&0xff] ^ (crc << 8)) & 0xffff
  #return crc
  return reduce(lambda crc,c: (crctab[((crc>>8)^ord(c))&0xff]^(crc << 8)),s,0)&0xffff

# number format for getbits() and setbits()
# b       b       b       b
# 0       1       2       3
# 01234567012345670123456701234567
# m      lm      lm      lm      l
# b: byte
# m: msb
# l: lsb

# getbits - return int as subset of string data
# the values are formatted in big-endiann:
#   0 is msb, 31 is lsb for a 32-bit word

def getbits(bit,nbits,data,signed=0):
  def getbits(x, p, n):
    return (x >> p) & ~(~0<<n)
  # grab 32-bits starting with the byte that contains bit
  byte = bit>>3
  # align size to a 32-bit word
  long = struct.unpack('>L',(data[byte:byte+4]+'\x00'*4)[:4])[0]
  val = getbits(long,32-(bit&7)-nbits,nbits)
  if signed and (val>>(nbits-1)):
    val |= ~0 << nbits
  return bit+nbits,int(val)

# setbits - set bits in subset of string data from int
def setbits(bit,nbits,data,value,debug=0):
  def setbits(x, p, n, y):
    m = ~(~0<<n)
    return (x&~(m<<p))|((m&y)<<p)
  # grab 32-bits starting with the byte that contains bit
  byte = bit>>3
  last = (bit+nbits+7)>>3
  s = data[byte:byte+4].tostring()
  # align size to a 32-bit word
  long = setbits(struct.unpack('>L',s)[0],32-(bit&7)-nbits,nbits,value)
  # readjust array to fit (bits+nbits)/8 bytes
  a = array('B',struct.pack('>L',long)[:last-byte])
  #print 'bit=%d nbits=%d byte=%d last=%d last-byte+1=%d len=%d len(a)=%d' % (
  #   bit,nbits,byte,last,last-byte,len(data),len(a))
  data[byte:last] = a
  #print data
  return bit+nbits

try:
  from nord.g2.bits import crc,setbits,getbits
except:
  pass

NVARIATIONS = 9 # 1-8, init
NMORPHS = 8     # 8 morphs
NKNOBS = 120    # 120 knob settings

# exception for throwing when there is an unrecoverable error
class NordG2Error(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

# Struct - generic class for creating named variables in objects
# i.e. s = Struct(one=1,two=2,three=3,...)
#      contains: s.one, s.two, s.three
class Struct(object):
  def __init__(self, **kw):
    self.__dict__ = kw

# Section - generic class that represents a section of .pch2 file.
#   all sections contain parse() and format() methods.
zeros = array('B', [0] * (64<<10))
class Section(Struct):
  def __init__(self, **kw):
    super(Section,self).__init__(**kw)
    self.data = zeros[:]

# holder object for patch/performance description
class Description(object):
  pass

# PatchDescription - section object for parse/format 
class PatchDescription(Section):
  def parse(self, patch, data):
    desc = patch.description = Description()

    bit,desc.reserved  = getbits(7*8,5,data)
    bit,desc.voicecnt  = getbits(bit,5,data)
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
    bit = setbits(bit,5,data,desc.voicecnt)
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

# ModuleList - section object for parse/format 
class ModuleList(Section):
  def parse(self, patch, data):
    bit,self.area = getbits(0,2,data)
    bit,modulecnt = getbits(bit,8,data)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    area.modules = [ None ] * modulecnt
    for i in range(modulecnt):
      #m = area.modules[i]
      bit,type       = getbits(bit,8,data)
      m = Module(modules.fromtype[type],area)
      area.modules[i] = m
      #m.type = modules.fromtype[type] # use type object instead of number
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

      #print 'modules %-10s t=%03d i=%02x h=%d v=%02d c=%02d r=%x l=%x s=%02x m=%x' % (
      #    modules.fromtype[m.type].shortnm, m.type, m.ndex,
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

# CurrentNote - section object for parse/format
class CurrentNote(Section):
  def parse(self, patch, data):
    lastnote = patch.lastnote = Note()
    bit, lastnote.note    = getbits(0,7,data)
    bit, lastnote.attack  = getbits(bit,7,data)
    bit, lastnote.release = getbits(bit,7,data)
    bit, notecnt          = getbits(bit,5,data)
    notes = patch.notes = [ Note() for i in range(notecnt+1) ]
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


# validatecable - if connection valid return 0, otherwise error
def validcable(area, smodule, sconn, direction, dmodule, dconn):

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

# CableList - section object for parse/format 
class CableList(Section):
  def parse(self, patch, data):

    bit,self.area = getbits(0,2,data)
    bit,cablecnt  = getbits(8,16,data)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    area.cables = [ None ] * cablecnt
    for i in range(cablecnt):
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
        print 'Invalid cable %d: "%s"(%d,%d) -%d-> "%s"(%d,%d)' % (
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
      #print '%d %02d %d -%d- %02d %d' % (c.color, c.source.module.index,
      #    c.source.index, c.source.direction, c.dest.module.index, c.dest.index)
      bit = setbits(bit,3,data,c.color)
      bit = setbits(bit,8,data,c.source.module.index)
      bit = setbits(bit,6,data,c.source.index)
      bit = setbits(bit,1,data,c.source.direction)
      bit = setbits(bit,8,data,c.dest.module.index)
      bit = setbits(bit,6,data,c.dest.index)

    return data[:(bit+7)>>3].tostring()

# holder object for module parameters/settings
class Parameter(object):
  def __init__(self,default=0):
    self.variations = [default]*NVARIATIONS
    self.knob = None
    self.mmap = None
    self.ctrl = None

# holder object for morph settings
class Morph(object):
  def __init__(self,index):
    self.dials = Parameter(0)
    self.modes = Parameter(1)
    self.params = []
    self.maps = [[] for variation in range(NVARIATIONS) ]
    self.index = index
    self.ctrl = None

# holder for patch settings
class Settings(object):
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

# PatchSettings - section object for parse/format 
class PatchSettings(Section):
  def parse(self, patch, data):
    settings = patch.settings = Settings()

    bit,self.area   = getbits(0,2,data)   # always 2 (0=fx,1=voice,2=settings)
    bit,sectioncnt  = getbits(bit,8,data) # always 7
    bit,nvariations = getbits(bit,8,data) # always 9

    bit,section  = getbits(bit,8,data) # 1 for morph settings
    bit,nentries = getbits(bit,7,data) # 16 parameters per variation

    for i in range(NVARIATIONS): # morph groups
      bit,variation = getbits(bit,8,data) # variation number
      for morph in range(NMORPHS):
        bit,settings.morphs[morph].dials.variations[variation] = getbits(bit,7,data)
      for morph in range(NMORPHS):
        bit,settings.morphs[morph].modes.variations[variation] = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 2 for volume/active settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation

    for i in range(NVARIATIONS): # variation volume/active
      bit,variation = getbits(bit,8,data)
      bit,settings.patchvol.variations[variation]    = getbits(bit,7,data)
      bit,settings.activemuted.variations[variation] = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 3 for glide/time settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation

    for i in range(NVARIATIONS): # variation glide
      bit,variation = getbits(bit,8,data)
      bit,settings.glide.variations[variation]     = getbits(bit,7,data)
      bit,settings.glidetime.variations[variation] = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 4 for bend/semi settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation

    for i in range(NVARIATIONS): # variation bend
      bit,variation = getbits(bit,8,data)
      bit,settings.bend.variations[variation] = getbits(bit,7,data)
      bit,settings.semi.variations[variation] = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 5 for vibrato/cents/rate settings
    bit,nentries = getbits(bit,7,data) # 3 parameters per variation

    for i in range(NVARIATIONS): # variation vibrato
      bit,variation = getbits(bit,8,data)
      bit,settings.vibrato.variations[variation] = getbits(bit,7,data)
      bit,settings.cents.variations[variation]   = getbits(bit,7,data)
      bit,settings.rate.variations[variation]    = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 6 for arp/time/type/octaves settings
    bit,nentries = getbits(bit,7,data) # 4 parameters per variation

    for i in range(NVARIATIONS): # variation arpeggiator
      bit,variation = getbits(bit,8,data)
      bit,settings.arpeggiator.variations[variation] = getbits(bit,7,data)
      bit,settings.arptime.variations[variation]     = getbits(bit,7,data)
      bit,settings.arptype.variations[variation]     = getbits(bit,7,data)
      bit,settings.octaves.variations[variation]     = getbits(bit,7,data)

    bit,section  = getbits(bit,8,data) # 7 for shift/sustain settings
    bit,nentries = getbits(bit,7,data) # 2 parameters per variation
      
    for i in range(NVARIATIONS): # variation octave shift
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

# ModuleParameters - section object for parse/format 
class ModuleParameters(Section):
  def parse(self, patch, data):
    bit,self.area   = getbits(0,2,data) # (0=fx,1=voice)
    bit,modulecnt   = getbits(bit,8,data)
    bit,nvariations = getbits(bit,8,data) # if any modules=9, otherwise=0

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    for i in range(modulecnt):
      bit,index = getbits(bit,8,data)
      m = area.findmodule(index)

      bit,paramcnt = getbits(bit,7,data)

      params = m.params
      mt = m.type
      for i in range(nvariations):
        bit,variation = getbits(bit,8,data)
        for param in range(paramcnt):
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

# MorphParameters - section object for parse/format 
class MorphParameters(Section):
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

# KnobAssignments - section object for parse/format 
class KnobAssignments(Section):
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
	  #print area,index,k.isled,param
	  k.param = patch.settings.morphs[param]
	#print '  %s%d-%d: %d %d' % ('ABCDE'[i/24],(i%24)>>3,(i%24)&7, index,param)
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

# CtrlMap - section object for parse/format 
class CtrlAssignments(Section):
  def parse(self, patch, data):
    bit,ctrlcnt = getbits(0,7,data)
    patch.ctrls = [ Ctrl() for i in range(ctrlcnt)]

    for i in range(ctrlcnt):
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

# MorphLabels - section object for parse/format 
class MorphLabels(Section):
  def parse(self, patch, data):
    bit,self.area = getbits(0,2,data)   # 0=fx,1=voice,2=morph

    #b = bit
    #s = ''
    #while b/8 < len(data):
    #  b,c = getbits(b,8,data)
    #  s += chr(c)
    #print 'morphlabels:'
    #print hexdump(s)

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

    #print 'morphlabels:'
    #print hexdump(t)

    for c in t:
      bit = setbits(bit,8,data,ord(c))

    return data[:(bit+7)>>3].tostring()

# ParameterLabels - section object for parse/format 
class ParameterLabels(Section):
  def parse(self, patch, data):

    bit, self.area = getbits(0,2,data) # 0=fx,1=voice,2=morph
    bit, modulecnt = getbits(bit,8,data)

    #b = bit
    #s = chr(modulecnt)
    #while b/8 < len(data):
    #  b,c = getbits(b,8,data)
    #  s += chr(c)
    #print 'paramlabels:'
    #print hexdump(s)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    for mod in range(modulecnt):

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
        #print index, paramlen, param, p.labels

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
          #print m.index,7*len(param.labels),i,param.labels
          ps = ''
          for nm in param.labels:
            ps += (nm+'\0'*7)[:7]
          ps = chr(i)+ps
          ps = chr(1)+chr(len(ps))+ps
          s += ps

      t += chr(m.index) + chr(len(s)) + s

    #print 'paramlabels:'
    #print hexdump(t)

    for c in t:
      bit = setbits(bit,8,data,ord(c))

    return data[:(bit+7)>>3].tostring()

# ModuleNames - section object for parse/format 
class ModuleNames(Section):
  def parse(self, patch, data):
    bit,self.area = getbits(0,2,data)
    bit,self.unk1 = getbits(bit,6,data)
    bit,modulecnt = getbits(bit,8,data)

    if self.area:
      area = patch.voice
    else:
      area = patch.fx

    names = data[bit/8:]
    for i in range(modulecnt):
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
      #print '%d "%s"' % (area.modules[i].index, nm)
      if len(nm) < 16:
        nm += '\0'
      for c in nm:
        bit = setbits(bit,8,data,ord(c))

    return data[:(bit+7)>>3].tostring()

# TextPad - section object for parse/format 
class TextPad(Section):
  def parse(self, patch, data):
    patch.textpad = data

  def format(self, patch):
    return patch.textpad

# Pch2File - main reading/writing object for .pch2 files
#   this may become generic G2 file for .pch2 and .prf2 files
#   just by handling the performance sections (and perhaps others)
#   and parsing all 4 patches within the .prf2 file.
class Pch2File(object):
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
Version=23\r
Info=BUILD 266\r
\0'''
  standardbinhdr = 23
  def __init__(self, fname=None):
    self.type = 'Patch'
    self.binrev = 0
    self.patch = Patch(fromname)
    if fname:
      self.read(fname)

  def parsepatch(self, patch, data, off):
    for section in Pch2File.patchsections:
      id,l = struct.unpack('>BH',data[off:off+3])
      off += 3
      if sectiondebug:
	nm = section.__class__.__name__
	print '0x%02x %-25s addr:0x%04x len:0x%04x' % (id,nm,off,l)
        print binhexdump(data[off:off+l])
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
      raise 'Invalid G2File "%s" missing null terminator.' % fname
    self.txthdr = data[:null]
    off = null+1
    self.binhdr = struct.unpack('BB',data[off:off+2])
    if self.binhdr[0] != self.standardbinhdr:
      print 'Warning: %s version %d' % ( fname, self.binhdr[0])
      print '         version %d supported. it may fail to load.' % (
      	  self.standardbinhdr)
    off += 2
    off = self.parse(data, off)

    ecrc = struct.unpack('>H',data[-2:])[0]
    acrc = crc(data[null+1:-2])
    if ecrc != acrc:
      print 'Bad CRC'

  def formatpatch(self, patch):
    s = ''
    for section in Pch2File.patchsections:
      section.data[:] = zeros[:]
      f = section.format(patch)
      if sectiondebug:
	nm = section.__class__.__name__
	print '0x%02x %-25s len:0x%04x total: 0x%04x' % (
	   section.type,nm,len(f),self.off+len(s)),
	tbl = string.maketrans(string.ascii_lowercase,' '*26)
	nm = nm.translate(tbl).replace(' ','')
	print nm
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
    hdr = Pch2File.standardtxthdr % self.type
    self.off = len(hdr)
    s = struct.pack('BB',Pch2File.standardbinhdr,self.binrev)
    self.off += len(s)
    s += self.format()
    out.write(hdr + s)
    out.write(struct.pack('>H',crc(s)))

class PerformanceDescription(Section):
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
      print '0x%02x %-25s addr:0x%04x len:0x%04x' % (id,nm,off,l)

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
      print '0x%02x %-25s             len:0x%04x total: 0x%04x' % (
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
#     desc.voicecnt
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
  print '"%s"' % fname
  pch2 = Pch2File(fname)
  #pch2.write(sys.argv.pop(0))

