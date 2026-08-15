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

The released top-level user-facing control inventory is complete. Direct-value mappings are documented for FOV, intros, sprint/jump stamina, sunflare, run-with-weapons, improved loot, movement, deeper pockets, vehicle noclip, ammo capacity, break-door effectiveness, durability, and bullet penetration.

Complex remaining mapping work is concentrated in:

- per-weapon/per-FOV `Better firearms POV` transforms;
- per-weapon/per-upgrade `Better firearms upgrading` transforms;
- native installed-file verification for the reverb transform, including exact call counts;
- AI difficulty ZIPs;
- zombie-size ZIPs;
- forced-spawn ZIPs;
- weather/time ZIPs.

The upstream reverb replacement pair has now been audited far enough to replace the full-file copy approach with a semantic transform. The modded form comments the `ReverbPreset` and `ReverbWetDryMix` declarations and uses. The nearby `Echo(...)` uses inspected in the default form are already commented, so the Linux transform leaves them unchanged. Exact counts still need validation against the installed native archive before this option is wired into a concrete patch definition.

Important upstream quirks recorded for parity decisions:

- movement enable compares checkbox value to `1s` instead of `1`;
- instant-door disable checks the durability checkbox variable;
- durability tooltip describes `1.0 -> 0.5`, while the handler writes `-9.0` to four durability-loss properties;
- the NoClip vehicle handler names trucks but released edits affect car/old-boat physics while truck edits are commented;
- FOV label `62 default` writes `62.5`.

The Linux port will preserve implemented gameplay values where feasible while correcting GUI/control-flow bugs and replacing brittle line-number mechanics with validated semantic transforms.

## Implemented Linux core

The Python core scaffold is implemented under `src/dirue/` with no proprietary game content:

- native Linux game-root validation using the ELF executable and required Data0 entries;
- ZIP-compatible Data0 validation with CRC, required-entry, traversal, backslash-path, and duplicate-member checks;
- safe temporary extraction;
- archive rebuilding from a working tree while preserving source member order/metadata where practical;
- strict semantic regex patch primitives for XML properties and `VarFloat` values;
- semantic reverb enable/disable handling with exact expected call counts, mixed-state rejection, and newline preservation;
- declarative direct patch definitions for nine source-derived options, applied to an in-memory member map without mutating the input;
- one-time pristine backup creation that will not overwrite an existing backup;
- validated atomic candidate installation;
- validated atomic restore;
- deterministic JSON CLI commands for game/archive validation.

Validation evidence currently recorded:

- the original core scaffold's 12-test standard-library `unittest` suite passed before the reverb change;
- the current `tests/test_patches.py` module passes all 8 tests, including four reverb-specific cases;
- six focused direct-definition tests pass, including missing-member and wrong-prior-state rejection;
- Python compilation passes for the changed patch/definition modules and focused tests;
- `pyproject.toml` previously parsed with SPDX license `GPL-3.0-only`;
- a wheel previously built successfully with setuptools without network dependencies.

The reverb tests verify comment-only transformation, round-trip restoration with CRLF preservation, exact-count failure, and rejection of mixed source state. The direct definitions are source-derived and still require native prior-state verification before live-game use.

This core has **not yet been run against or used to modify the installed Steam game**. Native-install QA remains a separate gate.

## Planned Linux architecture

- Python core and CLI
- PySide6 GUI after patch-engine parity is sufficiently established
- standard-library ZIP/file processing where sufficient
- deterministic patch engine independent of GUI
- declarative patch definitions with semantic match validation
- verified pristine-base model for repeatable option toggling
- backup/restore and transactional archive replacement
- local deterministic tests
- AppImage or other packaging only after parity validation

## Current gates

1. Expand the two large firearm transforms into semantic patch definitions.
2. Audit/diff the remaining bundled replacement files and ZIP presets and classify redistribution provenance.
3. Verify every resulting target/default state, including reverb call counts and direct-definition prior values, against the native Linux `Data0.pak` without committing extracted game content.
4. Add the remaining Milestone-1 patch definitions on top of the validated semantic primitives.
5. Exercise read-only game/archive validation against the native Steam installation.
6. Exercise candidate rebuild/validation against a disposable copy before any live-game write.
7. Validate pristine backup/restore and atomic replacement against the QA installation only after the transaction path is reviewed.
8. Reproduce all Milestone-1 gameplay options.
9. Add the Linux-native GUI.
10. Package only after functional validation.

## Publication state

No release, Nexus publication, upstream submission, or other external publication has been authorized. The public fork is the development repository; `linux-port` is the active porting branch.
