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
  s192 = 'AAAAAAACEEEEIIIIDNOOOOOOXOUUUUYpBaaaaaaaceeeeeiiiienooooo/ouuuuypy'
  def conv(c):
    o = ord(c)
    if o >= 192:
      return s192[o-192]
    elif o < 128:
      return c
    return ''
  return ''.join(map(conv, s))

# setv - set all variations to val
def setv(g2param,val):
  g2param.variations = [ val for variation in range(9) ]

# getv - get variation[0]
def getv(nmparam):
  return nmparam.variations[0]

# setav - set variations from array
def setav(g2param,array):
  g2param.variations = array[:9]

# cpv - copy variations 
def cpv(g2param,nmparam):
  g2param.variations = nmparam.variations[:]

# isnm1osc - is NM1 module an oscillator
def isnm1osc(module):
  shortnms = ['OscMaster','OscA','OscB','OscC',
              'OscSlvB','OscSlvC','OscSlvD','OscSlvE','OscSlvA','OscSlvFM',
              'PercOsc','FormantOsc','SpectralOsc','MasterOsc','OscSineBank']
  return module.type.shortnm in shortnms

# isnm1lfo - is NM1 module an lfo
def isnm1lfo(module):
  shortnms = ['LFOA','LFOB','LFOC',
              'LFOSlvB','LFOSlvC','LFOSlvD','LFOSlvE','LFOSlvF','ClkGen']
  return module.type.shortnm in shortnms
