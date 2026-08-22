# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- Release evidence branch: `release/final-verification`
- Frozen release source commit: `c3e3b97494058e8da199658f4f265e3eb84f0201`
- Main integration merge commit: `cc62b1d2874ad571e2c17370dca5d43a75adc477`
- Package version: `0.1.0.dev0`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful Linux port of released DIRUE behavior for Dead Island: Riptide Definitive Edition. Released gameplay parity is integrated on fork `main`; upstream remains untouched. New gameplay tweaks remain deferred.

Technical validation, main integration, and publication preparation are complete. No public binary release, Nexus publication, upstream submission, announcement, distribution/visibility change, or GitHub Actions use has been performed.

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

Primary end-user targets are Flatpak first and AppImage second. Normal packaged users do not need to install Python or PySide6 separately.

### Flatpak

Physical Bazzite proof QA passed with PySide6 `6.11.1`, bounded sandbox permissions, portal-based game-folder access, Validate, Apply, exact Restore, and clean exit. No blanket host-filesystem or network permission was needed.

### AppImage

Shared hardening stage 1 passed at `15437a1ee0172cb79092fdc5c230759ff2d3d3bb`.

Shared hardening stage 2 passed at `f37d39165212b84954cf60c34b0d97bdec313511` with:

- digest-pinned UBI 9 Python 3.11 baseline;
- glibc `2.34`, Python `3.11.13`, fixed `PYTHONHASHSEED=1`, and source-derived `SOURCE_DATE_EPOCH`;
- deterministic AppDir SHA-256 `5741e2dab0460061bc5a1d26187a8eb5323ec30a0b6187757c4cd067d5a175ce`;
- byte-identical final AppImages;
- stage-2 AppImage SHA-256 `07284a312c929cd46bcc191ba9f76f3683d2134f36e912622b77656079376dd4`;
- stage-2 size `60,246,520` bytes;
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

Bazaar still displays a generic package icon for this locally installed Flatpak in both the host-packaged and Flatpak Bazaar builds. Because the icon assets, export paths, application ID, raster dimensions, and direct GTK icon-theme resolution all pass, this is accepted as a Bazaar-side sideload/display limitation rather than a DIRDE packaging defect. No Bazaar-specific workaround is required.

## Frozen release candidate — complete

The frozen release source commit is `c3e3b97494058e8da199658f4f265e3eb84f0201` on `release/rc-0.1.0-dev0`. Both end-user formats were built from that exact state.

Accepted RC artifact identities:

- Flatpak: 56,117,784 bytes, SHA-256 `523e4b0921a09a1c05caa20d67cbcfe7e9090bb416d7d0520848665ced204031`;
- AppImage: 60,262,904 bytes, SHA-256 `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- AppImage finished-artifact audit: maximum required `GLIBC_2.34`.

The focused RC static suite passed 52 tests before packaging. The Flatpak retained the bounded permission model with no network permission or broad host/home filesystem permission. The AppImage packaging checker and finished ELF audit passed.

## Packaged Bazzite RC QA — complete

Physical Bazzite QA on 2026-08-22 exercised both exact RC artifacts.

The RC Flatpak passed exact hash recheck, per-user install, bounded permission inspection, launch, Browse, explicit Validate, `Reduce sprint stamina` Apply, `Restore original`, close, and restart.

The RC AppImage passed exact hash recheck, direct launch, Browse, explicit Validate, `Reduce sprint stamina` Apply, `Restore original`, close, and restart.

No RC defect requiring a source fix was found, so the frozen release source commit remained unchanged.

## Final rebuild/verification — complete

Physical Bazzite final verification on 2026-08-22 rebuilt both formats from the unchanged frozen release source commit.

Accepted final-verification results:

- focused static/package tests: PASS;
- final-verification Flatpak: 56,114,672 bytes, SHA-256 `1eec07e171303cf55b2ce4cfd944e543ced05a7ff05ef74a82368560c1bdc073`;
- final AppImage: 60,262,904 bytes, SHA-256 `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- final AppImage is byte-identical to the exact AppImage already accepted in packaged Bazzite QA;
- finished AppImage ELF audit: PASS with maximum required `GLIBC_2.34`.

The final-verification Flatpak has a different bundle hash/size from the physically exercised RC Flatpak. Flatpak bundle byte reproducibility was not a release requirement. The exact-artifact boundary is therefore recorded explicitly: Apply/Restore/restart QA applies to RC Flatpak SHA-256 `523e4b...`, while SHA-256 `1eec07...` is the later final-verification rebuild from the same unchanged frozen source state.

No source change occurred between RC acceptance and final verification.

## Main integration — complete

PR #7 integrated `release/final-verification` into `main` on 2026-08-22 at merge commit `cc62b1d2874ad571e2c17370dca5d43a75adc477`. This was an integration-only approval. It did not itself publish binaries or perform any external release action.

## Publication preparation — complete

Manual publication materials are prepared on the focused documentation branch:

- `docs/PUBLICATION.md` — artifact selection, installation text, Nexus Mods copy, Ko-fi announcement copy, compatibility boundaries, and manual publication checklist;
- `docs/RELEASE_NOTES_0.1.0.dev0.md` — public-facing release notes;
- `docs/RELEASE_CHECKSUMS_0.1.0.dev0.txt` — SHA-256 manifest for the recommended exact artifacts.

Recommended manual publication set:

- physically exercised RC Flatpak SHA-256 `523e4b0921a09a1c05caa20d67cbcfe7e9090bb416d7d0520848665ced204031`;
- AppImage SHA-256 `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`, which was physically exercised and reproduced byte-identically in final verification.

The later final-verification Flatpak SHA-256 `1eec07e171303cf55b2ce4cfd944e543ced05a7ff05ef74a82368560c1bdc073` remains preserved as build-integrity evidence and is not interchangeable with the stronger exact-artifact QA evidence for the RC Flatpak.

## Validation boundary

Verified:

- all 42 released non-default options pass candidate construction;
- representative gameplay QA and exact pristine restore pass;
- transaction/recovery behavior is validated;
- wheel/sdist reproducibility passes;
- Flatpak proof and packaged portal/functional flow pass;
- AppImage proof, hardening, reproducibility, and `GLIBC_2.34` audit pass;
- maintainer-approved custom icon is landed with source-level SVG/raster consistency coverage;
- packaged UI first-run clarity, validation flow, status/errors, Apply/Restore states, responsive window behavior, iconography, and About/version presentation received explicit maintainer acceptance;
- direct GTK icon-theme lookup resolves the exported DIRDE icon; Bazaar's remaining generic sideload icon is classified as an external display limitation;
- both RC artifacts are tied to frozen commit `c3e3b97494058e8da199658f4f265e3eb84f0201` with recorded hashes and sizes;
- both exact RC artifacts pass packaged Bazzite launch, validation, Apply, exact Restore, and restart QA;
- final rebuild/verification from the unchanged frozen commit passes;
- final AppImage exactly matches the accepted RC AppImage and remains bounded to `GLIBC_2.34`;
- validated release state is integrated into `main` through PR #7;
- public-safe manual publication copy and checksum manifest are prepared;
- no GitHub Actions were used.

Not claimed:

- the final-verification Flatpak is byte-identical to the RC Flatpak;
- the final-verification Flatpak itself received a second Apply/Restore/restart pass;
- Steam Deck- or Steam Machine-specific hardware validation;
- public release or publication.

## Remaining release gate

Public upload/publishing remains a manual external action. Before upload, the selected local files must be verified against their recorded sizes and `docs/RELEASE_CHECKSUMS_0.1.0.dev0.txt`. After publication, the public downloads must be rechecked against the same hashes before project state is updated to claim availability.

Artifact selection must preserve the recorded exact-artifact distinction rather than implying that the two Flatpak bundle hashes are interchangeable evidence.

## Cleanup and publication

Accepted evidence, provenance material, artifact hashes, and pristine recovery material remain preserved. Disposable worktrees, build environments, temporary candidates, and superseded QA residue are removed when no longer needed. Authentic game content and backups must never be committed.

Main integration and publication preparation are complete. No public release, binary publication, Nexus publication, upstream submission, announcement, GitHub Actions use, or other external publication has been performed.
