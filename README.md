# DIRUE Linux

Native-Linux port of FireEyeEian's **Dead Island Riptide Ultimate Edition (DIRUE)** mod menu for the native Linux build of *Dead Island: Riptide Definitive Edition*.

The original DIRUE project and this Linux port are licensed under GPL-3.0. Linux-port changes preserve FireEyeEian attribution and replace the Windows-only implementation rather than wrapping it with Wine or Proton.

## Status

Milestone 1 is released-feature parity with the original DIRUE menu. The `linux-port` branch contains the active native-Linux implementation and remains pre-release while final packaging validation is completed.

The current port provides:

- semantic, fail-closed patch definitions for the validated released options;
- a GUI-independent transaction/application layer;
- a PySide6 native Linux GUI;
- pristine-backup preservation, validated candidate construction, atomic Data0 replacement, and exact restore;
- native gameplay QA across representative direct, AI, camera/POV, firearm-upgrading, zombie-size, weather/time, and forced-spawn behavior.

Four released forced-spawn choices—Butcher, Ram, Bloater, and Thug—remain intentionally unavailable because their required game-derived identifiers do not yet have an acceptable redistribution-safe derivation.

## Requirements

- the native Linux version of *Dead Island: Riptide Definitive Edition*;
- Python 3.11 or newer;
- PySide6 for the GUI.

The project patches the user's own validated installed `DIR/Data0.pak`. It does **not** use the repository's inherited upstream `Data0.pak` as an install payload.

## Development install

From a clean checkout of `linux-port`, use an isolated Python environment and install the GUI extra:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[gui]'
```

Then launch:

```bash
dirue-gui
```

The CLI entry point is `dirue`.

## Safety model

Before the first modification, the Linux application validates the native game and source archive and preserves a pristine backup. Candidates are built in temporary storage, validated, bound to the source hash, and installed atomically. A modified live archive must be restored to pristine before applying a different selection.

The retained pristine backup is recovery material and must not be overwritten or deleted as routine cleanup.

## Packaging and game-content boundary

Tracked upstream history contains provenance-sensitive game-derived archives, presets, replacements, UI assets, sounds, and helper binaries. They are not Linux runtime dependencies and are explicitly excluded from Linux distribution artifacts. `tools/check_distribution.py` validates built wheel/sdist contents before any release can be considered.

See `docs/PROVENANCE.md` for the redistribution policy and `docs/FEATURE_PARITY.md` for the released-control inventory.

## Attribution

DIRUE was created by **FireEyeEian**. This repository's Linux-port work is a modified native-Linux implementation of that project.

Dead Island and Techland game assets are not licensed by this project's GPL notice. Users need their own legitimate native Linux game installation.
