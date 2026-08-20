# AppImage proof of concept

This directory contains the accepted second end-user packaging proof for DIRUE Linux. It follows the accepted Flatpak proof and proves that a single portable AppImage can launch the existing GUI on Bazzite without a user-managed Python or PySide6 environment.

## Design

The proof uses PyInstaller in **onedir** mode to freeze the Python runtime, DIRUE modules, PySide6, Qt, and their required libraries. That frozen directory becomes an AppDir, and the official `appimagetool` reference implementation turns the AppDir into a type-2 AppImage.

Using PyInstaller onedir inside the AppImage is deliberate: the AppImage itself is already the single user-facing file, so an additional PyInstaller onefile extraction layer is unnecessary.

The build consumes only the Linux runtime under `src/dirue` and the files in this directory. It does not copy the repository root and does not include inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, authentic backups, or game binaries.

## Accepted Bazzite proof

Physical Bazzite QA on 2026-08-20 accepted the proof at commit `7e1ad2f3a90571515a0646039e5f633d69b33687`.

The proof produced:

- artifact `DIRUE-Linux-0.1.0.dev0-x86_64.AppImage`;
- size `69,351,928` bytes;
- SHA-256 `7fec3fdd37c2698cca063755baa40b1fe1059026b2342a0477f90d9c429adc84`.

Accepted checks:

- nine static AppImage packaging checks passed;
- `git diff --check` passed for the focused AppImage change set;
- AppDir validation passed before image creation;
- extracted final-AppImage validation passed after image creation;
- the generated artifact hash matched the build-reported hash;
- the AppImage launched directly and displayed the existing Qt GUI;
- Browse selected and Validate accepted the native DIRDE installation against the retained pristine baseline;
- `Reduce sprint stamina` Apply completed successfully;
- Restore completed successfully and final status confirmed live Data0 matched the retained pristine backup;
- the same AppImage closed cleanly and launched successfully a second time.

The generated QA artifact and disposable build/worktree state were temporary evidence and are not committed or published.

## Proof build

From the repository root on x86-64 Linux:

```bash
python3 -m unittest tests.test_appimage_packaging
packaging/appimage/build.sh /path/to/output
```

The proof uses an isolated temporary virtual environment and currently pins:

- PyInstaller `6.22.2`;
- PySide6 `6.11.1`.

The proof downloads the official continuous x86-64 `appimagetool` into temporary storage when `APPIMAGETOOL` is not supplied. This is acceptable for the proof only. Shared packaging hardening must pin the exact AppImage build tool and verify its digest before release builds.

The generated AppDir and the extracted final AppImage are both checked before acceptance. The checker requires the bundled Python and PySide6 runtimes, rejects known inherited/game payload names, and rejects symlinks that escape the AppDir.

## Compatibility boundary

A Bazzite-built PyInstaller binary proves Bazzite execution, not universal Linux portability. PyInstaller does not bundle glibc and Linux bundles are forward-compatible with newer glibc rather than backward-compatible with older glibc. Before the AppImage becomes a general-Linux release artifact, shared packaging hardening must choose the oldest supported Linux/glibc baseline and build the release AppImage in a reproducible environment at or below that baseline.

SteamOS compatibility is therefore not claimed from this AppImage proof alone.

## Remaining release work

The initial AppImage proof is complete. Exact AppImage tool digest pinning, oldest-supported glibc baseline selection, reproducible release builds, final iconography/desktop integration, shared Flatpak/AppImage metadata and payload checks, UI polish, and release-candidate QA remain later release stages.
