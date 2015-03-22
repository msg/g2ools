#
# utils.py - misc util functions
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

# toascii remove bad characters
def toascii(s):
  # conversion strings for 192-255
  s161 = '!cL#Y|S"Ca<^-R-o+23\'uP.10>%%%?' \
         'AAAAAAACEEEEIIIIDNOOOOOOXOUUUUYpBaaaaaaaceeeeeiiiienooooo/ouuuuypy'
  def conv(c):
    o = ord(c)
    if o < 128:
      return c
    elif o < 161:
      return chr(c-64)
    else:
      return s161[o-161]
    return ''
  return ''.join([ conv(c) for c in s ])

def setv(g2param, val):
  '''setv(g2param, val) - set all variations to val.'''
  g2param.variations = [ val ] * 9

def getv(nmparam, variation=0):
  '''getv(nmparam) - get variations[variation].'''
  return nmparam.variations[variation]

def setav(g2param, array):
  '''setv(g2param, array) - set variations from array.'''
  g2param.variations = array[:9]

def cpv(g2param, nmparam):
  '''cpy(g2param, nmparam) - copy variations.'''
  g2param.variations = nmparam.variations[:]

def isnm1osc(module):
  '''isnm1osc(module) - is NM1 module an oscillator'''
  shortnms = ['OscMaster', 'OscA', 'OscB', 'OscC', 'OscSlvB', 'OscSlvC',
              'OscSlvD', 'OscSlvE', 'OscSlvA', 'OscSlvFM', 'PercOsc',
              'FormantOsc', 'SpectralOsc', 'MasterOsc', 'OscSineBank']
  return module.type.shortnm in shortnms

def isnm1lfo(module):
  '''isnm1lfo(module) - is NM1 module an lfo.'''
  shortnms = ['LFOA', 'LFOB', 'LFOC',
              'LFOSlvB', 'LFOSlvC', 'LFOSlvD', 'LFOSlvE', 'LFOSlvF', 'ClkGen']
  return module.type.shortnm in shortnms
