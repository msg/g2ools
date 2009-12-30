#!/usr/bin/env python

import struct, sys
from array import array
from home import hexdump
from nord import printf

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
  return  reduce(lambda a,b: crc16(ord(b),a),s,0) & 0xffff

sectiondesc = [
  'Patch Description',
  'Module List',
  'Module List',
  'Mystery Object 1',
  'Cable List',
  'Cable List',
  'Patch Settings',
  'Module Parameters',
  'Module Parameters',
  'Mystery Object 2',
  'Knob Assignment',
  'MIDI Control Assignments',
  'Mystery Object 3',
  'Mystery Object 3',
  'Mystery Object 3',
  'Module Names',
  'Module Names',
  'Textpad',
]

def getbits(bit,nbits,data):
  def getbits(x, p, n):
    return (x >> p) & ~(~0<<n)
  # grab 32-bits starting with the byte that contains bit
  byte = bit>>3
  s = data[byte:byte+4].tostring()
  # align size to a 32-bit word
  s += '\x00' * (4-len(s))
  long = struct.unpack('>L',s)[0]
  return bit+nbits,getbits(long,32-(bit&7)-nbits,nbits)

def setbits(bit,nbits,data,value):
  def setbits(x, p, n, y):
    m = ~(~0<<n)
    return (x&~(m<<p))|((m&y)<<p)
  # grab 32-bits starting with the byte that contains bit
  byte = bit>>3
  s = data[byte:byte+4].tostring()
  # align size to a 32-bit word
  s += '\x00' * (4-len(s))
  long = struct.pack('>L',s)[0]
  long = setbits(long,32-(bit&7)-nbits,nbits,value)
  data[byte:byte+4] = struct.pack('>L',long)[:len(s)]
  return bit+nbits

#def getbits(bit,nbits,data):
#  byte = bit>>3
#  msb = 8-(bit&7)
#  #printf('len(data)=%d byte=%d bit=%d nbits=%d\n',len(data), byte, bit, nbits)
#  bit += nbits
#  lsb = msb - nbits
#  if lsb >= 0:
#    val = (data[byte]>>lsb)&~(~0<<nbits)
#  else:
#    val = data[byte]&~(~0<<msb)
#    nbits -= msb
#    byte += 1
#    while lsb < 0:
#      lsb = 8 - nbits
#      val = (val<<8)|data[byte]
#      byte += 1
#      nbits -= 8
#    val >>= lsb
#  return bit,val

def printval(nm, val):
  printf(' %s=0x%x(%d)\n', nm, val, val)

def parsepatchdesc(data):
  bit = 7*8
  bit, unknown1 = getbits(bit,5,data)
  printval('unknown1',unknown1)
  bit, nvoices = getbits(bit,5,data)
  printval('nvoices',nvoices)
  bit, height = getbits(bit,14,data)
  printval('height',height)
  bit, unknown2 = getbits(bit,3,data)
  printval('unknown2',unknown2)
  bit, red = getbits(bit,1,data)
  printval('red',red)
  bit, blue = getbits(bit,1,data)
  printval('blue',blue)
  bit, yellow = getbits(bit,1,data)
  printval('yellow',yellow)
  bit, orange = getbits(bit,1,data)
  printval('orange',orange)
  bit, green = getbits(bit,1,data)
  printval('green',green)
  bit, purple = getbits(bit,1,data)
  printval('purple',purple)
  bit, white = getbits(bit,1,data)
  printval('white',white)
  bit, monopoly = getbits(bit,2,data)
  printval('monopoly',monopoly)
  bit, variation = getbits(bit,8,data)
  printval('variation',variation)
  bit, category = getbits(bit,8,data)
  printval('category',category)

def parsemodulelist(data):
  bit, location = getbits(0,2,data)
  printval('location',location)
  bit, nmodules = getbits(bit,8,data)
  printval('nmodules',nmodules)
  for mod in range(nmodules):
    print(' mod %d' % mod)
    bit, modtype = getbits(bit,8,data)
    printval(' modtype',modtype)
    bit, modindex = getbits(bit,8,data)
    printval(' modindex',modindex)
    bit, horiz = getbits(bit,7,data)
    printval(' horiz',horiz)
    bit, vert = getbits(bit,7,data)
    printval(' vert',vert)
    bit, color = getbits(bit,8,data)
    printval(' color',color)
    bit, unknown1 = getbits(bit,8,data)
    printval(' unknown1',unknown1)
    bit, nstatic = getbits(bit,4,data)
    printval(' nstatic',nstatic)
    for static in range(nstatic):
      print('  static %d' % static)
      bit, val = getbits(bit,6,data)
      printval('  val',val)

def parsecablelist(data):
  bit, location = getbits(0,2,data)
  printval('location',location)
  bit, ncables = getbits(16,8,data)
  printval('ncables',ncables)
  for cable in range(ncables):
    printf(' cable %d\n', cable)
    bit, color = getbits(bit,3,data)
    printval(' color',color)
    bit, modfrom = getbits(bit,8,data)
    printval(' modfrom',modfrom)
    bit, jackfrom = getbits(bit,6,data)
    printval(' jackfrom',jackfrom)
    bit, cabletype = getbits(bit,1,data)
    printval(' cabletype',cabletype)
    bit, modto = getbits(bit,8,data)
    printval(' modto',modto)
    bit, jackto = getbits(bit,6,data)
    printval(' jackto',jackto)

def parsepatchsettings(data):
  printf('%s\n',hexdump(data.tostring()))
  printf(' unknown %s',hexdump(data[:6].tostring()))
  bit = 6*8
  N=9
  for i in range(N): # morph groups
    printf(' %d\n', i)
    bit+=6*8
    for morph in range(8):
      bit, morphgroup = getbits(bit,8,data)
      printval(' morphgroup%d' % morph, morphgroup)
    bit+=8
  for i in range(N): # variation volume/active
    printf(' Volume/Active %d\n', i)
    bit, variation = getbits(bit,8,data)
    printval(' variation', variation)
    bit, patchvol = getbits(bit,8,data)
    printval(' patchvol', patchvol)
    bit, activemuted = getbits(bit,6,data)
    printval(' activemuted', activemuted)
  bit+=15
  for i in range(N): # variation glide
    printf(' Glide %d\n', i)
    bit, variation = getbits(bit,8,data)
    printval(' variation', variation)
    bit, glide = getbits(bit,7,data)
    printval(' glide', glide)
    bit, time = getbits(bit,7,data)
    printval(' time', time)
  bit+=15
  for i in range(N): # variation bend
    printf(' Bend %d\n', i)
    bit, variation = getbits(bit,8,data)
    printval(' variation', variation)
    bit, bend = getbits(bit,7,data)
    printval(' bend', bend)
    bit, semi = getbits(bit,7,data)
    printval(' semi', semi)
  bit+=15
  for i in range(N): # variation vibrato
    printf(' Vibrato %d\n', i)
    bit, variation = getbits(bit,8,data)
    printval(' variation', variation)
    bit, vibrato = getbits(bit,7,data)
    printval(' vibrato', vibrato)
    bit, cents = getbits(bit,7,data)
    printval(' cents', cents)
    bit, rate = getbits(bit,7,data)
    printval(' rate', rate)
  bit+=15
  for i in range(N): # variation arpeggiator
    printf(' Arpeggiator %d\n', i)
    bit, variation = getbits(bit,8,data)
    printval(' variation', variation)
    bit, arpeggiator = getbits(bit,7,data)
    printval(' arpeggiator', arpeggiator)
    bit, time = getbits(bit,7,data)
    printval(' time', time)
    bit, arptype = getbits(bit,7,data)
    printval(' arptype', arptype)
    bit, octaves = getbits(bit,7,data)
    printval(' octaves', octaves)
  bit+=15
  for i in range(N): # variation octave shift
    printf(' Octave Shift %d\n', i)
    bit, variation = getbits(bit,8,data)
    printval(' variation', variation)
    bit, octaveshift = getbits(bit,7,data)
    printval(' octaveshift', octaveshift)
    bit, sustain = getbits(bit,7,data)
    printval(' sustain', sustain)

def parsemoduleparams(data):
  bit, location = getbits(0,2,data)
  printval('location', location)
  bit, nmodules = getbits(bit,8,data)
  printval('nmodules', nmodules)
  bit, unknown = getbits(bit,8,data)
  printval('unknown', unknown)
  for mod in range(nmodules):
    printf(' mod %d\n', mod)
    bit, moduleidx = getbits(bit,8,data)
    printval(' moduleidx', moduleidx)
    bit, nparams = getbits(bit,7,data)
    printval(' nparams', nparams)
    for i in range(9):
      bit, variation = getbits(bit,8,data)
      printval('  variation', variation)
      printf('    ')
      for param in range(nparams):
	bit, val = getbits(bit,7,data)
	printf('%d=%03d ', param, val)
      printf('\n')
      if variation > 8:
        printf('bad variation\n')
	return

def parseknobassignments(data):
  bit, nknobs = getbits(0,16,data)
  for i in range(nknobs):
    bit, assigned = getbits(bit,1,data)
    if assigned:
      bit,unknown = getbits(bit,2,data)
      bit,moduleidx = getbits(bit,8,data)
      bit,unknown = getbits(bit,2,data)
      bit,paramidx = getbits(bit,7,data)
      printf('  %s%d-%d\n', 'ABCDE'[i/24],(i%24)>>3,(i%24)&7)
      printval('  moduleidx',moduleidx)
      printval('  paramidx',paramidx)

def parsemidicontroller(data):
  bit, nassignments = getbits(0,7,data)
  printval(' nassignments',nassignments)
  for i in range(nassignments):
    printf(' %d\n', i)
    bit,midicc = getbits(bit,7,data)
    printval('  midicc',midicc)
    bit,assigntype = getbits(bit,2,data)
    printval('  assigntype',assigntype)
    bit,moduleidx = getbits(bit,8,data)
    printval('  moduleidx',moduleidx)
    bit,paramidx = getbits(bit,7,data)
    printval('  paramidx',paramidx)

def parsemodulenames(data):
  bit,location = getbits(0,2,data)
  printval(' location',location)
  bit,unknown = getbits(bit,6,data)
  printval(' unknown',unknown)
  bit,nmodules = getbits(bit,8,data)
  printval(' nmodules',nmodules)
  names = data[bit/8:].tostring()
  for i in range(nmodules):
    null = names.find('\0')
    moduleidx,name = ord(names[0]),names[1:null]
    printf(' %03d: %s\n', moduleidx, name)
    names = names[null+1:]

def parseempty(data):
  pass

parse = [
  parsepatchdesc,
  parsemodulelist,
  parsemodulelist,
  None, # parsemysteryobject1,
  parsecablelist,
  parsecablelist,
  parsepatchsettings,
  parsemoduleparams,
  parsemoduleparams,
  None, # parsemysteryobject2,
  parseempty, # parseknobassignments,
  parseempty, # parsemidicontroller,
  None, # parsemysteryobject3,
  None, # parsemysteryobject3,
  None, # parsemysteryobject3,
  parseempty, # parsemodulenames,
  parseempty, # parsemodulenames,
  None, # parsetextpad,
]

class PatchDescription:
  def parse(self, data):
    pass

class ModuleList:
  def parse(self, data):
    pass

class Unknown1:
  def parse(self, data):
    pass

class CableList:
  def parse(self, data):
    pass

class PatchSettings:
  def parse(self, data):
    pass

class ModuleParameters:
  def parse(self, data):
    pass

class Unknown2:
  def parse(self, data):
    pass

class KnobAssignment:
  def parse(self, data):
    pass

class MIDIControlAssignments:
  def parse(self, data):
    pass

class Unknown3:
  def parse(self, data):
    pass

class ModuleNames:
  def parse(self, data):
    pass

class TextPad:
  def parse(self, data):
    pass

class G2File:
  def __init__(self, fname):
    self.read(fname)

  def read(self,fname):
    self.fname = fname
    bindata = open(fname).read()
    data = bindata[:]
    null = data.find('\0')
    if null < 0:
      raise 'Invalid G2File "%s"' % fname
    self.txthdr,data = data[:null],data[null+1:]
    self.binhdr,data = struct.unpack('BB',data[:2])[0],data[2:]
    off = null + 2
    self.sections = []
    while len(data)>3:
      id,l = struct.unpack('>BH',data[:3])
      self.sections.append([id, data[3:3+l], off])
      off += 3+l
      data = data[3+l:]
    filecrc = struct.unpack('>H',data)[0]
    printf('%s\n', self.txthdr.strip())
    printf('%s\n', self.binhdr)
    for i in range(len(self.sections)):
      section = self.sections[i]
      printf('0x%02x %s addr:0x%08x\n', section[0], sectiondesc[i], section[2])
      if parse[i]:
	parse[i](array('B',section[1]))
      else:
	printf('%s\n', hexdump(section[1]))
    printf('%d %d\n', filecrc, crc(bindata[null+1:-2]))

  def write(fname):
    pass

class Performance(G2File):
  pass

class Patch(G2File):
  pass
    
prog = sys.argv.pop(0)
fname = sys.argv.pop(0)
printf('fname=|%s|\n', fname)
patch = Patch(fname)

