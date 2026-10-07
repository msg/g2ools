import glob
import os

import pytest

from nord.g2.file import Patch as G2Patch
from nord.nm2g2 import NM2G2Converter, PatchConverter

TESTS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
PCH_FILES = sorted(glob.glob(os.path.join(TESTS_DIR, "*.pch")))
LFOS_PCH = os.path.join(ROOT_DIR, "lfos.pch")


def test_converter_aliases():
    assert PatchConverter is NM2G2Converter


@pytest.mark.parametrize("filepath", PCH_FILES)
def test_convert_all_17_patches(filepath, tmp_path):
    out_pch2 = str(tmp_path / (os.path.basename(filepath) + "2"))

    conv = PatchConverter(filepath)
    pch2 = conv.convert(output_filename=out_pch2)

    assert os.path.exists(out_pch2)
    assert pch2 is not None
    assert len(pch2.patch.voice.modules) > 0

    # Verify that the generated file parses cleanly back into a G2 Patch
    reloaded = G2Patch(out_pch2)
    assert len(reloaded.voice.modules) == len(pch2.patch.voice.modules)
    assert reloaded.description is not None


def test_convert_lfos_patch(tmp_path):
    out_pch2 = str(tmp_path / "lfos.pch2")

    conv = PatchConverter(LFOS_PCH)
    pch2 = conv.convert(output_filename=out_pch2)

    assert os.path.exists(out_pch2)
    assert len(pch2.patch.voice.modules) > 0

    reloaded = G2Patch(out_pch2)
    assert len(reloaded.voice.modules) == len(pch2.patch.voice.modules)


def test_conversion_options(tmp_path):
    testosc = os.path.join(TESTS_DIR, "testosc.pch")
    out_pch2 = str(tmp_path / "testosc_custom.pch2")

    from types import SimpleNamespace

    opts = SimpleNamespace(
        programpath="nm2g2",
        adsrforad=True,
        compresscolumns=True,
        debug=True,
        keepold=False,
        logiccombine=False,
        nolog=True,
        g2overdrive=True,
        padmixer=True,
        shorten=False,
        verbosity="0",
    )
    conv = PatchConverter(testosc, options=opts)
    pch2 = conv.convert(output_filename=out_pch2)

    assert os.path.exists(out_pch2)
    assert len(pch2.patch.voice.modules) > 0
