#!/usr/bin/env python

import os, string, sys
from nord.g2.file import Pch2File, Prf2File
from nord import types
from nord.g2.colors import g2cablecolors, g2conncolors, g2modulecolors
from nord import printf

__builtins__.printf = printf

def cleanline(line):
  comment = line.find('#')
  if comment < 0:
    return line.strip()
  else:
    return line[:comment].strip()

class G2Param(object):
  def __init__(self, param):
    self.param = param
  
  def set(self, *a):
    self.param.variations[:len(a)] = map(int, a)

  def label(self, *a):
    self.param.labels = a

class G2Port(object):
  def __init__(self, port):
    self.port = port

class G2ModuleType(object):
  def __init__(self):
    self.params = { }
    self.ports = { }

class G2Module(object):
  def __init__(self, module):
    self.module = module
    self.setup()

  def setup(self):
    module = self.module
    self.params = { }
    for param in module.params:
      self.params[param.type.name.lower()] = G2Param(param)

    self.ports = { }
    # adjust input/output conflicts by appending <name>in <name>in
    inputnames = [ i.type.name for i in module.inputs ]
    outputnames = [ o.type.name for o in module.outputs ]
    for input in inputnames:
      nm = input
      if nm in outputnames:
        nm += 'in'
      self.ports[nm.lower()] = G2Port(getattr(module.inputs, input))
    for output in outputnames:
      nm = output
      if nm in inputnames:
        nm += 'out'
      self.ports[nm.lower()] = G2Port(getattr(module.outputs, output))

class G2Patch:
  def __init__(self, filename):
    global g2oolsdir
    self.pch2 = Pch2File(os.path.join(g2oolsdir, 'initpatch.pch2'))
    self.current_area = self.pch2.patch.voice
    self.filename = filename[:filename.rfind('.')]
    self.variations = range(9)
    self.horiz = 0
    self.vert = 0
    self.cable_color = g2cablecolors.white
    self.module_color = g2modulecolors.grey
    self.module_types = { }  # new module types
    self.voice_modules = { }
    self.fx_modules = { }
    self.modules = self.voice_modules

  def update_rates(self):
    # loop through all module connections
    # check output rate and adjust rates of modules that are connected
    # change "white" cables to proper color (red, blue, yellow, orange)
    for area in [ self.pch2.patch.voice, self.pch2.patch.fx ]:
      for net in area.netlist:
	if net.output == None:
	  continue

	if net.output.rate == g2conncolors.red or \
	   net.output.rate == g2conncolors.orange:
	   uprate = 1
	else:
	   uprate = 0

	for input in net.inputs:
	  input.module.uprate = uprate
	  for cable in input.cables:
	    if cable.color == g2cablecolors.white:
	      cable.color = net.output.rate

  def write(self):
    self.pch2.write(self.filename + '.pch2')

  def parse_connection(self, connection):
    ref, port = connection.split('.',2)
    if not self.modules.has_key(ref):
      return None
    module = self.modules[ref]
    if not module.ports.has_key(port):
      return None
    return module.ports[port]

  def parse_parameter(self, parameter):
    ref, param = parameter.split('.')
    if not self.modules.has_key(ref):
      return None
    module = self.modules[ref]
    if not module.params.has_key(param):
      return None
    return module.params[param]

  def variations(self, args):
    self.variations = map(int, args)

  def column(self, args):
    horiz = (string.lowercase + string.uppercase).find(args[0])
    if horiz < 0:
      return -1

    self.horiz = horiz
    vert = 0
    for module in self.current_area.modules:
      if module.horiz != horiz:
	continue
      new_vert = module.vert + module.type.height
      if new_vert > vert:
	vert = new_vert
    self.vert = vert
    return 0

  def cablecolor(self, args):
    self.cable_color = g2cablecolors.fromname(args[0])

  def area(self, args):
    if len(args) < 1:
      return -1
    if args[0] == 'voice':
      self.current_area = self.pch2.patch.voice
      self.modules = self.voice_modules
    elif args[0] == 'fx':
      self.current_area = self.pch2.patch.voice
      self.modules = self.fx_modules
    else:
      return -1
    return 0

  def add(self, args):
    if len(args) < 2:
      return -1
    if self.modules.has_key(args[0]):
      return -1
    m = self.current_area.addmodule(args[0], name=args[1],
          horiz=self.horiz, vert=self.vert, color=self.module_color)
    self.modules[args[1]] = G2Module(m)
    self.vert += m.type.height

  def connect(self, args):
    lastconnection = None
    connections = []
    for arg in args:
      connection = self.parse_connection(arg)
      if connection:
        connections.append(connection)

    if len(connections) < 2: # if no connections
      return

    last = connections[0]
    for connection in connections[1:]:
      self.current_area.connect(last.port, connection.port, self.cable_color)
      last = connection

  def label(self, args):
    if len(args) < 2:
      return -1
    param = self.parse_parameter(args[0])
    if param == None:
      return -1
    param.label(args[1:])

  def set(self, args):
    if len(args) < 2:
      return -1
    param = self.parse_parameter(args[0])
    if param == None:
      return -1
    param.set(map(int, args[1:]))

class G2File:
  def __init__(self, filename):
    self.g2patch = G2Patch(filename)
    self.topfile = filename
    self.files = { }
    self.modules = { }
    self.build_files(filename)
    self.build_modules()
    self.build_patch()

  def write(self):
    self.g2patch.update_rates()
    self.g2patch.write()

  def handle_include(self, filenames):
    for filename in filenames:
      if not self.files.has_key(file):
        self.build_files(filename)

  def build_files(self, filename):
    lines = open(filename).readlines()
    self.files[filename] = zip(range(1,1+len(lines)),lines)
    for line in lines:
      line = cleanline(line)
      if not line:
        continue
      fields = line.strip().split()
      if fields[0] == 'include':
	self.handle_include(fields)

  def build_modules(self):
    pass

  def build_patch(self):
    lines = self.files[self.topfile]
    for lineno, line in lines:
      self.parse_line(cleanline(line))
    
  def parse_line(self, line):
    args = [ l.strip().lower() for l in line.split() ]
    if len(args) < 1:
      return
    func = args.pop(0)

    printf('%s(%s)\n', func, args)
    getattr(self.g2patch, func)(args)

  def parse(self, filename):
    lines = open(filename).readlines()
    for line in [ l.strip() for l in lines if l.strip() != '' ]:
      line = cleanline(line)
      self.parse_line(line)

if __name__ == '__main__':
  g2oolsdir = os.path.dirname(sys.argv.pop(0))
  g2file = G2File(sys.argv.pop(0))
  g2file.write()

