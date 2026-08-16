# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Stable branch: `main`
- Active branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. New gameplay tweaks remain deferred until released parity is implemented and validated.

## Verified native Linux baseline

Accepted physical evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a permanent compatibility requirement. The current GUI application layer intentionally uses it as the only first-backup compatibility baseline until additional native baselines are independently validated. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Candidate catalog

The catalog contains **38 semantic non-default options**, and all 38 pass disposable native candidate construction against the accepted 3060-entry baseline.

Native-validated families include direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, vehicle noclip, One Hit / Hard / Headshot Only AI, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, four non-default zombie-size modes, all eight non-default weather/time choices, forced Suiciders, forced bandits with guns, and forced bandits with melee.

Default camera FOV 62.5, normal zombie size, normal AI, default spawns, and vanilla weather/time are pristine-baseline states represented by absence of a non-default patch.

Choice groups fail closed on conflicting selections: One Hit / Hard / Headshot Only AI, the three Better Firearms POV variants, camera FOV 72/82, four non-default zombie sizes, eight non-default weather/time modes, and the three implemented forced-spawn modes.

A material maximal compatible candidate including Hard AI, Better Firearms Upgrading/POV82, camera FOV82, supersize zombies, armed-bandit spawn forcing, darker storm night, and the compatible direct options also passes while retaining 3060 entries.

## Firearm reconstruction

Accepted source-map evidence accounts for 744 active released firearm targets. Runtime transforms use contiguous repeated same-name `Item(...)` groups, complete call sequences, `UpgradeLevel(0,0,1,1,2,2,3,3)` marker validation, semantic insertions, and CRLF preservation. Historical line numbers are never runtime targets.

Better Firearms Upgrading accounts for all 157 active targets: 58 existing-call changes plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Better Firearms POV plus matching sway accounts for 177/177 active targets at FOV 62 and 205/205 at FOV 72 and 82.

Corrected recoil evidence maps the four authored shotgun/Crowd tier calls to blocks 2/4/6/8 of each eight-block item group. Camera FOV 72/82 candidates and material FOV/Upgrading/POV interactions pass.

## Preset-backed controls

### AI difficulty

Normal is baseline. One Hit, Hard, and Headshot Only are native-candidate validated and mutually exclusive. Hard is reconstructed as 209 named `ParamFloat` edits across 57 members and its native candidate changed all 57 intended members while retaining 3060 entries.

### Zombie size

Complete and native-candidate validated. Linux changes only `m_ForcedBodyScaleMin` / `m_ForcedBodyScaleMax` after validating occurrence counts and baseline value-sequence hashes. No preset file or native value vector is copied into Git.

### Forced spawn

Default matches native. Every non-default preset changes active `m_AIPresets` values in a 165-call vector.

Accepted sanitized evidence proves exact pristine donors exist for **Suicider** and **bandits with guns** only. Those runtime definitions validate exactly 165 active calls and the complete pristine-vector digest, validate the selected donor value by SHA-256, replace only quoted value spans, and preserve layout/comments.

- Suicider uses native donor ordinal 6, preserves ordinal 6, and changes the other 164 calls. **Native-validated.**
- Armed bandits use native donor ordinal 119, preserve ordinals 60 and 119, and change the other 163 calls. **Native-validated.**

Accepted sanitized reconstruction evidence proves **bandits with melee** can be derived entirely from the user's pristine vector without embedding its game-derived target identifier. Runtime starts from native ordinal 40, validates that source by SHA-256, copies six whole alphanumeric tokens from audited positions within native ordinal 37, validates the reconstructed target SHA-256, preserves ordinal 60, and replaces the other 164 quoted values. Separators/punctuation are inherited from the pristine base identifier and cannot be rewritten by the recipe. Its native disposable candidate retained 3060 entries, changed only `data/presets/aispawnbox_pre.def`, changed exactly 164 of 165 active spawn calls, preserved ordinal 60, and rejected combination with either other implemented forced-spawn mode. **Native-validated.**

Butcher, Ram, Bloater, and Thug remain a hard provenance boundary. Accepted sanitized audits establish that each preserves ordinal 60 and changes the other 164 calls, but no acceptable whole-token reconstruction exists from the pristine 165-value spawn vector, from any of the 1,573 quoted strings in native `aispawnbox_pre.def`, or from the bounded six-member native AI/preset source set (`aispawnbox_pre.def`, `zombieai.pre`, `zombieai_pre.def`, `infectedai.pre`, `infectedai_pre.def`, `bestiary.scr`). The project will not widen this into arbitrary whole-archive string assembly or character-level encoding. Those four choices remain unresolved unless new provenance/rights evidence or a comparably narrow semantic derivation appears.

### Weather/time

Vanilla matches native. Accepted structural, ambient, and private value-probe evidence established the full behavior of all eight non-default released choices. Linux reconstructs them semantically using named WEATHER-section/interior anchors, exact native-commented time priors, and strict named `VarFloat` value checks.

All eight non-default weather/time choices now pass native disposable candidate construction with the expected member scopes. The native regression also proved that semantic anchor matching must tolerate the observed blank line between the two WEATHER declarations without weakening the named/order preconditions.

## Upstream unconditional replacements

The Windows script unconditionally copied bundled replacements over `data/game.ini` and `data/menu/scr/menumain_pc.xui`. A sanitized read-only comparison against the accepted native baseline closes their Linux provenance/necessity gate:

- `game.ini` has the same 25 parsed calls in native and replacement form, with no native-only or replacement-only call identities; the only changed call is active `GameName#1`;
- `menumain_pc.xui` has no native-only component, exactly one replacement-only component (`MyText:T_Mylogo`), and becomes structurally equivalent to native after removing that component; no existing component property differs independently of the inserted child.

The replacement files therefore serve upstream branding/cosmetic behavior rather than released gameplay behavior. The Linux runtime and packaging will **not** copy or redistribute either replacement. The inherited files remain provenance-sensitive historical upstream material and are not treated as Linux payloads.

## Native application / GUI

A GUI-independent application service now wraps the validated transaction path. It validates selections against the exact ready catalog and exclusivity groups, refuses a first backup from an unknown Data0 hash, creates the retained pristine backup only from the currently validated compatibility baseline, builds candidates in temporary storage, installs only over the exact candidate source hash, and requires pristine restore before a different selection can be applied over a DIRUE-modified live archive.

The initial PySide6 GUI is present behind the optional `gui` dependency and `dirue-gui` entry point. Its metadata accounts for all 38 ready options exactly once. The four unresolved spawn choices remain visible but disabled. Qt code delegates validation/build/install/restore to the GUI-independent application service and asks for explicit confirmation before mutation.

This layer is **source-complete but not yet physically GUI-validated on Bazzite**. GUI launch, widget behavior, optional-dependency installation, and one bounded apply/restore smoke transaction still require physical-machine QA before packaging can be treated as validated.

## Transaction safety and native transaction QA

The transaction path provides strict ZIP validation, pristine backup preservation, source-hash binding, candidate/live/backup entry-count checks, exact candidate-hash binding, same-directory temporary writes, a second live-hash check immediately before `os.replace`, installed-hash verification, and expected-backup verification before restore.

Native transaction QA passed. A validated candidate was atomically installed, its live hash matched exactly, and the retained pristine backup restored the exact original 3060-entry baseline. The live game is pristine after that test.

The retained pristine backup is recovery material and must not be cleaned up or overwritten. The inherited repository `Data0.pak` remains forbidden as a Linux patch source or install payload.

## Validation evidence

Accepted evidence is scoped to the code state that produced it:

- all 38 current catalog options pass native disposable candidate construction;
- all native-tested choice conflicts reject incompatible selections, including the three implemented forced-spawn modes;
- material FOV/Upgrading/POV interactions and a maximal compatible multi-family candidate pass;
- accepted firearm source-map evidence supplies complete firearm reconstruction data;
- hardened preset evidence supplies Hard-AI/zombie-size behavior and preset boundaries;
- corrected recoil evidence supplies repeated-block camera-recoil mapping;
- sanitized unresolved/detail evidence supplies the public-safe spawn donor boundary and weather structure;
- sanitized spawn-recipe evidence proves the melee-bandit target can be reconstructed from native whole tokens;
- sanitized same-member and bounded-AI-source evidence closes further whole-token derivation for Butcher/Ram/Bloater/Thug without widening to arbitrary archive strings;
- private native weather/spawn evidence supplies the pristine spawn-vector digest and final whitelisted weather/time statement arguments;
- sanitized replacement comparison proves the inherited `game.ini` / `menumain_pc.xui` copies are branding/cosmetic only and unnecessary for Linux gameplay parity;
- native transaction evidence passes with exact-original recovery;
- GUI/application source and synthetic tests are present, but physical Bazzite GUI QA has not yet been performed;
- no GitHub Actions were used.

## Remaining gates

1. Treat Butcher, Ram, Bloater, and Thug as intentionally unavailable under the current provenance boundary; do not broaden derivation without materially new provenance/rights evidence.
2. Validate the optional PySide6 GUI/application layer on Bazzite: clean install into an isolated environment, full unit suite, launch/widget smoke test, and one bounded apply/restore transaction with exact-original recovery.
3. Perform bounded native gameplay/visual QA through the validated transaction/recovery path for representative option families.
4. Build reproducible Linux packaging only after GUI/native smoke evidence passes; releases, public binaries, Nexus publication, main integration, and upstream submission remain approval-gated.

## Cleanup and publication

Cleanup is continuous. Superseded failed weather/provenance/catalog-count diagnostics are obsolete after accepted successful evidence. The first spawn-recipe audit remains because it documents the accepted melee derivation. The broader same-member and bounded-AI exploratory audit modules/tests were removed after their accepted negative results closed that research path. Current accepted native-candidate, preset, recoil, source-map, native-baseline, transaction, unresolved/detail, replacement-provenance, spawn-recipe, final negative spawn evidence, and private value-probe evidence remain preserved while relevant. The pristine backup is retained recovery material.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
