# AppImage packaging

This directory contains the portable AppImage packaging for DIRDE UE Linux. The initial proof, shared packaging hardening, release-candidate QA, and final rebuild/verification are complete for the frozen source state.

## Design

The AppImage uses PyInstaller in **onedir** mode to freeze the Python runtime, DIRUE modules, PySide6, Qt, and required libraries. That frozen directory becomes an AppDir and `appimagetool` turns it into a type-2 AppImage. An additional PyInstaller onefile extraction layer is intentionally not used.

The build consumes only `src/dirue`, the AppImage build/check helpers, and public-safe shared metadata from `packaging/common`. It does not copy the repository root and does not include inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, authentic backups, private QA material, or game binaries.

Flatpak and AppImage share the application ID `io.github.Kamui2040.DIRUELinux`, desktop entry, AppStream metadata, icon identity, and `dirue-linux` launcher name.

## Pinned build inputs

The hardened build pins:

- PyInstaller `6.22.2`;
- PySide6 `6.11.1`;
- `appimagetool` `1.9.1` x86-64, SHA-256 `ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0`;
- AppImage type-2 runtime tag `20251108` x86-64, SHA-256 `2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d`;
- UBI 9 Python 3.11 baseline image `registry.access.redhat.com/ubi9/python-311@sha256:7b6cb58d3ff034df7b300800bd89a469d9bd2f739d43250d76b9c9e805307ab5`.

Both AppImage tool downloads are verified before execution. The runtime is passed explicitly with `--runtime-file`, so `appimagetool` cannot silently fetch a mutable continuous runtime during the build.

Physical Bazzite probing verified the pinned UBI image reports glibc `2.34`, provides Python `3.11.13` at `/usr/bin/python3.11`, exposes shared `libpython`, imports the required `_ssl`, `bz2`, `ctypes`, `lzma`, `venv`, and `zlib` modules, and has pip available.

The previously explored manylinux baseline was rejected for PyInstaller use because its probed CPython 3.11 runtimes were static. A temporary source-built CPython approach was also rejected after physical validation showed missing extension modules. Neither rejected path is used by the current builder.

## Build entry points

`build.sh` is the inner AppImage builder. It records the glibc version of the build environment and performs the AppDir construction and artifact checks.

`build-baseline.sh` is the release-portability entry point. It uses rootless Podman, mounts the repository read-only, writes only to the requested output directory, and runs under the exact digest-pinned UBI image. Before invoking `build.sh`, it requires glibc `2.34`, exact Python `3.11.13`, `Py_ENABLE_SHARED=1`, an installed shared `libpython`, the required extension modules, pip, and the inner build commands.

The wrapper fails closed unless exactly one AppImage appears in the host output directory after the container exits. It verifies the host-visible artifact is executable and emits authoritative `APPIMAGE_BASELINE_ARTIFACT`, `APPIMAGE_BASELINE_SHA256`, and `APPIMAGE_BASELINE_SIZE` values. Callers must use those host values rather than infer a host path from the container's `/output` path.

From the repository root on x86-64 Linux:

```bash
python3 -m unittest tests.test_appimage_packaging tests.test_flatpak_packaging tests.test_glibc_audit
packaging/appimage/build-baseline.sh /path/to/output
```

The generated AppDir and extracted final AppImage are both checked. The checker requires the bundled Python/PySide6 runtime, verifies shared desktop/AppStream identity, rejects known inherited/game payload names, rejects symlinks escaping the AppDir, and rejects base libraries deliberately required from the target system.

The finished AppImage is audited through ELF program/dynamic headers. The audit fails if a bundled dynamic ELF requires a `GLIBC_*` symbol newer than the declared `2.34` floor. Stripped or static ELFs do not need section tables for this audit.

## Hardened baseline history

Physical Bazzite QA on 2026-08-20 accepted the initial AppImage proof at commit `7e1ad2f3a90571515a0646039e5f633d69b33687`. That proof passed staged/final payload checks, direct GUI launch, Browse/Validate, representative Apply, exact Restore, clean exit, and restart.

A later UBI-wrapper baseline at commit `40813fc8260a94b9b0594dce4f23fb02ea0dbe1f` established that the pinned UBI environment could produce and launch the hardened AppImage. That artifact was `60,295,672` bytes with SHA-256 `4164af8cd4bfd762d7e0d0a2183475e017a1df09c55873252e05c1c3e81b6730`.

Physical stage-2 auditing identified a PyInstaller-collected `libgcc_s.so.1` requiring `GLIBC_2.35`. That copy came from the UBI build environment and would have raised the AppImage compatibility floor above the intended `2.34` target.

`libgcc_s.so.1` is therefore treated as a target-system base runtime rather than bundled payload. `build.sh` removes any collected copy before the AppDir is assembled, `check_appdir.py` rejects the name if it reappears, and the finished-artifact GLIBC audit remains mandatory.

Physical Bazzite QA on 2026-08-21 accepted the complete hardening stage 2 at commit `f37d39165212b84954cf60c34b0d97bdec313511`:

- both builds used glibc `2.34`, Python `3.11.13`, `PYTHONHASHSEED=1`, and the same source-derived `SOURCE_DATE_EPOCH`;
- both AppDirs matched at SHA-256 `5741e2dab0460061bc5a1d26187a8eb5323ec30a0b6187757c4cd067d5a175ce`;
- both final AppImages were byte-identical;
- final AppImage SHA-256 was `07284a312c929cd46bcc191ba9f76f3683d2134f36e912622b77656079376dd4`;
- final size was `60,246,520` bytes;
- the ELF audit inspected 179 files and reported maximum required `GLIBC_2.34`;
- the bundled `libgcc_s.so.1` exclusion remained enforced;
- direct launch passed.

This closed the stage-2 reproducibility defect tracked as Issue #5.

## Release-candidate evidence

The frozen release-candidate source commit is:

`c3e3b97494058e8da199658f4f265e3eb84f0201`

The accepted RC AppImage was:

- size: `60,262,904` bytes;
- SHA-256: `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- maximum required glibc symbol: `GLIBC_2.34`.

The focused RC static suite passed before packaging. The exact AppImage hash was rechecked before physical Bazzite QA, then the artifact passed direct launch, Browse, explicit Validate, `Reduce sprint stamina` Apply, `Restore original`, close, and restart on 2026-08-22.

No RC defect required a source change.

## Final rebuild/verification

Final verification rebuilt from the unchanged frozen source commit on 2026-08-22. The result was:

- size: `60,262,904` bytes;
- SHA-256: `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- byte-identical to the physically accepted RC AppImage;
- finished ELF audit: PASS with maximum required `GLIBC_2.34`.

Because the final AppImage is byte-identical to the exact artifact already exercised on physical Bazzite, the final rebuild preserves the accepted packaged QA evidence without requiring another gameplay or visual pass.

## Compatibility boundary

PySide6 `6.11.1` publishes its x86-64 Linux wheel for `manylinux_2_34`, so glibc `2.34` is the lowest practical x86-64 baseline for this pinned GUI dependency.

The pinned UBI 9 image enforces glibc `2.34` instead of inheriting the developer host's newer glibc. `libgcc_s.so.1` is intentionally resolved from the target system as a low-level base library. The accepted artifact has no audited bundled ELF requirement above `GLIBC_2.34` and launches on Bazzite.

This remains a bounded x86-64 compatibility claim. The UBI/RHEL 9 family may imply an x86-64-v2 CPU floor, so compatibility with older pre-v2 x86-64 processors is not established by this evidence.

## Publication state

Technical AppImage validation for the frozen source state is complete. No public AppImage binary has been authorized for release. Publication or integration still requires explicit approval.
