# Milestone 1 feature-parity inventory

This document is the authoritative released-control inventory for the native Linux port. `DIRUE.ahk` defines released behavior; historical source line numbers are provenance evidence only and are never runtime patch targets.

Status terms:

- **Native-validated**: semantic definition passed a disposable build against the validated native Data0.
- **Candidate-ready**: semantic definition is implemented and synthetically validated, but still needs a native disposable build.
- **Research**: released behavior is known but native semantic preconditions are not yet complete.
- **Preset unresolved**: the released option replaces bundled files and complete semantic behavior is not yet proven.
- **Inactive upstream**: handler exists but released GUI control is commented out.

## Application controls

| Released control | Released behavior | Linux direction |
|---|---|---|
| Select folder | Validates a Windows `.exe`/DLL/Data0 layout. | Validate native ELF `DeadIslandRiptideGame`, expected `DIR` layout, and safe ZIP-compatible Data0. |
| Enable music? | Starts/stops bundled Windows helper audio. | Not required for gameplay parity; Windows helper is not carried over. |
| Confirm modifications | Deletes live Data0 before rebuilding/copying. | Build from a pristine validated base, validate candidate, preserve backup, and use recoverable atomic replacement. |

Upstream also unconditionally replaces `data/game.ini` and `data/menu/scr/menumain_pc.xui` from bundled files. These remain provenance-sensitive and are not assumed necessary merely because the Windows script copied them.

## Direct gameplay controls

| Control | Semantic behavior | Status |
|---|---|---|
| Reduce sprint stamina | `MoveSprintStaminaConsumption 0.05 -> 0.03` | Native-validated |
| Reduce jump stamina | `JumpStaminaCost 0.06 -> 0.03` | Native-validated |
| Reduce sunflare 90% | glow factors `1.0 -> 0.1` in both glow scripts | Native-validated |
| Run with weapons | `HideWeaponsDuringSprint 1.0 -> 0.0` | Native-validated |
| Better movement | forward `3.5->3.70`, backward `2.5->2.70`, strafe `2.5->3.70`, acceleration `7.0->12.00`, deceleration `10.0->12.00` | Native-validated |
| Hold more ammo | pistol `50->200`, rifle `60->150`, shotgun `20->90` | Native-validated |
| Instantly break doors | `BreakDoorEffectivens 0 -> 99` | Native-validated |
| Increase durability | four durability-loss values -> `-9.0` as implemented by released handler | Native-validated |
| Bullet penetration | `BulletPenetrationChance 0. -> 0.98` | Native-validated |
| Even Deeper Pockets | five characters: `desc_params 2;4;6 -> 6;12;18`, `InventorySize 2 -> 6` | Native-validated |
| Skip intro videos | comment the active `File("Intro_720p", ...)` call by first quoted argument, preserving later arguments | Native-validated |
| Remove reverb/echo | disable the audited reverb preset/mix declarations and 52+52 calls; already-commented Echo statements remain untouched | Native-validated |
| NoClip vehicles | in car and old boat only, `SimpleObjects` and `NonODEObjects` `Ignore(0)->Ignore(1)` | Native-validated |

Known upstream GUI/handler quirks are preserved as documentation, not copied as Linux bugs: movement checks `1s`, door-disable checks the wrong variable, durability tooltip says `0.5` while handler writes `-9.0`, and vehicle naming implies more targets than the released handler actually edits.

## Improved Loot

Target: `data/default.loot`.

| Group | Native White/Green/Blue/Violet/Orange | Improved |
|---|---|---|
| Default chest | 91 / 7 / 2 / 0 / 0 | 55 / 32 / 8 / 3 / 2 |
| Lockpick 1 | 0 / 92 / 6 / 1 / 0 | 0 / 77 / 10 / 8 / 5 |
| Lockpick 2 | 0 / 85 / 11 / 3 / 1 | 0 / 55 / 16 / 15 / 14 |
| Lockpick 3 | 0 / 72 / 21 / 5 / 2 | 0 / 37 / 33 / 14 / 16 |
| Ram | 0 / 10 / 67 / 20 / 3 | 0 / 5 / 30 / 50 / 15 |
| MeleeFighter | 0 / 65 / 35 / 0 / 0 | 0 / 6 / 31 / 52 / 11 |

The GUI describes the final category as Butchers, but released code targets `MeleeFighter`. Status: **Native-validated**.

## Camera FOV dropdown

Released choices: `62 default`, `72`, `82`.

### FOV 62

- `CameraDefaultFOV 62.5`.
- The released handler performs no active recoil restoration.
- Linux builds from a pristine base, so selecting 62 can omit the 72/82 recoil transform instead of reproducing incremental-state behavior.

Status: **Research** until the complete dropdown definition is added with 72/82.

### FOV 72

- `CameraDefaultFOV -> 72`.
- Seven shotgun families plus `Firearm_leg_CrowdPleaser`: five active `ShootVertRecoil` writes per item, desired sequence `0.06, 0.14, 0.14, 0.14, 0.14`.
- Active pistol hip-fire writes: Desert Eagle `0.015`, Magnum `0.017`, M9 `0.015`, McCall `0.015`.
- The released 72 handler has no active Colt recoil write.
- Commented Desert Eagle/Magnum tier recoil lines stay excluded.

Status: **Research**. A compact read-only native audit is waiting to verify the five-call native prior sequence for the shotgun/Crowd items.

### FOV 82

- `CameraDefaultFOV -> 82`.
- Seven shotgun families plus CrowdPleaser: desired recoil sequence `0.033, 0.14, 0.14, 0.14, 0.14`.
- Active pistol hip-fire writes: Desert Eagle `0.008`, Magnum `0.010`, M9 `0.015`, McCall `0.015`, Colt `0.015`.
- Commented tier recoil lines stay excluded.

Status: **Research**, for the same native-prior audit gate.

## Better Firearms POV

Targets: `data/inventory_gen.scr` and `data/inventory_special.scr`.

Released FOV-specific variants change `AimBlurStart`, `HolderOffset`/`HandOffset`, `HandRot`, `AimFov`, and the matching sway handler. Families include Fury firearms, pistols/revolvers, seven shotgun families, automatic/burst/single-shot rifles, McCall, CrowdPleaser, and Defender.

The accepted source-map v2 report contains 744 active firearm targets across the upgrading, POV, and sway sections. Linux POV definitions account exactly for:

- FOV 62 POV + sway: 177/177 targets;
- FOV 72 POV + sway: 205/205 targets;
- FOV 82 POV + sway: 205/205 targets.

Runtime targeting uses named item identity and complete native call sequences. Pistol aimed offsets target verified HandOffset ordinals 3/6/9/12 inside the named item. Released call-type changes are expressed as scoped `HolderOffset -> HandOffset` replacements. The released asymmetric Desert Eagle FOV-82 offsets are preserved.

The three POV variants are mutually exclusive. They do not change `CameraDefaultFOV`; the camera dropdown is a separate released control.

Status: **Candidate-ready** for all three variants; native disposable builds pending.

## Better Firearms Upgrading

Target: `data/inventory_gen.scr`.

The released active handler uses `ShotTime`, `ReloadTime`, `ShootVertRecoil`, and, for automatic rifles, `ShootMaxAngle`. Several rifle `ShotTime` source lines are commented out and are excluded.

Native research established the intended 21 weapon items with a consistent upgrade-marker sequence `0,0,1,1,2,2,3,3`. Linux accounts for every active released upgrading target:

- 58 existing-call semantic replacements;
- 99 authored tier-local `ShotTime`/`ReloadTime` insertions;
- total 157/157 active source targets.

The insertions are anchored to validated named-item `UpgradeLevel` segments and reject non-pristine segments rather than duplicating calls.

Status: **Candidate-ready**; native disposable build pending.

## Zombie difficulty dropdown

| Choice | Released preset | Linux status |
|---|---|---|
| Normal | `ai_norm.zip` | Native tree represented by preset matches baseline; no transform needed from pristine base |
| One hit | `ai_Onehit.zip` | **Candidate-ready**: exactly two audited `ParamBool("one_shot", 0->1)` edits |
| Hard | `ai_hard.zip` | **Preset unresolved**: 56/57 differing members explained, one custom vessel file still structural |
| Headshot only | `ai_Headshot.zip` | **Native-validated** semantic definition across 20 audited files |

One-hit and headshot-only definitions are mutually exclusive because they represent alternatives from the same released dropdown.

## Zombie size dropdown

Released presets replace:

- `data/presets/infectedai.pre`;
- `data/presets/infectedai_pre.def`;
- `data/presets/zombieai.pre`;
- `data/presets/zombieai_pre.def`.

Choices: extra-small, midget, normal, large, supersize. Earlier evidence identified scale intent including `0.3`, `0.6`, `2.0`, and `5.0`, but the v4 completeness classifier exposed an over-certification edge case. The hardened preset audit must reclassify the complete four-file behavior before any size option is promoted.

Status: **Preset unresolved**.

## Forced-spawn dropdown

Target replaced by release: `data/presets/aispawnbox_pre.def`.

Choices: normal, Butchers, Rams, Bloaters, Thugs, Suiciders, bandits with guns, bandits with melee. Default preset matches native. Non-default variants remain unresolved until the hardened audit extracts the actual semantic difference rather than treating masked structure as sufficient evidence.

Status: **Preset unresolved**.

## Weather/time dropdown

Released choices:

- Default (vanilla)
- just night
- Rain (day)
- Rain (night)
- Storm (day)
- Storm (night)
- Just night (Darker)
- Rain (Darker night)
- Storm (Darker night)

The Windows release deletes/replaces combinations of:

- `data/scripts/weather/weather.scr`;
- `data/scripts/varlist_ambient.scd`;
- `data/scripts/varlist_ambient.scr`;
- `data/scripts/logic_script.scr`.

Vanilla matches native. Non-default variants still contain unresolved behavior in `logic_script.scr` and/or `weather.scr`, even where ambient named values are understood.

Status: **Preset unresolved**.

## Inactive/commented upstream controls

These remain outside released Milestone-1 UI parity unless later evidence shows they were user-facing in the released version:

- standalone High-FOV recoil-fix checkbox;
- Custom weapons;
- standalone Night-time Paradise checkbox.

The active FOV dropdown already carries its own recoil edits, and the active weather dropdown already exposes night variants.

## Transaction and provenance requirements

The Linux port intentionally does not reproduce these Windows implementation hazards:

1. using the repository-bundled Data0 as the patch base;
2. deleting live Data0 before a replacement is validated;
3. runtime hard-coded line-number targeting;
4. full-file preset replacement without provenance review;
5. placeholder-based disable paths tied to a prearranged bundled archive;
6. Windows helper executables or Proton/Wine dependencies.

Each semantic transform must specify a stable target, accepted prior state, desired state, and exact expected match/sequence count, and must fail closed on missing or ambiguous input.

## Current validation boundary

Fifteen earlier ready options have passed native disposable candidates individually and in one combined candidate. The newly implemented one-hit, upgrading, and three POV variants still need native disposable-candidate validation. The hardened preset audit and compact FOV-recoil audit also need one physical read-only run.

The installed native game has not yet been modified by the Linux port. Live replacement remains gated behind validated backup/restore and atomic-install QA.
