# PROJECT_CONTEXT.md

## Repository

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Default branch: `main`
- Active Linux-port branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

## Current milestone

**Milestone 1: native Linux feature-parity port of the existing DIRUE release.**

Scope is compatibility and faithful behavior. New gameplay tweaks stay deferred until parity is complete and validated.

## Verified native Linux baseline

A native Linux Steam installation has been checked with these results:

- `DeadIslandRiptideGame` is a native Linux ELF executable.
- `<DIRDE_ROOT>/DIR/Data0.pak` is ZIP-compatible.
- Archive entry count: 3060.
- Archive size: 7,932,941 bytes.
- SHA-256: `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

Representative patch targets were present, including `default_levels.xml`, `inventory_gen.scr`, intro movies, weather, and glow scripts.

Result: `NATIVE_DATA0_COMPATIBILITY_BASELINE_PASS`.

The hash is a known baseline, not a permanent requirement.

## Native parity evidence

A physical-machine read-only audit completed successfully on 2026-08-15. The repository's then-current 44-test suite passed first. Native validation, parity inspection, and the first preset comparison completed while `Data0.pak` retained the exact same SHA-256 before and after that run.

That audit verified these native prior states:

- all direct `default_levels.xml` values used by sprint/jump stamina, running with weapons, movement, ammo, door breaking, durability, bullet penetration, and default FOV;
- both sunflare variables at `1.0`;
- all five Deeper Pockets skill files at `desc_params="2;4;6"` and `InventorySize change="2"`;
- the six Improved Loot target blocks and their default color weights;
- one active intro `File` statement whose first quoted argument is `Intro_720p`, while the inspected DI intro/subtitle statements are already commented;
- one active declaration for each reverb directive plus 52 active `ReverbPreset` and 52 active `ReverbWetDryMix` calls.

The first disposable native-candidate report found one fail-closed bug in `skip_intro_videos`: the helper assumed the target `File` call had only one argument. The helper was corrected to identify the call by its first quoted argument and preserve later arguments.

A later uploaded candidate report then exercised all 13 original ready options against the native archive. Every individual candidate passed validation with 3060 entries, including `skip_intro_videos`, and the combined 13-option candidate also passed with 3060 entries. The combined candidate changed only the expected 11 semantic target members.

Raw local audit output, uploaded QA reports, and machine-specific paths are not committed to Git.

## Vehicle noclip evidence

The native car file has five active `Ignore` sites:

- `ContactParams:Terrain` = `0`
- `ContactParams:SimpleObjects` = `0`
- `ContactParams:NonODEObjects` = `0`
- `ContactParams:ODEObjects` = `0`
- `ContactParams:Water` = `1`

The old-boat file has the same five named contact blocks, all at `0`.

The released AHK changes car lines 77 and 91 and old-boat lines 64 and 78. The block-aware native audit maps those historical identities to `ContactParams("SimpleObjects")` and `ContactParams("NonODEObjects")` in both files. Linux therefore patches those two named blocks only, changing their single `Ignore(0)` call to `Ignore(1)` and leaving Terrain, ODEObjects, Water, and the commented-out truck edits unchanged.

Historical line numbers were used once to establish provenance and are not runtime patch targets. `noclip_vehicles` is now in the ready catalog, pending disposable native-candidate validation of the new semantic implementation.

## Firearm evidence

`DIRUE.ahk` remains the behavioral source for the intended firearm values. The native research report groups relevant calls by actual `Item:` block and records line numbers and per-call ordinals for research correlation only.

The latest evidence shows that many active native firearm statements still align with the released AHK's historical target numbers. That is useful for one-time mapping, but line numbers remain forbidden as runtime targets.

Better firearms upgrading is more sensitive because the released AHK writes `ShotTime` and `ReloadTime` into placeholder locations from its bundled working archive. Those locations are not equivalent active calls in the pristine native archive. The Linux port must reconstruct insertion points from named native items and semantic neighboring calls rather than reproduce the placeholder mechanism.

A new read-only `audit-source-map` command parses only the relevant public AHK handler sections and correlates their historical target lines to compact native item/call context. It reports the native item, line classification, and nearest relevant calls without copying native file contents. This is intended to finish POV/upgrading reconstruction on the next physical read.

## Preset-backed options

The latest preset comparison established:

- `ai_norm.zip` matches the represented native AI tree;
- one-hit AI differs in 2 files, with neither complete difference yet explained by the semantic normalizer;
- hard AI differs in 57 files, with only 1 complete difference currently explained;
- headshot-only AI differs in 20 files, and all 20 differences are completely explained by named `ParamFloat`/`ParamBool` values;
- `Default_spawns.zip` matches native, while each forced-spawn variant changes one target file and remains structurally incomplete;
- vanilla weather matches native; non-default weather/time choices still contain unresolved structural differences even where one ambient file is fully semantic;
- every zombie-size preset differs from the native target set in the latest comparison, and those differences remain structurally incomplete.

Headshot-only AI has therefore been converted to a public-safe semantic definition: six non-head health-influence parameters are set to zero across the 19 affected health files, with the audited `one_shot` exception restored from `1` to `0` in its one affected custom vessel file. No preset file content is copied into Git.

One-hit, hard, forced-spawn, weather/time, and zombie-size variants remain unready until their entire behavior can be represented by validated semantic transforms. Provenance-sensitive full replacements remain out of Git.

## Important upstream archive difference

The inherited repository `Data0.pak` is an older, different archive. The Linux port must not use it as an install payload or patch source.

Runtime work must start from the user's validated installed archive or a verified pristine backup derived from it. Candidate changes must be built in temporary storage, validated, and installed atomically.

## Upstream hazards not carried into Linux

`DIRUE.ahk` remains the Milestone-1 behavioral specification, but these implementation details are intentionally not copied:

- patching from the bundled repository `Data0.pak`;
- deleting the live archive before a replacement is validated;
- hard-coded line numbers as the patch mechanism;
- placeholder-based disable paths;
- full-file or directory preset replacement without provenance review;
- AutoHotkey/Win32 helpers and `.exe` processes.

## Implemented Linux core

The Python core under `src/dirue/` contains no newly added proprietary game content and currently provides:

- native Linux game-root validation using the ELF executable;
- ZIP validation with CRC, required-entry, traversal, backslash-path and duplicate-member checks;
- safe temporary extraction and metadata-preserving rebuild;
- pristine backup creation without silent overwrite;
- validated atomic candidate installation and restore;
- in-memory candidate building that refuses source overwrite, unresolved options, duplicate options, and no-op/non-pristine input;
- semantic XML, `VarFloat`, simple call, named call, scoped loot, Deeper Pockets, intro-comment and reverb transforms;
- structured named-block helpers with brace-aware scope validation;
- 13 original native-verified direct options plus native-identified semantic noclip and headshot-only AI, for 15 ready candidate options total;
- deterministic JSON CLI validation;
- `audit-native`, a read-only native parity audit;
- `audit-presets`, a read-only preset comparison with semantic completeness classification;
- `audit-research`, a read-only block-aware firearm/noclip research audit;
- `audit-source-map`, a read-only source-to-native firearm correlation audit.

No audit command extracts, installs, or modifies game content.

## Validation evidence

Validation evidence is kept specific to the code state it tested:

- the first physical read-only audit ran the then-current full 44-test suite successfully before accessing the native game;
- that physical audit proved `Data0.pak` remained byte-for-byte unchanged by hash;
- a later native candidate report records successful individual builds for all 13 original ready options plus a successful combined 13-option candidate, all with 3060 entries;
- earlier feature work passed its focused synthetic suites when introduced;
- the corrected multi-argument intro matcher passed focused synthetic regression checks before its successful native candidate rerun;
- the new noclip/headshot semantic definitions passed 4 focused local tests, including wrong-prior-state rejection;
- the corrected source-map correlation logic passed 2 focused local tests plus Python compilation;
- the newly committed advanced integration tests and the current full repository suite still require execution on the physical checkout;
- packaging previously produced a wheel successfully without network dependencies.

No GitHub Actions were used.

The installed Steam game has still **not been modified by the Linux port**. Native mutation remains a later, separate gate.

GitHub Issues are currently disabled for this repository. An attempt to create a focused firearm-mapping Issue returned HTTP 410, so unresolved work remains tracked here rather than changing repository settings.

## Current gates

1. Run the current full test suite and compilation on the physical checkout.
2. Run disposable native candidates for the two newly ready options (`noclip_vehicles`, `headshot_only_ai`) and a combined 15-option candidate.
3. Run `audit-source-map` against the native archive and tracked AHK source to finish firearm POV/upgrading semantic anchors.
4. Convert the resulting firearm mappings to named item/property definitions; never retain historical line numbers as runtime targets.
5. Continue semantic reconstruction of one-hit, hard, forced-spawn, weather/time, and zombie-size options only where complete preset behavior is explained.
6. Repeat disposable candidate rebuild/validation for every newly completed option before any live write.
7. Review and then test pristine backup/restore and atomic replacement on the QA installation.
8. Reproduce all Milestone-1 gameplay options.
9. Add the Linux-native GUI.
10. Package only after functional validation.

## Publication state

No main integration, release, public binary, Nexus publication, upstream submission, or other external publication has been authorized. `linux-port` remains the active development branch.
