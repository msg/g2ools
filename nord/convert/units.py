#
# units.py - unit convertion tables and functions
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
nm1adsrtime = [
     0.50,   0.70,   1.00,   1.30,   1.50,   1.80,   2.10,   2.30,
     2.60,   2.90,   3.20,   3.50,   3.90,   4.20,   4.60,   4.90,
     5.30,   5.70,   6.10,   6.60,   7.00,   7.50,   8.00,   8.50,
     9.10,   9.70,   10.0,   11.0,   12.0,   13.0,   13.0,   14.0,
     15.0,   16.0,   17.0,   19.0,   20.0,   21.0,   23.0,   24.0,
     26.0,   28.0,   30.0,   32.0,   35.0,   37.0,   40.0,   43.0,
     47.0,   51.0,   55.0,   59.0,   64.0,   69.0,   75.0,   81.0,
     88.0,   95.0,    103,    112,    122,    132,    143,    156,
      170,    185,    201,    219,    238,    260,    283,    308,
      336,    367,    400,    436,    476,    520,    576,    619,
      676,    738,    806,    881,    962,   1100,   1100,   1300,
     1400,   1500,   1600,   1800,   2000,   2100,   2300,   2600,
     2800,   3100,   3300,   3700,   4000,   4400,   4800,   5200,
     5700,   6300,   6800,   7500,   8200,   9000,   9800,  10700,
    11700,  12800,  14000,  15300,  16800,  18300,  20100,  21900,
    24000,  26300,  28700,  31400,  34400,  37600,  41100,  45000,
]

g2adsrtime = [
     0.50,   0.60,   0.70,   0.90,   1.10,   1.30,   1.50,   1.80,
     2.10,   2.50,   3.00,   3.50,   4.00,   4.70,   5.50,   6.30,
     7.30,   8.40,   9.70,   11.1,   12.7,   14.5,   16.5,   18.7,
     21.2,   24.0,   27.1,   30.6,   34.4,   38.7,   43.4,   48.6,
     54.3,   60.6,   67.6,   75.2,   83.6,   92.8,    103,    114,
      126,    139,    153,    169,    186,    204,    224,    246,
      269,    295,    322,    352,    384,    419,    456,    496,
      540,    586,    636,    690,    748,    810,    876,    947,
     1020,   1100,   1190,   1280,   1380,   1490,   1600,   1720,
     1850,   1990,   2130,   2280,   2450,   2620,   2810,   3000,
     3210,   3430,   3660,   3910,   4170,   4450,   4740,   5050,
     5370,   5720,   6080,   6470,   6870,   7300,   7750,   8220,
     8720,   9250,   9800,  10400,  11000,  11600,  12300,  13000,
    13800,  14600,  15400,  16200,  17100,  18100,  19100,  20100,
    21200,  22400,  23500,  24800,  26100,  27500,  28900,  30400,
    32000,  33600,  35300,  37100,  38900,  40900,  42900,  45000,
]

def nm1tog2time(nm1midival):
  nm1time = nm1adsrtime[nm1midival]
  g2min = 45000 # it'll never be that big
  g2midival = 0
  for midival in range(128):
    g2time = g2adsrtime[midival]
    if abs(g2time-nm1time) < g2min:
      g2min = abs(g2time-nm1time)
      g2midival = midival
  return g2midival

