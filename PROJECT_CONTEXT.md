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

A native Linux Steam installation has already been checked with these results:

- `DeadIslandRiptideGame` is a native Linux ELF executable.
- `<DIRDE_ROOT>/DIR/Data0.pak` is ZIP-compatible.
- Archive entry count: 3060.
- Archive size: 7,932,941 bytes.
- SHA-256: `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

Representative patch targets were present, including `default_levels.xml`, `inventory_gen.scr`, intro movies, weather, and glow scripts.

Result: `NATIVE_DATA0_COMPATIBILITY_BASELINE_PASS`.

This is compatibility evidence, not complete feature-parity evidence. The hash is a known baseline, not a permanent requirement.

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

- FOV 72/82 recoil changes cover the shotgun families plus selected pistols.
- Better firearms POV covers Fury firearms, shotguns, pistols/revolvers, automatic/burst/single rifles, with FOV-specific offsets, aim FOV, blur and sway values.
- Better firearms upgrading covers pistol upgrade tiers, automatic/burst/single rifle tiers, and shotgun tiers. Active changes use `ShotTime`, `ReloadTime`, `ShootVertRecoil`, and for automatic rifle families `ShootMaxAngle`. Several apparent `ShotTime`/spread edits in the AHK are commented out and are not part of released behavior.

The remaining firearm problem is not the desired values; it is mapping those old line-based edits to stable native block/tier identities. Linux will not use the historical line numbers as patch targets.

The reverb replacement pair has been reduced to a semantic transform that comments/uncomments `ReverbPreset` and `ReverbWetDryMix` declarations and calls. Nearby `Echo(...)` uses inspected in the default file were already commented and are left alone.

Vehicle noclip is represented semantically as exactly two `Ignore(0)` calls in the car file and two in the old-boat file becoming `Ignore(1)`. The upstream truck edits are commented out and excluded.

Deeper Pockets is represented semantically in all five character skill files by the `DeeperPockets` skill identity: `desc_params` changes from `2;4;6` to `6;12;18` and its `InventorySize` effect changes from `2` to `6`.

Improved Loot's six default/enabled weight sets are known from the AHK, but the native loot block identities must still be verified before implementation.

Preset-backed options still need native delta evidence:

- AI difficulty;
- zombie size;
- forced spawn;
- weather/time.

## Implemented Linux core

The Python core under `src/dirue/` contains no newly added proprietary game content and currently provides:

- native Linux game-root validation using the ELF executable;
- ZIP validation with CRC, required-entry, traversal, backslash-path and duplicate-member checks;
- safe temporary extraction and rebuild;
- pristine backup creation without silent overwrite;
- validated atomic candidate installation and restore;
- semantic XML, `VarFloat`, call-value, Deeper Pockets, and reverb transforms;
- declarative direct definitions for 11 source-derived options;
- deterministic JSON CLI validation;
- `audit-native`, a read-only native parity audit;
- `audit-presets`, a read-only comparison of the released preset ZIPs against native `Data0.pak`.

`audit-native` reports selected prior values, sunflare, all five Deeper Pockets states, noclip counts, reverb counts, short intro identifiers, loot summaries, and firearm block research hints. Historical AHK line numbers are used only to help discover native firearm block identities; they are never patch targets.

`audit-presets` validates the preset ZIPs, compares their members in memory against native targets, and reports only metadata, hashes, status, and short semantic key/value changes where they can be identified. It does not extract or install preset content and never uses the inherited repository `Data0.pak`.

## Validation evidence

Validation evidence is kept specific to the code state it tested:

- the original scaffold's 12-test suite passed before later feature additions;
- reverb, direct-definition and noclip changes each passed focused synthetic tests when introduced;
- the Deeper Pockets work passed a 22-test focused suite plus Python compilation and corrected whitespace/privacy checks;
- `audit-native` passed 9 focused synthetic tests, including a synthetic `Data0.pak` test proving the audit leaves archive bytes unchanged;
- `audit-presets` passed 5 focused synthetic tests, including checks that native and preset archive bytes stay unchanged;
- Python compilation passed for both audit work units;
- both audit submissions passed privacy scanning and whitespace checks;
- packaging previously produced a wheel successfully without network dependencies.

No GitHub Actions were used.

The current code has **not yet been run against or used to modify the installed Steam game**. Native execution remains a separate gate.

GitHub Issues are currently disabled for this repository. An attempt to create a focused firearm-mapping Issue returned HTTP 410, so unresolved work remains tracked here rather than changing repository settings.

## Current gates

1. Run `audit-native` and `audit-presets` read-only against the physical native installation/local repository.
2. Use that evidence to replace remaining firearm line references with stable block/tier identities.
3. Map Improved Loot and intro statements semantically from the same native evidence.
4. Confirm direct-option prior values and exact reverb call counts.
5. Convert preset deltas to minimal semantic transforms where possible and keep provenance-sensitive content out of Git.
6. Implement and test the remaining Milestone-1 definitions.
7. Run a candidate rebuild/validation against a disposable archive copy before any live write.
8. Review and then test pristine backup/restore and atomic replacement on the QA installation.
9. Reproduce all Milestone-1 gameplay options.
10. Add the Linux-native GUI.
11. Package only after functional validation.

## Publication state

No main integration, release, public binary, Nexus publication, upstream submission, or other external publication has been authorized. `linux-port` remains the active development branch.
