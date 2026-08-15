# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Stable branch: `main`
- Active branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux feature-parity port of the released DIRUE behavior. New gameplay tweaks remain deferred until parity is implemented and validated.

## Verified native Linux baseline

A native Linux Steam installation has been validated with:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is accepted baseline evidence, not a permanent compatibility requirement.

A physical read-only parity audit verified the native prior states used by the direct definitions, including default-level values, sunflare variables, all five Deeper Pockets skills, Improved Loot blocks, intro statement identity, and 52 active reverb preset/mix calls. The audit left the native archive byte-for-byte unchanged.

Raw local reports, machine paths, and copied game content are not committed to Git.

## Ready semantic options

The current ready candidate catalog contains 15 options:

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

The latest physical disposable-candidate run built every option individually against the native archive and all 15 passed validation with 3060 entries. A combined candidate containing all 15 also passed with 3060 entries. The installed game archive remained unchanged; the candidate files existed only in temporary storage.

The earlier Skip Intro failure was caused by assuming the native `File("Intro_720p", ...)` call had no later arguments. The matcher now identifies the first quoted argument while preserving later arguments, and the corrected option has passed native candidate validation.

## Vehicle noclip

The released AHK edits the car and old-boat physics files only; truck edits are commented out.

Block-aware native evidence maps the released car and old-boat edits to these named blocks in each file:

- `ContactParams("SimpleObjects")`
- `ContactParams("NonODEObjects")`

Linux changes each block's single `Ignore(0)` call to `Ignore(1)` and leaves Terrain, ODEObjects, Water, and truck behavior unchanged. Historical line numbers were used only to establish the released behavior and are not runtime patch targets.

`noclip_vehicles` has passed native disposable-candidate validation.

## Headshot-only AI

The inherited `ai_Headshot.zip` differs from native in 20 represented AI files. The previous read-only preset audit classified all 20 differences as completely explained by named `ParamFloat`/`ParamBool` values.

The Linux definition therefore applies those named semantic changes directly and does not copy preset file contents. `headshot_only_ai` has passed native disposable-candidate validation.

## Firearm parity status

`DIRUE.ahk` remains the behavioral source for Better Firearms POV, FOV-coupled sway/recoil behavior, and Better Firearms Upgrading.

The first full source-map report found all seven required released handler sections with no missing sections and produced 744 active source targets. It confirmed that historical AHK line positions are useful one-time provenance evidence but cannot be used as runtime patch targets: many positions land on braces, placeholders, or neighboring calls in pristine native data.

The read-only source mapper has therefore been strengthened to report, for every target:

- the compact native block path at the historical position;
- nearest same-call native candidates across named firearm items;
- per-call ordinal and native prior arguments;
- research-only line distance;
- for upgrading `ShotTime`/`ReloadTime` insertions, nearby `UpgradeLevel(...)` anchors.

`UpgradeLevel` is included only as a research anchor. The intended runtime model remains named `Item` + semantic call/sequence + accepted prior state + exact match count. No runtime firearm definition may depend on historical line numbers.

The enriched mapper still requires one physical read-only execution before POV/upgrading definitions can be completed.

## Preset-backed options

The accepted preset comparison currently establishes:

- normal AI matches the represented native AI tree;
- one-hit AI differs in two files and exposes `ParamBool("one_shot", 0 -> 1)` in both, but the previous strict structural classifier still reported additional unexplained text difference;
- hard AI differs in 57 files and remains incomplete;
- headshot-only AI is fully represented semantically and is implemented;
- default spawns match native, while forced-spawn variants each change one target file and remain structurally incomplete;
- vanilla weather matches native, while non-default weather/time variants still contain unresolved structure;
- zombie-size variants remain structurally incomplete or contain unresolved native-target differences.

The preset audit has now gained two additional conservative classifications for the next read:

1. recognized value differences plus indentation/blank/trailing whitespace only;
2. the same plus differing trailing comments on active code.

Fully commented-out lines remain significant, comments are not globally discarded, and unknown directives remain incomplete. This is intended to distinguish harmless preset formatting/annotation noise from behavior-changing structure without copying preset contents into Git.

One-hit, hard, forced-spawn, weather/time, and zombie-size variants remain unready until the complete released behavior is explained.

## Linux core and transaction safety

The Python core currently provides:

- native ELF/game-root validation;
- strict ZIP validation with CRC, unsafe-path and duplicate checks;
- safe extraction/rebuild helpers;
- pristine backup creation without silent overwrite;
- validated atomic candidate installation and restore;
- in-memory candidate building from the validated source archive;
- semantic XML, call, named-block, loot, intro, reverb, Deeper Pockets, noclip, and AI transformations;
- deterministic CLI validation;
- read-only native, preset, research, and source-map audits.

Linux patching must always start from the user's validated installed archive or a verified pristine backup derived from it. The inherited repository `Data0.pak` must never be used as the Linux patch source or install payload.

A failed candidate build or validation must leave the live archive unchanged. Live replacement remains gated behind validated pristine backup/recovery and atomic install testing.

## Validation evidence

Verified evidence is kept scoped to the code state that produced it:

- the initial physical parity run passed the then-current 44-test suite and left native Data0 unchanged;
- the latest native candidate run passed all 15 ready options individually and as one combined candidate;
- the current source-map enrichment passed five focused synthetic mapping tests;
- the current preset classifier passed nine focused synthetic/read-only tests;
- earlier patch-engine, archive, game, definition, audit, candidate, noclip, headshot, intro, and preset work passed focused tests when introduced;
- no GitHub Actions were used.

The latest audit-only commits still require the full repository suite and compilation on the physical checkout. Candidate behavior itself has not changed since the successful 15-option native run.

The installed Steam game has still not been modified by the Linux port.

## Current gates

1. Run the current full repository test suite, compilation, and whitespace checks on the physical checkout.
2. Run the enriched read-only `audit-source-map` against native Data0 and the tracked released AHK source.
3. Run the enriched read-only preset comparison to classify formatting/annotation-only residual differences.
4. Convert the resulting firearm evidence to semantic per-item/per-tier POV, sway/recoil, and upgrading definitions without line-number runtime targeting.
5. Promote additional preset-backed modes only where the entire released behavior is accounted for.
6. Run disposable native candidate validation for every newly completed option.
7. Review and test pristine backup/restore and atomic replacement on the QA installation before the first live game mutation.
8. Finish all released Milestone-1 behavior, add the Linux-native GUI, and package only after functional validation.

GitHub Issues are currently disabled in this repository; unresolved work remains tracked here instead of changing repository settings.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports must be removed from temporary and user-facing QA locations once replacement evidence is accepted, while current evidence, unresolved diagnostics, pristine backups, hashes, provenance material, and unrelated work are preserved.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
