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

The current catalog contains 20 semantic options.

### Native disposable-candidate validated

Sixteen options have passed individual native candidate builds against the validated archive:

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
- skip intro videos.

The earlier 15-option catalog also passed one combined native candidate with 3060 entries. One-hit was added later and passed its individual native candidate in the current 20-option validation attempt.

### Candidate-ready, native retry pending

Four firearm options remain candidate-ready but require a native rerun after the repeated-item grouping fix:

- `better_firearm_upgrading`;
- `better_firearm_pov_62`;
- `better_firearm_pov_72`;
- `better_firearm_pov_82`.

One-hit and headshot-only AI are mutually exclusive because they represent choices from one released difficulty dropdown. The three POV variants are likewise mutually exclusive. The latest physical run verified that both conflict groups are rejected before patch application.

## Latest physical candidate attempt

The latest physical checkout reached the expected `linux-port` state and passed the full 106-test suite, `git diff --check`, and Python compilation before native candidate work began.

The 20-option individual candidate pass produced:

- 16 successful individual candidates, each with 3060 entries;
- four failures, all on the firearm options above;
- both mutual-exclusion rejection checks passing;
- no combined candidates, because the script intentionally stopped combination work after individual failures.

All four firearm failures had the same cause: the runtime helper assumed a firearm name identified one `Item(...)` block, while native `inventory_gen.scr` represents a firearm such as `Firearm_ColtGen` as a contiguous group of repeated same-name `Item(...)` blocks. The native research reports had grouped those calls by item name, so the earlier synthetic implementation accidentally modeled the group as one large block.

The fix now treats a contiguous repeated same-name block group as the semantic item scope. It:

- validates that all matching same-name blocks are contiguous and fails closed if another `Item(...)` group intervenes;
- validates complete call sequences across the ordered group;
- validates `UpgradeLevel(0,0,1,1,2,2,3,3)` marker order across the group before tier insertions;
- keeps call-type replacements unique across the whole group;
- preserves CRLF line endings during sequence and call-type replacements.

Focused synthetic tests cover the eight-block layout, marker insertions, unique call replacement, CRLF preservation, interleaved-group rejection, and the actual Colt upgrading definition against the audited native group shape. Native candidate validation of this fix is still pending.

The failed run stopped before the hardened preset-v5 and compact FOV-recoil audits. Those audits still need to be run after the firearm candidate retry succeeds.

## Vehicle noclip

The released AHK modifies only the car and old-boat physics files; truck edits are commented out. Native block-aware evidence maps the released changes to exactly these two named blocks in each file:

- `ContactParams("SimpleObjects")`;
- `ContactParams("NonODEObjects")`.

Linux changes each block's single `Ignore(0)` to `Ignore(1)` and leaves Terrain, ODEObjects, Water, and truck behavior unchanged. Historical line numbers were used only for provenance correlation and are not runtime targets.

## AI difficulty

### Normal

`ai_norm.zip` matches the represented native AI tree, so normal mode requires no transform when building from a pristine base.

### One hit

The accepted preset-v4 comparison found exactly two differing native members, both changing `ParamBool("one_shot", 0 -> 1)` plus non-behavioral trailing annotations/layout. Linux applies those two named value changes directly. The option has now passed a native disposable candidate.

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

The hardened preset-v5 audit still requires physical execution before forced-spawn, weather/time, or zombie-size variants are promoted.

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

Commented-out rifle `ShotTime` lines from the released source remain excluded. Reapplying to a non-pristine tier segment fails closed rather than duplicating calls.

### Better Firearms POV

Each FOV-specific POV definition includes its released coupled sway handler. Source-map accounting matches the accepted report exactly:

- POV 62 + sway 62: 177/177 targets;
- POV 72 + sway 72: 205/205 targets;
- POV 82 + sway 82: 205/205 targets.

The implementation validates complete per-item-group native call sequences. Where the released source changes call type, Linux performs a scoped `HolderOffset -> HandOffset` replacement. Pistol tier offsets are identified by verified call ordinals across the same-name item group rather than by historical source lines. The released Desert Eagle FOV-82 asymmetry is intentionally preserved.

POV remains separate from the camera FOV dropdown, matching released control flow.

## Camera FOV status

Released camera choices are 62 default, 72, and 82.

- 62 writes `CameraDefaultFOV=62.5` only.
- 72 writes `CameraDefaultFOV=72` and active recoil changes for seven shotgun families, CrowdPleaser, Desert Eagle, Magnum, M9, and McCall. Its Colt recoil line is not active.
- 82 writes `CameraDefaultFOV=82`, the shotgun/Crowd recoil changes, and active hip-fire changes for Desert Eagle, Magnum, M9, McCall, and Colt.

The remaining blocker is the exact native five-call `ShootVertRecoil` prior sequence for the shotgun/Crowd targets. The compact read-only `audit-fov-recoil` command reports only the 13 relevant firearm sequences and requires exactly five active recoil calls per item. Its first physical run was skipped because candidate validation failed earlier.

## Other preset-backed controls

- Default spawn preset matches native. Forced-spawn variants remain unready pending the hardened preset audit.
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
- the latest physical checkout passed 106 tests before candidate work;
- the latest candidate attempt passed 16/20 individual options and both conflict-rejection checks, then failed closed on the four firearm options because of repeated same-name item blocks;
- the repeated-item grouping fix and prevention tests passed focused local checks;
- no GitHub Actions were used.

Next physical gates are:

1. run the current full repository test suite, `git diff --check`, and Python compilation;
2. rerun all 20 individual disposable candidates and the six maximal compatible combinations against native Data0;
3. run the hardened preset-v5 comparison;
4. run the compact `audit-fov-recoil` read-only audit;
5. verify Data0 is unchanged before/after;
6. use the recoil priors to finish camera FOV 72/82 semantics;
7. repeat disposable candidate validation for every option added afterward;
8. only then review pristine backup/restore and atomic live replacement on the QA installation;
9. finish remaining released preset-backed behavior, then add the Linux-native GUI and packaging.

GitHub Issues are disabled in this repository, so unresolved work remains tracked in project documentation rather than changing repository settings.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports should be removed once replacement evidence is accepted, while current evidence, unresolved diagnostics, pristine backups, hashes, provenance material, and unrelated work are preserved.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
