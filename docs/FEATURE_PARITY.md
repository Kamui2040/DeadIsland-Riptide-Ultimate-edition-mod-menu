# Milestone 1 feature-parity inventory

This document inventories the released DIRUE v1.2 user-facing controls and the behavior implemented by `DIRUE.ahk`. It is the migration checklist for the native Linux port.

Status terminology:

- **Direct transform**: the AHK writes identifiable values/text into files.
- **Preset replacement**: the AHK deletes target content and expands a bundled ZIP/replacement file. The Linux port must reconstruct or otherwise clear redistribution/provenance before reuse.
- **Application-only**: GUI/helper behavior with no gameplay archive change.
- **Inactive upstream**: code/handler exists but its GUI control is commented out in the released source.

The upstream script uses hard-coded line numbers extensively. Line numbers below are evidence only; the Linux implementation should target semantic identities and validate expected old values/content.

## Released application controls

| Control | Upstream behavior | Linux-port direction |
|---|---|---|
| Select folder | Requires `DeadIslandRiptideGame.exe`, `DIR`, `engine_x64_rwdi.dll`, then `DIR/Data0.pak`. | Replace with native-Linux validation: ELF `DeadIslandRiptideGame`, expected `DIR` layout, ZIP-compatible `Data0.pak`, compatibility checks. |
| Enable music? | Starts/stops bundled `background_music_riptide.exe`; checked by default. No Data0 effect. | Windows helper must not be carried over. Gameplay parity does not depend on it; optional native UI audio can be reconsidered later. |
| Confirm modifications | Deletes live `Data0.pak`, builds ZIP from working tree, then copies candidate into game directory. | Replace with validated candidate build, recoverable pristine backup, fsync/rename-style atomic replacement, and failure rollback. |

## Automatic upstream mutations (not explicit checkboxes)

After unpacking its bundled `Data0.pak`, upstream unconditionally replaces:

- `data/game.ini` from `Required_files_and_scripts/game.ini`
- `data/menu/scr/menumain_pc.xui` from `Required_files_and_scripts/menumain_pc.xui_version`

These files require provenance/content review before any Linux-port equivalent is implemented. They must not be assumed necessary for gameplay parity merely because upstream applied them automatically.

## Released gameplay controls

### FOV

**GUI choices:** `62 default`, `72`, `82`.

**Targets:**

- `data/skills/default_levels.xml`
- `data/inventory_gen.scr` for additional high-FOV recoil scaling at 72/82

**Core property:** `CameraDefaultFOV`

- default: `62.5`
- 72 option: `72`
- 82 option: `82`

At 72 and 82 the AHK also writes many weapon-specific `ShootVertRecoil` values in `inventory_gen.scr`, especially shotguns and pistols. These must be reconstructed semantically by weapon/block identity rather than source line number.

### Skip intro videos

**Target:** `data/menu/movies/intromovies.scr`

**Enabled:** comments out upstream lines 15-25 with `//`.

**Disabled/default:** removes that prefix from the same statements.

Linux transform: identify the intro movie statements as a block and toggle their comment state with exact-count validation.

### Reduce sprinting stamina cost

**Target:** `data/skills/default_levels.xml`

**Property:** `MoveSprintStaminaConsumption`

- default: `0.05`
- enabled: `0.03`

### Reduce jump stamina cost

**Target:** `data/skills/default_levels.xml`

**Property:** `JumpStaminaCost`

- default: `0.06`
- enabled: `0.03`

### Reduce sunflare by 90%

**Targets:**

- `data/scripts/varlist_glow.scd`: `f_pp_glow_factor`
- `data/scripts/varlist_glow.scr`: `f_glow_factor`

- default: `1.0` in both
- enabled: `0.1` in both

### Enable running with weapons

**Target:** `data/skills/default_levels.xml`

**Property:** `HideWeaponsDuringSprint`

- default: `1.0`
- enabled: `0.0`

### Improved Loot

**Target:** `data/default.loot`

Upstream changes color-weight distributions for default chests, three lockpick tiers, Rams, and `MeleeFighter` drops.

| Loot group | Default White/Green/Blue/Violet/Orange | Improved White/Green/Blue/Violet/Orange |
|---|---|---|
| Default chest | 91 / 7 / 2 / 0 / 0 | 55 / 32 / 8 / 3 / 2 |
| Lockpick 1 | 0 / 92 / 6 / 1 / 0 | 0 / 77 / 10 / 8 / 5 |
| Lockpick 2 | 0 / 85 / 11 / 3 / 1 | 0 / 55 / 16 / 15 / 14 |
| Lockpick 3 | 0 / 72 / 21 / 5 / 2 | 0 / 37 / 33 / 14 / 16 |
| Ram | 0 / 10 / 67 / 20 / 3 | 0 / 5 / 30 / 50 / 15 |
| MeleeFighter | 0 / 65 / 35 / 0 / 0 | 0 / 6 / 31 / 52 / 11 |

The GUI describes the last category as Butchers; the implementation targets the `MeleeFighter` loot group. Preserve the implemented data behavior unless later validation proves a different semantic identity.

### Better movement tweaks

**Target:** `data/skills/default_levels.xml`

| Property | Default | Intended enabled value |
|---|---:|---:|
| `MoveForwardMaxSpeed` | 3.5 | 3.70 |
| `MoveBackwardMaxSpeed` | 2.5 | 2.70 |
| `MoveStrafeMaxSpeed` | 2.5 | 3.70 |
| `MoveAcceleration` | 7.0 | 12.00 |
| `MoveDeceleration` | 10.0 | 12.00 |

Upstream quirk: the enable dispatcher compares the checkbox value to `1s` rather than `1`, while the disable branch checks `0`. The Linux port should implement the explicit intended values above and record this as an upstream GUI bug, not reproduce the broken comparison.

### Better firearms POV

**Targets:**

- `data/inventory_gen.scr`
- `data/inventory_special.scr`

The handler is FOV-dependent (62/72/82) and modifies many firearm blocks. Changed fields include:

- `AimBlurStart`
- `HolderOffset`
- `HandOffset`
- `HandRot`
- `AimFov`
- `SwayMaxAngle`

Weapon families include Fury firearms, shotguns, pistols/revolvers, automatic/burst/single-shot rifles, and legendary firearms. Values vary by weapon family and selected FOV.

**Port status:** authoritative top-level target identified; individual weapon/block transforms still require extraction into declarative semantic patch definitions. Do not port the AHK line numbers directly.

### Better firearms upgrading

**Target:** `data/inventory_gen.scr`

The enabled branch writes upgrade-tier-specific values across firearm families. Changed fields include:

- `ShotTime`
- `ReloadTime`
- `ShootVertRecoil`
- `ShootMaxAngle`

Representative implemented progression includes faster reload/fire timing and lower recoil/spread at higher upgrade tiers. The disable branch often writes placeholder marker lines rather than restoring a clean vanilla statement, demonstrating that the AHK depends on its bundled/prearranged archive state.

**Port status:** reconstruct semantic per-weapon/per-upgrade transforms against the native pristine archive. A fresh/pristine base makes the AHK's placeholder-based disable behavior unnecessary.

### Remove reverb/echo sound

**Target:** `data/gameaudioeffects.scr`

**Upstream implementation:** full-file replacement:

- enabled: `Required_files_and_scripts/gameaudioeffects.scr.modded`
- disabled/default: `Required_files_and_scripts/gameaudioeffects.scr.nomod`

**Port status:** diff/audit the two text files and express the smallest semantic transformation possible. Do not redistribute a game-derived full replacement without confirmed rights.

### Even Deeper Pockets

**Targets:**

- `data/skills/logan_skills.xml`
- `data/skills/purna_skills.xml`
- `data/skills/samb_skills.xml`
- `data/skills/xian_skills.xml`
- `data/skills/john_skills.xml`

For each character's `DeeperPockets` skill:

- default `desc_params`: `2;4;6`
- enabled `desc_params`: `6;12;18`
- default `InventorySize` change: `2`
- enabled `InventorySize` change: `6`

This preserves the upstream three-level progression, increasing the total bonus from 6 to 18 slots.

### NoClip vehicles

**Targets actually modified:**

- `data/odephysics/vehicle/cardi.phx`
- `data/odephysics/vehicle/old_boat_a.phx`

Two `Ignore(...)` entries in each file:

- default: `Ignore(0)`
- enabled: `Ignore(1)`

`truckdi.phx` edits exist in the handler but are commented out. The GUI/handler naming says trucks/vehicles, but released code modifies the car and old boat only. Port the implemented targets first and keep the mismatch documented.

### Hold more ammo

**Target:** `data/skills/default_levels.xml`

| Property | Default | Enabled |
|---|---:|---:|
| `MaxAmmoPistol` | 50 | 200 |
| `MaxAmmoRifle` | 60 | 150 |
| `MaxAmmoShotgun` | 20 | 90 |

There is additional `MaxAmmoSniper` interaction inside the inactive custom-weapons handler; it is not part of this released checkbox by itself.

### Instantly break doors

**Target:** `data/skills/default_levels.xml`

**Property:** `BreakDoorEffectivens` (spelling as used by the game data/upstream script)

- default: `0`
- enabled: `99`

Upstream quirk: the unchecked dispatcher tests `better_durability_var` instead of `Instant_breakdoor_var`. Linux should implement the checkbox's intended enable/disable semantics rather than the GUI bug.

### Increase weapon durability

**Target:** `data/skills/default_levels.xml`

| Property | Default | Enabled by actual handler |
|---|---:|---:|
| `BluntWpnDurabilityLoss` | 1.0 | -9.0 |
| `CutWpnDurabilityLoss` | 1.0 | -9.0 |
| `RangedWpnDurabilityLoss` | 0.1 | -9.0 |
| `BulletWpnDurabilityLoss` | 0.1 | -9.0 |

Important mismatch: the GUI tooltip says durability loss changes from `1.0` to `0.5`, but the released handler actually writes `-9.0`. For feature parity, treat the implemented value as the current behavioral specification until native-game QA establishes whether this is intentional or erroneous.

### Bullet penetration for enemies

**Target:** `data/skills/default_levels.xml`

**Property:** `BulletPenetrationChance`

- default: numeric zero (AHK writes `0.`)
- enabled: `0.98`

### Zombie difficulty

**Upstream implementation:** deletes the entire working `data/ai` directory and expands one preset ZIP into `data`.

| GUI choice | Bundled preset |
|---|---|
| Normal zombies | `ai_norm.zip` |
| One hit kill zombies | `ai_Onehit.zip` |
| hard zombies | `ai_hard.zip` |
| Headshot only zombies | `ai_Headshot.zip` |

The one-hit handler contains a commented semantic clue for `data/ai/zombie/vessel_data.scr`: `ParamBool("one_shot", 1)` with default `0`, but the released behavior uses the preset archive.

**Port status:** enumerate preset ZIP contents and diff each against the validated native archive. Convert to semantic/minimal transforms where possible; do not redistribute copied game AI files without rights.

### Zombie size

**Targets replaced:**

- `data/presets/infectedai.pre`
- `data/presets/infectedai_pre.def`
- `data/presets/zombieai.pre`
- `data/presets/zombieai_pre.def`

| GUI choice | Bundled preset |
|---|---|
| Extra small | `PRESETS_XTRASMOL_ZOMSIZE.zip` |
| small "Midget" zombies | `PRESETS_MIDGET_ZOMSIZE.zip` |
| normal size zombies | `PRESETS_NORM_ZOMSIZE.zip` |
| large zombies | `PRESETS_LARGE_ZOMSIZE.zip` |
| Supersize zombies | `PRESETS_SUPASIZE_ZOMSIZE.zip` |

**Port status:** inspect/diff preset contents and convert to semantic/minimal transforms where practical.

### Forced spawn override

**Target replaced:** `data/presets/aispawnbox_pre.def`

| GUI choice | Bundled preset |
|---|---|
| Normal spawns | `Default_spawns.zip` |
| Butchers | `force_butcher_spawn.zip` |
| Rams | `Force_ram_spawn.zip` |
| Bloaters | `Force_bloater_spawn.zip` |
| Thugs | `Force_thug_spawn.zip` |
| Suiciders | `Force_suicide_spawn.zip` |
| bandits w/guns | `Force_bandits_spawn_with_guns.zip` |
| bandits w/melee | `Force_bandits_spawn_with_no_guns.zip` |

**Port status:** inspect/diff the one replaced preset file for each choice and express the delta without bundling copied game content where possible.

### Weather/time override

The released dropdown provides:

- Default (vanilla)
- just night
- Rain (day)
- Rain (night)
- Storm (day)
- Storm (night)
- Just night (Darker)
- Rain (Darker night)
- Storm (Darker night)

Before applying a weather preset, upstream deletes these working files:

- `data/scripts/weather/weather.scr`
- `data/scripts/varlist_ambient.scd`
- `data/scripts/varlist_ambient.scr`
- `data/scripts/logic_script.scr`

It then expands one corresponding ZIP into `data`:

| GUI choice | Bundled preset |
|---|---|
| Default (vanilla) | `Time-weather_vanilla.zip` |
| just night | `time-weather_Just_night.zip` |
| Rain (day) | `time-weather_Rain_day.zip` |
| Rain (night) | `time-weather_Rain_night.zip` |
| Storm (day) | `time-weather_storm_day.zip` |
| Storm (night) | `time-weather_storm_night.zip` |
| Just night (Darker) | `time-weather_Just_night_darker.zip` |
| Rain (Darker night) | `time-weather_Rain_night_darker.zip` |
| Storm (Darker night) | `time-weather_storm_night_darker.zip` |

**Port status:** inspect and diff the four-file preset variants, then represent their behavior with minimal project-authored transformations if feasible.

## Inactive/commented upstream controls

These controls are present in source but commented out in the released GUI and therefore are not currently counted as released Milestone-1 UI features:

### High-FOV recoil fix

A `Recoil_hfov_fix` checkbox is commented out. Recoil adjustments are already coupled to the active FOV 72/82 handlers. Audit the remaining handler before deleting or consolidating it.

### Custom weapons

The `custom_wep_var` checkbox is commented out. Its handler contains extensive M60/M72, explosive-ammo, crafting/shop, `inventory_patch.scr`, `inventory_special.scr`, and DLC shop changes, plus interaction with `MaxAmmoSniper`.

This is not a released active control and should not silently enter Milestone 1. Preserve source history and defer any reactivation until after parity.

### Night-time Paradise checkbox

The standalone `NightTime_var` checkbox is commented out, although its handler remains. The handler changes:

- `data/scripts/weather/weather.scr` (`f_game_time`-related statements)
- `data/scripts/varlist_ambient.scr` (`f_engine_envprobe_factor`)

The active weather dropdown already exposes multiple night presets. Keep the inactive handler documented, but do not add a duplicate Linux GUI option during initial parity.

## Upstream implementation hazards to remove in the port

1. **Bundled archive as base:** upstream `FileInstall`s repository `Data0.pak` as a temporary ZIP and extracts it instead of extracting the user's installed archive.
2. **Destructive finalization:** upstream deletes the live game `Data0.pak` before the rebuilt archive has been validated/copied successfully.
3. **Hard-coded line numbers:** most direct edits assume one exact bundled archive layout.
4. **Replacement-file dependence:** several options copy full game-derived files or directories from bundled presets.
5. **Toggle restoration coupled to prearranged bundle:** some disable branches write placeholders/default copies rather than derive clean state from the installed archive.
6. **GUI-dispatch bugs/mismatches:** movement `1s`, door-disable wrong variable, durability tooltip vs actual `-9.0`, vehicle naming vs actual car/boat edits.

## Linux patch-model consequence

For deterministic toggling, the Linux port should maintain a verified pristine backup/base and build each requested configuration from that base rather than incrementally mutating an already modified archive. This eliminates most upstream "disable" rewrite logic: an unchecked option means its transform is simply not applied to the pristine working tree. If the installed game is externally updated, the pristine-base identity must be revalidated before reuse.

## Remaining inventory gates

The released **top-level control inventory is complete**. Remaining extraction work is:

1. expand `Better firearms POV` into semantic per-weapon/per-FOV definitions;
2. expand `Better firearms upgrading` into semantic per-weapon/per-upgrade definitions;
3. diff/audit `gameaudioeffects.scr.modded` against `.nomod`;
4. inspect/diff AI, zombie-size, spawn, and weather ZIP preset contents;
5. classify every bundled replacement/preset artifact for redistribution provenance;
6. verify each resulting target and expected default state against the native Linux `Data0.pak`.
