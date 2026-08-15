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

## Read-only native parity audit

A physical-machine read-only audit completed successfully on 2026-08-15. The repository's then-current 44-test suite passed first. Native game validation, the parity audit, and preset comparison all completed, and `Data0.pak` kept the exact same SHA-256 before and after the run.

The audit verified these native prior states:

- all direct `default_levels.xml` values used by sprint/jump stamina, running with weapons, movement, ammo, door breaking, durability, bullet penetration, and default FOV;
- both sunflare variables at `1.0`;
- all five Deeper Pockets skill files at `desc_params="2;4;6"` and `InventorySize change="2"`;
- the six Improved Loot target blocks and their default color weights;
- one active `File("Intro_720p")` intro statement while the inspected DI intro/subtitle statements are already commented;
- one active reverb declaration for each reverb directive plus 52 active `ReverbPreset` calls and 52 active `ReverbWetDryMix` calls.

The same audit exposed a vehicle noclip mismatch that must not be guessed through: the native car file contains four active `Ignore(0)` calls plus one `Ignore(1)`, and the old-boat file contains five active `Ignore(0)` calls. The released AHK edits only two calls in each file. Noclip is therefore excluded from the ready definition catalog until those two calls have stable block identities.

The first firearm research pass also proved that nearest-line matching is not reliable enough for native mapping. Some old AHK line hints drift into neighboring native weapon blocks. Historical line numbers remain research hints only and are never patch targets.

Raw local audit output and machine-specific paths are not committed to Git.

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

## Feature inventory status

`docs/FEATURE_PARITY.md` is the authoritative released-control inventory.

The top-level released controls are inventoried. Direct source values are known for FOV, sprint/jump stamina, sunflare, run-with-weapons, improved loot, movement, deeper pockets, vehicle noclip, ammo, break doors, durability, and bullet penetration.

Source audit has also established the intended family/tier values for the large firearm features:

- FOV 72/82 recoil changes cover the shotgun families plus selected pistols;
- Better firearms POV covers Fury firearms, shotguns, pistols/revolvers, automatic/burst/single rifles, with FOV-specific offsets, aim FOV, blur and sway values;
- Better firearms upgrading covers pistol upgrade tiers, automatic/burst/single rifle tiers, and shotgun tiers. Active changes use `ShotTime`, `ReloadTime`, `ShootVertRecoil`, and for automatic rifle families `ShootMaxAngle`. Several apparent edits in the AHK are commented out and are not part of released behavior.

The remaining firearm problem is mapping source behavior to stable native item/tier identities. A block-aware `audit-research` command now groups relevant calls by actual native `Item:` and nested block identities instead of treating nearby historical line numbers as evidence.

Reverb removal is now a concrete semantic definition using the verified native 52/52 call counts. It comments/uncomments only `ReverbPreset` and `ReverbWetDryMix`; nearby `Echo(...)` uses inspected in the default file are already commented and remain unchanged.

Deeper Pockets is represented semantically in all five character skill files by the `DeeperPockets` skill identity: `desc_params` changes from `2;4;6` to `6;12;18` and its `InventorySize` effect changes from `2` to `6`.

Improved Loot is now a concrete semantic definition scoped to the six verified `DefColorSet` blocks. It does not change the unrelated Suicider or Corrupter sets.

Skip Intro Videos is now a concrete semantic definition that comments the verified active `File("Intro_720p")` statement rather than replacing the full intro script.

Vehicle noclip remains unresolved as described above and is intentionally not exposed in the ready direct catalog.

## Preset-backed options

The first native preset comparison established this high-level delta surface:

- normal AI preset matches native for the compared files;
- one-hit AI differs in two files and reports `one_shot` changing from `0` to `1`;
- hard AI differs in 57 compared files;
- headshot-only AI differs in 20 compared files;
- default forced-spawn preset matches native, while each forced variant changes `aispawnbox_pre.def`;
- weather/time presets change a small group of logic/weather/ambient files depending on the selected variant;
- zombie-size presets change four target files, with the `.pre` files showing forced body-scale values while the paired definition-file changes still need classification.

The preset audit now also reports whether recognized semantic values explain the complete text difference for each member. This must be rerun on the physical machine before large preset-backed transforms are considered fully reconstructed.

## Implemented Linux core

The Python core under `src/dirue/` contains no newly added proprietary game content and currently provides:

- native Linux game-root validation using the ELF executable;
- ZIP validation with CRC, required-entry, traversal, backslash-path and duplicate-member checks;
- safe temporary extraction and rebuild;
- pristine backup creation without silent overwrite;
- validated atomic candidate installation and restore;
- semantic XML, `VarFloat`, simple call, named call, scoped loot, Deeper Pockets, intro-comment and reverb transforms;
- a ready direct catalog of 13 native-verified text options, with unresolved noclip excluded;
- deterministic JSON CLI validation;
- `audit-native`, a read-only native parity audit;
- `audit-presets`, a read-only preset comparison with semantic completeness classification;
- `audit-research`, a read-only block-aware firearm/noclip research audit.

No audit command extracts, installs, or modifies game content.

## Validation evidence

Validation evidence is kept specific to the code state it tested:

- the physical read-only audit ran the then-current full 44-test suite successfully before accessing the native game;
- that physical audit proved `Data0.pak` remained byte-for-byte unchanged by hash;
- earlier feature work passed its focused synthetic suites when introduced;
- the newly added intro, loot, reverb-count, block-aware research, and semantic-completeness logic passed 14 focused local tests plus Python compilation in isolated temporary storage;
- the current remote branch still needs a full-suite run after these latest additions;
- packaging previously produced a wheel successfully without network dependencies.

No GitHub Actions were used.

The installed Steam game has still **not been modified by the Linux port**. Native mutation remains a later, separate gate.

GitHub Issues are currently disabled for this repository. An attempt to create a focused firearm-mapping Issue returned HTTP 410, so unresolved work remains tracked here rather than changing repository settings.

## Current gates

1. Rerun the updated read-only preset audit to obtain `semantic_complete` results.
2. Run `audit-research` once against the physical native installation to capture stable firearm and vehicle block identities.
3. Use that evidence to finish firearm mapping and identify the two intended noclip calls per native file.
4. Convert only fully explained preset deltas to minimal semantic transforms and keep provenance-sensitive full replacements out of Git.
5. Implement and test the remaining Milestone-1 definitions.
6. Run the full repository test suite and compilation on the physical checkout after the new audit work.
7. Run a candidate rebuild/validation against a disposable archive copy before any live write.
8. Review and then test pristine backup/restore and atomic replacement on the QA installation.
9. Reproduce all Milestone-1 gameplay options.
10. Add the Linux-native GUI.
11. Package only after functional validation.

## Publication state

No main integration, release, public binary, Nexus publication, upstream submission, or other external publication has been authorized. `linux-port` remains the active development branch.
