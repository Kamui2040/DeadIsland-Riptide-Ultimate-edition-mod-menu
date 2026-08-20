# AppImage packaging

This directory contains the portable AppImage packaging for DIRUE Linux. The initial Bazzite proof is accepted; current work hardens the build so release artifacts do not inherit mutable external tooling or accidental host compatibility assumptions.

## Design

The AppImage uses PyInstaller in **onedir** mode to freeze the Python runtime, DIRUE modules, PySide6, Qt, and required libraries. That frozen directory becomes an AppDir and `appimagetool` turns it into a type-2 AppImage. An additional PyInstaller onefile extraction layer is intentionally not used.

The build consumes only `src/dirue`, this directory's build/check helpers, and public-safe shared metadata from `packaging/common`. It does not copy the repository root and does not include inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, authentic backups, or game binaries.

Flatpak and AppImage share the application ID `io.github.Kamui2040.DIRUELinux`, desktop entry, AppStream metadata, icon identity, and `dirue-linux` launcher name.

## Accepted Bazzite proof

Physical Bazzite QA on 2026-08-20 accepted the initial proof at commit `7e1ad2f3a90571515a0646039e5f633d69b33687`.

The proof produced `DIRUE-Linux-0.1.0.dev0-x86_64.AppImage`, size `69,351,928` bytes, SHA-256 `7fec3fdd37c2698cca063755baa40b1fe1059026b2342a0477f90d9c429adc84`.

Accepted checks included nine static packaging tests, focused `git diff --check`, staged/final payload checks, direct GUI launch, Browse/Validate against the native installation, `Reduce sprint stamina` Apply, exact Restore, clean exit, and successful second launch from the same AppImage.

The generated QA artifact and disposable build state were not committed or published.

## Hardened build inputs

The build currently pins:

- PyInstaller `6.22.2`;
- PySide6 `6.11.1`;
- `appimagetool` `1.9.1` x86-64, SHA-256 `ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0`;
- AppImage type-2 runtime tag `20251108` x86-64, SHA-256 `2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d`.

Both AppImage tool downloads are verified before execution. The runtime is passed explicitly with `--runtime-file`, so `appimagetool` cannot silently fetch a mutable continuous runtime during the build.

From the repository root on x86-64 Linux:

```bash
python3 -m unittest tests.test_appimage_packaging tests.test_flatpak_packaging
packaging/appimage/build.sh /path/to/output
```

The generated AppDir and extracted final AppImage are both checked. The checker requires the bundled Python/PySide6 runtime, verifies shared desktop/AppStream identity, rejects known inherited/game payload names, and rejects symlinks escaping the AppDir.

## Compatibility boundary

PySide6 `6.11.1` publishes its x86-64 Linux wheel for `manylinux_2_34`, so glibc `2.34` is the lowest practical x86-64 baseline for this pinned GUI dependency. The build records both the build host glibc and target baseline.

A Bazzite-built PyInstaller binary remains Bazzite execution evidence only. Before the AppImage becomes a general-Linux release artifact, the release build must run in a reproducible x86-64 environment whose glibc is at the chosen `2.34` baseline (or demonstrate an equivalent lower/equal symbol requirement) rather than inheriting the developer host's newer glibc.

SteamOS compatibility is not claimed from the Bazzite AppImage proof alone.

## Remaining release work

The initial AppImage proof is complete. Portable baseline build-environment enforcement, reproducibility checks, final iconography/desktop integration, UI polish, and release-candidate QA remain later release work.
