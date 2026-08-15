# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Stable branch: `main`
- Active branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of the released DIRUE behavior. New gameplay tweaks remain deferred until released parity is implemented and validated.

## Verified native Linux baseline

The physical native-Linux Steam installation has been validated with:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `<DIRDE_ROOT>/DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is accepted baseline evidence, not a permanent compatibility requirement. Read-only audits and disposable candidate runs performed so far left the installed archive unchanged.

Raw local reports, machine-specific paths, copied game content, and temporary candidate archives are not committed to Git.

## Candidate catalog

The current candidate-ready catalog contains 20 semantic options.

### Native disposable-candidate validated

These 15 options have already passed individual native candidate builds against the validated archive, and a combined 15-option candidate also passed with 3060 entries:

- better movement;
- bullet penetration;
- Deeper Pockets;
- headshot-only AI;
- hold more ammo;
- Improved Loot;
- increased durability;
- instant break doors;
- vehicle noclip;
- reduced jump stamina;
- reduced sprint stamina;
- reduced sunflare;
- reverb/echo removal;
- run with weapons;
- skip intro videos.

### Candidate-ready, native candidate validation pending

Five options were completed after that native run:

- `one_hit_ai`;
- `better_firearm_upgrading`;
- `better_firearm_pov_62`;
- `better_firearm_pov_72`;
- `better_firearm_pov_82`.

One-hit and headshot-only AI are mutually exclusive because they represent choices from one released difficulty dropdown. The three POV variants are likewise mutually exclusive. Candidate construction rejects conflicting selections before patch application.

## Vehicle noclip

The released AHK modifies only the car and old-boat physics files; truck edits are commented out. Native block-aware evidence maps the released changes to exactly these two named blocks in each file:

- `ContactParams("SimpleObjects")`;
- `ContactParams("NonODEObjects")`.

Linux changes each block's single `Ignore(0)` to `Ignore(1)` and leaves Terrain, ODEObjects, Water, and truck behavior unchanged. Historical line numbers were used only for provenance correlation and are not runtime targets.

## AI difficulty

### Normal

`ai_norm.zip` matches the represented native AI tree, so normal mode requires no transform when building from a pristine base.

### One hit

The accepted v4 preset comparison found exactly two differing native members:

- `data/ai/infected/infected_data.scr`;
- `data/ai/zombie/vessel_data.scr`.

Both differences are `ParamBool("one_shot", 0 -> 1)` plus non-behavioral trailing annotations/layout. Linux therefore implements two named value changes and copies no preset file content.

### Headshot only

The inherited headshot preset differs in 20 represented AI files. All 20 differences are completely represented by audited named `ParamFloat`/`ParamBool` changes. The semantic implementation has already passed native disposable-candidate validation.

### Hard

Hard AI differs in 57 represented files. The v4 audit explains 56 of those differences after conservative layout/trailing-comment normalization, but `data/ai/zombie/vessel_data_preset_custom_31.scr` still contains unresolved structure. Hard mode remains unready; no partial hard-mode transform is exposed.

## Preset audit safety

The v4 comparison exposed an audit-classification weakness: a masked semantic structure could appear complete even when the semantic-delta extractor had not actually named the changed value. The audit is now hardened so:

- semantic completeness on a differing member requires an actual extracted semantic delta;
- raw `layout_only` and `layout_or_trailing_comment_only` signals never mask values;
- active calls with trailing separators can still be parsed semantically;
- full-line commented code remains significant;
- unknown behavior remains incomplete.

This correction must be exercised on the physical archive before forced-spawn, weather/time, or zombie-size variants are promoted.

## Firearm source reconstruction

`DIRUE.ahk` remains the behavioral specification. The accepted source-map v2 report found all seven requested firearm sections with no missing sections and mapped 744 active released targets:

- Better Firearms Upgrading: 157;
- Better Firearms POV 62: 157;
- Better Firearms POV 72: 157;
- Better Firearms POV 82: 157;
- sway fix 62: 20;
- sway fix 72: 48;
- sway fix 82: 48.

Historical line numbers are research-only. Runtime firearm transforms use named `Item` blocks, complete accepted prior call sequences, semantic call identity, and exact-count validation.

### Better Firearms Upgrading

The native upgrade layout is consistently `UpgradeLevel(0,0,1,1,2,2,3,3)` across the 21 intended firearm items. The semantic implementation accounts for all 157 active released targets:

- 58 existing-call value replacements;
- 99 tier-local authored `ShotTime`/`ReloadTime` insertions.

Commented-out rifle `ShotTime` lines from the released source remain excluded. Reapplying to a non-pristine tier segment fails closed rather than duplicating calls.

### Better Firearms POV

Each FOV-specific POV definition includes its released coupled sway handler. Local source-map accounting matches the accepted report exactly:

- POV 62 + sway 62: 177/177 targets;
- POV 72 + sway 72: 205/205 targets;
- POV 82 + sway 82: 205/205 targets.

The implementation validates complete per-item native call sequences. Where the released source changes call type, Linux performs a scoped `HolderOffset -> HandOffset` replacement. Pistol tier offsets are identified by verified call ordinals within the named item rather than by historical source lines. The released Desert Eagle FOV-82 asymmetry is intentionally preserved.

POV remains separate from the camera FOV dropdown, matching released control flow.

## Camera FOV status

Released camera choices are 62 default, 72, and 82.

- 62 writes `CameraDefaultFOV=62.5` only.
- 72 writes `CameraDefaultFOV=72` and active recoil changes for seven shotgun families, CrowdPleaser, Desert Eagle, Magnum, M9, and McCall. Its Colt recoil line is not active.
- 82 writes `CameraDefaultFOV=82`, the shotgun/Crowd recoil changes, and active hip-fire changes for Desert Eagle, Magnum, M9, McCall, and Colt.

The remaining blocker is the exact native five-call `ShootVertRecoil` prior sequence for the shotgun/Crowd targets. A compact read-only `audit-fov-recoil` command now reports only the 13 relevant firearm sequences and requires exactly five active recoil calls per item. No FOV 72/82 runtime definition will be added until those native priors are read from the physical archive.

## Other preset-backed controls

- Default spawn preset matches native. Forced-spawn variants remain unready pending the hardened preset audit.
- Vanilla weather matches native. Non-default weather/time variants still contain unresolved script structure.
- Zombie-size presets contain known scale intent, but the complete four-file behavior must be reclassified by the hardened audit before implementation.

No full proprietary preset replacement is copied into the Linux implementation.

## Linux core and transaction safety

The Python core currently provides:

- native ELF/game-root validation;
- strict ZIP validation with CRC, unsafe-path and duplicate checks;
- safe extraction/rebuild helpers;
- pristine backup creation without silent overwrite;
- validated atomic candidate installation and restore primitives;
- in-memory candidate building from a validated source archive;
- semantic XML, named-call, named-block, loot, intro, reverb, Deeper Pockets, noclip, AI, firearm-upgrading, and firearm-POV transforms;
- mutual-exclusion validation for one-choice controls;
- deterministic JSON CLI validation;
- read-only native, preset, research, source-map, and compact FOV-recoil audits.

Linux patching must start from the user's validated installed archive or a verified pristine backup derived from it. The inherited repository `Data0.pak` is never a Linux patch source or install payload.

A failed candidate build or validation must leave the live archive unchanged. The installed Steam game has still not been modified by the Linux port.

## Validation evidence and current gates

Verified evidence is scoped to the code state that produced it:

- the initial physical parity run passed the then-current 44-test suite and left Data0 unchanged;
- the later native candidate run passed all then-ready 15 options individually and in one combined candidate;
- source-map v2 supplied complete 744-target firearm research evidence;
- preset v4 supplied the accepted one-hit result and identified the remaining hard-AI structural blocker;
- new one-hit, preset-hardening, firearm-upgrading, POV, and FOV-audit work passed focused synthetic checks when introduced;
- no GitHub Actions were used.

Next physical gates are:

1. run the current full repository test suite, `git diff --check`, and Python compilation;
2. run disposable native candidates for the five newly candidate-ready options, with representative compatible combinations;
3. rerun the hardened preset audit;
4. run the compact `audit-fov-recoil` read-only audit;
5. verify Data0 is unchanged before/after;
6. use the resulting recoil priors to finish camera FOV 72/82 semantics;
7. repeat disposable candidate validation for every option added afterward;
8. only then review pristine backup/restore and atomic live replacement on the QA installation;
9. finish remaining released preset-backed behavior, then add the Linux-native GUI and packaging.

GitHub Issues are disabled in this repository, so unresolved work remains tracked in project documentation rather than changing repository settings.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports should be removed once replacement evidence is accepted, while current evidence, unresolved diagnostics, pristine backups, hashes, provenance material, and unrelated work are preserved.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
