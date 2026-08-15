# Milestone 1 feature-parity inventory

This document is the authoritative released-control inventory for the native Linux port. `DIRUE.ahk` defines released behavior. Historical source line numbers are provenance evidence only and are never runtime patch targets.

Status terms:

- **Native-validated**: semantic definition passed a disposable build against validated native Data0.
- **Candidate-ready**: implemented and synthetically validated but still awaiting a native disposable build.
- **Research**: released behavior is known but complete semantic preconditions are not yet proven.
- **Preset unresolved**: released preset behavior is not yet represented by a public-safe complete semantic transform.
- **Inactive upstream**: handler exists but the released GUI control is commented out.

## Application controls

| Released control | Released behavior | Linux direction |
|---|---|---|
| Select folder | Windows `.exe`/DLL/Data0 validation | Validate native ELF `DeadIslandRiptideGame`, expected `DIR` layout, and safe ZIP-compatible Data0 |
| Enable music? | Starts/stops bundled Windows helper audio | Not required for gameplay parity; Windows helper is not carried over |
| Confirm modifications | Deletes live Data0 before rebuilding/copying | Build from a verified base, preserve a pristine backup, validate a candidate, bind installation to the source hash, and replace atomically |

Upstream also unconditionally replaces `data/game.ini` and `data/menu/scr/menumain_pc.xui` from bundled files. Those remain provenance-sensitive and are not assumed necessary merely because the Windows script copied them.

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
| Increase durability | four durability-loss values -> `-9.0` as released | Native-validated |
| Bullet penetration | `BulletPenetrationChance 0. -> 0.98` | Native-validated |
| Even Deeper Pockets | five characters: `desc_params 2;4;6 -> 6;12;18`, `InventorySize 2 -> 6` | Native-validated |
| Skip intro videos | comment active `File("Intro_720p", ...)`, preserving later arguments | Native-validated |
| Remove reverb/echo | disable audited reverb preset/mix declarations and calls; existing Echo comments stay untouched | Native-validated |
| NoClip vehicles | car and old boat: `SimpleObjects` and `NonODEObjects` `Ignore(0)->Ignore(1)` | Native-validated |

Known upstream GUI/handler quirks are documented rather than silently normalized: movement checks `1s`, door-disable checks the wrong variable, the durability tooltip says `0.5` while the handler writes `-9.0`, and vehicle naming implies more targets than the released handler actually edits.

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

The GUI describes the last category as Butchers, but released code targets `MeleeFighter`. Status: **Native-validated**.

## Camera FOV dropdown

Released choices are 62 default, 72, and 82.

- **62**: pristine `CameraDefaultFOV=62.5`; no active recoil restoration in the released handler; represented by absence of a non-default patch.
- **72**: `CameraDefaultFOV -> 72`; seven shotgun families plus CrowdPleaser become recoil sequence `0.06, 0.14, 0.14, 0.14, 0.14`; active pistol base recoil changes are Desert Eagle `0.015`, Magnum `0.017`, M9 `0.015`, McCall `0.015`; Colt is unchanged.
- **82**: `CameraDefaultFOV -> 82`; the same shotgun/Crowd families become `0.033, 0.14, 0.14, 0.14, 0.14`; active pistol base recoil changes are Desert Eagle `0.008`, Magnum `0.010`, M9 `0.015`, McCall `0.015`, Colt `0.015`.

Corrected native repeated-block evidence maps the four authored shotgun/Crowd tier calls to blocks 2/4/6/8 of each eight-block item group. Commented pistol tier lines remain excluded. Camera FOV 72/82 are mutually exclusive. Native candidate checks pass with Better Firearms Upgrading and matching POV variants.

Status: 62 baseline/no patch; 72 and 82 **Native-validated**.

## Better Firearms POV

Targets: `data/inventory_gen.scr` and `data/inventory_special.scr`.

Released FOV-specific variants change `AimBlurStart`, `HolderOffset`/`HandOffset`, `HandRot`, `AimFov`, and the matching sway handler. Runtime targeting uses named repeated-item groups and complete accepted call sequences. Pistol aimed offsets use verified semantic ordinals across the group. Released `HolderOffset -> HandOffset` changes and the asymmetric Desert Eagle FOV-82 values are preserved.

Accepted source-map accounting:

- FOV 62 POV + sway: 177/177 active targets;
- FOV 72 POV + sway: 205/205;
- FOV 82 POV + sway: 205/205.

The three POV variants are mutually exclusive and do not change `CameraDefaultFOV`. Status: **Native-validated** for all three variants.

## Better Firearms Upgrading

Target: `data/inventory_gen.scr`.

The released handler uses `ShotTime`, `ReloadTime`, `ShootVertRecoil`, and, for automatic rifles, `ShootMaxAngle`. Commented rifle `ShotTime` source lines are excluded.

Native reconstruction covers 21 weapon groups with `UpgradeLevel(0,0,1,1,2,2,3,3)` and all 157 active released targets: 58 existing-call replacements plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Insertions are anchored to validated marker segments and reject non-pristine segments rather than duplicating calls.

Status: **Native-validated**.

## Zombie difficulty dropdown

| Choice | Released preset | Linux status |
|---|---|---|
| Normal | `ai_norm.zip` | baseline/no transform |
| One hit | `ai_Onehit.zip` | **Native-validated**: two audited `ParamBool("one_shot", 0->1)` edits |
| Hard | `ai_hard.zip` | **Native-validated**: 209 named `ParamFloat` edits across all 57 differing members |
| Headshot only | `ai_Headshot.zip` | **Native-validated** across 20 audited files |

One Hit, Hard, and Headshot Only are mutually exclusive values from the same released control. Hard uses a digest-guarded semantic table from accepted preset-v5 evidence; the sanitized structural audit proved no hidden structural delta, and the native disposable candidate changed exactly 57 members while retaining 3060 entries.

## Zombie size dropdown

Released choices: extra-small, midget, normal, large, supersize.

Hardened preset evidence shows every non-default difference is confined to `m_ForcedBodyScaleMin`/`m_ForcedBodyScaleMax` in:

- `data/presets/infectedai.pre`;
- `data/presets/infectedai_pre.def`;
- `data/presets/zombieai.pre`;
- `data/presets/zombieai_pre.def`.

Released constants are extra-small `0.3`, midget `0.6`, large `2.0`, and supersize `5.0`; normal is pristine native state. Linux validates occurrence counts and baseline value-sequence SHA-256 digests, then changes only those call arguments. It does not copy preset archives or native value vectors.

Status: four non-default modes **Native-validated**; normal baseline/no patch.

## Forced-spawn dropdown

Target replaced by the release: `data/presets/aispawnbox_pre.def`.

Choices: normal, Butchers, Rams, Bloaters, Thugs, Suiciders, bandits with guns, bandits with melee.

Default matches native. Every non-default preset changes active `m_AIPresets` values in a 165-call vector. Sanitized evidence proves exact pristine donors exist for Suicider and bandits-with-guns. Butcher, Ram, Bloater, Thug, and bandits-with-melee have no exact quoted donor anywhere in the audited native Data0.

The literal identifier lists remain provenance-sensitive and are not copied into source. A narrow private-QA probe now records only the pristine 165-value vector digest so the two donor-backed modes can be implemented with complete prior-state validation.

Status: **Research / preset unresolved** as a complete dropdown. Two donor-backed choices are eligible for semantic implementation after the vector digest is collected; five choices remain provenance-gated.

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

Vanilla matches native. Sanitized structural evidence proves:

- rain/storm variants add a recognized `set("f_game_weather", ...)` call to `logic_script.scr`;
- day variants keep `f_weather_interior` commented while night variants activate it;
- night variants activate the native-commented `time = ...` and `Set("f_game_time", ...)` sites in `weather.scr`;
- day rain/storm leave `weather.scr` unchanged;
- ordinary night uses `f_engine_envprobe_factor -> 0.01`;
- darker night uses `0.0099` plus `f_lighting_indirect_factor 0.45 -> 0.05`.

The accepted detail-v1 report confirmed those ambient values but its simple recognized-call parser did not recover the argument tails of the logic/time calls. A new research-only probe handles nested arguments, comments, and CRLF and emits only those four whitelisted argument tails.

Status: **Research** pending that final private value probe.

## Inactive/commented upstream controls

Outside released Milestone-1 UI parity unless later evidence shows otherwise:

- standalone High-FOV recoil-fix checkbox;
- Custom weapons;
- standalone Night-time Paradise checkbox.

The active camera FOV dropdown already carries its recoil edits, and the active weather dropdown exposes night variants.

## Transaction and provenance requirements

The Linux port does not reproduce these Windows implementation hazards:

1. using repository-bundled Data0 as a patch base;
2. deleting live Data0 before validated replacement;
3. installing over a live archive whose hash no longer matches the candidate source;
4. accepting a pristine backup whose hash does not match that source;
5. runtime hard-coded line-number targeting;
6. full-file preset replacement without provenance review;
7. placeholder disable paths tied to a prearranged bundled archive;
8. Wine/Proton or Windows helper runtime dependencies.

Candidate installation validates candidate, live archive, and backup; requires source-hash agreement and matching entry counts; writes through a same-directory temporary file; rechecks the live hash immediately before atomic replacement; and verifies the installed hash afterward. Restore validates the backup hash and can recover even if the live archive is missing.

Native transaction QA passed: one validated candidate was atomically installed, its live hash matched exactly, and the retained pristine backup restored the exact original 3060-entry baseline. The live game is pristine and the backup is retained recovery material.

## Current validation boundary

All **27** semantic non-default catalog options are native disposable-candidate validated. Material FOV/Upgrading/POV interactions, a maximal compatible candidate, choice-conflict rejection, and native backup/install/restore transaction QA pass.

Remaining released parity work is weather/time, five provenance-gated forced-spawn choices, the upstream unconditional `game.ini` / `menumain_pc.xui` replacement review, then bounded gameplay/visual QA and Linux-native GUI/packaging. The research-only weather probe is the next physical read gate.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized.
