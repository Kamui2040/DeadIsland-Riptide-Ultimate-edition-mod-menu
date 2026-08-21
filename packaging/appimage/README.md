# AppImage packaging

This directory contains the portable AppImage packaging for DIRUE Linux. The initial Bazzite proof and shared packaging hardening are accepted; the hardened path is the basis for later release-candidate builds.

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

The build pins:

- PyInstaller `6.22.2`;
- PySide6 `6.11.1`;
- `appimagetool` `1.9.1` x86-64, SHA-256 `ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0`;
- AppImage type-2 runtime tag `20251108` x86-64, SHA-256 `2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d`;
- UBI 9 Python 3.11 baseline image `registry.access.redhat.com/ubi9/python-311@sha256:7b6cb58d3ff034df7b300800bd89a469d9bd2f739d43250d76b9c9e805307ab5`.

Both AppImage tool downloads are verified before execution. The runtime is passed explicitly with `--runtime-file`, so `appimagetool` cannot silently fetch a mutable continuous runtime during the build.

Physical Bazzite probing on 2026-08-21 verified that the pinned UBI image reports glibc `2.34`, provides Python `3.11.13` at `/usr/bin/python3.11`, exposes shared `libpython`, imports the required `_ssl`, `bz2`, `ctypes`, `lzma`, `venv`, and `zlib` modules, and has pip available.

The previously explored manylinux baseline was rejected for PyInstaller use because its probed CPython 3.11 runtimes were static. A temporary source-built CPython approach was also rejected after physical validation showed missing extension modules. Neither rejected approach is used by the current builder.

## Build entry points

`build.sh` is the inner AppImage builder. It is useful for bounded host-side proof work and records the glibc version of the environment that produced the artifact.

`build-baseline.sh` is the release-portability entry point. It uses rootless Podman, mounts the repository read-only, writes only to the requested output directory, and runs under the exact digest-pinned UBI image. Before invoking `build.sh`, it requires glibc `2.34`, exact Python `3.11.13`, `Py_ENABLE_SHARED=1`, an installed shared `libpython`, the required extension modules, pip, and the inner build commands.

The wrapper fails closed unless exactly one AppImage appears in the host output directory after the container exits. It verifies that host-visible artifact is executable and emits authoritative `APPIMAGE_BASELINE_ARTIFACT`, `APPIMAGE_BASELINE_SHA256`, and `APPIMAGE_BASELINE_SIZE` values. Callers must consume those host values rather than infer a host path from the container's `/output` path.

From the repository root on x86-64 Linux:

```bash
python3 -m unittest tests.test_appimage_packaging tests.test_flatpak_packaging tests.test_glibc_audit
packaging/appimage/build-baseline.sh /path/to/output
```

The generated AppDir and extracted final AppImage are both checked. The checker requires the bundled Python/PySide6 runtime, verifies shared desktop/AppStream identity, rejects known inherited/game payload names, rejects symlinks escaping the AppDir, and rejects base libraries that are deliberately required from the target system.

The finished AppImage is also audited through ELF program/dynamic headers. The audit fails if a bundled dynamic ELF requires a `GLIBC_*` symbol newer than the declared `2.34` floor; stripped or static ELFs do not need section tables to be audited correctly.

## Accepted baseline build

Physical Bazzite QA on 2026-08-21 accepted a full build through the UBI wrapper at commit `40813fc8260a94b9b0594dce4f23fb02ea0dbe1f`.

The wrapper verified glibc `2.34` and Python `3.11.13`, produced exactly one host-visible executable AppImage, and the artifact launched successfully. The artifact size was `60,295,672` bytes and SHA-256 was `4164af8cd4bfd762d7e0d0a2183475e017a1df09c55873252e05c1c3e81b6730`.

This established that the pinned UBI environment could produce and launch the hardened AppImage before the final reproducibility and ELF-compatibility gates were added.

## GLIBC audit finding

Physical stage-2 auditing on 2026-08-21 identified the PyInstaller-collected `libgcc_s.so.1` as requiring `GLIBC_2.35`. That copy came from the UBI build environment and would have raised the resulting AppImage's effective compatibility floor above the intended `2.34` target.

`libgcc_s.so.1` is therefore treated as a target-system base runtime rather than bundled payload. `build.sh` removes any collected copy before the AppDir is assembled, `check_appdir.py` rejects the name if it reappears anywhere in the AppImage payload, and the finished-artifact GLIBC audit remains mandatory for all bundled ELFs. The 2.34 floor is not raised to accommodate a container-specific base-library copy.

## Reproducible hardened baseline

An initial post-exclusion double build was not byte reproducible. PyInstaller documents that deterministic builds require a fixed `PYTHONHASHSEED`, so the builder now fixes `PYTHONHASHSEED=1`, fixes locale/timezone inputs, normalizes every AppDir timestamp including symlinks to the supplied `SOURCE_DATE_EPOCH`, and emits `APPIMAGE_APPDIR_CONTENT_SHA256` over entry type, mode, path, symlink target, and file content.

Physical Bazzite QA on 2026-08-21 accepted the complete hardening stage 2 at commit `f37d39165212b84954cf60c34b0d97bdec313511`:

- both builds used glibc `2.34`, Python `3.11.13`, `PYTHONHASHSEED=1`, and the same source-derived `SOURCE_DATE_EPOCH`;
- both AppDirs matched at SHA-256 `5741e2dab0460061bc5a1d26187a8eb5323ec30a0b6187757c4cd067d5a175ce`;
- both final AppImages were byte-identical;
- final AppImage SHA-256 was `07284a312c929cd46bcc191ba9f76f3683d2134f36e912622b77656079376dd4`;
- final size was `60,246,520` bytes;
- the ELF audit inspected 179 files and reported maximum required `GLIBC_2.34`;
- the bundled `libgcc_s.so.1` exclusion remained enforced;
- direct AppImage launch passed.

This closes the stage-2 reproducibility defect tracked as Issue #5 and completes shared AppImage packaging hardening.

## Compatibility boundary

PySide6 `6.11.1` publishes its x86-64 Linux wheel for `manylinux_2_34`, so glibc `2.34` is the lowest practical x86-64 baseline for this pinned GUI dependency.

The pinned UBI 9 image enforces glibc `2.34` rather than inheriting the developer host's newer glibc. `libgcc_s.so.1` is intentionally resolved from the target system as a low-level base library. The accepted artifact has no audited bundled ELF requirement above `GLIBC_2.34` and launches on Bazzite.

This is still a bounded x86-64 compatibility claim. The UBI/RHEL 9 family may imply an x86-64-v2 CPU floor, so compatibility with older pre-v2 x86-64 processors is not established by this evidence.

## Remaining release work

The initial AppImage proof, shared packaging hardening, and UI-polish gate are complete. The current stage is the release-candidate build on `release/rc-0.1.0-dev0`. The AppImage and Flatpak must be built from the same exact frozen commit, followed by packaged Bazzite QA, final rebuild/verification after any accepted RC fixes, and explicit approval before public release.
