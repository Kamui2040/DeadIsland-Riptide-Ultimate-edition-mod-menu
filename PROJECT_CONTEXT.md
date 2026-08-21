# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- Active release branch: `release/ui-polish`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful Linux port of released DIRUE behavior for Dead Island: Riptide Definitive Edition. Released gameplay parity is integrated on fork `main`; upstream remains untouched. New gameplay tweaks remain deferred.

Release sequence: Flatpak proof, AppImage proof, shared packaging hardening, UI polish, release candidate, packaged Bazzite QA, final rebuild/verification, then explicitly approved release.

## Verified game baseline

Accepted physical evidence for the audited installation:

- ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is accepted evidence for the audited installation, not a universal requirement. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed.

## Gameplay parity and transaction safety

Integrated `main` contains **42 semantic non-default options** covering released DIRUE gameplay controls. All 42 pass disposable candidate construction against the accepted baseline. Representative gameplay QA, all released forced-spawn families, transaction safeguards, and exact pristine restore are accepted.

Choice groups fail closed. Runtime transforms validate source state, exact match counts, archive identity, and result state rather than relying on line numbers. Inherited preset ZIP payloads are not copied, installed, or packaged.

The GUI-independent application service validates compatibility and selection state before mutation, preserves a pristine backup, builds candidates in temporary storage, validates before install, rechecks the live source before atomic replacement, and requires pristine restore before applying a different selection over a modified archive.

## Distribution evidence

Reproducible developer/source artifacts were accepted:

- wheel SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

Primary end-user targets are Flatpak first and AppImage second. Normal users must not need to install Python or PySide6.

### Flatpak

Physical Bazzite proof QA passed with PySide6 `6.11.1`, bounded sandbox permissions, portal-based game-folder access, Validate, Apply, exact Restore, and clean exit. No blanket host-filesystem or network permission was needed.

### AppImage

Shared hardening stage 1 passed at `15437a1ee0172cb79092fdc5c230759ff2d3d3bb`.

Shared hardening stage 2 passed at `f37d39165212b84954cf60c34b0d97bdec313511` with:

- digest-pinned UBI 9 Python 3.11 baseline;
- glibc `2.34`, Python `3.11.13`, fixed `PYTHONHASHSEED=1`, and source-derived `SOURCE_DATE_EPOCH`;
- deterministic AppDir SHA-256 `5741e2dab0460061bc5a1d26187a8eb5323ec30a0b6187757c4cd067d5a175ce`;
- byte-identical final AppImages;
- final AppImage SHA-256 `07284a312c929cd46bcc191ba9f76f3683d2134f36e912622b77656079376dd4`;
- final size `60,246,520` bytes;
- 179 ELF files audited with maximum required `GLIBC_2.34`;
- incompatible container-collected `libgcc_s.so.1` excluded and checker-enforced;
- direct packaged launch passed.

Issue #5 is closed. Portability evidence is bounded to x86-64 systems meeting the glibc 2.34 floor and target-system base-library expectations; older pre-x86-64-v2 CPUs are not proven compatible.

## UI polish — active

Earlier packaged functional checks passed on both AppImage and Flatpak. They established the explicit validation flow, portal Browse behavior, bounded Flatpak permissions, packaged launch, and no game mutation. These passes did **not** constitute maintainer visual approval.

The maintainer then supplied a consolidated visual/usability review. The current `release/ui-polish` implementation now includes:

- app short name **DIRDE UE Linux**;
- long title **Dead Island: Riptide DE Linux - Ultimate Edition**;
- FireEyeEian and Kamui2040 author credit;
- About links for the project GitHub page, Kamui2040 Ko-fi, and the original Nexus mod;
- a new original project SVG icon with no game assets;
- removed introductory technical paragraph and removed `native` from user-facing GUI wording;
- short validation messages such as `Game folder validated.` and `Can't validate game folder.`;
- Flatpak game-folder field is read-only because portal Browse is the supported access path; non-Flatpak builds still allow typed paths;
- Activity is limited to three visible recent lines;
- a taller default window and more vertical space for options;
- responsive option layout: AI and Firearms stay on one row when space permits and wrap when the window narrows;
- Gameplay options grouped by Movement, Combat, Gear & loot, Comfort, and Vehicles, with groups reflowing across available width;
- short natural hover help for every checkbox, choice group, and choice;
- an inline `NoClip vehicles` warning that appears when enabled because the option can leave the player stuck;
- source-level regression tests for naming, validation flow, layout, hover help, warning behavior, metadata, and custom icon identity.

This post-review UI revision has **not yet received packaged visual approval**. Because UI and shared metadata changed after the earlier packaged functional passes, run focused static/package smoke checks again before using a newly built package for the next maintainer visual review.

## Validation boundary

Verified:

- all 42 released non-default options pass candidate construction;
- representative gameplay QA and exact pristine restore pass;
- transaction/recovery behavior is validated;
- wheel/sdist reproducibility passes;
- Flatpak proof and earlier packaged UI functional/portal flow pass;
- AppImage proof, hardening, reproducibility, and `GLIBC_2.34` audit pass;
- no GitHub Actions were used.

Pending:

- static/package smoke validation of the latest consolidated UI revision;
- explicit maintainer visual approval of the newly packaged UI.

## Remaining release gates

1. **Finish UI polish** — validate the latest consolidated UI revision in packaged form, obtain explicit maintainer visual approval, and fix any accepted findings.
2. **Release candidate** — freeze one exact source commit and build both primary formats from it.
3. **Packaged Bazzite QA** — exercise both release-candidate artifacts as users receive them, including launch, validation, Apply, exact Restore, restart, and artifact/privacy checks.
4. **Final rebuild/verification** after accepted RC fixes.
5. **Explicit approval** before public release/binaries, Nexus publication, upstream submission, announcements, distribution/visibility changes, or GitHub Actions use.

## Cleanup and publication

Accepted evidence, provenance material, artifact hashes, and pristine recovery material remain preserved. Disposable worktrees, build environments, temporary candidates, and superseded QA residue are removed when no longer needed. Authentic game content and backups must never be committed.

No public release, binary publication, Nexus publication, upstream submission, announcement, GitHub Actions use, or other external publication has been authorized.
