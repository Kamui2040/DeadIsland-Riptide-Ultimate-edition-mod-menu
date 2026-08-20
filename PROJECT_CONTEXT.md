# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- Active release branch: `release/flatpak-proof`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. Released-option parity is integrated on fork `main`. The validated 42-option parity state was integrated on 2026-08-17 and upstream remains untouched.

New gameplay tweaks remain deferred until a separate post-parity decision.

The active release phase is end-user packaging. The required order is documented in `docs/RELEASE.md`: Flatpak proof, AppImage proof, shared packaging hardening, UI polish, release candidate, packaged Bazzite QA, final rebuild/verification, then explicitly approved release.

## Verified native Linux baseline

Accepted physical evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a universal game requirement. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Current implementation state

Integrated `main` contains **42 semantic non-default options** covering the released gameplay controls. All 42 pass disposable native candidate construction against the accepted 3060-entry baseline.

Validated families include direct gameplay controls, Improved Loot, AI difficulty, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, all four non-default zombie-size modes, all eight non-default weather/time modes, and all seven non-default forced-spawn modes.

Choice groups fail closed on incompatible selections. Runtime transforms validate expected source state, exact match counts, archive identity, and result state rather than using historical line numbers.

## Forced-spawn parity and provenance

Default spawning matches native behavior. Forced-spawn transforms validate the complete pristine 165-call `m_AIPresets` vector before mutation.

- **Suiciders**: native donor; Native-validated and gameplay-validated.
- **Bandits with guns**: native donor; Native-validated.
- **Bandits with melee**: bounded whole-token reconstruction from validated pristine native values; Native-validated.
- **Butcher, Ram, Bloater, and Thug**: use only the minimum machine-facing compatibility identifier lists required to reproduce released behavior. Each target is pinned by SHA-256, syntax/identifier count, pristine-vector validation, preserved ordinal 60, exact 164-call replacement count, and post-transform validation.

The four formerly blocked modes were derived read-only from inherited upstream preset blobs as compatibility evidence. The preset ZIPs themselves are not copied, installed, or packaged. This narrow treatment does not assert redistribution rights over those ZIPs, Data0 archives, replacement files, or other Techland-derived content.

Issue #2 records the completed provenance, candidate, gameplay, restore, and packaging acceptance path and is closed as completed.

## Native candidate and gameplay QA

Accepted physical candidate QA for Butcher, Ram, Bloater, and Thug proves each candidate:

- retains all 3060 entries and archive member order;
- changes only `data/presets/aispawnbox_pre.def`;
- preserves active ordinal 60;
- replaces exactly the other 164 active `m_AIPresets` calls;
- passes ZIP integrity, candidate-hash, selected-option, and changed-member verification;
- leaves the live pristine Data0 unchanged during candidate-only QA.

Accepted bounded native gameplay QA then installed each mode through the normal application transaction path. Butchers, Rams, Bloaters, and Thugs were each confirmed in the native game. After every run, the native ELF process exited and the exact pristine Data0 was restored before the observation was accepted. The retained pristine backup remained valid and unchanged.

Representative accepted gameplay evidence also covers camera FOV82, Better Firearms POV82, darker storm/night, Run with weapons, One Hit AI, supersize active infected/walkers, Forced Suiciders, and Better Firearms Upgrading.

## Application and transaction safety

The GUI-independent application service validates selections, compatibility, archive identity, and exclusivity before mutation. It preserves a pristine backup from a recognized baseline, builds candidates in isolated temporary storage, validates candidates before installation, rechecks live source identity immediately before atomic replacement, and requires pristine restore before applying a different selection over a modified live archive.

The retained pristine backup is recovery material and must not be deleted or overwritten.

The integrated GUI exposes all 42 ready options. UI/catalog tests verify the ready options match the semantic catalog exactly.

## Packaging and distribution validation

The existing Python build system pins `setuptools==83.0.0`, uses a repo-local deterministic PEP 517 backend wrapper, disables implicit package-data inclusion, and excludes provenance-sensitive inherited payloads from Linux distributions. `tools/check_distribution.py` requires `forced_spawn_compat.py` in both wheel and sdist so the runtime module cannot be silently omitted.

A physical Bazzite packaging run for the 42-option state used an isolated PyPA `build==1.5.0` frontend and a commit-derived `SOURCE_DATE_EPOCH`. Two clean builds were byte-identical:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

Both artifact copies passed the distribution payload checker. The built wheel installed in an isolated environment; `pip check`, the `dirue` console entry point, direct `python -m dirue.cli`, the 42-option semantic/UI catalog, all four compatibility-mode registrations, and CLI/GUI entry-point metadata passed.

Those wheel/sdist results remain development/source-distribution evidence. They are not the primary end-user release path.

## End-user release packaging

The primary release targets are:

- **Flatpak first** for SteamOS, Bazzite, and other Flatpak-friendly Linux systems;
- **AppImage second** as the portable Linux alternative.

Normal users must not be required to install Python, create a virtual environment, install PySide6, or use development commands to launch the GUI.

### Accepted Flatpak proof

The Flatpak proof uses `org.kde.Platform` and `io.qt.PySide.BaseApp` 6.11, packages only `src/dirue` plus public-safe desktop metadata, and excludes the repository root and inherited game-content payloads from its source boundary. It requests no blanket host-filesystem or network permission.

Physical Bazzite QA on 2026-08-20 accepted the proof at commit `92bed2cab98d6ecc5c2255a28a5f11bdd7024bab`:

- the six static packaging checks passed;
- Flatpak Builder completed and installed the application;
- packaged imports reported DIRUE `0.1.0.dev0` and PySide6 `6.11.1`;
- permission inspection confirmed no blanket host-filesystem access;
- the graphical folder chooser granted sufficient scoped access to the selected native DIRDE installation without extra permissions;
- native game validation passed against the accepted pristine Data0 baseline;
- a single `Reduce sprint stamina` Apply transaction completed successfully;
- Restore completed successfully and final status confirmed live Data0 matched the retained pristine backup;
- the packaged GUI exited normally.

KDE/UDisks D-Bus disconnect warnings were observed during the GUI run, but they did not block Browse, Validate, Apply, Restore, or clean exit. They are not treated as a proof blocker; recurrence during later packaged QA should still be observed.

The initial Flatpak proof is therefore **complete**. Final iconography, screenshots, release metadata, Flathub submission lint, UI polish, and release-candidate artifact checks remain later release work.

AppImage proof work follows next. UI polish remains after both packaging proofs.

SteamOS is treated as an operating-system target, not as a Steam Deck-only target. Hardware-specific Steam Deck or Steam Machine validation is not claimed without corresponding hardware evidence.

## Validation boundary

- all 42 integrated non-default options pass native disposable candidate construction;
- the four formerly blocked forced-spawn modes pass bounded native gameplay QA with exact pristine restore;
- UI/catalog accounting passes at 42 options;
- forced-spawn exclusivity and fail-closed validation pass;
- application transaction and recovery behavior remain validated;
- reproducible wheel/sdist packaging and isolated installed-wheel checks pass for the 42-option state;
- bounded Flatpak build/import/sandbox/portal/Apply/Restore proof passes on physical Bazzite;
- no GitHub Actions were used.

No further routine gameplay or legacy wheel/sdist QA is required absent a newly identified risk. AppImage packaging, shared packaging hardening, UI polish, and final release-candidate QA remain separate pending gates.

## Remaining gates

1. Build and validate the AppImage proof from the same application source without host Python/PySide6 requirements.
2. Harden shared packaging/resource/config behavior and artifact-content checks for Flatpak and AppImage.
3. Polish the UI and validate it from packaged builds.
4. Freeze and build a release candidate from one exact source commit.
5. Complete packaged Bazzite end-to-end QA for Flatpak and AppImage.
6. Rebuild and verify final-version artifacts after any accepted RC fixes.
7. Obtain explicit approval before public release, binaries, Nexus publication, upstream submission, announcements, distribution, visibility changes, or GitHub Actions use.

## Cleanup and publication

Accepted evidence, provenance material, artifact hashes, and the pristine recovery backup remain preserved. Temporary candidates, build environments, disposable worktrees, and superseded QA residue are removed when no longer needed. Authentic game content and backups must never be committed.

No public release, binary publication, Nexus publication, upstream submission, announcement, GitHub Actions use, or other external publication has been authorized.
