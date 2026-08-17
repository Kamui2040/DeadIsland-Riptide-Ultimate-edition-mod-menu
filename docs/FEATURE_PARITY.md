# Milestone 1 feature-parity inventory

This document is the authoritative released-control inventory for the native Linux port. `DIRUE.ahk` defines released behavior. Historical source line numbers are provenance evidence only and are never runtime patch targets.

Status terms:

- **Native-validated**: semantic definition passed a disposable build against validated native Data0.
- **Gameplay-validated**: Native-validated behavior was additionally confirmed in the native game with exact pristine restore after the bounded test.
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

Upstream also unconditionally replaces `data/game.ini` and `data/menu/scr/menumain_pc.xui`. A sanitized native comparison shows these are branding/cosmetic, not gameplay requirements: `game.ini` differs only at `GameName#1`, and the menu replacement differs only by one replacement-only `MyText:T_Mylogo` component once the native tree is normalized. Linux therefore does not copy or redistribute either replacement.

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

One Hit, Hard, and Headshot Only are mutually exclusive values from the same released control. Hard uses a digest-guarded semantic table from accepted preset evidence; sanitized structural evidence proved no hidden structural delta, and the native disposable candidate changed exactly 57 members while retaining 3060 entries.

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

Target: `data/presets/aispawnbox_pre.def`.

Released choices: normal, Butchers, Rams, Bloaters, Thugs, Suiciders, bandits with guns, bandits with melee.

Default matches native. Every non-default preset changes active `m_AIPresets` values in a 165-call vector. Runtime transformations validate the complete pristine-vector digest before deriving or replacing any value.

- **Suiciders**: validate all 165 calls and vector digest, take the value at donor ordinal 6, validate its SHA-256, preserve ordinal 6, replace the other 164 values. **Native-validated; gameplay-validated.**
- **Bandits with guns**: take the value at donor ordinal 119, validate its SHA-256, preserve ordinals 60 and 119, replace the other 163 values. **Native-validated.**
- **Bandits with melee**: no exact desired-value donor exists. Sanitized reconstruction evidence proves the target can instead be rebuilt entirely from pristine native values: validate native ordinal 40 by SHA-256 and its 47-part token/separator shape, copy six whole alphanumeric tokens from audited positions within native ordinal 37 after validating that value by SHA-256, preserve all punctuation/separators from the base, validate the reconstructed target SHA-256, preserve ordinal 60, and replace the other 164 quoted values. No target identifier or token text is stored in source. Its native disposable candidate retained all 3060 entries, changed only `data/presets/aispawnbox_pre.def`, changed 164 calls while preserving ordinal 60, and rejected combination with either donor-backed mode. **Native-validated.**
- **Butchers, Rams, Bloaters, and Thugs**: earlier audits found neither exact pristine donors nor acceptable bounded whole-token reconstructions. A later provenance review accepted only the minimum machine-facing compatibility identifier lists required for released behavior, extracted read-only from the inherited upstream preset blobs while keeping those ZIPs excluded from runtime/package payloads. Each literal is pinned by SHA-256, syntax, identifier count, complete pristine-vector validation, preserved ordinal `(60,)`, exact changed-call count `164`, and post-transform result checks. Each disposable native candidate retained all 3060 entries, preserved member order, changed only `data/presets/aispawnbox_pre.def`, and reproduced the released 164/165 call pattern. Bounded native gameplay QA confirmed the intended enemy behavior for all four modes and restored the exact pristine Data0 after every run. **Native-validated; gameplay-validated.**

Only quoted `m_AIPresets` value spans are replaced; layout/comments remain intact. All seven non-default forced-spawn modes share one exclusivity group. Issue #2 records the completed provenance and native-game acceptance path for the four formerly blocked choices.

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

Vanilla matches native. Accepted structural, ambient, and private value evidence establishes the complete released non-default behavior:

| Choice | Weather | Interior | Time | Ambient |
|---|---|---|---|---|
| Just night | unchanged | active `0.3` | freeze `TIME * 0.0`, game-time scale `8.0` | envprobe `0.01` |
| Rain day | `0.8` | commented `0.1` | native comments unchanged | native |
| Rain night | `0.8` | active `0.3` | night behavior | envprobe `0.01` |
| Storm day | `1.0` | commented `0.1` | native comments unchanged | native |
| Storm night | `1.0` | active `0.3` | night behavior | envprobe `0.01` |
| Just night darker | unchanged | active `1.0` | night behavior | envprobe `0.0099`, indirect `0.05` |
| Rain darker night | `0.8` | commented `0.3` | night behavior | envprobe `0.0099`, indirect `0.05` |
| Storm darker night | `1.0` | commented `0.3` | night behavior | envprobe `0.0099`, indirect `0.05` |

The native time sites are comments containing `float time = TIME * 0.1` and `Set("f_game_time", (time - floor(time)) * 24.0)`. Linux validates those semantic priors, activates them as `float time = TIME * 0.0` and scale `8.0`, and preserves the native trailing explanatory comment. Logic overrides are inserted at the named WEATHER section and `interior_inv` calculation anchors, not by line number. The anchor permits the observed blank/whitespace line between the two native WEATHER declarations while still requiring the unique named section, named declarations, and audited order. Ambient changes use strict named `VarFloat` prior-value validation.

All eight non-default choices are mutually exclusive and **Native-validated**. Every individual native disposable candidate retained 3060 entries with the expected member scope. A maximal compatible candidate combining darker storm night with armed-bandit forcing and the previously validated option families also passed.

## Upstream unconditional replacement files

The released Windows workflow always overwrote `data/game.ini` and `data/menu/scr/menumain_pc.xui` from bundled files. Accepted sanitized native comparison establishes that these replacements are cosmetic/branding only:

- native and replacement `game.ini` each contain the same 25 parsed call identities; there are no native-only or replacement-only calls, and only `GameName#1` has different arguments while remaining active in both;
- the menu replacement contains one extra component, `MyText:T_Mylogo`; there are no native-only components, and the replacement becomes structurally equivalent to native after removing that one component.

These copies are not required for released gameplay parity. Linux does not reproduce the unconditional overwrite and will not redistribute either replacement as runtime/package content. Their inherited repository copies remain provenance-sensitive historical upstream material.

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
8. unconditional bundled `game.ini` / menu replacement for cosmetic branding;
9. Wine/Proton or Windows helper runtime dependencies.

Candidate installation validates candidate, live archive, and backup; requires source-hash agreement and matching entry counts; writes through a same-directory temporary file; rechecks the live hash immediately before atomic replacement; and verifies the installed hash afterward. Restore validates the backup hash and can recover even if the live archive is missing.

Native transaction QA passed at both engine and GUI/application levels. A validated candidate was atomically installed and restored to the exact original 3060-entry baseline, and the real Qt Apply/Restore handlers also passed confirmation, apply-lock/reapply rejection, exact install, and exact restore checks. The four newly resolved forced-spawn modes were also installed through the normal application transaction path one at a time, gameplay-confirmed, and restored to the exact pristine archive after every run. The pristine backup is retained recovery material.

## Current validation boundary

Integrated `main` contains **38 semantic non-default options, all Native-validated** against the accepted native baseline. Focused branch `agent/forced-spawn-identifiers` contains **42 semantic non-default options**, and all 42 pass native disposable candidate construction. All seven non-default forced-spawn choices are mutually exclusive on the focused branch.

The Linux-native application/GUI layer is physically validated on Bazzite for the integrated state: isolated optional-GUI installation, PySide6 import, catalog accounting, offscreen construction, real on-screen visual QA, native installation validation, wheel construction, and the real confirmation-driven Apply/Restore transaction all pass. On the focused branch, UI/catalog tests verify the four formerly disabled spawn choices are enabled and the 42-option UI catalog matches the semantic catalog exactly.

Representative native gameplay QA validates camera FOV82, Better Firearms POV82, darker storm/night, Run with weapons, One Hit AI, supersize behavior on active infected/walker AI, Forced Suiciders, Better Firearms Upgrading, Forced Butchers, Forced Rams, Forced Bloaters, and Forced Thugs, with stable playable sessions and exact pristine restore after each bounded test. The Better Firearms Upgrading evidence uses the same fully upgraded Magnum/revolver path before and after mutation and preserves the exact pristine-to-UI multiplier implied by the accepted raw reload values. The supersize release-equivalent four-member transform does not necessarily affect every corpse-decoy/ground actor; that observed entity-state variation is retained as upstream/native behavior rather than expanded beyond the released preset.

Linux packaging is physically validated on Bazzite for the focused 42-option state. The distribution checker requires `src/dirue/forced_spawn_compat.py` in the sdist and `dirue/forced_spawn_compat.py` in the wheel; provenance-sensitive inherited payloads remain excluded. Using an isolated PyPA `build==1.5.0` frontend and a commit-derived `SOURCE_DATE_EPOCH`, two clean builds produced byte-identical artifacts:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

Both artifact copies passed distribution payload validation. The wheel installed in isolation; `pip check`, the `dirue` entry point, direct `python -m dirue.cli`, 42-option semantic/UI catalog accounting, the four compatibility-mode registrations, and CLI/GUI entry-point metadata all passed. The run left the primary branch, HEAD, and working-tree status unchanged and removed the disposable worktrees, artifacts, and QA environments.

The unconditional `game.ini` / `menumain_pc.xui` replacement question is closed: accepted native comparison proves it is cosmetic/branding-only and unnecessary for Linux gameplay parity. Released gameplay-option parity and the bounded packaging integration-readiness gate are complete on the focused branch.

No further routine gameplay or packaging QA is required absent a newly identified risk. Integrating the focused branch into `main` and realigning `linux-port` still requires explicit approval. No release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized.
