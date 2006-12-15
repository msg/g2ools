#!/usr/bin/env python

import sys
from string import *
import re

class Module:
  pass

commentre=re.compile(';.*$')
modulere=re.compile('(\d+)\s+(\S+)')
remarkre=re.compile('remark\s+(\S+)')
namedblre=re.compile('(\w+)\s+(\d+.\d+)')
nameintre=re.compile('(\w+)\s+(\d+)')
parameterre=re.compile('(\d+)\s+"([^"]+)"\s+(\d+)\.\.(\d+)\s+"([^"]+)"')
inoutre=re.compile('(\d+)\s+"([^"]+)"\s+(\S+)')
customre=parameterre

entries=open('patch303.txt','r').read().split('----------\r\n')
entries.pop(0)
fromtype={}
fromname={}
modules=[]
for entry in entries:
  data=entry.split('\r\n')
  m=modulere.match(data.pop(0))
  if m:
    #print m.group(1), m.group(2)
    mod=Module()
    mod.type = m.group(1)
    mod.name = m.group(2)
    # remove remark
    data.pop(0)
    # get float attributes
    for i in range(2,8):
      mnd=namedblre.match(data.pop(0))
      if mnd:
        setattr(mod,mnd.group(1),float(mnd.group(2)))
        #print mnd.group(1), mnd.group(2)
    mni=nameintre.match(data.pop(0))
    if mni:
      setattr(mod,mni.group(1),int(mni.group(2)))
    # the rest is parameters, inputs, outpus, custom
    mod.parameters = []
    mod.inputs = []
    mod.outputs = []
    mod.custom = []
    while len(data):
      s=data.pop(0)
      if s == 'parameters':
        section = mod.parameters
        sectionre = parameterre
      elif s == 'inputs':
        section = mod.inputs
        sectionre = inoutre
      elif s == 'outputs':
        section = mod.outputs
        sectionre = inoutre
      elif s == 'custom':
        section = mod.custom
        sectionre = customre
      else:
        ms = sectionre.match(s)
        if ms:
          section.append(ms.groups()[:])
    fromtype[mod.type] = mod
    fromname[mod.name] = mod
    modules.append(mod)

for module in modules:
  print module.name, module.type
  if len(module.parameters):
    print ' parameters'
    print '',str(module.parameters)
  if len(module.inputs):
    print ' inputs'
    print '',str(module.inputs)
  if len(module.outputs):
    print ' outputs'
    print '',str(module.outputs)
  if len(module.custom):
    print ' custom'
    print '',str(module.custom)

