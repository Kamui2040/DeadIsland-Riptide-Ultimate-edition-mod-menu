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

The Linux port must not install or patch from that inherited archive. Runtime patching must begin from the user's validated installed archive and use backup, temporary working storage, validation, and atomic replacement.

## Upstream implementation observations

`DIRUE.ahk` is the behavioral specification for Milestone 1. The original implementation combines GUI behavior, file extraction, hard-coded line edits, preset merges, archive rebuilding, and Windows helper processes.

Windows-only implementation details to replace include:

- AutoHotkey GUI/runtime
- `.exe`-based helper processes
- Windows executable/path validation
- AHK ZIP/text helper libraries
- optional menu sound/music helper process behavior where it has no gameplay effect

## User-facing feature inventory status

Initial active controls identified from the AHK GUI:

- FOV: 62/default, 72, 82
- Skip intro videos
- Reduce sunflare by 90%
- Reduce sprint stamina cost
- Reduce jump stamina cost
- Enable running with weapons
- Improved loot
- Better movement tweaks
- Better firearms POV
- Better firearms upgrading
- Remove reverb/echo sound
- Even Deeper Pockets
- NoClip vehicles
- Hold more ammo
- Instantly break doors
- Increase weapon durability
- Bullet penetration for enemies
- Zombie size presets
- Weather/time presets
- Zombie difficulty presets
- Forced zombie/bandit spawn presets

Commented/inactive controls observed in upstream source include high-FOV recoil fix, custom weapons, and a Night-time Paradise checkbox. Their underlying handlers/assets must still be reviewed before deciding whether they are part of the released behavioral surface.

The complete option-to-target/default/modified/preset mapping is **not yet complete** and remains the next inventory task.

## Planned Linux architecture

Expected implementation direction:

- Python
- PySide6 GUI
- standard-library ZIP/file processing where sufficient
- deterministic patch engine independent of GUI
- declarative patch definitions with semantic match validation
- backup/restore and transactional archive replacement
- CLI/test surface for local deterministic validation
- AppImage or other packaging only after parity validation

## Current gates

1. Complete the authoritative inventory of every released user-facing AHK option and handler.
2. Map each option to target archive paths, expected default values/content, modified values/content, and bundled preset/replacement dependencies.
3. Audit bundled upstream files for provenance/redistribution suitability before reusing any of them.
4. Verify every required target against the native Linux `Data0.pak` without committing extracted game content.
5. Implement game discovery and archive validation.
6. Implement deterministic semantic patch primitives and tests.
7. Implement backup/restore and atomic replacement.
8. Reproduce all Milestone 1 gameplay options.
9. Add the Linux-native GUI.
10. Validate against the native Steam installation.
11. Package only after functional validation.

## Publication state

No release, Nexus publication, upstream submission, or other external publication has been authorized. The fork is a development repository; `linux-port` is the active porting branch.
