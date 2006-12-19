#
# __init__.py - package init for convert
#

from convert import *
import inout
import osc
import lfo
import env
import filter
import mixer
#import audio
import ctrl
#import logic
#import seq

typetable = {
    1: inout.ConvKeyboard, 
   63: inout.ConvKeyboardPatch,
   65: inout.ConvMIDIGlobal,
    2: inout.ConvAudioIn,
  127: inout.ConvPolyAreaIn,
    5: inout.Conv1Output,
    4: inout.Conv2Output,
    3: inout.Conv4Output,
   67: inout.ConvNoteDetect,
  100: inout.ConvKeyboardSplit,

   97: osc.ConvMasterOsc,
    7: osc.ConvOscA,
    8: osc.ConvOscB,
    9: osc.ConvOscC,
  107: osc.ConvSpectralOsc,
   96: osc.ConvFormantOsc,
   14: osc.ConvOscSlvA,
   10: osc.ConvOscSlvB,
   11: osc.ConvOscSlvC,
   12: osc.ConvOscSlvD,
   13: osc.ConvOscSlvE,
  106: osc.ConvOscSineBank,
   85: osc.ConvOscSlvFM,
   31: osc.ConvNoise,
   95: osc.ConvPercOsc,
   58: osc.ConvDrumSynth,

   24: lfo.ConvLFOA,
   25: lfo.ConvLFOB,
   26: lfo.ConvLFOC,
   80: lfo.ConvLFOSlvA,
   27: lfo.ConvLFOSlvB,
   28: lfo.ConvLFOSlvC,
   29: lfo.ConvLFOSlvD,
   30: lfo.ConvLFOSlvE,
   68: lfo.ConvClkGen,
   33: lfo.ConvClkRndGen,
   34: lfo.ConvRndStepGen,
  110: lfo.ConvRandomGen,
   35: lfo.ConvRndPulseGen,
   99: lfo.ConvPatternGen,

   20: env.ConvADSR_Env,
   84: env.ConvAD_Env,

   50: filter.ConvFilterC,
   49: filter.ConvFilterD,
   51: filter.ConvFilterE,

   19: mixer.ConvMixer,

   43: ctrl.ConvConstant,
}

