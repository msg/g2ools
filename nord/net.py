#
# net.py - maintain netlist from cable connections
#

class Net:
  def __init__(self, output, inputs):
    self.output = output
    self.inputs = inputs

# updatenetlist - update the netlist based on source and dest
def updatenetlist(netlist, source, dest):
  found = 0
  for net in netlist:
    if source == net.output or source in net.inputs or dest in net.inputs:
      found = 1
      if not dest in net.inputs: # just in case two connections are made
        net.inputs.append(dest)
      if source.direction:
        if net.output and not source is net.output:
          raise \
            'Two outputs connected to net: source=%d:%d net.source=%d:%d' % (
            source.module.index, source.index,
            net.output.module.index, net.output.index)
        net.output = source
      elif not source in net.inputs: # just in case two connections are made
        net.inputs.append(source)

  # add new net if one not found
  if found == 0:
    if source.direction:
      net = Net(source,[dest])
    else:
      net = Net(None,[dest,source])
    netlist.append(net)

  # update source and dest nets list
  if not net in source.nets:
    source.nets.append(net)

  if not net in dest.nets:
    dest.nets.append(net)

