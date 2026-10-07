# g2ools — Nord Modular G2 Tools

**g2ools** is a Python suite and library for working with Clavia Nord Modular synthesizers:
- Nord Modular G2 patch files (`.pch2`) and performance files (`.prf2`)
- Nord Modular Classic / G1 patch files (`.pch`)
- Yamaha DX7 SysEx patch conversion (`.syx`)

Originally written by Matt Gerassimoff with extensive module modeling and conversion tables by 3phase (Sven Roehrig).

## Requirements

- Python >= 3.10
- [`uv`](https://docs.astral.sh/uv/) (recommended) or standard `pip`

## Quick Start with `uv`

The recommended way to run and install `g2ools` is with `uv`.

### Run Without Installing

You can run any tool directly in the repository without manual virtualenv creation:

```bash
# Convert a G1 patch to G2
uv run nm2g2 input.pch

# Inspect a G2 patch
uv run pch2cat patch.pch2
```

### Install as CLI Tools (Global / User Environment)

To install the CLI commands into your path:

```bash
uv tool install .
```

After installation, the tools (`nm2g2`, `pch2cat`, `dx2g2`, `nmcat`, `pch2cmp`, `pch2tog2`, `prf2cat`) are directly executable:

```bash
nm2g2 input.pch
pch2cat output.pch2
```

### Development / Editable Installation

For local development and experimentation:

```bash
uv pip install -e .
```

## Tools & Usage

### 1. `nm2g2` — G1 to G2 Patch Converter

Converts Clavia Nord Modular (G1) `.pch` patch files into Nord Modular G2 `.pch2` patch files.

```bash
uv run nm2g2 [options] <pch-files-or-dirs>
```

#### Common Options

- `-r`, `--recursive`: Recursively scan directories for all `.pch` files.
- `-v <0-4>`, `--verbose=<0-4>`: Verbosity level (0: critical, 1: error, 2: warning, 3: info, 4: debug; default: 2).
- `-k`, `--keep-old`: Do not overwrite existing `.pch2` files.
- `-a`, `--all-files`: Process all files, not just `.pch`.
- `-A`, `--adsr-for-ad`: Replace AD modules with ADSR modules.
- `-c`, `--compress-columns`: Remove columns not containing modules.
- `-p`, `--pad-mixer`: Use mixers with Pad when possible.
- `-o`, `--g2-overdrive`: Use G2 overdrive model.
- `-d`, `--debug`: Allow exceptions to print full stack trace.

#### Examples

```bash
# Convert a single patch
uv run nm2g2 Bass.pch

# Convert an entire directory of patches recursively
uv run nm2g2 -r /path/to/nm1_patches/
```

### 2. `pch2cat` — G2 Patch Inspector

Parses and displays the internal structure of a Nord Modular G2 `.pch2` patch file, including:
- Patch description, category, voice count, variation settings
- Voice area & FX area modules, coordinates, parameters, and modes
- Cables and internal connection netlists
- Knob assignments and MIDI CC mappings
- Morph assignments across all 8 morph groups and 9 variations

```bash
uv run pch2cat <patch.pch2>
```

#### Example

```bash
uv run pch2cat "/Users/eek/Development/elijahr-nm-patches/g2/bpurppan simpl.pch2"
```

### 3. `dx2g2` — Yamaha DX7 to G2 Converter

Converts Yamaha DX7 sysex (`.syx`) files into G2 patches. Each converted G2 patch contains 8 DX7 patches using the G2's native `DXRouter` and `Operator` modules with custom circuitry for LFO, PitchEG, and transpose.

```bash
uv run dx2g2 [options] <syx-files-or-dirs>
```

### 4. `nmcat` — G1 Patch Inspector

Parses and inspects Nord Modular G1 `.pch` patch files, showing voice and FX module setups, cable routings, netlists, knobs, and morph assignments.

```bash
uv run nmcat patch.pch
```

### 5. `pch2cmp` — Patch Comparator

Compares G2 patch files by netlist topology and module configurations to detect duplicate or closely related patches.

```bash
uv run pch2cmp patch1.pch2 patch2.pch2 ...
```

### 6. `pch2tog2` — Patch Disassembler

Decompiles a binary `.pch2` file into a textual representation suitable for analysis or script-based reconstruction.

```bash
uv run pch2tog2 patch.pch2
```

### 7. `prf2cat` — Performance Inspector

Inspects Nord Modular G2 `.prf2` performance files, showing slot assignments (A/B/C/D), keyboard splits, clock settings, and detailed patch dumps for each slot.

```bash
uv run prf2cat perf.prf2
```

## Python Library

The `nord` package can be imported into your own Python code:

```python
from nord.g2.file import Pch2File
from nord.nm1.file import PchFile
from nord.nm2g2 import NM2G2Converter

# Load a G2 patch
g2_patch = Pch2File("patch.pch2")
print("Patch category:", g2_patch.patch.description.category)
```

## License

This project is licensed under the GNU General Public License v2 or later (GPL-2.0-or-later). See [COPYING](COPYING) for details.
