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
  __slots__ = ( 'output', 'inputs' )
  def __init__(self, output, inputs):
    self.output = output
    self.inputs = inputs

class NetList:
  def __init__(self):
    self.nets = []

  def copy(self):
    new = NetList()
    new.nets = self.nets[:]
    return new

  def combine(self, source, dest):
    sout, dout = source.net.output, dest.net.output
    if sout and dout and (sout != dout): # shouldn't happen
      printf('source %s\n', self.nettos(source.net))
      printf('dest %s\n', self.nettos(dest.net))
      raise NetError(
        'source and dest both have outputs: source=%s:%s dest=%s:%s' % (
        sout.module.type.shortnm, sout.type.name,
        dout.module.type.shortnm, dout.type.name))

    self.nets.remove(dest.net)

    if dout:
      source.net.output = dout
      source.net.output.net = source.net

    source.net.inputs += dest.net.inputs
    for input in dest.net.inputs:
      input.net = source.net

  def add(self, source, dest):
    snet, dnet = source.net, dest.net
    if snet and dnet and snet == dnet:
      printf('net already created\n')
      printf('%r %r\n', snet, dnet)
      printf('  %d:%s -> %d:%s\n',
          source.module.index, source.type.name,
          dest.module.index, dest.type.name)
      printf('source net: %s\n', self.nettos(snet))
      printf('dest net: %s\n', self.nettos(dnet))
      return

    if snet and dnet: # two separate nets need to be combined
      self.combine(source, dest)
      return

    if snet:
      net = snet
      net.inputs.append(dest)
    elif dnet:
      net = dnet
      if source.direction:
        if net.output and source != net.output:
          raise NetError(
            'both nets have outputs: source=%s:%s net.source=%s:%s' % (
            source.module.type.shortnm, source.type.name,
            net.output.module.type.shortnm, net.output.type.name))
        net.output = source
      else:
        net.inputs.append(source)
    else:
      net = None

    # add new net if one not found
    if not net:
      if source.direction:
        net = Net(source, [dest])
      else:
        net = Net(None, [dest, source])
      self.nets.append(net)

    # update source and dest nets list
    if not source.net:
      source.net = net
    if not dest.net:
      dest.net = net

  def delete(self, source, dest):
    if source.net != dest.net:
      raise NetError('source=%s:%s dest=%s:%s not connected' % (
        source.module.name, source.type.name,
        dest.module.name, dest.type.name))
    if 0 and not source.net in self.nets:
      raise NetError('source=%s:%s dest=%s:%s not in netlist' % (
        source.module.name, source.type.name,
        dest.module.name, dest.type.name))

    # remove net from netlist and rebuild two nets
    net = source.net
    if net.output:
      net.output.net = None
    for input in net.inputs:
      input.net = None
    self.nets.remove(net)

  def nettos(self, net):
    if not net:
      return '<empty>'
    if net.output:
      nout = net.output
      out = '%s(%s)%d:%s' % (nout.module.name, nout.module.type.shortnm,
          nout.module.index, nout.type.name)
    else:
      out = '<none>'
    inp = ','.join([
        '%s(%s)%d:%s' % (inp.module.name, inp.module.type.shortnm,
                inp.module.index, inp.type.name)
        for inp in net.inputs])
    return '%s -> %s' % (out, inp)

