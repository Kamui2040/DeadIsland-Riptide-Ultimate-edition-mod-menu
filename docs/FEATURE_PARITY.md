# Milestone 1 feature-parity inventory

This document is the authoritative released-control inventory for the native Linux port. `DIRUE.ahk` defines released behavior; historical source line numbers are provenance evidence only and are never runtime patch targets.

Status terms:

- **Native-validated**: semantic definition passed a disposable build against the validated native Data0.
- **Candidate-ready**: semantic definition is implemented and synthetically validated but still needs a native disposable build.
- **Research**: released behavior is known but native semantic preconditions are not complete.
- **Preset unresolved**: released preset behavior is not yet represented by a public-safe complete semantic transform.
- **Inactive upstream**: handler exists but released GUI control is commented out.

## Application controls

| Released control | Released behavior | Linux direction |
|---|---|---|
| Select folder | Validates a Windows `.exe`/DLL/Data0 layout. | Validate native ELF `DeadIslandRiptideGame`, expected `DIR` layout, and safe ZIP-compatible Data0. |
| Enable music? | Starts/stops bundled Windows helper audio. | Not required for gameplay parity; Windows helper is not carried over. |
| Confirm modifications | Deletes live Data0 before rebuilding/copying. | Build from a verified base, validate a candidate, preserve a pristine backup, bind installation to the source hash, and replace atomically. |

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
| Skip intro videos | comment active `File("Intro_720p", ...)` by first quoted argument while preserving later arguments | Native-validated |
| Remove reverb/echo | disable audited reverb preset/mix declarations and calls; already-commented Echo statements remain untouched | Native-validated |
| NoClip vehicles | car and old boat: `SimpleObjects` and `NonODEObjects` `Ignore(0)->Ignore(1)` | Native-validated |

Known upstream GUI/handler quirks are documented rather than normalized silently: movement checks `1s`, door-disable checks the wrong variable, durability tooltip says `0.5` while the handler writes `-9.0`, and vehicle naming implies more targets than the released handler actually edits.

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

Released choices: 62 default, 72, 82.

### FOV 62

- pristine `CameraDefaultFOV=62.5`;
- no active recoil restoration in the released handler;
- represented by absence of the 72/82 non-default transform.

Status: baseline/no patch required.

### FOV 72

- `CameraDefaultFOV -> 72`;
- seven shotgun families plus CrowdPleaser: `ShootVertRecoil` becomes `0.06, 0.14, 0.14, 0.14, 0.14`;
- active pistol base recoil: Desert Eagle `0.015`, Magnum `0.017`, M9 `0.015`, McCall `0.015`;
- Colt has no active 72 recoil write;
- commented pistol tier lines remain excluded.

Native repeated-block evidence maps the four authored tier recoil calls to blocks 2/4/6/8 of each eight-block item group. Runtime targeting validates the full marker sequence and never uses source lines.

Status: **Native-validated**.

### FOV 82

- `CameraDefaultFOV -> 82`;
- seven shotgun families plus CrowdPleaser: `ShootVertRecoil` becomes `0.033, 0.14, 0.14, 0.14, 0.14`;
- active pistol base recoil: Desert Eagle `0.008`, Magnum `0.010`, M9 `0.015`, McCall `0.015`, Colt `0.015`;
- commented tier lines remain excluded.

Status: **Native-validated**.

Camera FOV 72/82 are mutually exclusive. Native candidate interaction checks pass with Better Firearms Upgrading and with matching POV variants. When Upgrading is also selected, it is applied first and the camera edit changes only verified base recoil while preserving the upgraded tier tail.

## Better Firearms POV

Targets: `data/inventory_gen.scr` and `data/inventory_special.scr`.

Released FOV-specific variants change `AimBlurStart`, `HolderOffset`/`HandOffset`, `HandRot`, `AimFov`, and the matching sway handler. Families include Fury firearms, pistols/revolvers, seven shotgun families, automatic/burst/single-shot rifles, McCall, CrowdPleaser, and Defender.

The accepted source-map evidence contains 744 active firearm targets across upgrading, POV, and sway sections. Linux POV definitions account exactly for:

- FOV 62 POV + sway: 177/177;
- FOV 72 POV + sway: 205/205;
- FOV 82 POV + sway: 205/205.

Runtime targeting uses named repeated-item groups and complete native call sequences. Pistol aimed offsets use verified call ordinals across the group. Released `HolderOffset -> HandOffset` call-type changes and the asymmetric Desert Eagle FOV-82 values are preserved.

The three POV variants are mutually exclusive and do not change `CameraDefaultFOV`.

Status: **Native-validated** for all three variants.

## Better Firearms Upgrading

Target: `data/inventory_gen.scr`.

The released active handler uses `ShotTime`, `ReloadTime`, `ShootVertRecoil`, and, for automatic rifles, `ShootMaxAngle`. Commented rifle `ShotTime` source lines are excluded.

Native research established 21 weapon groups with upgrade markers `0,0,1,1,2,2,3,3`. Linux accounts for all 157 active targets:

- 58 existing-call semantic replacements;
- 99 tier-local authored `ShotTime`/`ReloadTime` insertions.

Insertions are anchored to validated named-item marker segments and reject non-pristine segments rather than duplicating calls.

Status: **Native-validated**.

## Zombie difficulty dropdown

| Choice | Released preset | Linux status |
|---|---|---|
| Normal | `ai_norm.zip` | Native baseline; no transform needed |
| One hit | `ai_Onehit.zip` | **Native-validated**: two audited `ParamBool("one_shot", 0->1)` edits |
| Hard | `ai_hard.zip` | **Preset unresolved**: 56/57 differing members explained, one custom vessel member remains structural |
| Headshot only | `ai_Headshot.zip` | **Native-validated** across 20 audited files |

One-hit and headshot-only are mutually exclusive alternatives from the same released control.

## Zombie size dropdown

Released choices: extra-small, midget, normal, large, supersize.

The hardened preset audit shows normal matches native and every non-default difference is confined to `m_ForcedBodyScaleMin`/`m_ForcedBodyScaleMax` in exactly four members:

- `data/presets/infectedai.pre`;
- `data/presets/infectedai_pre.def`;
- `data/presets/zombieai.pre`;
- `data/presets/zombieai_pre.def`.

Released constants:

- extra-small `0.3`;
- midget `0.6`;
- normal = pristine native values;
- large `2.0`;
- supersize `5.0`.

Linux does not copy preset archives. It validates exact native Min/Max sequences with occurrence counts and SHA-256 digests, then changes only those call arguments. The four non-default options are mutually exclusive.

Status: **Native-validated** for extra-small, midget, large, and supersize; normal is baseline/no patch required.

## Forced-spawn dropdown

Target replaced by the release: `data/presets/aispawnbox_pre.def`.

Choices: normal, Butchers, Rams, Bloaters, Thugs, Suiciders, bandits with guns, bandits with melee.

Hardened preset evidence confirms default matches native and non-default modes contain large semantic sets of AI-preset identifier replacements. Those strings are provenance-sensitive and a public-safe complete algorithmic reconstruction has not been proven.

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

The release replaces combinations of `weather.scr`, ambient varlists, and `logic_script.scr`. Vanilla matches native. Non-default modes still contain unresolved script behavior even where named ambient values are understood.

Status: **Preset unresolved**.

## Inactive/commented upstream controls

These remain outside released Milestone-1 UI parity unless later evidence shows they were user-facing:

- standalone High-FOV recoil-fix checkbox;
- Custom weapons;
- standalone Night-time Paradise checkbox.

The active camera FOV dropdown already carries its recoil edits, and the active weather dropdown exposes night variants.

## Transaction and provenance requirements

The Linux port intentionally does not reproduce Windows implementation hazards:

1. using the repository-bundled Data0 as a patch base;
2. deleting live Data0 before validated replacement;
3. installing over a live archive whose hash no longer matches the candidate source;
4. accepting a pristine backup whose hash does not match that source;
5. runtime hard-coded line-number targeting;
6. full-file preset replacement without provenance review;
7. placeholder disable paths tied to a prearranged bundled archive;
8. Wine/Proton or Windows helper runtime dependencies.

Candidate installation validates candidate, live archive, and backup; requires source-hash agreement and matching entry counts; writes through a same-directory temporary file; rechecks the live hash immediately before atomic replacement; and verifies the installed hash afterward. Restore validates the backup and can recover even if the live archive is missing.

Each gameplay transform must specify stable targets, accepted prior state, desired state, exact match/sequence expectations, and fail closed on missing, ambiguous, malformed, or unexpected input.

## Current validation boundary

All 26 semantic non-default catalog options are native disposable-candidate validated. The latest candidate run also passed four material FOV interactions, one maximal compatible combination containing the newly added families, and both camera-FOV and zombie-size conflict checks.

The installed native game has not been modified by the Linux port. The next physical gate is backup/install/restore transaction QA using the newly hash-bound CLI path. Gameplay/visual QA follows only after the exact original Data0 is restored successfully.
