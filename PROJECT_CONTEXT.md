# PROJECT_CONTEXT.md

## Repository

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Default branch: `main`
- Active Linux-port branch: `linux-port`
- License: GNU GPLv3 (inherited and preserved)

## Current milestone

**Milestone 1: native Linux feature-parity port of the existing DIRUE release.**

Scope is compatibility and faithful behavior. New gameplay tweaks are deferred until parity is complete and validated.

## Verified native Linux compatibility baseline

A native Linux Steam installation of Dead Island: Riptide Definitive Edition has been validated with these results:

- `DeadIslandRiptideGame` is a native Linux ELF executable.
- `DeadIslandRiptideGame.exe` is absent.
- `<DIRDE_ROOT>/DIR/Data0.pak` exists and is ZIP-compatible.
- Archive entry count: 3060.
- Installed native Linux `Data0.pak` size: 7,932,941 bytes.
- Installed native Linux `Data0.pak` SHA-256: `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

Representative upstream patch targets verified present in that native archive:

- `data/skills/default_levels.xml`
  - `CameraDefaultFOV`
  - `MoveSprintStaminaConsumption`
- `data/inventory_gen.scr`
  - `ShootVertRecoil`
- `data/menu/movies/intromovies.scr`
- `data/scripts/weather/weather.scr`
  - `f_game_time`
- `data/scripts/varlist_glow.scd`
  - `f_pp_glow_factor`
- `data/scripts/varlist_glow.scr`
  - `f_glow_factor`

Baseline result: `NATIVE_DATA0_COMPATIBILITY_BASELINE_PASS`.

This is evidence for compatibility of core Data0 transformations, not yet proof of complete feature parity.

## Important upstream archive difference

The inherited upstream repository contains `Data0.pak` with size 7,647,523 bytes. It differs from the validated native Linux Steam archive above.

The Linux port must not install or patch from that inherited archive. Runtime patching must begin from a validated installed archive or a verified pristine backup derived from it and use temporary working storage, validation, and atomic replacement.

## Upstream implementation observations

`DIRUE.ahk` is the behavioral specification for Milestone 1. The original implementation combines GUI behavior, file extraction, hard-coded line edits, preset merges, archive rebuilding, and Windows helper processes.

Confirmed hazards that must not be copied into the Linux implementation:

- upstream extracts its bundled repository `Data0.pak` rather than the user's installed archive;
- finalization deletes the live `Data0.pak` before the candidate has been safely validated/replaced;
- many edits use fixed line numbers tied to the bundled archive;
- some option-disable paths depend on placeholder/default content already present in the bundled archive;
- several options replace complete files/directories from bundled presets with unresolved redistribution provenance.

Windows-only implementation details to replace include:

- AutoHotkey GUI/runtime
- `.exe`-based helper processes
- Windows executable/DLL path validation
- AHK ZIP/text helper libraries
- optional menu sound/music helper behavior where it has no gameplay effect

## Feature inventory status

`docs/FEATURE_PARITY.md` is the authoritative Milestone-1 control inventory.

The released top-level user-facing control inventory is now complete. It includes application controls, all active gameplay checkboxes/dropdowns, FOV behavior, automatic upstream mutations, and commented/inactive controls.

Direct-value mappings have been extracted for FOV, intros, sprint/jump stamina, sunflare, run-with-weapons, improved loot, movement, deeper pockets, vehicle noclip, ammo capacity, break-door effectiveness, durability, and bullet penetration.

Complex remaining mapping work is concentrated in:

- per-weapon/per-FOV `Better firearms POV` transforms;
- per-weapon/per-upgrade `Better firearms upgrading` transforms;
- reverb replacement-file diff;
- AI difficulty ZIPs;
- zombie-size ZIPs;
- forced-spawn ZIPs;
- weather/time ZIPs.

Important upstream quirks recorded for parity decisions:

- movement enable compares checkbox value to `1s` instead of `1`;
- instant-door disable checks the durability checkbox variable;
- durability tooltip describes `1.0 -> 0.5`, while the handler writes `-9.0` to four durability-loss properties;
- the NoClip vehicle handler names trucks but released edits affect car/old-boat physics while truck edits are commented;
- FOV label `62 default` writes `62.5`.

The Linux port will preserve implemented gameplay values where feasible while correcting GUI/control-flow bugs and replacing brittle line-number mechanics with validated semantic transforms.

## Planned Linux architecture

Expected implementation direction:

- Python
- PySide6 GUI
- standard-library ZIP/file processing where sufficient
- deterministic patch engine independent of GUI
- declarative patch definitions with semantic match validation
- verified pristine-base model for repeatable option toggling
- backup/restore and transactional archive replacement
- CLI/test surface for local deterministic validation
- AppImage or other packaging only after parity validation

## Current gates

1. Expand the two large firearm transforms into semantic patch definitions.
2. Audit/diff bundled replacement files and ZIP presets and classify redistribution provenance.
3. Verify every resulting target/default state against the native Linux `Data0.pak` without committing extracted game content.
4. Implement native game discovery and archive validation.
5. Implement deterministic semantic patch primitives and tests.
6. Implement pristine backup/restore and atomic replacement.
7. Reproduce all Milestone-1 gameplay options.
8. Add the Linux-native GUI.
9. Validate against the native Steam installation.
10. Package only after functional validation.

## Publication state

No release, Nexus publication, upstream submission, or other external publication has been authorized. The public fork is the development repository; `linux-port` is the active porting branch.
