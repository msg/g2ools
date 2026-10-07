import glob
import os

import pytest

from nord.nm1.file import Patch, PchFile

TESTS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
PCH_FILES = sorted(glob.glob(os.path.join(TESTS_DIR, "*.pch")))
LFOS_PCH = os.path.join(ROOT_DIR, "lfos.pch")


def test_pch_file_count():
    assert len(PCH_FILES) == 17


@pytest.mark.parametrize("filepath", PCH_FILES)
def test_load_all_17_nm1_patches(filepath):
    patch = Patch(filepath)
    assert patch.header is not None
    assert len(patch.voice.modules) > 0

    # Verify each module has valid name, location, and parameters
    for mod in patch.voice.modules:
        assert isinstance(mod.name, str)
        assert len(mod.name) > 0
        assert isinstance(mod.horiz, int)
        assert isinstance(mod.vert, int)
        assert hasattr(mod, "type")
        assert mod.type is not None

    # Verify cables have valid source and destination
    for cable in patch.voice.cables:
        assert cable.source is not None
        assert cable.dest is not None
        assert cable.source.module is not None
        assert cable.dest.module is not None


@pytest.mark.parametrize("filepath", PCH_FILES)
def test_pchfile_interface(filepath):
    pch = PchFile(filepath)
    assert pch.patch is not None
    assert len(pch.patch.voice.modules) > 0


def test_load_lfos_patch():
    assert os.path.exists(LFOS_PCH)
    patch = Patch(LFOS_PCH)
    assert len(patch.voice.modules) == 15
    assert len(patch.voice.cables) == 0


def test_query_module_and_netlist():
    testosc = os.path.join(TESTS_DIR, "testosc.pch")
    patch = Patch(testosc)
    assert len(patch.voice.modules) == 22

    mod1 = patch.voice.find_module(1)
    assert mod1 is not None
    assert isinstance(mod1.name, str)
    assert mod1.index == 1

    # Verify netlist connections
    assert hasattr(patch.voice, "netlist")
    assert len(patch.voice.netlist.nets) > 0
