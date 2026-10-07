import os
import shutil
import subprocess
import sys

import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INIT_PATCH = os.path.join(ROOT_DIR, "initpatch.pch2")
DX7_PATCH = os.path.join(ROOT_DIR, "dx7.pch2")
TESTOSC_PCH = os.path.join(os.path.dirname(__file__), "testosc.pch")

CLI_MODULES = ["nm2g2", "pch2cat", "dx2g2", "nmcat", "pch2cmp", "pch2tog2", "prf2cat"]


@pytest.mark.parametrize("module_name", CLI_MODULES)
def test_cli_help(module_name):
    cmd = [sys.executable, "-m", module_name, "--help"]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    output = res.stdout or res.stderr
    assert len(output.strip()) > 0
    assert "usage" in output.lower()


def test_cli_nm2g2_conversion(tmp_path):
    dst_pch = str(tmp_path / "testosc.pch")
    shutil.copy(TESTOSC_PCH, dst_pch)

    cmd = [sys.executable, "-m", "nm2g2", dst_pch]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0

    expected_pch2 = dst_pch + "2"
    assert os.path.exists(expected_pch2)
    assert os.path.getsize(expected_pch2) > 0


def test_cli_pch2cat_initpatch():
    cmd = [sys.executable, "-m", "pch2cat", INIT_PATCH]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    assert "patchdescription:" in res.stdout
    assert "modules:" in res.stdout
    assert "cables:" in res.stdout


def test_cli_pch2cat_dx7():
    cmd = [sys.executable, "-m", "pch2cat", DX7_PATCH]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    assert "Operator1" in res.stdout
    assert "DXRouter1" in res.stdout
    assert "cables:" in res.stdout


def test_cli_nmcat_testosc():
    cmd = [sys.executable, "-m", "nmcat", TESTOSC_PCH]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    assert "voice:" in res.stdout
    assert "modules:" in res.stdout
    assert "cables:" in res.stdout


def test_cli_pch2tog2():
    cmd = [sys.executable, "-m", "pch2tog2", INIT_PATCH]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    assert "setting category" in res.stdout
    assert "setting voices" in res.stdout


def test_cli_pch2cmp():
    cmd = [sys.executable, "-m", "pch2cmp", INIT_PATCH, INIT_PATCH]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
