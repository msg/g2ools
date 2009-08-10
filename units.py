#!/usr/bin/env python
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

from Numeric import *

def ts(x,ty):
  return (1-exp(x*ty))/(1-exp(ty))

x = array(range(0,127,8)+[127],typecode=Float)

printf('Nord Modular G2 Units\n\n')
printf('ts(x,ty) = (1-exp(x*ty))/(1-exp(ty))\n')
printf('Lfo Rate Lo: ')
printf('y[0]+y[-1]*ts(x[i]/127.,7.337)\n')
ylo = array([1/62.9,1/39.6,1/25.0,1/15.7,0.10,0.16,0.25,0.40,
           0.64,1.02,1.62,2.56,4.07,6.46,10.3,16.3,24.4],typecode=Float)
y = ylo
for i in range(len(x)):
  cy = y[0]+y[-1]*ts(x[i]/127.,7.337) # 7.34
  cy = int(cy*100)/100.
  if y[i] < 10.0:
    printf('%3d %4.2f %4.2f\n', x[i], y[i], cy)
  else:
    printf('%3d %4.1f %4.1f\n', x[i], y[i], cy)

printf('\nLfo Rate Hi ')
printf('y[0]+y[-1]*ts(x[i]/127.,7.337)\n')
yhi = array([0.26,0.41,0.64,1.02,1.62,2.58,4.09,6.49,10.3,16.4,
           26.0,41.2,65.4,104,165,262,392],typecode=Float)
y = yhi
for i in range(len(x)):
  cy = y[0]+y[-1]*ts(x[i]/127.,7.337) # 7.34
  cy = int(cy*100)/100.
  if y[i] < 10.0:
    printf('%3d %4.2f %4.2f %10.6f\n', x[i], y[i], cy, cy)
  elif y[i] < 100.0:
    printf('%3d %4.1f %4.1f %10.6f\n', x[i], y[i], cy, cy)
  else:
    printf('%3d %4.0f %4.0f %10.6f\n', x[i], y[i], cy, cy)

printf('\nBPM 20 to 240\n\n')
printf('Lfo Rate Sub ')
printf('1/(x[i]*(1/y[-1]-1/y[0])/127.+1/y[0])\n')
ysub = array([699,77.7,41.1,28.0,21.2,17.1,14.3,12.3,10.8,
           9.58, 8.63,7.85,7.21,6.66,6.19,5.78,5.46],typecode=Float)
y = ysub
iy = 1/y
for i in range(len(x)):
  cy = x[i]*(iy[-1]-iy[0])/127.+iy[0]
  cy = 1/cy
  #cy = int(cy*100+0.5)/100.
  if y[i] < 10.0:
    printf('%3d %4.2f %4.2f %10.6f\n', x[i], y[i], cy, cy)
  elif y[i] < 100.0:
    printf('%3d %4.1f %4.1f %10.6f\n', x[i], y[i], cy, cy)
  else:
    printf('%3d %4.0f %4.0f %10.6f\n', x[i], y[i], cy, cy)

printf('\nEnv ADSR Time\n')
ytim = array([0.0005,0.0021,0.0073,0.0212,0.0543,0.126,0.269,0.540,1.02,
              1.85,3.21,5.37,8.72,13.8,21.2,32.0,45.0],typecode=Float)
y = ytim
for i in range(len(x)):
  cy = y[0]+y[-1]*ts(x[i]/127.,7.337) # 7.34
  if y[i] < 1.0:
    cym = cy*1000.
    ym = y[i]*1000.
    printf('%3d %4.2fm %4.2fm %10.6fm\n', x[i], ym, cym, cym)
  elif y[i] < 10.0:
    printf('%3d %4.2fs %4.2fs %10.6fs\n', x[i], y[i], cy, cy)
  else:
    printf('%3d %4.1fs %4.1fs %10.6fs\n', x[i], y[i], cy, cy)

