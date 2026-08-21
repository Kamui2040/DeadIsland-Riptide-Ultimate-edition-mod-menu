# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- Active release branch: `release/rc-0.1.0-dev0`
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

## UI polish — complete

The accepted UI implementation is based on source state `2082bd88bc7960fc68104284d0e8dab7f90733c5`. The maintainer visually approved the packaged main window and About dialog and confirmed the required behavior on physical Bazzite.

Accepted UI behavior and presentation include:

- app short name **DIRDE UE Linux** and long title **Dead Island: Riptide DE Linux - Ultimate Edition**;
- explicit first-run sequence: choose folder, validate, select options, apply changes;
- Browse selects only; Validate performs explicit validation; Apply stays disabled until validation succeeds; changing the path invalidates prior validation;
- clear hierarchy and spacing, responsive option layout, bounded Activity area, and sensible dropdown sizing;
- clear status/error presentation and enabled/disabled Apply/Restore affordances;
- user-facing restore wording **Restore original**;
- responsive window behavior under resize/maximize/restore without inaccessible controls;
- concise hover help and the inline `NoClip vehicles` warning;
- footer version/authorship/license information and an About dialog with FireEyeEian attribution, Linux-port credit, project/support/original-mod links, and GPLv3 notice;
- maintainer-approved custom red penguin/Ripper icon shared by Flatpak and AppImage metadata.

The Flatpak exports scalable SVG plus 64x64 and 128x128 PNG icon variants under the standard hicolor paths. Physical checks confirmed both PNG files resolve to the intended dimensions, the SVG is present, and GTK resolves the application ID directly to the exported 128x128 PNG.

Bazaar still displays a generic package icon for this locally installed Flatpak in both the host-packaged and Flatpak Bazaar builds. Because the icon assets, export paths, application ID, raster dimensions, and direct GTK icon-theme resolution all pass, this is accepted as a Bazaar-side sideload/display limitation rather than a DIRDE packaging defect. No Bazaar-specific workaround is required for the release candidate.

## Release candidate — active

`release/rc-0.1.0-dev0` was created from the accepted UI source state. The branch is the release-candidate freeze line: build both end-user formats from one exact branch-head commit and do not add unrelated changes. Any accepted RC fix must be recorded, validated, and followed by a new exact RC build state.

## Validation boundary

Verified:

- all 42 released non-default options pass candidate construction;
- representative gameplay QA and exact pristine restore pass;
- transaction/recovery behavior is validated;
- wheel/sdist reproducibility passes;
- Flatpak proof and packaged UI functional/portal flow pass;
- AppImage proof, hardening, reproducibility, and `GLIBC_2.34` audit pass;
- maintainer-approved custom icon is landed with source-level SVG/raster consistency coverage;
- downloaded Flatpak sideload/install and Plasma launcher integration were observed on Bazzite with no game mutation;
- packaged UI first-run clarity, validation flow, status/errors, Apply/Restore states, responsive window behavior, iconography, and About/version presentation received explicit maintainer acceptance;
- direct GTK icon-theme lookup resolves the exported DIRDE icon; Bazaar's remaining generic sideload icon is classified as an external display limitation;
- no GitHub Actions were used.

Pending:

- build one Flatpak and one AppImage from the same exact RC branch-head commit;
- record authoritative artifact identity/hash/size for both;
- exercise both RC artifacts on physical Bazzite as users receive them, including launch, validation, Apply, exact Restore, restart, and artifact/privacy checks.

## Remaining release gates

1. **Release candidate** — build both primary formats from the same frozen `release/rc-0.1.0-dev0` commit and record their identities.
2. **Packaged Bazzite QA** — exercise both release-candidate artifacts as users receive them, including launch, validation, Apply, exact Restore, restart, and artifact/privacy checks.
3. **Final rebuild/verification** after any accepted RC fixes.
4. **Explicit approval** before public release/binaries, Nexus publication, upstream submission, announcements, distribution/visibility changes, or GitHub Actions use.

## Cleanup and publication

Accepted evidence, provenance material, artifact hashes, and pristine recovery material remain preserved. Disposable worktrees, build environments, temporary candidates, and superseded QA residue are removed when no longer needed. Authentic game content and backups must never be committed.

No public release, binary publication, Nexus publication, upstream submission, announcement, GitHub Actions use, or other external publication has been authorized.
