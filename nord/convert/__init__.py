#
# __init__.py - package init for convert
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

from nord.convert.convert import Convert
from nord.convert import inout
from nord.convert import osc
from nord.convert import lfo
from nord.convert import env
from nord.convert import filter
from nord.convert import mixer
from nord.convert import audio
from nord.convert import ctrl
from nord.convert import logic
from nord.convert import seq

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
   23: env.ConvMod_Env,
   46: env.ConvAHD_Env,
   52: env.ConvMulti_Env,
   71: env.ConvEnvFollower,

   86: filter.ConvFilterA,
   87: filter.ConvFilterB,
   50: filter.ConvFilterC,
   49: filter.ConvFilterD,
   51: filter.ConvFilterE,
   92: filter.ConvFilterF,
   45: filter.ConvVocalFilter,
  108: filter.ConvVocoder,
   32: filter.ConvFilterBank,
  103: filter.ConvEqMid,
  104: filter.ConvEqShelving,

   19: mixer.Conv3Mixer,
   40: mixer.Conv8Mixer,
   44: mixer.ConvGainControl,
   18: mixer.ConvX_Fade,
   47: mixer.ConvPan,
  113: mixer.Conv1to2Fade,
  114: mixer.Conv2to1Fade,
  111: mixer.ConvLevMult,
  112: mixer.ConvLevAdd,
   76: mixer.ConvOnOff,
   79: mixer.Conv4_1Switch,
   88: mixer.Conv1_4Switch,
   81: mixer.ConvAmplifier,

   61: audio.ConvClip,
   62: audio.ConvOverdrive,
   74: audio.ConvWaveWrap,
   54: audio.ConvQuantizer,
   78: audio.ConvDelay,
   53: audio.ConvSampleNHold,
   82: audio.ConvDiode,
   94: audio.ConvStereoChorus,
  102: audio.ConvPhaser,
   57: audio.ConvInvLevShift,
   83: audio.ConvShaper,
   21: audio.ConvCompressor,
  105: audio.ConvExpander,
  118: audio.ConvDigitizer,
  117: audio.ConvRingMod,

   43: ctrl.ConvConstant,
   39: ctrl.ConvSmooth,
   48: ctrl.ConvPortamentoA,
   16: ctrl.ConvPortamentoB,
   72: ctrl.ConvNoteScaler,
   75: ctrl.ConvNoteQuant,
   98: ctrl.ConvKeyQuant,
   22: ctrl.ConvPartialGen,
   66: ctrl.ConvControlMixer,
  115: ctrl.ConvNoteVelScal,

   36: logic.ConvPosEdgeDly,
   64: logic.ConvNegEdgeDly,
   38: logic.ConvPulse,
   37: logic.ConvLogicDelay,
   70: logic.ConvLogicInv,
   73: logic.ConvLogicProc,
   59: logic.ConvCompareLev,
   89: logic.ConvCompareAB,
   69: logic.ConvClkDiv,
   77: logic.ConvClkDivFix,

   17: seq.ConvEventSeq,
   91: seq.ConvCtrlSeq,
   15: seq.ConvNoteSeqA,
   90: seq.ConvNoteSeqB,
}

