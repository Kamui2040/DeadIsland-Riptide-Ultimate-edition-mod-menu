# DIRDE UE Linux

Linux port of FireEyeEian's **Dead Island Riptide Ultimate Edition (DIRUE)** mod menu for *Dead Island: Riptide Definitive Edition*.

The project targets the game's native Linux build. It is not a Wine wrapper, Proton frontend, Windows launcher, or general-purpose mod manager.

The original DIRUE project and this Linux port are licensed under GPL-3.0. Linux-port changes preserve FireEyeEian attribution. Techland game content is not covered by the repository's GPL license and is not redistributed by the Linux packages.

## Status

Milestone 1 released-feature parity is complete. The Linux port implements all 42 released non-default gameplay options with semantic, fail-closed patching and validated transaction/restore behavior.

The frozen release-candidate source commit is:

`c3e3b97494058e8da199658f4f265e3eb84f0201`

Flatpak and AppImage release-candidate builds from that exact source state passed packaged Bazzite validation, including launch, Browse, explicit Validate, representative Apply, exact Restore, close, and restart. Final rebuild/verification also passed from the unchanged frozen source state. The AppImage final rebuild is byte-identical to the accepted RC AppImage and remains bounded to `GLIBC_2.34`.

No public binary release has been published. The package version remains pre-release (`0.1.0.dev0`), and integration/publication still requires explicit approval. See `docs/RELEASE.md` for the recorded release evidence and artifact identities.

## End-user packages

The intended end-user formats are:

- **Flatpak** — first-class package for Bazzite, SteamOS, and other Flatpak-friendly Linux systems;
- **AppImage** — portable x86-64 Linux alternative.

Packaged users do **not** need to install Python or PySide6 separately. These packages have been validated but are not yet publicly released from this repository.

The application operates on the user's own installed `DIR/Data0.pak`. It never uses the repository's inherited upstream `Data0.pak`, preset archives, or replacement assets as an install payload.

## Development setup

Development requires Python 3.11 or newer. From a clean checkout, use an isolated environment and install the GUI extra:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[gui]'
```

Launch the development GUI with:

```bash
dirue-gui
```

The CLI entry point is `dirue`.

## Safety model

Before the first modification, the application validates the native Linux game installation and source archive and preserves a pristine backup. Candidates are built in temporary storage, validated, bound to the source state, and installed atomically only after all checks pass.

A modified live archive must be restored to pristine before a different selection is applied. The retained pristine backup is recovery material and must not be overwritten or deleted as routine cleanup.

## Packaging and game-content boundary

Linux distribution artifacts use only the Linux runtime source and public-safe packaging metadata. They exclude inherited game archives, preset payloads, replacement assets, Windows helpers, authentic backups, private QA material, and game binaries.

Reproducible developer/source artifacts were previously accepted:

- wheel SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

See `docs/PROVENANCE.md` for redistribution policy, `docs/FEATURE_PARITY.md` for the released-control inventory, and `docs/RELEASE.md` for release validation state.

## Attribution

**FireEyeEian** created the original Ultimate Edition mod. **Kamui2040** authors and maintains the Linux port.

Dead Island and Techland game assets are not licensed by this project's GPL notice. Users need their own legitimate native Linux game installation.
