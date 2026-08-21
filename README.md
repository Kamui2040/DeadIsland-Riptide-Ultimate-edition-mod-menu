# DIRDE UE Linux

Linux port of FireEyeEian's **Dead Island Riptide Ultimate Edition (DIRUE)** mod menu for *Dead Island: Riptide Definitive Edition*.

The original DIRUE project and this Linux port are licensed under GPL-3.0. Linux-port changes preserve FireEyeEian attribution and replace the Windows-only implementation rather than wrapping it with Wine or Proton.

## Status

Milestone 1 released-feature parity is integrated on fork `main`. The four formerly missing forced-spawn choices—Butcher, Ram, Bloater, and Thug—are implemented and have passed native candidate, gameplay, transaction-restore, and reproducible packaging validation. `main` and `linux-port` are aligned at the validated parity commit. No public release or binary has been published; the package version remains pre-release (`0.1.0.dev0`).

The integrated Linux port provides:

- 42 semantic, fail-closed non-default patch options covering the released gameplay controls;
- a GUI-independent transaction/application layer;
- a PySide6 Linux GUI;
- pristine-backup preservation, validated candidate construction, atomic Data0 replacement, and exact restore;
- gameplay QA across representative direct, AI, camera/POV, firearm-upgrading, zombie-size, weather/time, and all released forced-spawn families;
- reproducible wheel/sdist packaging with provenance-sensitive inherited payloads excluded.

Butcher, Ram, Bloater, and Thug forced spawning use only the minimum machine-facing compatibility identifiers required for released behavior. The inherited preset ZIPs remain provenance-sensitive historical material and are not Linux runtime or package payloads.

## Requirements

- the Linux version of *Dead Island: Riptide Definitive Edition*;
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

Before the first modification, the application validates the game and source archive and preserves a pristine backup. Candidates are built in temporary storage, validated, bound to the source hash, and installed atomically. A modified live archive must be restored to pristine before applying a different selection.

The retained pristine backup is recovery material and must not be overwritten or deleted as routine cleanup.

## Packaging and game-content boundary

Tracked upstream history contains provenance-sensitive game-derived archives, presets, replacements, UI assets, sounds, and helper binaries. They are not Linux runtime dependencies and are explicitly excluded from Linux distribution artifacts. `tools/check_distribution.py` validates built wheel/sdist contents before any release can be considered and requires `forced_spawn_compat.py` in both artifact types.

The validated 42-option state produced byte-identical clean builds with commit-derived `SOURCE_DATE_EPOCH`:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

The wheel also passed isolated installation, `pip check`, console/module CLI execution, 42-option catalog verification, forced-spawn compatibility registration, and CLI/GUI entry-point metadata checks.

See `docs/PROVENANCE.md` for the redistribution policy and `docs/FEATURE_PARITY.md` for the released-control inventory.

## Attribution

**FireEyeEian** created the original Ultimate Edition mod. **Kamui2040** authors and maintains the Linux port.

Dead Island and Techland game assets are not licensed by this project's GPL notice. Users need their own legitimate Linux game installation.
