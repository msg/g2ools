#!/usr/bin/env python2
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

import logging
import os, sys, time, traceback
from optparse import OptionParser, make_option
from glob import glob
sys.path.append('.')
from nord.nm2g2 import NM2G2Converter, NM1Error

#__builtins__.printf = printf

nm2g2_options = [
  make_option('-a', '--all-files', action='store_true',
      dest='allfiles', default=False,
      help='Process all files (not just *.pch)'),
  make_option('-A', '--adsr-for-ad', action='store_true',
      dest='adsrforad', default=False,
      help='Replace AD modules with ADSR modules'),
  make_option('-c', '--compress-columns', action='store_true',
      dest='compresscolumns', default=False,
      help='Remove columns not containing modules'),
  make_option('-d', '--debug', action='store_true',
      dest='debug', default=False,
      help='Allow exceptions to terminate application'),
  make_option('-k', '--keep-old', action='store_true',
      dest='keepold', default=False,
      help='If .pch2 file exists, do not replace it'),
  make_option('-l', '--no-logic-combine', action='store_false',
      dest='logiccombine', default=True,
      help='Do not combine logic and inverter modules'),
  make_option('-n', '--no-log', action='store_true',
      dest='nolog', default=False,
      help='Do not generated failed patches log'),
  make_option('-o', '--g2-overdrive', action='store_true',
      dest='g2overdrive', default=False,
      help='Use g2 overdrive model'),
  make_option('-p', '--pad-mixer', action='store_true',
      dest='padmixer', default=False,
      help='Use mixers with Pad when possible'),
  make_option('-r', '--recursive', action='store_true',
      dest='recursive', default=False,
      help='On dir arguments, convert all .pch files'),
  make_option('-s', '--no-shorten', action='store_false',
      dest='shorten', default=True,
      help='Turn off shorten cable connections'),
  make_option('-v', '--verbose', action='store',
      dest='verbosity', default='2', choices=map(str, range(5)),
      help='Set converter verbosity level 0-4'),
]

def doconvert(filename, options):
  # general algorithm for converter:
  try:
    nm2g2 = NM2G2Converter(filename, options, options.log)
    nm2g2.convert()
  except KeyboardInterrupt:
    sys.exit(1)
  except NM1Error, s:
    nm2g2log.error(s)
    return '%s\n%s' % (filename, s)
  except Exception, e:
    if options.debug:
      return '%s\n%s' % (filename, traceback.format_exc())
    else:
      return '%s\n%s' % (filename, e)
  return ''

def process_file(filename, options):
  if filename[-5:].lower() == '.pch2':
    return
  if filename[-4:].lower() == '.pch' or options.allfiles:
    testname = filename
    if filename[-4:].lower() != '.pch':
      testname = filename+'.pch'
    if options.keepold and os.path.exists(testname + '2'):
      return
    options.log.error('"%s"' % filename)
    failed = doconvert(filename, options)
    if failed:
      options.failedpatches.append(failed)
    options.log.info('-' * 20)

def main(argv, stream):
  global nm2g2_options

  parser = OptionParser("usage: %prog [options] <pch-files-or-dirs>",
      option_list=nm2g2_options)
  (options, args) = parser.parse_args(argv[:])
  options.programpath = args.pop(0)
  verbosity = [
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
  ][int(options.verbosity)]

  options.log = logging.getLogger('nm2g2')
  options.failedpatches = []

  fmt = logging.Formatter('%(message)s', None)
  hdlr = logging.StreamHandler(stream)
  hdlr.setFormatter(fmt)
  options.log.addHandler(hdlr)
  options.log.setLevel(verbosity)
  options.log.propagate = False

  while len(args):
    arg = args.pop(0)
    pathlist = glob(arg)
    if len(pathlist) == 0:
      failedpatches.append(arg)
      continue
    for path in pathlist:
      if os.path.isdir(path) and options.recursive:
        for root, dirnamess, filenames in os.walk(path):
          for name in filenames:
            filename = os.path.join(root, name)
            process_file(filename, options)
      else:
        process_file(path, options)

  if len(options.failedpatches):
    s = 'Failed patches: \n %s\n' % '\n '.join(options.failedpatches)
    if not options.nolog:
      date = time.strftime('%m-%d-%y-%H:%M:%S', time.localtime())
      open('failedpatches-%s.txt' % (date), 'w').write(s)
    options.log.warning(s)

class StdoutStream:
  def __init__(self, file=sys.stdout):
    self.file = file
    self.str = ''

  def write(self, s):
    self.str += s

  def flush(self):
    self.file.write(self.str)
    self.str = ''

if __name__ == '__main__':
  main(sys.argv, StdoutStream())
