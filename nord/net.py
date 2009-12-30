#
# net.py - maintain netlist from cable connections
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

from nord import printf

'''These classes should not be used by user applications.  It's all
internal representations of cable netlists of patches.'''

class NetError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Net:
  def __init__(self, output, inputs):
    self.output = output
    self.inputs = inputs

def combinenet(netlist, source, dest):
  if source.net.output and dest.net.output and (
      source.net.output != dest.net.output): # shouldn't happen
    printf('source ')
    printnet(source.net)
    printf('dest ')
    printnet(dest.net)
    raise NetError(
      'source and dest both have outputs: source=%s:%s dest=%s:%s' % (
      source.module.type.shortnm, source.type.name,
      dest.net.output.module.type.shortnm, dest.net.output.type.name))

  #printf('Combine:\n')
  #printf(' source ')
  #printnet(source.net)
  #printf(' dest ')
  #printnet(dest.net)

  netlist.remove(dest.net)

  if dest.net.output:
    source.net.output = dest.net.output
    source.net.output.net = source.net

  source.net.inputs += dest.net.inputs
  for input in dest.net.inputs:
    #source.net.inputs.append(input)
    input.net = source.net

  #printf(' combine ')
  #printnet(source.net)
  #printf('\n')
  return

# addnet - update the netlist adding source and dest
def addnet(netlist, source, dest):
  if source.net and dest.net and source.net == dest.net:
    printf('Connecting already created net\n')
    printf('%r %r\n', source.net, dest.net)
    printf('  %d:%s -> %d:%s\n', source.module.index,source.type.name,
        dest.module.index,dest.type.name)
    printf('source net:\n')
    printnet(source.net)
    printf('dest net:\n')
    printnet(dest.net)
    return

  if source.net and dest.net: # two separate nets need to be combined
    combinenet(netlist, source, dest)
    return

  net = None
  if source.net:
    net = source.net
    net.inputs.append(dest)
  elif dest.net:
    net = dest.net
    if source.direction:
      if net.output and source != net.output:
        raise NetError(
          'Two outputs connected to net: source=%s:%s net.source=%s:%s' % (
          source.module.type.shortnm, source.type.name,
          net.output.module.type.shortnm, net.output.type.name))
      net.output = source
    else:
      net.inputs.append(source)

  # add new net if one not found
  if not net:
    if source.direction:
      net = Net(source,[dest])
    else:
      net = Net(None,[dest,source])
    netlist.append(net)

  # update source and dest nets list
  if not source.net:
    source.net = net

  if not dest.net:
    dest.net = net

# delnet - remove a net from the netlist with checks
def delnet(netlist, source, dest):
  #printf('delnet source=%s:%s dest=%s:%s\n', (
  #    source.module.name,source.type.name,
  #    dest.module.name,dest.type.name)
  if source.net != dest.net:
    raise NetError('source=%s:%s dest=%s:%s not connected' % (
      source.module.name,source.type.name,
      dest.module.name,dest.type.name))
    return
  if not source.net in netlist:
    raise NetError('source=%s:%s dest=%s:%s not in netlist' % (
      source.module.name,source.type.name,
      dest.module.name,dest.type.name))
    return
  # remove net from netlist and rebuild two nets
  net = source.net
  if net.output:
    net.output.net = None
  for input in net.inputs:
    input.net = None
  netlist.remove(net)

def printnet(net):
  if not net:
    printf('<empty>\n')
    return
  if net.output:
    out = '%s(%s):%s' % (net.output.module.name, net.output.module.type.shortnm,
        net.output.type.name)
  else:
    out = '<none>'
  inp = ','.join([
      '%s(%s):%s' % (inp.module.name, inp.module.type.shortnm, inp.type.name)
      for inp in net.inputs])
  printf('%s -> %s\n', out, inp)

