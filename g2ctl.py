#!/usr/bin/env python2
#
# g 2 c t l
#
import os, struct, sys
from nord import printf
from nord.g2.categories import g2categories
from nord.g2.file import Pch2File
from array import array

# vim: set sw=2:

############################################################
# command processing
class Command:
  def __init__(self, name, params, description, func):
    self.name = name
    self.params = params
    self.description = description
    self.func = func

def debug(fmt, *a):
  if 0:
    printf(fmt, *a)

commands = {}
commandlist = []
def add_command(name, params, desc, func):
  command = Command(name, params, desc, func)
  commands[name] = command
  commandlist.append(command)

def run(name, args):
  error = -1
  if commands.has_key(name):
    command = commands[name]
    func = command.func
    l = len(command.params)
    a = args[:l]
    if len(a) < l:
      printf('error: %s missing %s\n', name,
          ' '.join([ '<%s>' % p for p in command.params[len(a):]]))
      error = -1
    else:
      args[:l] = []
      printf('%s %s\n', name, ' '.join(a))
      error = func(command, *a)
    if error:
       printf('usage: %s %s\n', name,
            ' '.join(['<%s>' % p for p in command.params ]))
    printf('\n')
  else:
    printf('error: bad command "%s"\n', name)
  return error

def process(args):
  error = 0
  while len(args):
    name = args.pop(0)
    error = run(name, args)
    if error:
      break
  return error

prog = ''
# default main
def main(argv):
  global prog
  prog = argv[0]
  try:
    args = argv[1:]
    rc = 0
    printf('\n')
    if len(args) == 0:
      process(['help'])
    rc = process(args)
    if rc:
      printf('use "help" command to see list of commands and arguments.\n')
      rc = -1
  except:
    import traceback
    printf('%s\n', traceback.format_exc())
    rc = -1
  sys.exit(rc)

def clean_line(line):
  cl = line.find('#')
  if cl > -1:
    line = line[:cl]
  return line.strip()

# default script command
def cmd_script(command, filename):
  lines = map(clean_line, open(filename, 'r').readlines())
  newargs = ' '.join(lines).split()
  return process(newargs)
add_command('script', ['file'], 'execute command from <file>', cmd_script)

def wrap_lines(s, maxlen=80):
  lines = []
  words = s.split()
  line = words.pop(0)
  while len(words):
    if len(line) + len(words[0]) + 1 > maxlen:
      lines.append(line)
      line = words.pop(0)
    else:
      line += ' ' + words.pop(0)
  lines.append(line)
  return lines

# default help system
def cmd_help(command):
  global prog
  printf('usage: %s [commands]*\n', prog)
  printf('  commands:\n')
  for command in commandlist:
    sep = ''
    if len(command.params):
      sep = ' '
    params = [ '<%s>' % p for p in command.params ]
    usage = '%s%s%s:' % (command.name, sep, ' '.join(params))
    desc = wrap_lines(command.description, 80-30)
    printf('    %-25s %s\n', usage, desc.pop(0))
    while len(desc):
      printf('    %-25s %s\n', '', desc.pop(0))
  printf('\n  multiple commands are executed consecutively\n')
  return 0
add_command('help', [], 'display list of commands', cmd_help)

######################## g2ctl functions ########################

import struct
import usb

def hexdump(bytes, addr=0, size=1):
  def out(x):
    if x < 32 or x >= 127:
      return '.'
    return chr(x)

  '''hexdump(bytes,addr,size) -> string
  return hex dump of size itmes using addr as address'''
  s = []
  if size == 4:
    a = array('L', [])
    fmt = '%08x'
    l = 17
  elif size == 2:
    a = array('H', [])
    fmt = '%04x'
    l = 19
  else:
    a = array('B', [])
    fmt = '%02x'
    l = 23
  a.fromstring(bytes)
  ofmt = '%04x: %-*s  %-*s | %s'
  for off in range(0, len(bytes), 16):
    hex = [fmt % i for i in a[off/size:(off+16)/size]]
    s.append(ofmt % (addr+off,
      l, ' '.join(hex[:8/size]), l, ' '.join(hex[8/size:]),
      ''.join([out(ord(byte)) for byte in bytes[off:off+16]])))
  return '\n'.join(s)

def crc16(val, icrc):
  k = (((icrc>>8)^val)&0xff)<<8
  crc = 0
  for bits in range(8):
    if (crc^k)&0x8000 != 0:
      crc = (crc<<1)^0x1021
    else:
      crc <<= 1
    k <<= 1
  return (icrc<<8)^crc

def crc(s):
  return reduce(lambda a, b: crc16(ord(b), a), s, 0) & 0xffff

CMD_A    = 0x08
CMD_B    = 0x09
CMD_C    = 0x0a
CMD_D    = 0x0b
CMD_SYS  = 0x0c
CMD_INIT = 0x80
CMD_MASK = 0xf0
CMD_REQ  = 0x20
CMD_SEND = 0x30
CMD_RESP = 0x00

class G2USBInterface:
  def __init__(self):
    vendorid, productid = 0xffc, 2 # clavia, g2

    # find g2 usb device
    g2dev = None
    for bus in usb.busses():
      for device in bus.devices:
        if device.idVendor == vendorid and device.idProduct == productid:
          g2dev = device
    if not g2dev:
      raise Exception('No g2 device found')
    self.g2dev = g2dev

    # get 3 endpoints
    g2conf = g2dev.configurations[0]
    g2intf = g2conf.interfaces[0][0]
    g2eps = g2intf.endpoints
    self.g2iin  = g2eps[0].address
    self.g2bin  = g2eps[1].address
    self.g2bout = g2eps[2].address

    self.g2h = g2dev.open()
    self.g2h.setConfiguration(g2conf)
    self.g2h.reset()

  def bwrite(self, addr, data):
    return self.g2h.bulkWrite(addr, data.tostring()) # self.g2bout

  def bread(self, addr, len, timeout=100):
    try:
      data = self.g2h.bulkRead(addr, len, timeout) # self.g2bin
      return array('B', [ byte & 0xff for byte in data ])
    except:
      return []

  def iread(self, addr, len, timeout=100):
    data = self.g2h.interruptRead(addr, len, timeout) # self.g2iin
    return array('B', [ byte & 0xff for byte in data ])

  def read_message(self):
    try:
      diin = self.iread(self.g2iin, 16, 100)
      s =  hexdump(diin.tostring()).replace('\n','\n       ')
      debug('<%d %s\n', self.g2iin & 0x7f, s)
    except:
      diin = None
    return diin

  def format_message(self, data, type):
    # handle 0x80 (init) messages specially
    if data[0] == CMD_INIT:
      # message 0x80 is just itself
      s = array('B', data).tostring()
    else:
      # messages start with 0x01 0xRC 0xDD 0xDD .. 0xDD
      # C: command (usually just the lower nibble)
      # R: 0x2 when request, 0x0 for response
      #    0x3 ? maybe response-less request
      # DD: data for command
      s = array('B', [0x01]+[data[0]|type]+data[1:]).tostring()

    # messages are sent formatted as bytes:
    # SS SS MM MM MM .. MM CC CC
    # SS: Big endian 16-bit size of message
    # MM: Message (variable length)
    # CC: Big endian 16-bit crc of MM MM .. MM
    l = len(s)+4  # length includes SS SS and CC CC (add 4 bytes)
    c = crc(s)    # calculate the crc
    # encode and send the message to be sent
    ns = array('B', struct.pack('>H%dsH' % len(s), l, s, c))
    # max message len 4096, break message into 4096 byte chunks
    return [ ns[i:i+4096] for i in range(0, len(ns), 4096) ]

  def extended_message(self, din, data):
    sz = (din[1]<<8)|din[2]
    bin = []
    retries = 5 # the message has to return within 5 tries
    while retries != 0 and sz != len(bin):
      bin = self.bread(self.g2bin, sz)
      retries -= 1
    s = hexdump(bin.tostring()).replace('\n','\n   ')
    debug('<%d %s\n', self.g2bin & 0x7f, s)
    if retries == 0:
      raise Exception('Could not get result')
    elif bin[0] == CMD_INIT: # 0x80 special case
      pass
    elif bin[1] == data[0]: # if result is same as command we got message
      pass
    else:
      return None
    
    ecrc = crc(bin[:-2].tostring()) # expected crc
    acrc = (bin[-2]<<8)|bin[-1]     # actual crc
    if ecrc != acrc:
      printf('bad crc exp: 0x%04x act: 0x%04x\n', ecrc, acrc)
    return bin

  def embedded_message(self, din, data):
    dil = din.pop(0)>>4 # length encoded in upper nibble of header byte
    ecrc = crc(din[:dil-2].tostring()) # expected crc
    acrc = (din[dil-2]<<8)|din[dil-1]  # actual crc
    if ecrc != acrc:
      printf('bad crc exp: 0x%04x act: 0x%04x\n', ecrc, acrc)
    return din[:dil]

  def is_extended(self, data):
    return data[0] & 0xf == 1

  def is_embedded(self, data):
    return data[0] & 0xf == 2

  def send_message(self, data, type=CMD_REQ):

    packets = self.format_message(data, type)
    for packet in packets:
      self.bwrite(self.g2bout, packet)
      s = hexdump(packet.tostring()).replace('\n','\n   ')
      debug('>%d %s\n', self.g2bout & 0x7f, s)

    if type != CMD_REQ:
      return ''

    # retry 5 times or til the correct reponse is returned
    # which is usually the command without the request bit (0x20) set
    result = None
    for retries in range(5):
      din = self.bread(self.g2iin, 16, 100)
      if len(din) == 0:
        continue

      # result message first byte:
      #   0xLT 0xDD 0xDD .. 0xDD 0xCC 0xCC (16 0xDD bytes)
      #   T: message type (1=extended message, 2=embedded message)
      #   L: embedded message length (<=0xf, always zero for extended message)
      #   0xDD
      s = hexdump(din.tostring()).replace('\n','\n   ')
      debug('<%d %s\n', self.g2iin & 0x7f, s)
      if self.is_extended(din):
        result = self.extended_message(din, data)
      elif self.is_embedded(din):
        result = self.embedded_message(din, data)

      if result:
        break

    return result

def parse_name(data):
  s = data[:16]
  if type(s) != type(''):
    s = s.tostring()
  null = s.find('\0')
  if null < 0:
    return s, data[16:]
  else:
    return s[:null], data[null+1:]

def format_name(name):
  if len(name) < 16:
    return name + '\0'
  else:
    return name[:16]

###################### commands ########################
class G2Interface(object):

  def __setattr__(self, name, value):
    if self.__dict__.get('usb', None) == None:
      self.__dict__['usb'] = G2USBInterface()
    setattr(self.usb, name, value)

  def __getattr__(self, name):
    if self.__dict__.get('usb', None) == None:
      self.__dict__['usb'] = G2USBInterface()
    return getattr(self.usb, name)

g2usb = G2Interface()

def cmd_list(command):
  JUMP, SKIP, BANK, MODE, CONTINUE = [1, 2, 3, 4, 5]
  LAST = CONTINUE
  PATCH_MODE, PERFORMANCE_MODE, END_MODE = range(3)
  modes = ['Pch2', 'Prf2']
  mode = PATCH_MODE
  bank = 0
  patch = 0
  while mode < END_MODE:
    cmd = [CMD_SYS, 0x41, 0x14, mode, bank, patch]
    data = g2usb.send_message(cmd)
    data = data[9:-2].tostring()
    while len(data):
      c = ord(data[0])
      if c > LAST:
        name, data = parse_name(data)
        category, data = ord(data[0]), data[1:]
        printf('%s %-6s %-9s %s\n', modes[mode],
                '%d:%d' % (bank+1, patch+1), g2categories[category], name)
        patch += 1
      elif c == CONTINUE:
        data = data[1:]
      elif c == BANK:
        bank, patch, data = ord(data[1]), ord(data[2]), data[3:]
      elif c == JUMP:
        patch, data = ord(data[1]), data[2:]
      elif c == SKIP:
        patch, data = patch+1, data[1:]
      elif c == MODE:
        mode, bank, patch, data = mode+1, 0, 0, data[1:]
  return 0
add_command('list', [], 'list all patches and performances', cmd_list)

def read_g2_file(filename):
  data = open(filename).read()
  null = data.find('\0')
  if null < 0:
    printf('invalid pch2 %s\n', filename)
    return []
  return data[null:]

def cmd_loadslot(command, slot, filename):
  data = read_g2_file(filename)
  if len(data) == 0:
    return -1
  data = data[3:-2]
  patchname = format_name(os.path.splitext(os.path.basename(filename))[0])

  slot = 'abcd'.find(slot.lower())
  if slot < 0:
    return -1
  a = array('B', [CMD_A+slot, 0x53, 0x37, 0x00, 0x00, 0x00]) 
  a.fromstring(patchname)
  a.fromstring(data)
  g2usb.send_message(a.tolist())
  return 0
add_command('loadslot', ['slot', 'file'], 'load patch into a slot',
    cmd_loadslot)

def cmd_showslot(command, slot):
  slot = 'abcd'.find(slot.lower())
  if slot < 0:
    return -1
  sloti = g2usb.send_message([CMD_SYS, 0x41, 0x35, slot])
  data = g2usb.send_message([CMD_A+slot, sloti[5], 0x3c])
  name = g2usb.send_message([CMD_A+slot, sloti[5], 0x28])
  name, junk = parse_name(name[4:])
  #printf("%s\n", hexdump(data[1:-2].tostring()))
  pch2 = Pch2File()
  data = data[0x03:0x15] + data[0x17:-2]
  pch2.parse(data.tostring(), 0)

  from pch2tog2 import print_patch
  printf('# %s\n', name)
  print print_patch(pch2.patch)
  return 0
add_command('showslot', ['slot'], 'show patch in a slot',
    cmd_showslot)

def parse_bank_patch(location):
  bank, patch = map(int, location.split(':'))
  if bank < 1 or bank > 32:
    printf('invalid bank %d, must be 1 to 32\n', bank)
    return -1, -1
  if patch < 1 or patch > 127:
    printf('invalid patch %d, must be 1 to 127\n', patch)
    return -1, -1
  return bank, patch

def cmd_store(command, location, filename):
  data = read_g2_file(filename)
  l = len(data)
  if l == 0:
    return -1
  bank, patch = parse_bank_patch(location)
  if bank < 0:
    return -1
  name, ext = os.path.splitext(os.path.basename(filename))
  name = format_name(name)
  printf('%s %s\n', name, ext)
  if ext.lower() == '.prf2':
    mode = 1
  else:
    mode = 0
  printf("%d:%d %s\n", bank, patch, name)
  a = array('B', [CMD_SYS, 0x41, 0x19, mode, bank-1, patch-1])
  a.fromstring(name)
  a.extend([ (l>>8)&0xff, l&0xff, 0x17 ])
  a.fromstring(data)
  g2usb.send_message(a.tolist())
  return 0
add_command('store', ['loc', 'file'], 'store file at location', cmd_store)

def cmd_clear(command, location):
  bank, patch = parse_bank_patch(location)
  if bank < 1:
    return -1
  if patch < 1 or 128 < patch:
    return -1
  g2usb.send_message([CMD_SYS, 0x41, 0x0c, 0x00, bank-1, patch-1, 0x00])
  return 0
add_command('clear', ['loc'], 'clear location', cmd_clear)

def cmd_dump(command, bank):
  bank = int(bank) - 1
  if bank < 0:
    return -1
  #name, ext = os.path.splitext(os.path.basename(filename))
  #name = format_name(name)
  #printf('%s %s\n', name, ext)
  for patch in range(128):
    data = g2usb.send_message([CMD_SYS, 0x41, 0x17, 0x00, bank, patch])
    if data[3] == 0x18:
      continue
    data = data[5:]
    #bank, patch = data[:2]
    name, data = parse_name(data[2:])
    printf('%d:%d %s\n', bank+1, patch+1, name)
  #print hexdump(pch2.tostring())
  return 0
add_command('dump', ['loc'], 'dump location to .pch2 file', cmd_dump)

def cmd_settings(command):
  g2usb.send_message([CMD_SYS, 0x41, 0x35, 0x04])
  syst = g2usb.send_message([CMD_SYS, 0x41, 0x02])
  synthname, syst = parse_name(syst[4:])
  printf('%s:\n', synthname)
  printf(' mode: %s\n', ['Patch', 'Performance'][syst[0]>>7])
  printf(' midi:\n')
  printf('  slots: a:%d b:%d c:%d d:%d glob:%d\n', *syst[5:5+5])
  printf('  sysex: %d\n', syst[10]+1)
  printf('  local: %s\n', ['off','on'][syst[11]>>7])
  printf('  prgch: %s\n', ['off','send','recv','send/recv'][syst[12]])
  printf('  clkse: %s\n', ['on','off'][(syst[13]>>6)&1])
  printf('  clkre: %s\n', ['on','off'][(syst[13]>>5)&1])
  printf(' tune semi: %d\n', struct.unpack('b',chr(syst[18]))[0])
  printf(' tune cent: %d\n', struct.unpack('b',chr(syst[15]))[0])
  printf(' pedal polarity: %s\n', ['open','closed'][syst[20]>>7])
  printf(' pedal gain: %.2f\n', 1.0 + 0.5*syst[21]/32)
  sels = g2usb.send_message([CMD_SYS, 0x41, 0x81])
  data = g2usb.send_message([CMD_SYS, sels[2], 0x10])
  perfname, data = parse_name(data[4:])
  if syst[0] >> 7:
    printf('Performance: %s\n', perfname)
  else:
    printf('Patches:\n')
  printf(' focus: %s\n', 'abcd'[(data[4]>>2)&3])
  printf(' range enable: %s\n', ['off','on'][0x01 & data[5]])
  printf(' master clock: %d BPM: %s\n', data[6], ['stop','run'][data[8]&0x01])
  printf(' kb split: %s\n', ['off','on'][0x01 & data[7]])
  data = data[11:]
  for slot in range(4):
    name, data = parse_name(data)
    fields = data[:10]
    active, key, hold, bank, patch, low, high = fields[:7]
    printf(' slot %s: %d:%d "%-16s"\n', 'abcd'[slot], bank+1, patch+1, name)
    printf('  active: %-3s, ', ['off','on'][active])
    printf('key: %-3s, ', ['off','on'][key])
    printf('hold: %-3s, ', ['off','on'][hold])
    printf('range: %d-%d\n', low, high)
    data = data[10:]
  return 0
add_command('settings', [], 'print patch performance settings',
    cmd_settings)

def cmd_slot(command, slot):
  ion = g2usb.send_message([CMD_SYS, 0x41, 0x7d, 0x00])
  slot = 'abcd'.find(slot.lower())
  if slot < 0:
    retur -1
  g2usb.send_message([CMD_SYS, ion[3], 0x07, 0x08>>slot, 0x0f, 0x08>>slot])
  g2usb.send_message([CMD_SYS, ion[3], 0x09, slot])
  g2usb.send_message([CMD_A+slot, 0x0a, 0x70])
  return 0
add_command('slot', ['slot'], 'select slot (A,B,C,D)', cmd_slot)

def cmd_variation(command, variation):
  variation = int(variation)
  if variation < 1 or 8 < variation:
    return -1
  slota = g2usb.send_message([CMD_SYS, 0x41, 0x35, 0x00])
  g2usb.send_message([CMD_A, slota[5], 0x6a, variation-1])
  return 0
add_command('variation', ['variation'], 'select variation', cmd_variation)
 
def cmd_parameterpage(command, page):
  row = 'abcde'.find(page[0].lower())
  if row < 0:
    printf('Invalid row %s\n', page[0].lower())
    return -1
  col = int(page[1]) - 1
  if col < 0 or 2 < col:
    printf('Invalid col %d\n', col)
    return -1
  slota = g2usb.send_message([CMD_SYS, 0x41, 0x35, 0x00])
  g2usb.send_message([0x08, slota[6], 0x2d, (row*3)+col])
  return 0
add_command('parameterpage', ['page'], 'select parameterpage',
    cmd_parameterpage)

def cmd_sleep(command, seconds):
  import time
  seconds = float(seconds)
  time.sleep(seconds)
add_command('sleep', ['seconds'], 'sleep for seconds', cmd_sleep)
if __name__ == '__main__':
  main(sys.argv)

