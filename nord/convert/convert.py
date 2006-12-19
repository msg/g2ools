#
# convert.py - main convert object
#
from nord.g2.modules import fromname as g2name

def setv(g2param,val):
  g2param.variations = [ val for variation in range(9) ]

def getv(nmparam):
  return nmparam.variations[0]

def setav(g2param,array):
  g2param.variations = array[:9]

def cpv(g2param,nmparam):
  g2param.variations = nmparam.variations[:]

class Convert:
  def __init__(self, nmarea, g2area, nmmodule):
    print nmmodule.type.shortnm
    self.nmarea = nmarea
    self.g2area = g2area
    nmm = self.nmmodule = nmmodule
    # use for cabling
    for output in nmmodule.outputs:
      output.conv = self 
    for input in nmmodule.inputs:
      input.conv = self 
    self.nmmodule.conv = self # to get back here when needed (cables)
    self.g2modules = []
    self.outputs = []
    self.inputs = []

    g2m = self.g2module = g2area.addmodule(g2name[self.maing2module])
    g2m.name = nmm.name
    self.horiz = g2m.horiz = nmm.horiz
    #self.vert = g2m.vert = nmm.vert # calculated later
    self.height = g2m.type.height

  # reposition module based on nm1's separation from module above
  def reposition(self, convabove):
    nmm,g2m = self.nmmodule,self.g2module
    if not convabove:
      g2m.vert = nmm.vert
      return

    nma,g2a = convabove.nmmodule,convabove.g2module
    sep = nmm.vert - nma.vert - nma.type.height
    g2m.vert = g2a.vert + convabove.height + sep
    for g2mod in self.g2modules:
      g2mod.vert += g2m.vert

# dualpitchmod -returns p1,p2,g2mm
# handle pitch inputs and if necessary, create a Mix-21B for input
# NOTE: could check the PitchMod1 and PitchMod2 for maximum modulation.
#       in that case, the Pitch input could be used (if no knob tied
#       to the said PitchModX dial).
def dualpitchmod(nmm,g2m,conv):
  p1 = p2 = None
  if len(nmm.inputs.Pitch1.cables) and len(nmm.inputs.Pitch2.cables):
    g2area = conv.g2area
    g2mm = g2area.addmodule(g2name['Mix2-1B'])
    g2mm.name = 'PitchMod'
    conv.g2modules.append(g2mm)
    g2mm.vert = g2m.type.height
    conv.height = g2mm.vert + g2mm.type.height
    color=0
    g2area.connect(g2mm.outputs.Out,g2m.inputs.PitchVar,color)
    p1,p2 = g2mm.inputs.In1,g2mm.inputs.In2
    setv(g2m.params.PitchMod,127)
    cpv(g2mm.params.Lev1,nmm.params.PitchMod1)
    cpv(g2mm.params.Lev2,nmm.params.PitchMod2)
  elif len(nmm.inputs.Pitch1.cables):
    p1 = g2m.inputs.PitchVar
    cpv(g2m.params.PitchMod,nmm.params.PitchMod1)
  elif len(nmm.inputs.Pitch2.cables):
    p2 = g2m.inputs.PitchVar
    cpv(g2m.params.PitchMod,nmm.params.PitchMod2)

  return p1, p2

