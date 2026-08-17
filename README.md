# DIRUE Linux

Native-Linux port of FireEyeEian's **Dead Island Riptide Ultimate Edition (DIRUE)** mod menu for the native Linux build of *Dead Island: Riptide Definitive Edition*.

The original DIRUE project and this Linux port are licensed under GPL-3.0. Linux-port changes preserve FireEyeEian attribution and replace the Windows-only implementation rather than wrapping it with Wine or Proton.

## Status

Milestone 1 is released-feature parity with the original DIRUE menu. The previously integrated native-Linux implementation remains stable on `main`; focused branch `agent/forced-spawn-identifiers` now completes the four remaining released forced-spawn choices and has passed native candidate and gameplay validation with exact pristine restore. `main` is unchanged pending explicit integration approval. No public release or binary has been published; the package version remains pre-release (`0.1.0.dev0`).

The current validated focused branch provides:

- 42 semantic, fail-closed non-default patch options covering the released gameplay controls;
- a GUI-independent transaction/application layer;
- a PySide6 native Linux GUI;
- pristine-backup preservation, validated candidate construction, atomic Data0 replacement, and exact restore;
- native gameplay QA across representative direct, AI, camera/POV, firearm-upgrading, zombie-size, weather/time, and all released forced-spawn families.

Butcher, Ram, Bloater, and Thug forced spawning are now implemented on the focused branch using only the minimum machine-facing compatibility identifiers required for released behavior. The inherited preset ZIPs remain provenance-sensitive historical material and are not Linux runtime or package payloads.

## Requirements

- the native Linux version of *Dead Island: Riptide Definitive Edition*;
- Python 3.11 or newer;
- PySide6 for the GUI.

The project patches the user's own validated installed `DIR/Data0.pak`. It does **not** use the repository's inherited upstream `Data0.pak` as an install payload.

## Development install

From a clean checkout of `main` or the active Linux development branch, use an isolated Python environment and install the GUI extra:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[gui]'
```

Then launch:

```bash
dirue-gui
```

The CLI entry point is `dirue`. Direct module execution with `python -m dirue.cli` is also supported.

## Safety model

Before the first modification, the Linux application validates the native game and source archive and preserves a pristine backup. Candidates are built in temporary storage, validated, bound to the source hash, and installed atomically. A modified live archive must be restored to pristine before applying a different selection.

The retained pristine backup is recovery material and must not be overwritten or deleted as routine cleanup.

## Packaging and game-content boundary

Tracked upstream history contains provenance-sensitive game-derived archives, presets, replacements, UI assets, sounds, and helper binaries. They are not Linux runtime dependencies and are explicitly excluded from Linux distribution artifacts. `tools/check_distribution.py` validates built wheel/sdist contents before any release can be considered.

Reproducible packaging evidence remains accepted for the integrated 38-option state. The focused 42-option branch adds a new packaged Python module and a CLI-entry fix, so a bounded packaging refresh is required before integration; this does not reopen gameplay parity.

See `docs/PROVENANCE.md` for the redistribution policy and `docs/FEATURE_PARITY.md` for the released-control inventory.

## Attribution

DIRUE was created by **FireEyeEian**. This repository's Linux-port work is a modified native-Linux implementation of that project.

Dead Island and Techland game assets are not licensed by this project's GPL notice. Users need their own legitimate native Linux game installation.