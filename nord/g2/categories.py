#
# categories.py - g2 category definitions
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
G2Categories = {
  0: 'No Cat',
  1: 'Acoustic',
  2: 'Sequencer',
  3: 'Bass',
  4: 'Classic',
  5: 'Drum',
  6: 'Fantasy',
  7: 'FX',
  8: 'Lead',
  9: 'Organ',
  10: 'Pad',
  11: 'Piano',
  12: 'Synth',
  13: 'Audio In',
  14: 'User 1',
  15: 'User 2',
}

__names = {}
for key in G2Categories:
  nm = G2Categories[key]
  __names[nm.lower()] = key

def namefromtype(type_):
  return G2Categories[type_]

def typefromname(name):
  return __names[name.lower()]
