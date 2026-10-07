import binascii
import os
from struct import unpack

import pytest

from nord.g2.crc import crc
from nord.g2.file import Patch, Pch2File

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INIT_PATCH = os.path.join(ROOT_DIR, "initpatch.pch2")
DX7_PATCH = os.path.join(ROOT_DIR, "dx7.pch2")


def test_load_initpatch():
    patch = Patch(INIT_PATCH)
    assert patch.description is not None
    assert patch.description.voices == 1
    assert patch.description.height == 600
    assert len(patch.modules) == 0
    assert len(patch.voice.modules) == 0
    assert len(patch.fx.modules) == 0
    assert len(patch.cables) == 0
    assert len(patch.voice.cables) == 0
    assert len(patch.fx.cables) == 0


def test_load_dx7():
    patch = Patch(DX7_PATCH)
    assert patch.description is not None
    assert patch.description.voices == 23
    assert patch.description.height == 474

    # DX7 patch contains both voice and FX area modules
    assert len(patch.voice.modules) == 35
    assert len(patch.fx.modules) == 9
    assert len(patch.modules) == 44

    assert len(patch.voice.cables) == 83
    assert len(patch.fx.cables) == 19
    assert len(patch.cables) == 102


def test_pch2file_interface():
    pch2 = Pch2File(DX7_PATCH)
    assert pch2.type == "Patch"
    assert len(pch2.patch.voice.modules) == 35
    assert len(pch2.patch.fx.modules) == 9


def test_query_modules_and_parameters():
    patch = Patch(DX7_PATCH)
    op1 = patch.voice.find_module(1)
    assert op1 is not None
    assert op1.name == "Operator1"
    assert op1.type.shortnm == "Operator"
    assert op1.horiz == 0
    assert op1.vert == 21
    assert len(op1.params) > 0

    # Query specific module parameters
    param_names = [p.name for p in op1.type.params]
    assert "FreqCoarse" in param_names
    assert "FreqFine" in param_names
    assert "FreqDetune" in param_names


def test_query_cables_and_metadata():
    patch = Patch(DX7_PATCH)
    cables = patch.voice.cables
    assert len(cables) > 0
    first_cable = cables[0]
    assert hasattr(first_cable, "color")
    assert hasattr(first_cable, "source")
    assert hasattr(first_cable, "dest")
    assert first_cable.source.module is not None
    assert first_cable.dest.module is not None


def test_crc_computation_and_integrity():
    for filepath in [INIT_PATCH, DX7_PATCH]:
        data = open(filepath, "rb").read()
        null_idx = data.find(b"\0")
        assert null_idx > 0

        memview = memoryview(data)[null_idx + 1 :]
        expected_crc = unpack(">H", data[-2:])[0]
        calculated_crc = crc(memview[:-2])
        assert calculated_crc == expected_crc, f"CRC mismatch in {filepath}"

        # Standard CRC32 check on the complete binary payload
        crc32_val = binascii.crc32(data)
        assert isinstance(crc32_val, int)
        assert crc32_val != 0


def test_serialization_and_roundtrip(tmp_path):
    for filepath in [INIT_PATCH, DX7_PATCH]:
        orig_patch = Patch(filepath)
        raw_bytes = orig_patch.format_file()
        assert len(raw_bytes) > 0

        # Verify CRC of formatted output
        null_idx = raw_bytes.find(b"\0")
        memview = memoryview(raw_bytes)[null_idx + 1 :]
        expected_crc = unpack(">H", raw_bytes[-2:])[0]
        calculated_crc = crc(memview[:-2])
        assert calculated_crc == expected_crc

        # Save to disk and reload
        out_file = tmp_path / os.path.basename(filepath)
        orig_patch.save(str(out_file))
        assert out_file.exists()

        reloaded = Patch(str(out_file))
        assert len(reloaded.voice.modules) == len(orig_patch.voice.modules)
        assert len(reloaded.fx.modules) == len(orig_patch.fx.modules)
        assert len(reloaded.voice.cables) == len(orig_patch.voice.cables)
        assert len(reloaded.fx.cables) == len(orig_patch.fx.cables)
        assert reloaded.description.voices == orig_patch.description.voices
