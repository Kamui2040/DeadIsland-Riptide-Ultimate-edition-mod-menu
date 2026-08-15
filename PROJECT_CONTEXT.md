# PROJECT_CONTEXT.md

## Repository

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Default branch: `main`
- Active Linux-port branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

## Current milestone

**Milestone 1: native Linux feature-parity port of the existing DIRUE release.**

Scope is compatibility and faithful behavior. New gameplay tweaks stay deferred until parity is complete and validated.

## Verified native Linux baseline

A native Linux Steam installation has been checked with these results:

- `DeadIslandRiptideGame` is a native Linux ELF executable.
- `<DIRDE_ROOT>/DIR/Data0.pak` is ZIP-compatible.
- Archive entry count: 3060.
- Archive size: 7,932,941 bytes.
- SHA-256: `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

Representative patch targets were present, including `default_levels.xml`, `inventory_gen.scr`, intro movies, weather, and glow scripts.

Result: `NATIVE_DATA0_COMPATIBILITY_BASELINE_PASS`.

The hash is a known baseline, not a permanent requirement.

## Native parity evidence

A physical-machine read-only audit completed successfully on 2026-08-15. The repository's then-current 44-test suite passed first. Native validation, parity inspection, and the first preset comparison completed while `Data0.pak` retained the exact same SHA-256 before and after that run.

That audit verified these native prior states:

- all direct `default_levels.xml` values used by sprint/jump stamina, running with weapons, movement, ammo, door breaking, durability, bullet penetration, and default FOV;
- both sunflare variables at `1.0`;
- all five Deeper Pockets skill files at `desc_params="2;4;6"` and `InventorySize change="2"`;
- the six Improved Loot target blocks and their default color weights;
- one active intro `File` statement whose first quoted argument is `Intro_720p`, while the inspected DI intro/subtitle statements are already commented;
- one active declaration for each reverb directive plus 52 active `ReverbPreset` and 52 active `ReverbWetDryMix` calls.

A later disposable-candidate report exercised the 13-option ready catalog against the same native baseline. Twelve options produced validated 3060-entry candidates. `skip_intro_videos` alone failed closed because its first implementation incorrectly required `File("Intro_720p")` to have no later arguments. The Linux helper has since been corrected to identify the call by its first quoted argument while preserving any later arguments; a regression test now covers that native-style shape. A physical rerun is still required before calling all 13 candidates native-validated.

Raw local audit output, uploaded QA reports, and machine-specific paths are not committed to Git.

## Vehicle noclip evidence

The native car file has five active `Ignore` sites:

- `ContactParams:Terrain` = `0`
- `ContactParams:SimpleObjects` = `0`
- `ContactParams:NonODEObjects` = `0`
- `ContactParams:ODEObjects` = `0`
- `ContactParams:Water` = `1`

The old-boat file has the same five named contact blocks, all at `0`.

The released AHK changes exactly two calls in each file. That source behavior is not enough by itself to choose two native blocks safely. Noclip therefore remains excluded from the ready catalog. `audit-research` now records native line numbers plus block/call ordinals so the historical source lines can be correlated once for research without becoming runtime patch targets.

## Firearm evidence

`DIRUE.ahk` remains the behavioral source for the intended firearm values. The native research report now groups relevant calls by actual `Item:` block. It confirms stable weapon identities for pistols/revolvers, shotgun families, automatic/burst/single-shot rifles, Fury firearms, legendary firearms, and additional native weapons.

The original nearest-line research proved that blindly choosing the call nearest an old AHK line can drift into a neighboring weapon block. Historical line numbers are therefore research hints only.

The remaining firearm task is to correlate source edits to the correct occurrence inside each named native item. The updated research audit reports each relevant call's native line number and ordinal within its item/property sequence. Final Linux patch rules must use named item identity plus validated property sequences and expected prior values, never historical source lines.

Better firearms upgrading is especially sensitive because the AHK writes `ShotTime`/`ReloadTime` into placeholder locations that are not active calls in the pristine native archive. The Linux port must reconstruct those insertions from native semantic anchors rather than reproduce the placeholder mechanism.

## Preset-backed options

The second preset report established the following high-level state:

- `ai_norm.zip` matches the native AI tree represented by the preset;
- one-hit AI differs in two native AI files;
- hard AI differs in 57 files;
- headshot-only AI differs in 20 files;
- `Default_spawns.zip` matches the native forced-spawn target, while every forced variant changes `aispawnbox_pre.def`;
- `Time-weather_vanilla.zip` matches the compared native weather targets, while the other weather/time variants change one or three principal files depending on the choice;
- `PRESETS_NORM_ZOMSIZE.zip` matches the native zombie-size targets, while the four non-default size choices change four principal preset files.

The report also confirmed that many preset differences are structural rather than simple unique key/value replacements. Full preset files are not being copied into Git. The preset audit has since been expanded to number repeated semantic identities and recognize simple generic call-argument changes so the next physical read can distinguish true structural replacements from earlier parser blind spots.

Preset-derived transformations will be accepted only when their entire behavior can be represented by public-safe semantic definitions with validated prior state. Provenance-sensitive full replacements remain out of Git.

## Important upstream archive difference

The inherited repository `Data0.pak` is an older, different archive. The Linux port must not use it as an install payload or patch source.

Runtime work must start from the user's validated installed archive or a verified pristine backup derived from it. Candidate changes must be built in temporary storage, validated, and installed atomically.

## Upstream hazards not carried into Linux

`DIRUE.ahk` remains the Milestone-1 behavioral specification, but these implementation details are intentionally not copied:

- patching from the bundled repository `Data0.pak`;
- deleting the live archive before a replacement is validated;
- hard-coded line numbers as the patch mechanism;
- placeholder-based disable paths;
- full-file or directory preset replacement without provenance review;
- AutoHotkey/Win32 helpers and `.exe` processes.

## Implemented Linux core

The Python core under `src/dirue/` contains no newly added proprietary game content and currently provides:

- native Linux game-root validation using the ELF executable;
- ZIP validation with CRC, required-entry, traversal, backslash-path and duplicate-member checks;
- safe temporary extraction and metadata-preserving rebuild;
- pristine backup creation without silent overwrite;
- validated atomic candidate installation and restore;
- in-memory candidate building that refuses source overwrite, unresolved options, duplicate options, and no-op/non-pristine input;
- semantic XML, `VarFloat`, simple call, named call, scoped loot, Deeper Pockets, intro-comment and reverb transforms;
- structured named-block helpers with brace-aware scope validation for future vehicle/firearm work;
- a ready direct catalog of 13 native-verified text options, with unresolved noclip excluded;
- deterministic JSON CLI validation;
- `audit-native`, a read-only native parity audit;
- `audit-presets`, a read-only preset comparison with semantic completeness classification;
- `audit-research`, a read-only block-aware firearm/noclip research audit.

No audit command extracts, installs, or modifies game content.

## Validation evidence

Validation evidence is kept specific to the code state it tested:

- the first physical read-only audit ran the then-current full 44-test suite successfully before accessing the native game;
- that physical audit proved `Data0.pak` remained byte-for-byte unchanged by hash;
- twelve ready options later produced validated individual candidates against the native baseline; the intro option failed closed and exposed the multi-argument call assumption described above;
- earlier feature work passed its focused synthetic suites when introduced;
- the previous intro/loot/reverb-count/block-research/preset-completeness work passed 14 focused local tests plus Python compilation before the latest refinements;
- the corrected multi-argument intro matcher passed a focused synthetic round-trip check after the native failure was analyzed;
- repeated preset semantic identity numbering passed a focused synthetic check;
- the current remote branch still needs a full-suite run after the latest structured/research/preset changes;
- packaging previously produced a wheel successfully without network dependencies.

No GitHub Actions were used.

The installed Steam game has still **not been modified by the Linux port**. Native mutation remains a later, separate gate.

GitHub Issues are currently disabled for this repository. An attempt to create a focused firearm-mapping Issue returned HTTP 410, so unresolved work remains tracked here rather than changing repository settings.

## Current gates

1. Run the current full test suite and compilation on the physical checkout.
2. Rerun `audit-research` to collect line numbers and call ordinals for the already identified native vehicle/firearm blocks.
3. Rerun the expanded preset audit to separate true structural differences from generic/repeated semantic value changes.
4. Rerun the 13-option disposable candidate audit and require `skip_intro_videos` plus the combined candidate to pass.
5. Use that evidence to finish firearm semantic mapping and choose the two intended noclip blocks per native file.
6. Convert only fully explained preset deltas to minimal semantic transforms and implement the remaining Milestone-1 definitions.
7. Repeat disposable candidate rebuild/validation for every newly completed option before any live write.
8. Review and then test pristine backup/restore and atomic replacement on the QA installation.
9. Reproduce all Milestone-1 gameplay options.
10. Add the Linux-native GUI.
11. Package only after functional validation.

## Publication state

No main integration, release, public binary, Nexus publication, upstream submission, or other external publication has been authorized. `linux-port` remains the active development branch.
