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

The hash is evidence for the audited installation, not a permanent compatibility requirement. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Candidate catalog

The catalog contains **37 semantic non-default options**, and all 37 pass disposable native candidate construction against the accepted 3060-entry baseline.

Validated families include direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, vehicle noclip, One Hit / Hard / Headshot Only AI, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, four non-default zombie-size modes, all eight non-default weather/time choices, forced Suiciders, and forced bandits with guns.

Default camera FOV 62.5, normal zombie size, normal AI, default spawns, and vanilla weather/time are pristine-baseline states represented by absence of a non-default patch.

Choice groups fail closed on conflicting selections: One Hit / Hard / Headshot Only AI, the three Better Firearms POV variants, camera FOV 72/82, four non-default zombie sizes, eight non-default weather/time modes, and the two implemented forced-spawn modes.

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

Accepted sanitized evidence proves exact pristine donors exist for **Suicider** and **bandits with guns** only. The public-safe runtime definitions validate exactly 165 active calls and the complete pristine-vector digest, validate the selected donor value by SHA-256, replace only quoted value spans, and preserve layout/comments.

- Suicider uses native donor ordinal 6, preserves ordinal 6, and changes the other 164 calls.
- Armed bandits use native donor ordinal 119, preserve ordinals 60 and 119, and change the other 163 calls.

Both modes now pass native disposable candidate construction and their exclusivity check passes.

Butcher, Ram, Bloater, Thug, and bandits with melee have no exact desired-value donor anywhere in the audited native Data0. Their literal identifier lists remain provenance-sensitive and are not embedded in source, so those five choices remain unresolved.

### Weather/time

Vanilla matches native. Accepted structural, ambient, and private value-probe evidence established the full behavior of all eight non-default released choices. Linux reconstructs them semantically using named WEATHER-section/interior anchors, exact native-commented time priors, and strict named `VarFloat` value checks.

All eight non-default weather/time choices now pass native disposable candidate construction with the expected member scopes. The native regression also proved that semantic anchor matching must tolerate the observed blank line between the two WEATHER declarations without weakening the named/order preconditions.

## Upstream unconditional replacements

The Windows script unconditionally copied bundled replacements over `data/game.ini` and `data/menu/scr/menumain_pc.xui`. A sanitized read-only comparison against the accepted native baseline closes their Linux provenance/necessity gate:

- `game.ini` has the same 25 parsed calls in native and replacement form, with no native-only or replacement-only call identities; the only changed call is active `GameName#1`;
- `menumain_pc.xui` has no native-only component, exactly one replacement-only component (`MyText:T_Mylogo`), and becomes structurally equivalent to native after removing that component; no existing component property differs independently of the inserted child.

The replacement files therefore serve upstream branding/cosmetic behavior rather than released gameplay behavior. The Linux runtime and packaging will **not** copy or redistribute either replacement. The inherited files remain provenance-sensitive historical upstream material and are not treated as Linux payloads.

## Transaction safety and native transaction QA

The transaction path provides strict ZIP validation, pristine backup preservation, source-hash binding, candidate/live/backup entry-count checks, exact candidate-hash binding, same-directory temporary writes, a second live-hash check immediately before `os.replace`, installed-hash verification, and expected-backup verification before restore.

Native transaction QA passed. A validated candidate was atomically installed, its live hash matched exactly, and the retained pristine backup restored the exact original 3060-entry baseline. The live game is pristine after that test.

The retained pristine backup is recovery material and must not be cleaned up or overwritten. The inherited repository `Data0.pak` remains forbidden as a Linux patch source or install payload.

## Validation evidence

Accepted evidence is scoped to the code state that produced it:

- all 37 current catalog options pass native disposable candidate construction;
- all current choice conflicts tested at the native-candidate layer reject incompatible selections;
- material FOV/Upgrading/POV interactions and a maximal compatible multi-family candidate pass;
- accepted firearm source-map evidence supplies complete firearm reconstruction data;
- hardened preset evidence supplies Hard-AI/zombie-size behavior and preset boundaries;
- corrected recoil evidence supplies repeated-block camera-recoil mapping;
- sanitized unresolved/detail evidence supplies the public-safe spawn donor boundary and weather structure;
- private native weather/spawn evidence supplies the pristine spawn-vector digest and final whitelisted weather/time statement arguments;
- sanitized replacement comparison proves the inherited `game.ini` / `menumain_pc.xui` copies are branding/cosmetic only and unnecessary for Linux gameplay parity;
- native transaction evidence passes with exact-original recovery;
- no GitHub Actions were used.

## Remaining gates

1. Keep the five no-donor forced-spawn choices unresolved unless a public-safe derivation is found without embedding proprietary identifier lists.
2. Perform bounded native gameplay/visual QA through the validated transaction/recovery path.
3. Add and validate the Linux-native GUI and packaging when released parity is complete enough to expose safely.

## Cleanup and publication

Cleanup is continuous. Superseded failed weather/provenance diagnostics are obsolete after accepted successful replacement evidence; current accepted native-candidate, preset, recoil, source-map, native-baseline, transaction, unresolved/detail, replacement-provenance, and private value-probe evidence remain preserved while open questions still depend on them. The pristine backup is retained recovery material.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
