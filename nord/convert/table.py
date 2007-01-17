
#
# table.py - convertion tables
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
# FMAmod conversion table calculated by 3phase
# mod conversion table calculated by 3phase
# kbt conversion table calculated by 3phase 
fmamod = [ # [fmmod,mix,inv]
  [  0,  0,  0],  [  1,  0, 55],  [  1, 49,  0],  [  1, 76,  0],
  [  2,  0, 87],  [  2,  0, 77],  [  2,  0, 58],  [  2, 37,  0],
  [  2, 71,  0],  [  3,  0, 64],  [  3,  0, 17],  [  3, 62,  0],
  [  4,  0, 55],  [  4, 37,  0],  [  5,  0, 61],  [  5, 20,  0],
  [  6,  0, 60],  [  6,  0,  0],  [  7,  0, 57],  [  7, 29,  0],
  [  8,  0, 52],  [  8, 41,  0],  [  9,  0, 44],  [  9, 50,  0],
  [ 10,  0, 25],  [ 11,  0, 52],  [ 11, 38,  0],  [ 12,  0,  0],
  [ 12, 51,  0],  [ 13, 24,  0],  [ 14,  0, 44],  [ 14, 47,  0],
  [ 15, 16,  0],  [ 16,  0, 43],  [ 16, 47, 16],  [ 17, 22,  7],
  [ 18,  7,  7],  [ 18, 49, 16],  [ 19, 32,  4],  [ 20,  7, 32],
  [ 21, 11, 46],  [ 21, 41,  7],  [ 22, 19,  7],  [ 23, 10, 36],
  [ 23, 49, 10],  [ 24, 39,  3],  [ 25, 21,  0],  [ 26, 10, 32],
  [ 27, 11, 42],  [ 27, 42,  0],  [ 28, 33, 11],  [ 29,  0,  6],
  [ 30,  0, 31],  [ 31, 11, 31],  [ 31, 43, 13],  [ 32, 36, 11],
  [ 33, 25,  0],  [ 34,  0, 16],  [ 35,  6, 30],  [ 36, 13, 37],
  [ 37, 12, 41],  [ 37, 39, 41],  [ 38, 34,  7],  [ 39, 28,  7],
  [ 40, 17,  0],  [ 41,  2, 17],  [ 42,  4, 26],  [ 43,  7, 31],
  [ 44,  2, 34],  [ 45,  9, 37],  [ 46,  9, 39],  [ 46, 37,  7],
  [ 47, 36, 17],  [ 48, 32, 17],  [ 49, 32, 19],  [ 50, 26,  6],
  [ 51, 22,  2],  [ 52, 18,  4],  [ 53, 11,  3],  [ 54,  0,  9],
  [ 55,  2, 16],  [ 56,  5, 20],  [ 57,  5, 22],  [ 58,  6, 24],
  [ 59,  4, 25],  [ 60,  3, 26],  [ 61,  4, 27],  [ 62,  7, 28],
  [ 63,  0, 28],  [ 64,  6, 29],  [ 65,  0, 29],  [ 66,  0, 30],
  [ 67,  5, 30],  [ 68,  1, 30],  [ 69, 10, 31],  [ 70, 10, 31],
  [ 71,  6, 31],  [ 72,  4, 31],  [ 73,  1, 31],  [ 74, 11, 32],
  [ 75,  9, 32],  [ 76,  9, 32],  [ 77,  6, 32],  [ 78,  3, 32],
  [ 78, 33,  7],  [ 79, 33, 11],  [ 80, 33, 14],  [ 81, 31,  3],
  [ 82, 31,  9],  [ 83, 30,  7],  [ 84, 29,  4],  [ 85, 28,  1],
  [ 86, 28, 10],  [ 87, 27,  9],  [ 88, 25,  3],  [ 89, 24,  5],
  [ 90, 22,  2],  [ 91, 20,  0],  [ 92, 19,  0],  [ 93, 15,  3],
  [ 94, 10,  3],  [ 95,  0,  6],  [ 96,  5, 15],  [ 97,  2, 18],
  [ 98,  4, 21],  [ 99,  4, 24],  [100,  4, 26],  [101,  9, 28],
]

modtable = [ # [pitchmod,mix,inv]
  [  0,  0,  0],  [  1, 41,  0],  [  2, 41,  0],  [  2, 41,  0],
  [  2, 37,  0],  [  2, 48,  0],  [  2, 64,  0],  [  4,  0, 41],
  [  4,  0, 41],  [  5,  0, 41],  [  6,  0, 67],  [  6,  0, 61],
  [  6,  0,  0],  [  7,  0,  0],  [  7,  0,  0],  [  8,  0, 46],
  [  9,  0, 47],  [ 10,  0, 48],  [ 10,  0, 25],  [ 11,  0, 59],
  [ 12,  0, 46],  [ 12, 22,  0],  [ 13,  0, 37],  [ 13, 48,  0],
  [ 14, 24,  0],  [ 15,  0, 13],  [ 16,  0, 44],  [ 17,  0, 50],
  [ 17, 34,  0],  [ 18,  0, 12],  [ 19,  0, 46],  [ 19, 46, 11],
  [ 20, 33,  0],  [ 21, 25,  5],  [ 22,  0, 27],  [ 23,  0, 39],
  [ 24,  0, 41],  [ 25,  0, 48],  [ 25, 37,  0],  [ 26, 17,  0],
  [ 27,  0,  0],  [ 28,  0, 24],  [ 29,  0, 34],  [ 30,  0, 37],
  [ 31,  0, 38],  [ 32, 20, 44],  [ 33,  0, 43],  [ 34,  0, 42],
  [ 34, 39,  0],  [ 35, 39,  0],  [ 37,  0, 45],  [ 37, 35, 11],
  [ 38, 37,  9],  [ 40,  0, 43],  [ 41, 16, 43],  [ 42,  0, 43],
  [ 42, 39,  0],  [ 43, 39,  2],  [ 44, 41,  5],  [ 46,  1, 35],
  [ 47,  0, 32],  [ 48, 12, 29],  [ 49,  0, 22],  [ 50,  0, 15],
  [ 51, 17,  1],  [ 52, 26,  7],  [ 53, 31,  9],  [ 54, 35,  6],
  [ 56,  0, 34],  [ 57,  0, 29],  [ 58,  0, 22],  [ 59, 14,  0],
  [ 60, 24,  3],  [ 61, 31,  0],  [ 62, 36,  5],  [ 64,  5, 29],
  [ 65,  0, 19],  [ 66, 16,  0],  [ 68,  6, 39],  [ 69,  6, 35],
  [ 70,  0, 28],  [ 71,  7, 21],  [ 72, 17,  0],  [ 73, 28,  4],
  [ 75,  0, 32],  [ 76,  0, 25],  [ 77,  0, 10],  [ 78, 24, 10],
  [ 79, 31,  6],  [ 81, 15, 30],  [ 82,  0, 17],  [ 83, 18,  0],
  [ 84, 28,  0],  [ 86, 10, 30],  [ 87,  5, 21],  [ 88, 15,  0],
  [ 89, 26,  0],  [ 91,  7, 30],  [ 92,  6, 22],  [ 93, 11,  2],
  [ 94, 24,  0],  [ 96, 16, 32],  [ 97, 13, 25],  [ 98,  0,  4],
  [ 99, 22,  0],  [100, 29,  4],  [102, 29, 25],  [103,  2, 13],
  [104, 19,  1],  [105, 28, 11],  [107,  0, 26],  [108,  3, 18],
  [109, 12,  0],  [110, 25, 11],  [111, 29,  5],  [113,  5, 23],
  [114,  7, 14],  [115, 17,  2],  [116, 26, 12],  [118,  3, 27],
  [119,  4, 22],  [120,  4, 13],  [122,  5, 34],  [123,  0, 31],
  [124,  6, 28],  [125,  6, 24],  [126,  3, 18],  [127,  0,  1],
]

kbttable = [ # [lev1,lev2]
  [  0,  0],  [  2,  0],  [  4,  0],  [  6,  0],
  [  8,  0],  [ 10,  0],  [ 12,  0],  [ 14,  0],
  [ 16,  0],  [ 18,  0],  [ 20,  0],  [ 22,  0],
  [ 24,  0],  [ 26,  0],  [ 28,  0],  [ 30,  0],
  [ 32,  0],  [ 34,  0],  [ 36,  0],  [ 38,  0],
  [ 40,  0],  [ 42,  0],  [ 44,  0],  [ 46,  0],
  [ 48,  0],  [ 50,  0],  [ 52,  0],  [ 54,  0],
  [ 56,  0],  [ 58,  0],  [ 60,  0],  [ 62,  0],
  [ 64,  0],  [ 66,  0],  [ 68,  0],  [ 70,  0],
  [ 72,  0],  [ 74,  0],  [ 76,  0],  [ 78,  0],
  [ 80,  0],  [ 82,  0],  [ 84,  0],  [ 86,  0],
  [ 88,  0],  [ 90,  0],  [ 92,  0],  [ 94,  0],
  [ 96,  0],  [ 98,  0],  [100,  0],  [102,  0],
  [104,  0],  [106,  0],  [108,  0],  [110,  0],
  [112,  0],  [114,  0],  [116,  0],  [118,  0],
  [120,  0],  [122,  0],  [124,  0],  [126,  0],
  [127,  0],  [127,  2],  [127,  4],  [127,  6],
  [127,  8],  [127, 10],  [127, 12],  [127, 14],
  [127, 16],  [127, 18],  [127, 20],  [127, 22],
  [127, 24],  [127, 26],  [127, 28],  [127, 30],
  [127, 32],  [127, 34],  [127, 36],  [127, 38],
  [127, 40],  [127, 42],  [127, 44],  [127, 46],
  [127, 48],  [127, 50],  [127, 52],  [127, 54],
  [127, 56],  [127, 58],  [127, 60],  [127, 62],
  [127, 64],  [127, 66],  [127, 68],  [127, 70],
  [127, 72],  [127, 74],  [127, 76],  [127, 78],
  [127, 80],  [127, 82],  [127, 84],  [127, 86],
  [127, 88],  [127, 90],  [127, 92],  [127, 94],
  [127, 96],  [127, 98],  [127,100],  [127,102],
  [127,104],  [127,106],  [127,108],  [127,110],
  [127,112],  [127,114],  [127,116],  [127,118],
  [127,120],  [127,122],  [127,124],  [127,127],
]

notescale = [ # [24g2,8g2]
 [  0,  0], [  3,  0], [  6,  0], [  9,  0],
 [ 11,  0], [ 14,  0], [ 17,  0], [ 19,  0],
 [ 22,  0], [ 24,  0], [ 27,  0], [ 30,  0],
 [ 32,  0], [ 35,  0], [ 37,  0], [ 40,  0],
 [ 43,  0], [ 45,  8], [ 48, 16], [ 51, 24],
 [ 53, 32], [ 56, 40], [ 59, 48], [ 61, 56],
 [ 64, 64], [ 67, 72], [ 69, 80], [ 72, 88],
 [ 74, 96], [ 77,104], [ 80,112], [ 82,120],
 [ 85,127], [ 87,127], [ 90,127], [ 93,127],
 [ 95,127], [ 98,127], [101,127], [103,127],
 [106,127], [109,127], [111,127], [114,127],
 [116,127], [119,127], [122,127], [124,127],
 [127,127],
]

glide = [
   0,  0,  0,  1,  1,  2,  2,  3,  3,  4,  4,  5,  5,  6,  6,  7,
   7,  7,  7,  8,  8,  8,  8,  8,  8,  9,  9,  9,  9,  9, 10, 10,
  10, 10, 10, 10, 11, 11, 11, 12, 14, 15, 17, 18, 20, 21, 23, 24,
  26, 27, 27, 28, 28, 29, 29, 30, 30, 30, 31, 31, 32, 32, 33, 34,
  34, 35, 36, 37, 37, 38, 39, 40, 40, 41, 42, 43, 43, 44, 45, 46,
  46, 47, 48, 49, 49, 50, 51, 51, 52, 52, 53, 53, 54, 54, 55, 55,
  56, 56, 57, 57, 58, 59, 60, 60, 61, 62, 63, 63, 64, 65, 66, 66,
  67, 68, 68, 69, 70, 70, 71, 72, 73, 73, 74, 75, 76, 76, 78, 79,
]

fmbmod = [ # [phasemod,mix,inv]
 [  0,  0,  0], [  1,  0,  0], [  1,  0,  0], [  1,  0,  0],
 [  1,  0,  0], [  1,  0,  0], [  1,  0,  0], [  1,  0,  0],
 [  1,  0,  0], [  2,  0,  0], [  2,  0,  0], [  2,  0,  0],
 [  2,  0,  0], [  2,  0,  0], [  3,  0,  0], [  3,  0,  0],
 [  3,  0,  0], [  4,  0, 64], [  4,  0,  0], [  5,  0,  0],
 [  5,  0,  0], [  5,  0,  0], [  6,  0, 64], [  6,  0,  0],
 [  6, 64,  0], [  7,  0,  0], [  7,  0,  0], [  8,  0,  0],
 [  8,  0,  0], [  9,  0,  0], [  9,  0,  0], [ 10,  0,  0],
 [ 11,  0,  0], [ 11,  0,  0], [ 12,  0,  0], [ 12, 64,  0],
 [ 13,  0,  0], [ 14,  0,  0], [ 14, 64,  0], [ 15,  0,  0],
 [ 15, 64,  0], [ 16,  0,  0], [ 17,  0,  0], [ 17, 64,  0],
 [ 18,  0,  0], [ 19,  0,  0], [ 20,  0,  0], [ 21,  0,  0],
 [ 21,  0,  0], [ 22,  0,  0], [ 22,  0,  0], [ 23,  0,  0],
 [ 23,  0,  0], [ 24,  0, 64], [ 24, 64,  0], [ 25,  0,  0],
 [ 26,  0,  0], [ 27,  0,  0], [ 27,  0,  0], [ 28,  0,  0],
 [ 29,  0,  0], [ 29,  0,  0], [ 30,  0,  0], [ 31,  0,  0],
 [ 32,  0,  0], [ 32,  0,  0], [ 33,  0,  0], [ 34,  0,  0],
 [ 34,  0,  0], [ 35,  0,  0], [ 36,  0,  0], [ 37,  0,  0],
 [ 37,  0,  0], [ 38,  0,  0], [ 39,  0,  0], [ 40,  0,  0],
 [ 40,  0,  0], [ 41,  0,  0], [ 42,  0,  0], [ 42,  0,  0],
 [ 43,  0,  0], [ 44,  0,  0], [ 45,  0,  0], [ 45,  0,  0],
 [ 46,  0,  0], [ 47,  0,  0], [ 47, 64,  0], [ 48,  0,  0],
 [ 49,  0,  0], [ 50,  0,  0], [ 51,  0,  0], [ 52,  0,  0],
 [ 52,  0,  0], [ 53,  0,  0], [ 54,  0,  0], [ 54, 55,  0],
 [ 55,  0,  0], [ 56,  0,  0], [ 57,  0,  0], [ 58,  0,  0],
 [ 59,  0,  0], [ 59,  0,  0], [ 60,  0,  0], [ 61,  0,  0],
 [ 62,  0,  0], [ 63,  0,  0], [ 64,  0,  0], [ 64, 32,  0],
 [ 65,  0,  0], [ 66,  0,  0], [ 67,  0,  0], [ 67,  0,  0],
 [ 68,  0,  0], [ 69,  0,  0], [ 70,  0,  0], [ 70,  0,  0],
 [ 71,  0,  0], [ 72,  0,  0], [ 73,  0,  0], [ 73,  0,  0],
 [ 74,  0,  0], [ 75,  0,  0], [ 76,  0,  0], [ 76, 41,  0],
 [ 77,  0,  0], [ 78,  0,  0], [ 79,  0,  0], [ 80,  0,  0],
]

wavewrap = [
   0,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20,
  21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
  37, 38, 39, 40, 41, 42, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
  52, 53, 54, 55, 56, 57, 58, 59, 60, 60, 61, 62, 63, 64, 65, 66,
  67, 68, 69, 70, 71, 72, 73, 73, 74, 75, 76, 77, 78, 79, 80, 81,
  82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97,
  98, 99,100,100,101,102,103,104,105,106,107,107,108,109,110,111,
 112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,
]
