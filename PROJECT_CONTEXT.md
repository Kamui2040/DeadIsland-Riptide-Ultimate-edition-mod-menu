# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- Active release branch: `release/packaging-hardening`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. Released-option parity is integrated on fork `main`; upstream remains untouched. New gameplay tweaks remain deferred until a separate post-parity decision.

The release workflow is documented in `docs/RELEASE.md` and proceeds in this order: Flatpak proof, AppImage proof, shared packaging hardening, UI polish, release candidate, packaged Bazzite QA, final rebuild/verification, then explicitly approved release.

## Verified native Linux baseline

Accepted physical evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a universal requirement. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed.

## Current implementation state

Integrated `main` contains **42 semantic non-default options** covering released gameplay controls. All 42 pass disposable native candidate construction against the accepted baseline. Validated families include direct gameplay controls, Improved Loot, AI difficulty, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, all four non-default zombie-size modes, all eight non-default weather/time modes, and all seven non-default forced-spawn modes.

Choice groups fail closed. Runtime transforms validate source state, exact match counts, archive identity, and result state rather than relying on line numbers.

Forced-spawn parity is complete. Suiciders and both Bandit modes use native/bounded native-derived values; Butcher, Ram, Bloater, and Thug use only the minimum compatibility identifier lists required for released behavior, with SHA-256, syntax/count, pristine-vector, preserved-ordinal, exact-replacement, and post-transform validation. The inherited preset ZIP payloads are not copied, installed, or packaged. Issue #2 is closed as completed.

Accepted gameplay QA includes all four formerly blocked forced-spawn modes plus representative camera/FOV, firearm, weather, stamina, AI, zombie-size, and upgrading behavior. Every accepted live-game mutation used the normal transaction path and exact pristine restore.

## Application and transaction safety

The GUI-independent application service validates selections, compatibility, archive identity, and exclusivity before mutation. It preserves a pristine backup, builds candidates in isolated temporary storage, validates before install, rechecks the live source immediately before atomic replacement, and requires pristine restore before applying a different selection over a modified live archive.

The retained pristine backup is recovery material and must not be overwritten or deleted. The GUI exposes all 42 ready options and UI/catalog tests match the semantic catalog.

## Existing Python distribution evidence

The Python build pins `setuptools==83.0.0`, uses a deterministic PEP 517 backend wrapper, disables implicit package-data inclusion, and excludes provenance-sensitive inherited payloads. Reproducible Bazzite packaging produced byte-identical artifacts:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

Both passed payload checks and isolated installed-wheel validation. These remain developer/source-distribution evidence, not the primary one-click release path.

## End-user packaging

Primary targets:

- **Flatpak first** for SteamOS, Bazzite, and other Flatpak-friendly systems;
- **AppImage second** as the portable Linux alternative.

Normal users must not need to install Python, create a virtual environment, install PySide6, or use development commands.

### Accepted Flatpak proof

Physical Bazzite QA on 2026-08-20 accepted the bounded Flatpak proof at commit `92bed2cab98d6ecc5c2255a28a5f11bdd7024bab`.

- six static packaging checks passed;
- Flatpak Builder built and installed the application;
- packaged imports reported DIRUE `0.1.0.dev0` and PySide6 `6.11.1`;
- no blanket host-filesystem or network permission was required;
- the Qt folder chooser provided sufficient scoped access to the selected native DIRDE installation;
- native validation passed against the accepted pristine baseline;
- `Reduce sprint stamina` Apply succeeded;
- Restore succeeded and final status confirmed the live Data0 matched the retained pristine backup;
- GUI exit was clean.

KDE/UDisks D-Bus disconnect warnings appeared but did not block Browse, Validate, Apply, Restore, or exit. They are not an initial proof blocker and should be observed again during final packaged QA.

The initial Flatpak proof is complete. Final iconography, screenshots, release metadata, Flathub lint/submission work, and release-candidate checks remain later gates.

### Accepted AppImage proof

Physical Bazzite QA on 2026-08-20 accepted the AppImage proof at commit `7e1ad2f3a90571515a0646039e5f633d69b33687`.

The proof produced `DIRUE-Linux-0.1.0.dev0-x86_64.AppImage`, size `69,351,928` bytes, SHA-256 `7fec3fdd37c2698cca063755baa40b1fe1059026b2342a0477f90d9c429adc84`.

- nine static packaging checks passed;
- focused `git diff --check` passed;
- staged AppDir and extracted final-AppImage payload validation passed;
- artifact hash matched the build-reported hash;
- the AppImage launched directly and displayed the GUI;
- Browse and native validation passed;
- `Reduce sprint stamina` Apply succeeded;
- Restore succeeded and final status confirmed the pristine state;
- the same AppImage closed cleanly and launched successfully a second time.

The generated proof artifact and temporary build/worktree state were not committed or published.

The initial AppImage proof is complete.

### Shared packaging hardening

Stage 1 hardening is implemented on `release/packaging-hardening`. Flatpak and AppImage share one application identity, desktop entry, metainfo, icon, and launcher name. The Flatpak retains its bounded permission model. The AppImage builder pins and verifies `appimagetool` and the type-2 runtime rather than relying on mutable `continuous` assets, and records both the builder glibc and the intended compatibility floor.

Physical Bazzite QA on 2026-08-20 accepted hardening stage 1 at commit `15437a1ee0172cb79092fdc5c230759ff2d3d3bb`:

- 16 focused Flatpak/AppImage static tests passed;
- Flatpak hardened build passed;
- Flatpak packaged imports passed with DIRUE `0.1.0.dev0` and PySide6 `6.11.1`;
- Flatpak sandbox inspection still showed no blanket host-filesystem access;
- hardened AppImage build passed with pinned `appimagetool` `1.9.1` and runtime tag `20251108`;
- the Bazzite builder reported glibc `2.43` while the declared AppImage target floor is `2.34`;
- hardened AppImage artifact size was `69,351,928` bytes and SHA-256 `be8c05e18b7eadbc4dbf594aca7c97c2d47d732581c60421a28334566e9284a6`;
- artifact hash verification passed;
- `PACKAGING_HARDENING_STAGE1=PASS`.

Hardening stage 2 pins the portable AppImage build environment to `quay.io/pypa/manylinux_2_34_x86_64@sha256:64decb8ae4b373180c246525a755c0afb2ca136334f0d64b41cf5f229283a7b6`. Physical Bazzite probing on 2026-08-20 verified that exact image reports glibc `2.34`, but all probed bundled CPython 3.11.11 executables are static (`Py_ENABLE_SHARED=0`) and therefore cannot satisfy PyInstaller's shared-libpython requirement.

The baseline wrapper now builds pinned CPython `3.11.16` from the official source tarball inside the same digest-pinned glibc-2.34 container with `--enable-shared`. The source SHA-256 is pinned as `91bcdebfdde239a003ae93738a7fce0f9230fee5c4bc2b86f6e6e8c6f98aabe8`. Before invoking the hardened AppImage builder, the wrapper verifies the source digest, exact Python version, `Py_ENABLE_SHARED=1`, installed `libpython`, required standard-library modules, and pip. It still requires exactly one host-visible executable AppImage and emits authoritative host artifact/hash/size values.

This shared-CPython path is implemented but not yet physically accepted. The remaining stage-2 gate is a physical baseline build followed by double-build reproducibility, ELF glibc-symbol inspection, and packaged launch validation. Broader SteamOS/general-Linux AppImage portability is not claimed until those checks pass.

## UI-polish decision carried from packaging QA

The final GUI should use explicit validation: **Browse selects the folder only; Validate performs validation once.** Changing the selected path must invalidate the prior validation and disable Apply until the user validates the new path. This change belongs to the UI-polish stage, after packaging hardening.

## Validation boundary

Verified now:

- all 42 integrated non-default options pass native disposable candidate construction;
- the four formerly blocked forced-spawn modes pass bounded native gameplay QA with exact pristine restore;
- UI/catalog accounting passes at 42 options;
- transaction/recovery behavior remains validated;
- reproducible wheel/sdist packaging passes;
- bounded Flatpak build/import/sandbox/portal/Apply/Restore proof passes on physical Bazzite;
- bounded AppImage build/payload/launch/Apply/Restore/relaunch proof passes on physical Bazzite;
- shared packaging hardening stage 1 passes on physical Bazzite;
- the exact glibc-2.34 baseline image is physically verified on Bazzite;
- the image's bundled CPython 3.11.11 runtimes are physically verified as unsuitable for PyInstaller because they lack shared libpython;
- no GitHub Actions were used.

No further routine gameplay or legacy wheel/sdist QA is required absent a newly identified risk.

## Remaining release gates

1. **Finish shared packaging hardening** — physically validate the pinned shared-CPython baseline build, then validate two baseline AppImage builds for reproducibility, inspect ELF glibc requirements, verify packaged launch, keep Flatpak/AppImage metadata and payload checks aligned, and complete remaining artifact-integrity checks.
2. **UI polish** — including manual validation flow, first-run clarity, hierarchy/spacing, status/error presentation, Apply/Restore affordances, iconography, window behavior, and version/about information.
3. **Release candidate** — freeze one exact source commit and build both primary formats from it.
4. **Packaged Bazzite QA** — exercise both release-candidate artifacts as users receive them, including launch, validation, Apply, exact Restore, restart, and artifact/privacy checks.
5. **Final rebuild/verification** after accepted RC fixes.
6. **Explicit approval** before public release/binaries, Nexus publication, upstream submission, announcements, distribution/visibility changes, or GitHub Actions use.

## Cleanup and publication

Accepted evidence, provenance material, artifact hashes, and pristine recovery material remain preserved. Disposable worktrees, build environments, temporary candidates, and superseded QA residue are removed when no longer needed. Authentic game content and backups must never be committed.

No public release, binary publication, Nexus publication, upstream submission, announcement, GitHub Actions use, or other external publication has been authorized.
