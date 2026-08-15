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

The current catalog contains 20 semantic options. The latest physical retry passed all 20 individual disposable candidates against the validated native archive. It also passed all six maximal compatible combinations and both mutual-exclusion rejection checks before moving on to the preset and FOV audits.

The 20 individually validated options are:

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
- `better_firearm_upgrading`;
- `better_firearm_pov_62`;
- `better_firearm_pov_72`;
- `better_firearm_pov_82`.

One-hit and headshot-only AI are mutually exclusive because they represent choices from one released difficulty dropdown. The three POV variants are likewise mutually exclusive. Candidate construction rejects conflicting selections before patch application.

The latest retry's successful candidate JSON remained in temporary storage because a later read-only FOV audit failed and the shell cleanup trap removed the temporary work directory. The terminal control flow still establishes that individual, compatible-combination, and conflict-rejection validation all passed before the subsequent audits started. No live archive was modified.

## Repeated firearm item groups

An earlier 20-option native attempt passed 16 individual candidates and failed only the four firearm options. All four failures had the same cause: the runtime helper assumed a firearm name identified one `Item(...)` block, while native `inventory_gen.scr` represents firearms as contiguous groups of repeated same-name `Item(...)` blocks.

The fix treats that contiguous repeated same-name block group as the semantic item scope. It:

- fails closed if another `Item(...)` group is interleaved;
- validates complete call sequences across the ordered group;
- validates `UpgradeLevel(0,0,1,1,2,2,3,3)` marker order before tier insertions;
- keeps call-type replacements unique across the whole group;
- preserves CRLF line endings.

Prevention tests model the native eight-block layout and the actual Colt upgrading definition. The following physical retry then passed all four firearm candidates as part of the successful 20-option candidate phase.

## Vehicle noclip

The released AHK modifies only the car and old-boat physics files; truck edits are commented out. Native block-aware evidence maps the released changes to exactly these two named blocks in each file:

- `ContactParams("SimpleObjects")`;
- `ContactParams("NonODEObjects")`.

Linux changes each block's single `Ignore(0)` to `Ignore(1)` and leaves Terrain, ODEObjects, Water, and truck behavior unchanged. Historical line numbers were used only for provenance correlation and are not runtime targets.

## AI difficulty

### Normal

`ai_norm.zip` matches the represented native AI tree, so normal mode requires no transform when building from a pristine base.

### One hit

The accepted preset-v4 comparison found exactly two differing native members, both changing `ParamBool("one_shot", 0 -> 1)` plus non-behavioral trailing annotations/layout. Linux applies those two named value changes directly. The option has passed a native disposable candidate.

### Headshot only

The inherited headshot preset differs in 20 represented AI files. All 20 differences are completely represented by audited named `ParamFloat`/`ParamBool` changes. The semantic implementation has passed native disposable-candidate validation.

### Hard

Hard AI differs in 57 represented files. Preset-v4 explains 56 of those differences after conservative layout/trailing-comment normalization, but `data/ai/zombie/vessel_data_preset_custom_31.scr` still contains unresolved structure. Hard mode remains unready; no partial hard-mode transform is exposed.

## Preset audit safety

Preset-v4 exposed a classifier weakness: a masked semantic structure could appear complete even when the semantic-delta extractor had not actually named the changed value. The audit is now hardened so:

- semantic completeness on a differing member requires an actual extracted semantic delta;
- raw `layout_only` and `layout_or_trailing_comment_only` signals never mask values;
- active calls with trailing separators can still be parsed semantically;
- full-line commented code remains significant;
- unknown behavior remains incomplete.

The latest physical retry executed the hardened preset-v5 command successfully, but its report was still temporary when the later FOV audit failed and was therefore cleaned by the shell trap. Preset-v5 must be rerun once to publish durable evidence before new preset-backed options are promoted.

## Firearm source reconstruction

`DIRUE.ahk` remains the behavioral specification. The accepted source-map-v2 report found all seven requested firearm sections with no missing sections and mapped 744 active released targets:

- Better Firearms Upgrading: 157;
- Better Firearms POV 62: 157;
- Better Firearms POV 72: 157;
- Better Firearms POV 82: 157;
- sway fix 62: 20;
- sway fix 72: 48;
- sway fix 82: 48.

Historical line numbers are research-only. Runtime firearm transforms use named item groups, complete accepted prior call sequences, semantic call identity, marker order, and exact-count validation.

### Better Firearms Upgrading

The native upgrade layout is `UpgradeLevel(0,0,1,1,2,2,3,3)` across the repeated same-name item group for each intended firearm. The semantic implementation accounts for all 157 active released targets:

- 58 existing-call value replacements;
- 99 tier-local authored `ShotTime`/`ReloadTime` insertions.

Commented-out rifle `ShotTime` lines from the released source remain excluded. Reapplying to a non-pristine tier segment fails closed rather than duplicating calls. Native disposable candidate validation now passes.

### Better Firearms POV

Each FOV-specific POV definition includes its released coupled sway handler. Source-map accounting matches the accepted report exactly:

- POV 62 + sway 62: 177/177 targets;
- POV 72 + sway 72: 205/205 targets;
- POV 82 + sway 82: 205/205 targets.

The implementation validates complete per-item-group native call sequences. Where the released source changes call type, Linux performs a scoped `HolderOffset -> HandOffset` replacement. Pistol tier offsets are identified by verified call ordinals across the same-name item group rather than by historical source lines. The released Desert Eagle FOV-82 asymmetry is intentionally preserved. All three POV variants now pass native disposable candidate validation.

POV remains separate from the camera FOV dropdown, matching released control flow.

## Camera FOV status

Released camera choices are 62 default, 72, and 82.

- 62 writes `CameraDefaultFOV=62.5` only.
- 72 writes `CameraDefaultFOV=72` and active recoil changes for seven shotgun families, CrowdPleaser, Desert Eagle, Magnum, M9, and McCall. Its Colt recoil line is not active.
- 82 writes `CameraDefaultFOV=82`, the shotgun/Crowd recoil changes, and active hip-fire changes for Desert Eagle, Magnum, M9, McCall, and Colt.

The first compact physical FOV audit exposed an incorrect Linux-port assumption. Native `Firearm_ShotgunShortGen` has one active `ShootVertRecoil` call rather than the five calls written by the released Windows handler. Retained block-aware evidence shows the shotgun/Crowd families have one active base recoil call plus four tier-local sway sites, while the five pistol families already have five native recoil calls across their repeated item group.

The revised read-only `audit-fov-recoil` no longer assumes the Windows five-write shape already exists natively. For each of the 13 relevant firearm groups it validates and reports:

- eight contiguous repeated `Item(...)` blocks;
- `UpgradeLevel(0,0,1,1,2,2,3,3)`;
- each block ordinal and header line;
- active `ShootVertRecoil`, `SwayMaxAngle`, and `ShootMaxAngle` sites with block ordinal, arguments, and line number;
- one recoil plus four sway sites for the seven shotgun families and CrowdPleaser;
- five recoil plus four sway sites for Colt, Magnum, M9, Desert Eagle, and McCall.

Its first physical test checkout stopped inside the synthetic test suite before any native read because `_active_relevant_calls()` did not accept CRLF line endings for indented calls. The parser is now CRLF-safe, and the full repeated-block fixture plus wrong-upgrade and wrong-recoil negative cases pass in focused local checks. The shotgun/Crowd records remain explicitly research-only tier-recoil insertion candidates until the corrected physical audit is collected.

## Other preset-backed controls

- Default spawn preset matches native. Forced-spawn variants remain unready pending durable preset-v5 evidence.
- Vanilla weather matches native. Non-default weather/time variants still contain unresolved script structure.
- Zombie-size presets contain known scale intent, but complete behavior must be reclassified by the hardened audit before implementation.

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
- the earlier native candidate run passed all then-ready 15 options individually and in one combined candidate;
- source-map-v2 supplied complete 744-target firearm research evidence;
- preset-v4 supplied the accepted one-hit result and identified the remaining hard-AI structural blocker;
- the repeated-item fix checkout passed 111 tests, `git diff --check`, and Python compilation;
- that same physical retry passed all 20 individual disposable candidates, all six maximal compatible combinations, and both conflict-rejection checks before continuing;
- the hardened preset-v5 command then completed, but its temporary report was lost when the subsequent FOV audit failed;
- the first compact FOV audit failed closed on its old five-recoil assumption and did not modify Data0;
- the next physical checkout ran 114 tests but stopped with two failures and one error confined to the revised FOV-audit tests because their CRLF fixture exposed an end-of-line parser bug; native Data0 was not reached in that run;
- the FOV call parser is now CRLF-safe, and the complete repeated-block fixture plus intended negative cases pass focused local checks;
- no GitHub Actions were used.

Next physical gates are narrow because candidate behavior has not changed since the successful 20-option phase:

1. run the current full repository test suite, `git diff --check`, and Python compilation;
2. rerun hardened preset-v5 and publish its report;
3. run the corrected compact `audit-fov-recoil` and publish its report;
4. verify Data0 is unchanged before/after;
5. use the repeated-block recoil evidence to finish camera FOV 72/82 semantics without line-number runtime targeting;
6. run disposable native candidates for each FOV option added afterward;
7. only then review pristine backup/restore and atomic live replacement on the QA installation;
8. finish remaining released preset-backed behavior, then add the Linux-native GUI and packaging.

GitHub Issues are disabled in this repository, so unresolved work remains tracked in project documentation rather than changing repository settings.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports should be removed once replacement evidence is accepted, while current evidence, unresolved diagnostics, pristine backups, hashes, provenance material, and unrelated work are preserved.

The obsolete failed 20-option candidate report should be deleted from the physical Downloads folder after the next successful audit-report publication because the following physical retry proved that candidate phase succeeds. The accepted baseline/native evidence and any reports still needed for unresolved parity work must be preserved.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
