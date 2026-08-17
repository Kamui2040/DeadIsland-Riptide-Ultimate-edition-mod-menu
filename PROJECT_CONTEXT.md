# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- Focused parity branch: `agent/forced-spawn-identifiers`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. The previously validated Linux implementation was integrated into fork `main` by approved fast-forward on 2026-08-16. The focused branch now resolves the final four released forced-spawn choices—Butcher, Ram, Bloater, and Thug—and has passed native candidate, live gameplay, exact-restore, and reproducible packaging validation. Released-option parity is technically complete on the focused branch. `main` remains unchanged until explicit integration approval.

New gameplay tweaks remain deferred until the validated parity branch is integrated.

## Verified native Linux baseline

Accepted physical evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a universal game requirement. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Current implementation state

Integrated `main` contains **38 semantic non-default options**. Focused branch `agent/forced-spawn-identifiers` contains **42 semantic non-default options** after adding Butcher, Ram, Bloater, and Thug forced spawning. All 42 pass disposable native candidate construction against the accepted 3060-entry baseline.

Validated families include direct gameplay controls, Improved Loot, AI difficulty, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, all four non-default zombie-size modes, all eight non-default weather/time modes, and all seven non-default forced-spawn modes.

Choice groups fail closed on incompatible selections. Runtime transforms validate expected source state, exact match counts, archive identity, and result state rather than using historical line numbers.

## Forced-spawn parity and provenance

Default spawning matches native behavior. Forced-spawn transforms validate the complete pristine 165-call `m_AIPresets` vector before mutation.

- **Suiciders**: native donor; Native-validated and gameplay-validated.
- **Bandits with guns**: native donor; Native-validated.
- **Bandits with melee**: bounded whole-token reconstruction from validated pristine native values; Native-validated.
- **Butcher, Ram, Bloater, and Thug**: use only the minimum machine-facing compatibility identifier lists required to reproduce released behavior. Each target is pinned by SHA-256, syntax/identifier count, pristine-vector validation, preserved ordinal 60, exact 164-call replacement count, and post-transform validation.

The four formerly blocked modes were derived read-only from the inherited upstream preset blobs as compatibility evidence. The preset ZIPs themselves are not copied, extracted into runtime state, installed, or packaged. This narrow treatment does not assert redistribution rights over those ZIPs, Data0 archives, replacement files, or other Techland-derived content.

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

The focused branch enables all four formerly disabled forced-spawn choices. UI/catalog tests verify the 42 ready options match the semantic catalog exactly.

## Packaging and distribution validation

The build system pins `setuptools==83.0.0`, uses a repo-local deterministic PEP 517 backend wrapper, disables implicit package-data inclusion, and excludes provenance-sensitive inherited payloads from Linux distributions. `tools/check_distribution.py` now requires `forced_spawn_compat.py` in both wheel and sdist so the new runtime module cannot be silently omitted.

A fresh physical Bazzite packaging run for the 42-option focused branch used an isolated PyPA `build==1.5.0` frontend and a commit-derived `SOURCE_DATE_EPOCH`. Two clean builds were byte-identical:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

Both artifact copies passed the distribution payload checker. The built wheel installed in an isolated environment; `pip check`, the `dirue` console entry point, direct `python -m dirue.cli`, the 42-option semantic/UI catalog, all four compatibility-mode registrations, and CLI/GUI entry-point metadata passed. The primary working branch, HEAD, and status remained unchanged, and disposable worktrees/build artifacts/QA environments were removed.

Earlier 38-option reproducible hashes remain historical evidence only; the hashes above are the accepted artifacts for the current focused-branch head tested on 2026-08-17.

## Validation boundary

- all 42 focused-branch non-default options pass native disposable candidate construction;
- the four newly resolved forced-spawn modes pass bounded native gameplay QA with exact pristine restore;
- UI/catalog accounting passes at 42 options;
- forced-spawn exclusivity and fail-closed validation pass;
- application transaction and recovery behavior remain validated;
- fresh reproducible wheel/sdist packaging and isolated installed-wheel checks pass for the 42-option state;
- no GitHub Actions were used.

No further routine gameplay or packaging QA is required absent a newly identified risk.

## Remaining gates

1. **Explicit approval is required before integrating `agent/forced-spawn-identifiers` into fork `main` and realigning `linux-port`.**
2. Public releases/binaries, Nexus publication, upstream submission, announcements, distribution/visibility changes, and GitHub Actions remain unauthorized unless separately approved.

## Cleanup and publication

Accepted evidence, provenance material, artifact hashes, and the pristine recovery backup remain preserved. Temporary candidates, build environments, disposable worktrees, and superseded QA residue are removed when no longer needed. Authentic game content and backups must never be committed.

No public release, binary publication, Nexus publication, upstream submission, announcement, GitHub Actions use, or other external publication has been authorized.
