#!/usr/bin/env python2

import sys
from nord.g2.file import Pch2File
from nord import printf

unavailable = [
  '4-Out',
  '2-In',
  '4-In',
  'Operator',
  'DXRouter',
  'Vocoder',
  'CtrlSend',
  'PCSend',
  'NoteSend',
  'CtrlRcv',
  'NoteRcv',
  'NoteZone',
  'Automate',
]

for arg in sys.argv[1:]:
  try:
    pch2 = Pch2File(arg)
    p = pch2.patch
    demo = True
    for module in p.voice.modules + p.fx.modules:
      if module.type.shortnm in unavailable:
        demo = False
    if demo:
      printf('%s\n', arg)
  except:
    printf('"%s" not a pch2.\n\n', arg)

