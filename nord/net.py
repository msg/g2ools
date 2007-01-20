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

class NetError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Net:
  def __init__(self, output, inputs):
    self.output = output
    self.inputs = inputs

# addnet - update the netlist adding source and dest
def addnet(netlist, source, dest):
  if source.net and dest.net and source.net == dest.net:
    print 'Connecting already created net'
    print source.net, dest.net
    print '  %d:%s -> %d:%s' % (source.module.index,source.type.name,
        dest.module.index,dest.type.name),
    print 'source net:'
    printnet(source.net)
    print 'dest net:'
    printnet(dest.net)
    return

  if source.net and dest.net: # two separate nets need to be combined
    if source.net.output and dest.net.output and (
        source.net.output != dest.net.output): # shouldn't happen
      raise NetError(
        'source and dest both have outputs: source=%s:%s dest=%s:%s' % (
        source.module.type.shortnm, source.type.name,
        dest.net.output.module.type.shortnm, dest.net.output.type.name))

    #print 'Combine:'
    #print ' source',
    #printnet(source.net)
    #print ' dest',
    #printnet(dest.net)

    netlist.remove(dest.net)

    source.net.inputs += dest.net.inputs
    for input in dest.net.inputs:
      #source.net.inputs.append(input)
      input.net = source.net

    if dest.net.output:
      source.net.output = dest.net.output
      source.net.output.net = source.net

    #print ' combine',
    #printnet(source.net)
    return

  found = 0
  for net in netlist:
    if source == net.output or source in net.inputs or dest in net.inputs:
      found = 1
      if not dest in net.inputs: # just in case two connections are made
        net.inputs.append(dest)

      if source.direction:
        if net.output and source != net.output:
          raise NetError(
            'Two outputs connected to net: source=%s:%s net.source=%s:%s' % (
            source.module.type.shortnm, source.type.name,
            net.output.module.type.shortnm, net.output.type.name))
        net.output = source
      elif not source in net.inputs: # just in case two connections are made
        net.inputs.append(source)
      break

  # add new net if one not found
  if found == 0:
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
  #print 'delnet source=%s:%s dest=%s:%s' % (
  #  source.module.name,source.type.name,
  #  dest.module.name,dest.type.name)
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
    print '<empty>'
    return
  if net.output:
    out = '%s:%s' % (net.output.module.name,net.output.type.name)
  else:
    out = '<none>'
  inp = ','.join([
      '%s:%s' % (inp.module.name,inp.type.name) for inp in net.inputs])
  print '%s -> %s' % (out, inp)

