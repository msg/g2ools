#
# colors.py - NM1 colors
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

from nord import Mapping

nm1cablecolors = Mapping(
  red = 0,
  blue = 1,
  yellow = 2,
  grey = 3,
  green = 4,
  purple = 5,
  white = 6
)

nm1conncolors = Mapping(
  audio = 0,
  control = 1,
  logic = 2,
  slave = 3
)

