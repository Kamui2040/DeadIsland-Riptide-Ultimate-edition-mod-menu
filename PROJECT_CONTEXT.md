# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Stable branch: `main`
- Active branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of the released DIRUE behavior. New gameplay tweaks remain deferred until released parity is implemented and validated.

## Verified native Linux baseline

Accepted physical native-Linux evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a permanent compatibility requirement. All read-only audits and disposable candidate runs so far left the installed archive unchanged.

Raw local reports, machine-specific paths, extracted game content, and temporary candidate archives are not committed to Git.

## Current candidate catalog

The catalog now contains 26 semantic non-default options.

### Native disposable-candidate validated

Twenty options passed individual disposable builds against the validated native archive. The physical retry also passed all six then-maximal compatible combinations and the then-current conflict-rejection checks:

- better movement;
- bullet penetration;
- Deeper Pockets;
- headshot-only AI;
- hold more ammo;
- Improved Loot;
- increased durability;
- instant break doors;
- vehicle noclip;
- one-hit AI;
- reduced jump stamina;
- reduced sprint stamina;
- reduced sunflare;
- reverb/echo removal;
- run with weapons;
- skip intro videos;
- Better Firearms Upgrading;
- Better Firearms POV 62;
- Better Firearms POV 72;
- Better Firearms POV 82.

### Candidate-ready, native build pending

Six options were added from the accepted read-only FOV and preset audits and focused synthetic tests:

- camera FOV 72;
- camera FOV 82;
- zombie size extra-small (`0.3`);
- zombie size midget (`0.6`);
- zombie size large (`2.0`);
- zombie size supersize (`5.0`).

Default camera FOV 62.5 and normal zombie size are pristine-baseline states, so they are intentionally represented by the absence of a non-default patch rather than no-op definitions.

Choice groups fail closed on conflicting selections: one-hit/headshot-only AI, the three Better Firearms POV variants, camera FOV 72/82, and the four non-default zombie-size variants.

## Repeated firearm item groups

Native `inventory_gen.scr` represents each audited firearm as a contiguous group of repeated same-name `Item(...)` blocks rather than one large block.

Runtime firearm transforms therefore:

- require the matching same-name blocks to be contiguous;
- reject interleaved `Item(...)` groups;
- validate complete call sequences across the ordered group;
- validate `UpgradeLevel(0,0,1,1,2,2,3,3)` before tier-local insertions;
- preserve CRLF;
- never use historical line numbers as runtime targets.

This grouping model passed the physical 20-option candidate retry.

## Direct and AI controls

The native-validated semantic set includes the released direct value controls, Improved Loot, Deeper Pockets, intro skipping, reverb removal, vehicle noclip, one-hit AI, and headshot-only AI.

Vehicle noclip is limited to `ContactParams("SimpleObjects")` and `ContactParams("NonODEObjects")` in the released car and old-boat targets. Terrain, ODEObjects, Water, and the commented-out truck source edits remain untouched.

Normal AI matches the represented native tree. One-hit changes only the two audited `ParamBool("one_shot", ...)` values. Headshot-only is represented by the complete named-value delta across 20 audited members.

Hard AI remains unready: 56 of 57 differing members are semantically explained, while one custom vessel member still contains unresolved structure. No partial hard-mode transform is exposed.

## Better Firearms Upgrading and POV

The accepted source-map evidence found all seven requested firearm sections and 744 active released targets.

Better Firearms Upgrading accounts for all 157 active targets:

- 58 existing-call value changes;
- 99 authored tier-local `ShotTime`/`ReloadTime` insertions.

The commented rifle `ShotTime` source lines remain excluded.

Better Firearms POV plus the matching sway handler accounts for:

- FOV 62: 177/177 active targets;
- FOV 72: 205/205 active targets;
- FOV 82: 205/205 active targets.

All four firearm options now pass native disposable candidate builds. POV remains separate from the camera FOV dropdown, matching released control flow.

## Camera FOV reconstruction

Released choices are 62 default, 72, and 82.

- 62 uses pristine `CameraDefaultFOV=62.5` and has no active recoil restoration in the released handler.
- 72 writes `CameraDefaultFOV=72`.
- 82 writes `CameraDefaultFOV=82`.

The accepted corrected native recoil audit verifies 13 relevant firearm groups, each with eight repeated `Item(...)` blocks and `UpgradeLevel(0,0,1,1,2,2,3,3)`.

For the seven shotgun families plus CrowdPleaser:

- pristine native has one base `ShootVertRecoil(0.1)` in block 1;
- the four tier-local slots map to repeated-item blocks 2, 4, 6, and 8;
- FOV 72 produces `0.06, 0.14, 0.14, 0.14, 0.14`;
- FOV 82 produces `0.033, 0.14, 0.14, 0.14, 0.14`.

For the five pistol groups, native already has five recoil calls across blocks 1, 2, 4, 6, and 8. The released camera handlers change only the active base calls:

- FOV 72: Desert Eagle `0.015`, Magnum `0.017`, M9 `0.015`, McCall `0.015`; Colt is unchanged.
- FOV 82: Desert Eagle `0.008`, Magnum `0.010`, M9 `0.015`, McCall `0.015`, Colt `0.015`.

Commented tier-recoil lines remain excluded.

Camera FOV and Better Upgrading can be selected together. Candidate construction deterministically applies upgrading before camera FOV, and the FOV base-recoil edit accepts either the pristine or verified upgraded pistol tail while preserving that tail.

The implementation accounts for 45 active released writes at FOV 72 and 46 at FOV 82. Both options are candidate-ready and still need disposable native builds.

## Hardened preset evidence

The accepted preset-v5 comparison is read-only and keeps unknown structure fail-closed.

### Zombie size

Normal size matches native. Each non-default size differs in exactly four members:

- `data/presets/infectedai.pre`;
- `data/presets/infectedai_pre.def`;
- `data/presets/zombieai.pre`;
- `data/presets/zombieai_pre.def`.

Every classified difference is a `m_ForcedBodyScaleMin` or `m_ForcedBodyScaleMax` value change, and all four members are semantically complete apart from layout/trailing active comments.

Linux does not copy the preset files. It validates the exact native Min/Max value sequences using occurrence counts and SHA-256 digests, then changes only those named call arguments to the selected released constant. This preserves proprietary native/preset value vectors outside Git.

The four non-default modes are candidate-ready; normal is the pristine baseline.

### Forced spawn

Default spawn matches native. Non-default variants now expose large semantic sets of AI-preset identifier replacements in `aispawnbox_pre.def`. Those identifiers are provenance-sensitive and no public-safe algorithmic transform has yet been proven, so forced spawn remains unready rather than copying the preset content.

### Weather/time

Vanilla matches native. Non-default variants still contain unresolved behavior in `logic_script.scr` and/or `weather.scr`, even where ambient named values are understood. They remain unready.

## Linux core and transaction safety

The Python core provides:

- native ELF/game-root validation;
- strict ZIP validation with CRC, unsafe-path, and duplicate checks;
- safe extraction/rebuild helpers;
- pristine backup creation without silent overwrite;
- validated atomic candidate installation and restore primitives;
- in-memory candidate building from a validated source archive;
- semantic XML, named-call, named-block, loot, intro, reverb, Deeper Pockets, noclip, AI, firearm-upgrading, firearm-POV, camera-FOV, and zombie-size transforms;
- one-choice conflict validation;
- deterministic option interaction ordering where required;
- deterministic JSON CLI validation;
- read-only native, preset, research, source-map, and FOV-recoil audits.

Linux patching must start from the validated installed archive or a verified pristine backup derived from it. The inherited repository `Data0.pak` is never a Linux patch source or install payload.

A failed candidate build or validation must leave the live archive unchanged. The installed game has not yet been modified by the Linux port.

## Validation evidence and next gates

Accepted evidence is scoped to the code state that produced it:

- the earlier 15-option catalog passed individual and combined native disposable candidates;
- the repeated-item fix checkout passed the then-current full suite and the following physical retry passed all 20 individual candidates, all six maximal compatible combinations, and conflict rejection;
- source-map-v2 supplied complete 744-target firearm reconstruction evidence;
- preset-v5 supplied durable hardened preset evidence;
- the corrected FOV-recoil audit supplied durable repeated-block recoil evidence for all 13 requested groups;
- focused local synthetic checks pass for the newly added FOV and zombie-size transforms;
- no GitHub Actions were used.

Next physical gates:

1. run `git diff --check`, the full unit suite, and Python compilation on the current branch;
2. build disposable native candidates for the six newly added options;
3. validate camera FOV with Better Upgrading and representative POV combinations, plus one maximal compatible candidate containing a zombie-size choice;
4. verify the installed Data0 hash is unchanged before and after;
5. only after new candidates pass, review pristine backup/restore and atomic live replacement on the QA installation;
6. finish unresolved forced-spawn, hard-AI, and weather/time parity before release work;
7. add and validate the Linux-native GUI and packaging.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports should be removed after replacement evidence is accepted. Current evidence, unresolved diagnostics, pristine backups, hashes, provenance/licensing material, authentic user data, unrelated work, and Git history must be preserved.

The accepted preset-v5 and corrected FOV-recoil reports supersede their older preset/FOV audit generations. The source-map-v2 evidence remains current while firearm parity work is still being completed.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
