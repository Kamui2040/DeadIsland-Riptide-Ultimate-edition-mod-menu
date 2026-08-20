# AppImage proof of concept

This directory contains the second end-user packaging proof for DIRUE Linux. It follows the accepted Flatpak proof and is intentionally limited to proving a single portable AppImage can launch the existing GUI on Bazzite without host Python or PySide6.

## Design

The proof uses PyInstaller in **onedir** mode to freeze the Python runtime, DIRUE modules, PySide6, Qt, and their required libraries. That frozen directory becomes an AppDir, and the official `appimagetool` reference implementation turns the AppDir into a type-2 AppImage.

Using PyInstaller onedir inside the AppImage is deliberate: the AppImage itself is already the single user-facing file, so an additional PyInstaller onefile extraction layer is unnecessary.

The build consumes only the Linux runtime under `src/dirue` and the files in this directory. It does not copy the repository root and does not include inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, authentic backups, or game binaries.

## Proof build

From the repository root on x86-64 Linux:

```bash
python3 -m unittest tests.test_appimage_packaging
packaging/appimage/build.sh /path/to/output
```

The build uses an isolated temporary virtual environment and currently pins:

- PyInstaller `6.22.2`;
- PySide6 `6.11.1`.

The proof downloads the official continuous x86-64 `appimagetool` into temporary storage when `APPIMAGETOOL` is not supplied. This is acceptable for the proof only. Shared packaging hardening must pin the exact AppImage build tool and verify its digest before release builds.

The generated AppDir and the extracted final AppImage are both checked before acceptance. The checker requires the bundled Python and PySide6 runtimes, rejects known inherited/game payload names, and rejects symlinks that escape the AppDir.

## Compatibility boundary

A Bazzite-built PyInstaller binary proves Bazzite execution, not universal Linux portability. PyInstaller does not bundle glibc and Linux bundles are forward-compatible with newer glibc rather than backward-compatible with older glibc. Before the AppImage becomes a general-Linux release artifact, shared packaging hardening must choose the oldest supported Linux/glibc baseline and build the release AppImage in a reproducible environment at or below that baseline.

SteamOS compatibility is therefore not claimed from this AppImage proof alone.

## Acceptance

The initial physical proof must demonstrate on Bazzite that the generated `.AppImage`:

- launches without host Python or PySide6 setup;
- opens the existing Qt GUI;
- can Browse to and Validate the native DIRDE installation;
- can Apply one bounded representative option and Restore the retained pristine backup exactly;
- can be closed and launched again from the same artifact;
- leaves no build residue outside the requested output and disposable temporary storage.

Final iconography, desktop integration, update metadata, broad distribution compatibility, reproducible tool pinning, UI polish, and release-candidate artifact checks belong to later release stages.
