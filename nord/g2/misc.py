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
from nord.g2.colors import g2conncolors

def midicc_reserved(cc):
  reservedmidiccs = [ 0, 1, 7, 11, 17, 18, 19, 32, 64, 70, 80, 96, 97 ] + \
      range(120, 128)
  return cc in reservedmidiccs

def handle_uprate(g2area):
  # parse the entire netlist of the area and .uprate=1 all
  # modules with blue_red and yellow_orange inputs connected to red outputs.
  # scan module list until we don't change any modules
  done = 0
  while not done:
    modified = 0
    for module in g2area.modules:
      #debug('%s:%s' % (module.name, module.type.shortnm))
      for minput in module.inputs:
        if not minput.net:
          continue
        #debug(' %s:%d' % (minput.type.name, minput.rate))
        # try and make all logic run at control rate.
        if minput.rate == g2conncolors.yellow_orange:
          minput.rate = g2conncolors.yellow
          continue
        if minput.rate != g2conncolors.blue_red:
          continue
        if not minput.net.output:
          continue
        if minput.net.output.rate == g2conncolors.red:
          #debug('%s:%s %s' % (
          #     module.name, minput.type.name, minput.net.output.type.name))
          modified = 1
          module.uprate = 1
          minput.rate = g2conncolors.red
          # change all outputs to red for next iteration
          for output in module.outputs:
            if output.rate == g2conncolors.blue_red:
              output.rate = g2conncolors.red
            if output.rate == g2conncolors.yellow_orange:
              output.rate = g2conncolors.orange
          break
    if not modified:
      done = 1

