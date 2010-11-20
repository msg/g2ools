#!/usr/bin/env python2

import os, string, sys, traceback
from nord.g2.file import Pch2File, Prf2File
from nord.g2.misc import handle_uprate, midicc_reserved
from nord.g2.colors import g2cablecolors, g2conncolors, g2modulecolors
from nord import printf
from nord.file import Ctrl

def debug(fmt, *a):
  if 0:
    printf(fmt, *a)

class G2Exception(Exception):
  pass

def cleanline(line):
  comment = line.find('#')
  if comment < 0:
    return line.strip()
  else:
    return line[:comment].strip()

class G2ModuleParam(object):
  def __init__(self, param):
    self.param = param
  
  def set(self, *a):
    for i in range(9):
      v = a[0][i % len(a[0])]
      if v[0] == '=':
        map = self.param.type.type.map[0]
        if not map.has_key(v[1:]):
          raise G2Exception('No name %s: pick from %s' % (v[1:], map.keys()))
        v = map[v[1:]]
      self.param.variations[i] = int(v)

  def label(self, *a):
    self.param.labels = a

class G2ModulePort(object):
  def __init__(self, port):
    self.port = port

class G2Module(object):
  def __init__(self, module):
    self.module = module
    self.height = self.module.type.height
    self.params = { }
    self.ports = { }
    self.setup()

  def setup(self):
    self.params = { }
    module = self.module
    for param in module.params:
      self.params[param.type.name.lower()] = G2ModuleParam(param)

    self.ports = { }
    # adjust input/output conflicts by appending <name>in <name>in
    inputnames = [ i.type.name for i in module.inputs ]
    outputnames = [ o.type.name for o in module.outputs ]
    for input in inputnames:
      nm = input
      if nm in outputnames:
        nm += 'in'
      self.ports[nm.lower()] = G2ModulePort(getattr(module.inputs, input))
    for output in outputnames:
      nm = output
      if nm in inputnames:
        nm += 'out'
      self.ports[nm.lower()] = G2ModulePort(getattr(module.outputs, output))

module_types = { }

def get_module_type(name):
  global module_types
  if module_types.has_key(name):
    return module_types[name]
  else:
    return G2ModuleType(name)

class G2Section(object):
  def __init__(self, section):
    self.cable_color = g2cablecolors.white
    self.module_color = g2modulecolors.grey
    self.section = section
    self.modules = { }
    self.horiz = section.horiz
    self.vert = section.vert

  def addmodule(self, typename, name):
    mt = get_module_type(typename)
    m = mt.add(self.section.current_area, name=name,
        horiz=self.section.horiz, vert=self.section.vert,
        color=self.module_color)
    self.section.vert += m.height
    return m

  def parse_connection(self, connection):
    ref, port = connection.split('.')
    if not self.modules.has_key(ref):
      raise G2Exception('No module "%s".' % ref)
    module = self.modules[ref]
    if not module.ports.has_key(port):
      raise G2Exception('No port "%s" on module "%s".' % (port, ref))
    return module.ports[port]

  def parse_parameter(self, parameter):
    ref, param = parameter.split('.')
    if not self.modules.has_key(ref):
      raise G2Exception('No module "%s".' % ref)
    module = self.modules[ref]
    if not module.params.has_key(param):
      raise G2Exception('No param "%s" on module "%s"' % (param, ref))
    return module.params[param]

  def connect(self, *args):
    connections = []
    for arg in args:
      connection = self.parse_connection(arg)
      if connection:
        connections.append(connection)

    if len(connections) < 2: # if no connections
      raise G2Exception("Must have at least 2 connections.")

    last = connections[0]
    for connection in connections[1:]:
      self.section.current_area.connect(last.port, connection.port,
          self.cable_color)
      last = connection

  def cablecolor(self, color):
    self.cable_color = getattr(g2cablecolors, color)

  def modulecolor(self, color):
    self.module_color = getattr(g2modulecolors, color)

class G2GroupParamCalc(object):
  def __init__(self, param, equation):
    self.param = param
    self.equation = equation

class G2GroupParam(object):
  def __init__(self, group, name, default, minimum, maximum):
    self.calcs = []
    self.group = group
    self.name = name
    self.variations = [ int(default) ] * 9
    self.minimum = minimum
    self.maximum = maximum

  def add_calc(self, param, equation):
    self.calcs.append(G2GroupParamCalc(param, equation))
    variations = self.variations[:]
    self.set(*variations)

  def setupvars(self, variation, value):
    paramvars = { }
    for param in self.group.params:
      paramvars[param] = self.group.params[param].variations[variation]
    paramvars[self.name] = value
    return paramvars

  def set(self, *variations):
    for calc in self.calcs:
      vals = []
      for var in range(len(variations)):
        variation = variations[var]
        self.variations[var] = variation
        paramvars = self.setupvars(var, variation)
        val = eval(calc.equation, paramvars)
        vals.append('%s' % val)
      calc.param.set(vals)

  def label(self, *a):
    pass

class G2Group(G2Section):
  def __init__(self, section):
    super(G2Group, self).__init__(section)
    self.params = { }
    self.ports = { }
    self.height = 0

  def add(self, typename, name):
    self.modules[name] = self.addmodule(typename, name)

  def separate(self, rows):
    self.section.vert += int(rows)

  def set(self, name, *variations):
    param = self.parse_parameter(name)
    if param == None:
      raise G2Exception('No parameter "%s"' % name)
    param.set(variations)
    #getattr(param, 'set', map(int, variations))

  def label(self, param, *names):
    param = self.parse_parameter(param)
    if param == None:
      return -1
    param.label(*names)

  def param(self, name, default, minimum, maximum):
    self.params[name] = G2GroupParam(self, name, default, minimum, maximum)

  def gparam(self, name, parameter, default):
    modparam = self.parse_parameter(parameter)
    self.params[name] = G2GroupParam(self, name,
        default, modparam.param.type.type.low, modparam.param.type.type.high)
    self.params[name].add_calc(modparam, name)

  def calc(self, name, parameter, equation):
    param = self.params[name]
    modparam = self.parse_parameter(parameter)
    param.add_calc(modparam, equation)

  def port(self, name, modport):
    port = self.parse_connection(modport)
    if port == None:
      raise G2Exception('No module port "%s"' % modport)
    if self.ports.has_key(name):
      raise G2Exception('No port "%s"' % name)
    self.ports[name] = port
    return 0

  def input(self, name, modoutput):
    return self.port(name, modoutput)

  def output(self, name, modoutput):
    return self.port(name, modoutput)

class G2ModuleType(object):
  def __init__(self, shortnm):
    self.shortnm = shortnm
    self.height = 0

  def add(self, area, **kw):
    m = G2Module(area.addmodule(self.shortnm, **kw))
    self.height = m.module.type.height
    return m

class G2GroupType(G2ModuleType):
  def __init__(self, g2patch, code):
    self.g2patch = g2patch
    self.code = code

  def add(self, area, **kw):
    gm = G2Group(self.g2patch)
    for lineno, line in self.code:
      args = [ l.lower() for l in line.split() ]
      cmd = args.pop(0)
      debug('group %d: %s(%s)\n', lineno, cmd, args)
      try:
        getattr(gm, cmd)(*args)
      except G2Exception as e:
        printf('%d: %s\n\t%s\n', lineno, line.strip(), e)
        debug('%s\n', traceback.format_exc())
    gm.height = 0 # height calculated on each module
    return gm

class G2Patch(G2Section):
  def __init__(self, filename):
    global g2oolsdir
    self.horiz = 0
    self.vert = 0
    pch2 = Pch2File(os.path.join(g2oolsdir, 'initpatch.pch2'))
    super(G2Patch, self).__init__(self)
    self.pch2 = pch2
    self.filename = filename[:filename.rfind('.')]
    self.current_area = pch2.patch.voice
    self.variations = range(9)
    self.voice_modules = { }
    self.fx_modules = { }
    self.modules = self.voice_modules

  def update_inputs(self, net, uprate):
    # loop through all net inputs
    # get proper color based on rate
    # update all cables connected to each input
    for input in net.inputs:
      if not net.output:
        continue

      color = g2cablecolors.white
      if net.output.rate == g2conncolors.blue_red:
        color = [g2cablecolors.blue, g2cablecolors.red][uprate]
      if net.output.rate == g2conncolors.red:
        color = g2cablecolors.red
      elif net.output.rate == g2conncolors.blue:
        color = g2cablecolors.blue
      elif net.output.rate == g2conncolors.yellow_orange:
        color = [g2cablecolors.yellow, g2cablecolors.orange][uprate]

      for cable in input.cables:
        if cable.color == g2cablecolors.white:
          cable.color = color

  def update_rates(self):
    # loop through all module connections
    # check output rate and adjust rates of modules that are connected
    # change "white" cables to proper color (red, blue, yellow, orange)
    for area in [ self.pch2.patch.voice, self.pch2.patch.fx ]:
      handle_uprate(area)
      for net in area.netlist.nets:
        if net.output == None:
          continue

        self.update_inputs(net, net.output.module.uprate)

  def write(self):
    printf('Writing %s\n', self.filename + '.pch2')
    self.pch2.write(self.filename + '.pch2')

  def separate(self, rows):
    self.vert += rows

  def column(self, col):
    horiz = (string.lowercase + string.uppercase).find(col)
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

  def area(self, areaname):
    if areaname == 'voice':
      self.current_area = self.pch2.patch.voice
      self.modules = self.voice_modules
    elif areaname == 'fx':
      self.current_area = self.pch2.patch.fx
      self.modules = self.fx_modules
    else:
      return -1
    return 0

  def add(self, typename, name, label=None):
    if self.modules.has_key(name):
      raise G2Exception('Module %s already exists.' % name)
    if label == None:
      label = name
    self.modules[name] = self.addmodule(typename, label)

  def label(self, param, *names):
    param = self.parse_parameter(param)
    if param == None:
      return -1
    param.label(names)

  def set(self, name, *variations):
    param = self.parse_parameter(name)
    if param == None:
      return -1
    param.set(variations)

  def parse_knob(self, knob):
    rc, index = knob.split('.', 1)
    row, col = list(rc)
    col = 'abcde'.find(col.lower())
    row = '123'.find(row)
    index = '12345678'.find(index)
    if index < 0 or col < 0 or row < 0:
      raise G2Exception('Invalid knob %s.' % knob)
    return knob-1, row, col
    
  def parse_morph(self, morph):
    m = int(morph)-1
    if morph < 0 or morph > 7:
      raise G2Exception('Invalid morph %s.' % morph)
    return m

  def parse_control(self, control, nomorph=False):
    area, param = control.split('.', 1)
    if area == 'voice' or area == 'fx':
      saved_area, saved_modules = self.current_area, self.modules
      self.area(area)
      control = self.parse_parameter(param)
      area_type = self.current_area.index
      self.current_area, self.modules = saved_area, saved_modules
    elif not nomorph and area == 'morph':
      control = self.parse_morph(param)
      area_type = 2
    else:
      raise G2Exception('Invalid control %s' % control)
    return control, area_type

  def knob(self, knob, control):
    knob, row, col = self.parse_knob(knob)
    index = (col * 24) + (row * 8) + knob
    knob = self.pch2.knobs[index]
    knob.param = self.parse_control(control)[0]
    knob.assigned = 1
    knob.isled = 0

  def midicc(self, cc, control):
    cc = int(cc)
    if midicc_reserved(cc):
      raise G2Exception('midicc %d reserved' % cc)
    param, area_type = self.parse_control(control)
    m = None
    for ctrl in self.pch2.ctrls:
      if ctrl.midicc == cc:
        m = ctrl
        break
    if m == None:
      m = Ctrl()
      self.pch2.ctrls.append(m)
    m.midicc = cc
    m.param, m.type = param, area_type
   
  def morph(self, morph, command, *args):
    #control = self.parse_control(control, nomorph=True)[0]
    command = command.lower()
    if command == 'dial':
      pass
    elif command == 'mode':
      pass
    elif command == 'name':
      pass
    elif command == 'add':
      pass

  def table(self, name, filename):
    pass

  def setting(self, setting, *variations):
    nonvariation = [ 'category', 'voices', 'height', 'monopoly', 'variation' ]
    if setting in nonvariation:
      setattr(self.pch2.patch.description, setting, variations[0])
    elif setting in self.pch2.patch.settings.groups:
      #getattr(self.pch2.patch.settings, setting).varations = variations
      pass
    elif setting == 'colors':
      pass

class G2File(object):
  def __init__(self, filename):
    self.g2patch = G2Patch(filename)
    self.topfile = filename
    self.files = { }
    self.file_stack = [ ]
    self.include_path = [ '.' ]

  def parse(self):
    self.build_files(self.topfile)
    self.build()

  def write(self):
    self.g2patch.update_rates()
    self.g2patch.write()

  def find_include(self, filename):
    for include in self.include_path:
      path = os.path.join(include, filename)
      if os.path.exists(path):
        return path
    return ''

  def handle_include(self, filename):
    path = self.find_include(filename)
    if not path:
      raise G2Exception('%s not found in path %s' % (filename,
          self.include_path))
    if path in self.file_stack:
      raise G2Exception('%s include loop.\ncurrent stack %s' % (path,
          self.file_stack))
    self.file_stack.append(path)
    if not path in self.files:
      self.build_files(path)
    self.file_stack.remove(path)

  def build_files(self, filename):
    lines = [ line.rstrip() for line in open(filename).readlines() ]
    self.file_stack = [ filename ]
    self.files[filename] = zip(range(1, 1+len(lines)), lines)
    inmodule = False
    for lineno, line in self.files[filename]:
      line = cleanline(line)
      if not line:
        continue
      fields = line.strip().split()
      if fields[0] == 'module':
        inmodule = True
      if fields[0] == 'endmodule':
        inmodule = False
      elif fields[0] == 'include':
        if inmodule:
          printf('%s:%d - include inside module definition\n', filename, lineno)
        else:
          self.handle_include(fields[1])

  def build_module(self, name, lines):
    module_types[name] = G2GroupType(self.g2patch, lines)

  def build_file(self, filename):
    filelines = []
    module = []
    module_name = ''
    inmodule = 0
    for lineno, line in self.files[filename]:
      debug('%d: %s\n', lineno, line)
      args = cleanline(line).split()
      debug('args=%s\n', args)
      if len(args) < 1:
        continue
      cmd = args.pop(0)
      if cmd == 'module':
        inmodule = 1
        module_name = args[0]
      elif cmd == 'endmodule':
        self.build_module(module_name, module)
        inmodule = 0
        module = []
      elif cmd == 'include':
        path = self.find_include(args[0])
        filelines += self.build_file(path)
      elif inmodule:
        module.append((lineno, line))
      else:
        filelines.append((lineno, line))

    if inmodule:
      printf('%s: no endmodule tag found\n', self.topfile)
      return
      
    return filelines

  def build(self):
    for lineno, line in self.build_file(self.topfile):
      self.parse_command(cleanline(line), lineno)

  def parse_command(self, line, lineno):
    args = [ l.strip().lower() for l in line.split() ]
    if len(args) < 1:
      return
    cmd = args.pop(0)

    debug('%d: %s(%s)\n', lineno, cmd, args)
    try:
      getattr(self.g2patch, cmd)(*args)
    except Exception as e:
      printf('%d: %s\n\t%s\n', lineno, line.rstrip(), e)
      debug('%s\n', traceback.format_exc())

if __name__ == '__main__':
  g2oolsdir = os.path.dirname(sys.argv.pop(0))
  g2file = G2File(sys.argv.pop(0))
  g2file.include_path.append('g2lib')
  g2file.parse()
  g2file.write()

