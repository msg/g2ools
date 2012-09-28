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

import struct
from array import array

# number format for getbits() and setbits()
# b       b       b       b
# 0       1       2       3
# 01234567012345670123456701234567
# m      lm      lm      lm      l
# b: byte
# m: msb
# l: lsb

def getbits(bit, nbits, data, signed=0):
  '''getbits(bit, nbits, data, signed=0) - return int as subset of string data.
  the values are formatted in big-endiann:
  0 is msb, 31 is lsb for a 32-bit word.
'''

  def getbits_(x, p, n):
    return (x >> p) & ~(~0<<n)
  # grab 32-bits starting with the byte that contains bit
  byte = bit >> 3
  # align size to a 32-bit word
  long_ = struct.unpack('>L', (data[byte:byte+4]+'\x00'*4)[:4])[0]
  val = getbits_(long_, 32-(bit&7)-nbits, nbits)
  if signed and (val>>(nbits-1)):
    val |= ~0 << nbits
  return bit+nbits, int(val)

def setbits(bit, nbits, data, value):
  '''setbits(bit, nbits, data, value) - set bits in subset
  of string data from int.
'''
  def setbits_(x, p, n, y):
    m = ~(~0<<n)
    return (x&~(m<<p))|((m&y)<<p)
  # grab 32-bits starting with the byte that contains bit
  byte = bit >> 3
  last = (bit+nbits+7)>>3
  s = data[byte:byte+4].tostring()
  # align size to a 32-bit word
  long_ = setbits_(struct.unpack('>L', s)[0], 32-(bit&7)-nbits, nbits, value)
  # readjust array to fit (bits+nbits)/8 bytes
  a = array('B', struct.pack('>L', long_)[:last-byte])
  #printf('bit=%d nbits=%d byte=%d last=%d last-byte+1=%d len=%d len(a)=%d\n',
  #   bit, nbits, byte, last, last-byte, len(data), len(a))
  data[byte:last] = a
  #printf('%s\n', data)
  return bit+nbits

class BitStream(object):
  def __init__(self, data):
    self.data = data
    self.bit = 0

  def setup(self, bit=0, data=None):
    self.bit = bit
    if data:
      self.data = data

  def read_bits(self, nbits):
    self.bit, value = getbits(self.bit, nbits, self.data)
    return value

  def read_bitsa(self, nbitsa):
    return [ self.read_bits(nbits) for nbits in nbitsa ]

  def write_bits(self, nbits, value):
    self.bit = setbits(self.bit, nbits, self.data, value)

  def write_bitsa(self, nbitsa, values):
    for nbits, value in zip(nbitsa, values):
      self.write_bits(nbits, value)

  def string(self):
    return str(self.data[:(self.bit+7)>>3])

try:
  from nord.g2._bits import setbits, getbits, BitStream
except:
  pass

