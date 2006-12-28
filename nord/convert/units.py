#
# units.py - unit convertion tables and functions
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

def nm2g2val(nm1midival,nm1vals,g2vals):
  nm1val = nm1vals[nm1midival]
  g2min = 1000000 # nothing here will never be that big
  g2midival = 0
  for midival in range(128):
    g2val = g2vals[midival]
    if abs(g2val-nm1val) < g2min:
      g2min = abs(g2val-nm1val)
      g2midival = midival
  return g2midival

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

nm1fltfreq = [
    10.00,  11.00,  12.00,  12.00,  13.00,  14.00,  15.00,  15.00,
    16.00,  17.00,  18.00,  19.00,  21.00,  22.00,  23.00,  24.00,
    26.00,  28.00,  29.00,  31.00,  33.00,  35.00,  37.00,  39.00,
    41.00,  44.00,  46.00,  49.00,  52.00,  55.00,  58.00,  62.00,
    65.00,  69.00,  73.00,  78.00,  82.00,  87.00,  92.00,  98.00,
    104.0,  110.0,  117.0,  123.0,  131.0,  139.0,  147.0,  156.0,
    165.0,  175.0,  185.0,  196.0,  208.0,  220.0,  233.0,  247.0,
    262.0,  277.0,  294.0,  311.0,  330.0,  349.0,  370.0,  392.0,
    415.0,  440.0,  466.0,  494.0,  523.0,  554.0,  587.0,  622.0,
    659.0,  698.0,  740.0,  784.0,  831.0,  880.0,  932.0,  988.0,
    1050.,  1110.,  1170.,  1240.,  1320.,  1400.,  1480.,  1570.,
    1660.,  1760.,  1860.,  1980.,  2090.,  2220.,  2350.,  2490.,
    2640.,  2790.,  2960.,  3140.,  3320.,  3520.,  3730.,  3950.,
    4190.,  4430.,  4700.,  4980.,  5270.,  5590.,  5920.,  6270.,
    6640.,  7040.,  7460.,  7900.,  8370.,  8870.,  9400.,  9960.,
   10500., 11200., 11800., 12500., 13300., 14100., 14900., 15800.,
]

g2fltfreq = [
    13.75,  14.57,  15.43,  16.35,  17.32,  18.35,  19.45,  20.60,
    21.83,  23.12,  24.50,  25.96,  27.50,  29.14,  30.87,  32.70,
    34.65,  36.71,  38.89,  41.20,  43.65,  46.25,  49.00,  51.91,
    55.00,  58.27,  61.74,  65.41,  69.30,  73.42,  77.78,  82.41,
    87.31,  92.50,  98.00,  103.8,  110.0,  116.5,  123.5,  130.8,
    138.6,  146.8,  155.8,  164.8,  174.6,  185.0,  196.0,  207.7,
    220.0,  233.1,  246.9,  261.8,  277.2,  293.7,  311.1,  329.6,
    349.2,  370.0,  392.0,  415.3,  440.0,  466.2,  493.9,  523.3,
    554.4,  587.3,  622.3,  659.3,  698.5,  740.0,  784.0,  830.6,
    880.0,  932.3,  987.8,  1050.,  1110.,  1170.,  1240.,  1320.,
    1400.,  1480.,  1570.,  1660.,  1760.,  1860.,  1980.,  2090.,
    2220.,  2350.,  2490.,  2640.,  2790.,  2960.,  3140.,  3320.,
    3520.,  3730.,  3950.,  4190.,  4430.,  4700.,  4980.,  5270.,
    5590.,  5920.,  6270.,  6640.,  7040.,  7460.,  7900.,  8370.,
    8870.,  9400.,  9960., 10500., 11200., 11800., 12500., 13300.,
   14100., 14900., 15800., 16700., 17700., 18800., 19900., 21100.,
]

nm1logictime = [
     1.00,   1.10,   1.20,   1.30,   1.40,   1.50,   1.60,   1.70,
     1.90,   2.00,   2.20,   2.30,   2.50,   2.70,   2.90,   3.20,
     3.40,   3.70,   4.00,   4.30,   4.70,   5.00,   5.40,   5.90,
     6.30,   6.80,   7.40,   8.00,   8.60,   9.30,  10.00,  11.00,
    12.00,  13.00,  14.00,  15.00,  16.00,  17.00,  19.00,  20.00,
    22.00,  23.00,  25.00,  27.00,  30.00,  32.00,  34.00,  37.00,
    40.00,  43.00,  47.00,  51.00,  55.00,  59.00,  64.00,  69.00,
    74.00,  80.00,  87.00,  94.00,  101.0,  109.0,  118.0,  128.0,
    138.0,  149.0,  161.0,  174.0,  187.0,  202.0,  219.0,  236.0,
    255.0,  275.0,  295.0,  321.0,  347.0,  375.0,  405.0,  437.0,
    472.0,  510.0,  550.0,  595.0,  642.0,  693.0,  749.0,  809.0,
    874.0,  943.0,  1000.,  1100.,  1200.,  1300.,  1400.,  1500.,
    1600.,  1700.,  1900.,  2000.,  2200.,  2400.,  2600.,  2800.,
    3000.,  3200.,  3500.,  3800.,  4100.,  4400.,  4700.,  5100.,
    5500.,  6000.,  6500.,  7000.,  7500.,  8100.,  8800.,  9500.,
   10000., 11000., 12000., 13000., 14000., 15000., 16000., 18000.,
]

g2logictime = [
     1.04,   1.11,   1.19,   1.28,   1.37,   1.47,   1.57,   1.69,
     1.81,   1.94,   2.08,   2.23,   2.39,   2.56,   2.75,   2.94,
     3.16,   3.38,   3.63,   3.89,   4.17,   4.48,   4.80,   5.15,
     5.52,   5.93,   6.36,   6.82,   7.32,   7.85,   8.42,   9.04,
     9.70,  10.40,  11.20,  12.00,  12.90,  13.80,  14.80,  15.90,
    17.10,  18.30,  19.70,  21.10,  22.70,  24.40,  26.20,  28.10,
    30.20,  32.40,  34.80,  37.40,  40.20,  43.20,  46.40,  49.80,
    53.50,  57.50,  61.80,  66.40,  71.30,  76.70,  82.40,  88.60,
    95.20,  102.0,  110.0,  118.0,  127.0,  137.0,  147.0,  158.0,
    170.0,  183.0,  196.0,  211.0,  227.0,  244.0,  263.0,  283.0,
    304.0,  327.0,  352.0,  379.0,  408.0,  439.0,  472.0,  508.0,
    547.0,  588.0,  633.0,  681.0,  734.0,  790.0,  850.0,  915.0,
    985.0,  1070.,  1150.,  1240.,  1330.,  1430.,  1540.,  1660.,
    1790.,  1930.,  2070.,  2230.,  2410.,  2590.,  2790.,  3010.,
    3240.,  3490.,  3760.,  4060.,  4370.,  4710.,  5080.,  5480.,
    5900.,  6360.,  6860.,  7400.,  7980.,  8600.,  9280., 10000.,
]

nm1levamp = [
     0.25,   0.26,   0.26,   0.27,   0.27,   0.28,   0.28,   0.29,
     0.30,   0.30,   0.31,   0.32,   0.32,   0.33,   0.34,   0.35,
     0.35,   0.36,   0.37,   0.38,   0.39,   0.39,   0.40,   0.41,
     0.42,   0.43,   0.44,   0.45,   0.46,   0.47,   0.48,   0.49,
     0.50,   0.51,   0.52,   0.53,   0.55,   0.56,   0.57,   0.58,
     0.59,   0.61,   0.62,   0.63,   0.65,   0.66,   0.68,   0.69,
     0.71,   0.72,   0.74,   0.75,   0.77,   0.79,   0.81,   0.82,
     0.84,   0.86,   0.88,   0.90,   0.92,   0.94,   0.96,   0.99,
     1.00,   1.02,   1.04,   1.07,   1.09,   1.11,   1.14,   1.16,
     1.19,   1.22,   1.24,   1.27,   1.30,   1.33,   1.35,   1.38,
     1.41,   1.45,   1.48,   1.51,   1.54,   1.59,   1.61,   1.65,
     1.68,   1.72,   1.76,   1.79,   1.83,   1.87,   1.92,   1.96,
     2.00,   2.04,   2.09,   2.13,   2.18,   2.23,   2.28,   2.33,
     2.38,   2.43,   2.48,   2.54,   2.59,   2.65,   2.71,   2.77,
     2.83,   2.89,   2.95,   3.02,   3.08,   3.15,   3.22,   3.29,
     3.36,   3.44,   3.51,   3.59,   3.67,   3.75,   3.83,   4.00,
]

g2levamp = [
     0.00,   0.01,   0.02,   0.03,   0.04,   0.05,   0.06,   0.07,
     0.08,   0.09,   0.10,   0.11,   0.13,   0.14,   0.15,   0.16,
     0.17,   0.18,   0.19,   0.20,   0.21,   0.22,   0.23,   0.24,
     0.25,   0.26,   0.27,   0.28,   0.29,   0.30,   0.31,   0.32,
     0.33,   0.34,   0.35,   0.37,   0.38,   0.39,   0.41,   0.42,
     0.44,   0.45,   0.47,   0.48,   0.50,   0.52,   0.54,   0.55,
     0.57,   0.59,   0.62,   0.64,   0.66,   0.68,   0.71,   0.73,
     0.76,   0.78,   0.81,   0.84,   0.87,   0.90,   0.93,   0.97,
     1.00,   1.02,   1.04,   1.07,   1.09,   1.11,   1.14,   1.16,
     1.19,   1.22,   1.24,   1.27,   1.30,   1.33,   1.35,   1.38,
     1.41,   1.45,   1.48,   1.51,   1.54,   1.58,   1.61,   1.65,
     1.68,   1.72,   1.76,   1.79,   1.83,   1.87,   1.92,   1.96,
     2.00,   2.05,   2.09,   2.14,   2.19,   2.24,   2.29,   2.34,
     2.39,   2.45,   2.50,   2.56,   2.62,   2.67,   2.74,   2.80,
     2.86,   2.92,   2.99,   3.06,   3.13,   3.20,   3.27,   3.34,
     3.42,   3.50,   3.58,   3.66,   3.74,   3.83,   3.91,   4.00,
]

ratios = [
    0.025,  0.026,  0.028,  0.029,  0.031,  0.033,  0.035,  0.037,
    0.039,  0.042,  0.044,  0.047,  0.050,  0.053,  0.056,  0.059,
    0.062,  0.066,  0.070,  0.074,  0.079,  0.083,  0.088,  0.094,
    0.099,  0.105,  0.111,  0.118,  0.125,  0.132,  0.140,  0.149,
    0.157,  0.167,  0.177,  0.187,  0.198,  0.210,  0.223,  0.236,
    0.250,  0.265,  0.281,  0.297,  0.315,  0.334,  0.354,  0.375,
    0.397,  0.420,  0.445,  0.472,  0.500,  0.530,  0.561,  0.595,
    0.630,  0.667,  0.707,  0.749,  0.794,  0.841,  0.891,  0.944,
    1.000,  1.059,  1.122,  1.189,  1.260,  1.335,  1.414,  1.498,
    1.587,  1.682,  1.782,  1.888,  2.000,  2.119,  2.245,  2.378,
    2.520,  2.670,  2.828,  2.997,  3.175,  3.364,  3.563,  3.775,
    4.000,  4.238,  4.490,  4.757,  5.040,  5.339,  5.657,  5.993,
    6.350,  6.727,  7.127,  7.551,  8.000,  8.846,  8.980,  9.514,
   10.080, 10.680, 11.310, 11.990, 12.700, 13.450, 14.250, 15.100,
   16.000, 16.950, 17.960, 19.230, 20.160, 21.360, 22.630, 23.970,
   25.400, 26.910, 28.510, 30.200, 32.000, 33.900, 25.920, 38.050,
]
