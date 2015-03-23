#!/usr/bin/env python2

import os, string, sys, traceback
from nord.g2.file import Pch2File, Prf2File, MorphMap
from nord.g2.file import NVARIATIONS, NMORPHS, NMORPHMAPS
from nord.g2.misc import handle_uprate, midicc_reserved
from nord.g2.colors import g2cablecolors, g2conncolors, g2modulecolors
from nord import printf
from nord.file import Ctrl

DEBUG = 1

def debug(fmt, *a):
  if DEBUG:
    printf(fmt, *a)

class G2Exception(Exception):
  pass

def clean_line(line):
  comment = line.find('#')
  if comment < 0:
    return line.strip()
  else:
    return line[:comment].strip()

class G2Param(object):
  def __init__(self, param):
    self.param = param

  def set(self, *a):
    for i in range(NVARIATIONS):
      v = a[i % len(a)]
      if v[0] == '.':
        name = v[1:]
        map = self.param.type.type.map[0]
        if not map.has_key(name):
          raise G2Exception('No name %s: pick from %s' % (v[1:], map.keys()))
        v = map[name]
      self.param.variations[i] = int(v)

  def label(self, *a):
    labels = [ label.strip() for label in (' '.join(a)).split(':') ]
    self.param.labels = labels

class G2Mode(object):
  def __init__(self, mode):
    self.mode = mode

class G2Morph(object):
  def __init__(self, morph):
    self.morph = morph
    self.params = {
      'mode': G2Param(self.morph.mode),
      'dial': G2Param(self.morph.dial),
    }

class G2ModulePort(object):
  def __init__(self, port):
    self.port = port

class G2Module(object):
  def __init__(self, module):
    self.module = module
    self.height = self.module.type.height
    self.params = { }
    self.modes = { }
    self.ports = { }
    self.setup()

  def setup(self):
    self.params = { }
    module = self.module
    for param in module.params:
      self.params[param.type.name.lower()] = G2Param(param)
    for mode in module.modes:
      self.modes[mode.type.name.lower()] = G2Mode(mode)

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

class ModuleTypes(object):
  def __init__(self):
    self.types = { }

  def add(self, name, type):
    self.types[name] = type

  def get(self, name):
    if self.types.has_key(name):
      return self.types[name]
    else:
      return G2ModuleType(name)

module_types = ModuleTypes()

class G2Section(object):
  def __init__(self, section):
    self.cable_color = g2cablecolors.white
    self.module_color = g2modulecolors.grey
    self.section = section
    self.modules = { }
    self.horiz = section.horiz
    self.vert = section.vert
    self.actions = { }
    self.actions['connect']     = self.connect
    self.actions['cablecolor']  = self.cablecolor
    self.actions['modulecolor'] = self.modulecolor

  def add_module(self, typename, label):
    module_type = module_types.get(typename)
    section = self.section
    module = module_type.add(section.current_area, name=label,
        horiz=section.horiz, vert=section.vert, color=section.module_color)
    section.vert += module.height
    return module

  def parse_member(self, path):
    module_name, postfix = path.split('.')
    module = self.modules.get(module_name)
    if not module:
      raise G2Exception('No module "%s".' % module_name)
    return module, postfix

  def parse_connection(self, connection):
    module, name = self.parse_member(connection)
    port = module.ports.get(name)
    if not port:
      raise G2Exception('No port "%s" on module "%s".' % (name, connection))
    return port

  def parse_parameter(self, parameter):
    module, name = self.parse_member(parameter)
    param = module.params.get(name)
    if not param:
      raise G2Exception('No param "%s" on module "%s"' % (name, param))
    return param

  def parse_mode(self, path):
    module, name = self.parse_member(path)
    mode = module.modes.get(name)
    if not mode:
      raise G2Exception('No mode "%s" on module "%s"' % (name, path))
    return mode

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

class G2ModelParamCalc(object):
  def __init__(self, param, equation):
    self.param = param
    self.equation = equation

class G2ModelParam(object):
  def __init__(self, model, name, default, minimum, maximum):
    self.calcs = []
    self.model = model
    self.name = name
    self.variations = [ int(default) ] * NVARIATIONS
    self.minimum = minimum
    self.maximum = maximum

  def add_calc(self, param, equation):
    self.calcs.append(G2ModelParamCalc(param, equation))
    variations = self.variations[:]
    self.set(*variations)

  def setup_vars(self, variation, value):
    paramvars = { }
    for param in self.model.params:
      paramvars[param] = self.model.params[param].variations[variation]
    paramvars[self.name] = value
    return paramvars

  #def set(self, *variations):
  #  for variation in range(len(variations)):
  #    value = variations[variation]
  #    self.variations[variation] = value
  #  for calc in self.calcs:
  #    values = []
  #    for variation in range(len(variations)):
  #      paramvars = self.setup_vars(variation, value)
  #      value = eval(calc.equation, paramvars)
  #      values.append('%s' % value)
  #    calc.param.set(values)
  def set(self, *variations):
    for i in range(NVARIATIONS):
      v = variations[i % len(variations)]
      self.variations[i] = v
    self.model.do_calc()

  def label(self, *a):
    pass

class G2Model(G2Section):
  def __init__(self, section):
    super(G2Model, self).__init__(section)
    self.calcs = []
    self.params = { }
    self.ports = { }
    self.height = 0
    self.actions['add']    = self.add
    self.actions['set']    = self.set
    self.actions['label']  = self.label
    self.actions['param']  = self.param
    self.actions['mparam'] = self.mparam
    self.actions['calc']   = self.calc
    self.actions['input']  = self.input
    self.actions['output'] = self.output

  def add(self, typename, name):
    name = self.name + '-' + name
    self.modules[name] = self.add_module(typename, name)

  def connect(self, *args):
    args = [ self.name + '-' + arg for arg in args ]
    G2Section.connect(self, *args)

  def separate(self, rows):
    self.section.vert += int(rows)

  def set(self, name, *variations):
    name = self.name + '-' + name
    param = self.parse_parameter(name)
    if param == None:
      raise G2Exception('No parameter "%s"' % name)
    param.set(*variations)
    #getattr(param, 'set', map(int, variations))

  def label(self, param, *names):
    param = self.name + '-' + param
    param = self.parse_parameter(param)
    if param == None:
      return -1
    param.label(*names)

  def param(self, name, default, minimum, maximum):
    self.params[name] = G2ModelParam(self, name, default, minimum, maximum)

  def mparam(self, name, parameter, default):
    modparam = self.parse_parameter(parameter)
    type = modparam.param.type.type
    self.params[name] = G2ModelParam(self, name, default, type.low, type.high)
    self.params[name].add_calc(modparam, name)

  def add_calc(self, param, equation):
    self.calcs.append(G2ModelParamCalc(param, equation))

  def setup_vars(self, variation):
    paramvars = { }
    for param in self.params:
      paramvars[param] = self.params[param].variations[variation]
    return paramvars

  def do_calc(self):
    for calc in self.calcs:
      variations = []
      for variation in range(NVARIATIONS):
        paramvars = self.setup_vars(variation)
        variations.append(str(eval(calc.equation, paramvars)))
      calc.param.set(*variations)

  def calc(self, parameter, equation):
    parameter = self.name + '-' + parameter
    param = self.parse_parameter(parameter)
    self.add_calc(param, equation)

  def port(self, name, modport):
    modport = self.name + '-' + modport
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
    module = G2Module(area.add_module(self.shortnm, **kw))
    self.height = module.module.type.height
    return module

class G2ModelType(object):
  def __init__(self, g2patch, code):
    self.g2patch = g2patch
    self.code = code

  def add(self, area, **kw):
    gm = G2Model(self.g2patch)
    gm.name = kw['name']
    d = ' '.join('%s=%s' % (k, kw[k]) for k in kw)
    # save colors, setup models colors
    gm.cable_color = orig_cable_color  = self.g2patch.cable_color
    gm.module_color = orig_module_color = self.g2patch.module_color
    for lineno, line in self.code:
      self.g2patch.cable_color = gm.cable_color
      self.g2patch.module_color = gm.module_color
      args = [ l.lower() for l in line.split() ]
      cmd = args.pop(0)
      debug('model %d: %s(%s) %s\n', lineno, cmd, args, d)
      try:
        getattr(gm, cmd)(*args)
      except G2Exception as e:
        printf('%d: %s\n\t%s\n', lineno, line.strip(), e)
        debug('%s\n', traceback.format_exc())
    gm.height = 0 # height calculated on each module
    # restore colors
    self.g2patch.cable_color  = orig_cable_color
    self.g2patch.module_color = orig_module_color
    return gm

class G2Patch(G2Section):
  def __init__(self, filename):
    global g2oolsdir
    self.horiz = 0
    self.vert = 0
    G2Section.__init__(self, self)
    self.pch2 = Pch2File(os.path.join(g2oolsdir, 'initpatch.pch2'))
    self.filename = filename[:filename.rfind('.')]
    self.current_area = self.pch2.patch.voice
    self.variations = range(9)
    self.voice_modules = { }
    self.fx_modules = { }
    self.modules = self.voice_modules
    self.actions['separate'] = self.separate
    self.actions['column']   = self.column
    self.actions['area']     = self.area
    self.actions['add']      = self.add
    self.actions['label']    = self.label
    self.actions['mode']     = self.mode
    self.actions['set']      = self.set
    self.actions['knob']     = self.knob
    self.actions['midicc']   = self.midicc
    self.actions['setting']  = self.setting

  def update_inputs(self, net, uprate):
    # loop through all net inputs
    # get proper color based on rate
    # update all cables connected to each input
    for input in net.inputs:
      if not net.output:
        continue

      color = g2cablecolors.white
      rate = net.output.rate
      if rate == g2conncolors.blue_red:
        color = [g2cablecolors.blue, g2cablecolors.red][uprate]
      elif rate == g2conncolors.red:
        color = g2cablecolors.red
      elif rate == g2conncolors.blue:
        color = g2cablecolors.blue
      elif rate == g2conncolors.yellow_orange:
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

  def parse_knob(self, knob):
    rowcol, index = knob.split('.', 1)
    row, col = list(rowcol)
    row = 'abcde'.find(row.lower())
    col = '123'.find(col)
    index = '12345678'.find(index)
    if index < 0 or col < 0 or row < 0:
      raise G2Exception('Invalid knob %s.' % knob)
    return index, row, col

  def parse_morph(self, morph):
    name, morph = morph.split('.', 1)
    return self.pch2.patch.settings.morphs[int(morph)-1]

  def parse_morph_param(self, morph_param):
    name, morphi, param = morph_param.split('.')
    morph = self.pch2.patch.settings.morphs[int(morphi)-1]
    if param == 'mode':
      return morph.mode
    elif param == 'dial':
      return morph.dial

  def is_area(self, name):
    return name in [ 'voice', 'fx', 'settings' ]

  def parse_control(self, control, nomorph=False):
    area_or_module, param = control.split('.', 1)
    if self.is_area(area_or_module):
      saved_area, saved_modules = self.current_area, self.modules
      self.area(area_or_module)
      control = self.parse_parameter(param)
      area_type = self.current_area.index
      self.current_area, self.modules = saved_area, saved_modules
    elif not nomorph and area_or_module == 'morph':
      control = int(param) - 1
      if not (0 < control < NMORPHS):
        raise G2Exception('Invalid morph %s.' % param)
      area_type = 2
    else:
      control = self.parse_parameter(control)
      area_type = self.current_area.index
    return control, area_type

  def separate(self, rows):
    self.vert += int(rows)

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

  def area(self, area_name):
    if area_name == 'voice':
      self.current_area = self.pch2.patch.voice
      self.modules = self.voice_modules
    elif area_name == 'fx':
      self.current_area = self.pch2.patch.fx
      self.modules = self.fx_modules
    else:
      self.current_area = self.pch2.patch.settings.area
      self.modules = None
      return -1
    return 0

  def add_morph(self, morph, variation, control, range):
    settings = self.pch2.patch.settings
    if len(settings.morphmaps) >= NMORPHMAPS:
      raise G2Exception('Only %d morphs allowed per variation' % NMORPHMAPS)
    morph = self.parse_morph(morph)
    morph_map = MorphMap()
    morph_map.variation = int(variation)  # make variations base 1
    param, area_type = self.parse_control(control)
    morph_map.param = param.param
    morph_map.range = int(range)
    morph_map.morph = morph
    morph_map.morph.maps[morph_map.variation].append(morph_map)
    settings.morphmaps[morph_map.variation].append(morph_map)

  def add(self, typename, name, *args):
    if typename.startswith('morph'):
      return self.add_morph(typename, name, *args)

    if self.modules.has_key(name):
      raise G2Exception('Module %s already exists.' % name)
    if len(args) == 0:
      label = name
    else:
      label = ' '.join(args)
      if label[0] == '"' or label[0] == "'":
        label = label[1:-1]
    self.modules[name] = self.add_module(typename, label)

  def label(self, param, *name):
    if param.startswith('morph'):
      morph = self.parse_morph(param)
      morph.label = ' '.join(name)
    else:
      param = self.parse_parameter(param)
      if param == None:
        return -1
      param.label(*name)

  def set_morph(self, name, *args):
    morph = self.parse_morph_param(name)

  def mode(self, name, value):
    mode = self.parse_mode(name)
    if mode == None:
      raise G2Exception('Node mode %s' % name)
    mode.value = int(value)

  def set(self, name, *variations):
    if name.startswith('morph'):
      return self.set_morph(name, *variations)

    param = self.parse_parameter(name)
    if param == None:
      return -1
    param.set(*variations)

  def knob(self, knob, control):
    knob, row, col = self.parse_knob(knob)
    index = (col * 24) + (row * 8) + knob
    knob = self.pch2.patch.knobs[index]
    param, area_type = self.parse_control(control)
    knob.param = param.param
    knob.assigned = 1
    knob.isled = 0

  def midicc(self, cc, control):
    cc = int(cc)
    if control.startswith('setting'):
      return
    if midicc_reserved(cc):
      #raise G2Exception('midicc %d reserved' % cc)
      printf('midicc %d reserved\n', cc)
      return
    new_ctrl = None
    ctrls = self.pch2.patch.ctrls
    for ctrl in ctrls:
      if ctrl.midicc == cc:
        new_ctrl = ctrl
        break
    if new_ctrl == None:
      new_ctrl = Ctrl()
      ctrls.append(new_ctrl)
    new_ctrl.midicc = cc
    new_ctrl.param, new_ctrl.type = self.parse_control(control)

  def table(self, name, filename):
    pass

  def setting(self, setting, *variations):
    nonvariation = [ 'voices', 'height', 'monopoly', 'variation' ]
    if setting in nonvariation:
      setattr(self.pch2.patch.description, setting, int(variations[0]))
    elif setting in self.pch2.patch.settings.groups:
      variations = map(int, variations)
      variations = variations[:] + [variations[-1]] * 9
      variations = variations[:9]
      getattr(self.pch2.patch.settings, setting).varations = variations
    elif setting == 'category':
      self.pch2.patch.description.category = 0
    elif setting == 'cables':
      for color in 'red blue yellow orange green purple white'.split():
        if color[0].lower() in variations[0]:
          setattr(self.pch2.patch.description, color, 1)
        else:
          setattr(self.pch2.patch.description, color, 0)

class G2File(object):
  def __init__(self, filename):
    self.g2patch = G2Patch(filename)
    self.topfile = filename
    self.files = { }
    self.file_stack = [ ]
    self.include_path = [ '.' ]

  def slot(self, slot_location, name):
    pass

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

  def parse_command(self, line, lineno):
    args = line.split()
    if len(args) < 1:
      return
    cmd = args.pop(0).lower()

    debug('%d: %s(%s)\n', lineno, cmd, args)
    try:
      self.g2patch.actions[cmd](*args)
    except Exception as e:
      printf('%d: %s\n\t%s\n', lineno, line.rstrip(), e)
      debug('%s\n', traceback.format_exc())

  def build(self):
    for lineno, line in self.build_file(self.topfile):
      self.parse_command(clean_line(line), lineno)

  def build_files(self, filename):
    lines = [ line.rstrip() for line in open(filename).readlines() ]
    self.file_stack = [ filename ]
    #self.files[filename] = list(enumerate(lines, 1)
    self.files[filename] = zip(range(1, 1+len(lines)), lines)
    in_module = False
    for lineno, line in self.files[filename]:
      line = clean_line(line)
      if not line:
        continue
      fields = line.strip().split()
      if   fields[0] == 'model':
        in_module = True
      elif fields[0] == 'endmodel':
        in_module = False
      elif fields[0] == 'include':
        if in_module:
          printf('%s:%d - include inside model definition\n', filename, lineno)
        else:
          self.handle_include(fields[1])

  def build_group(self, name, code):
    module_types.add(name, G2ModelType(self.g2patch, code))

  def build_file(self, filename):
    filelines = []
    module = []
    module_name = ''
    in_module = 0
    for lineno, line in self.files[filename]:
      #debug('%d: %s\n', lineno, line)
      args = clean_line(line).split()
      #debug('args=%s\n', args)
      if len(args) < 1:
        continue
      cmd = args.pop(0)
      if   cmd == 'model':
        in_module = 1
        module_name = args[0]
      elif cmd == 'endmodel':
        self.build_group(module_name, module)
        in_module = 0
        module = []
      elif cmd == 'include':
        path = self.find_include(args[0])
        filelines += self.build_file(path)
      elif in_module:
        module.append((lineno, line))
      else:
        filelines.append((lineno, line))

    if in_module:
      printf('%s: no endmodel tag found\n', self.topfile)
      return

    return filelines

  def parse(self):
    self.build_files(self.topfile)
    self.build()

if __name__ == '__main__':
  g2oolsdir = os.path.dirname(sys.argv.pop(0))
  g2file = G2File(sys.argv.pop(0))
  g2file.include_path.append('g2lib')
  g2file.parse()
  g2file.write()

