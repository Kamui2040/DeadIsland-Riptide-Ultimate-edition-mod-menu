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

The catalog contains **37 semantic non-default options**.

Twenty-seven options pass disposable native candidate construction against the accepted 3060-entry baseline. Validated families include direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, vehicle noclip, One Hit / Hard / Headshot Only AI, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, and four non-default zombie-size modes.

Ten additional options are candidate-ready from accepted native read-only evidence and focused semantic tests:

- all eight non-default weather/time choices;
- forced Suiciders;
- forced bandits with guns.

Default camera FOV 62.5, normal zombie size, normal AI, default spawns, and vanilla weather/time are pristine-baseline states represented by absence of a non-default patch.

Choice groups fail closed on conflicting selections: One Hit / Hard / Headshot Only AI, the three Better Firearms POV variants, camera FOV 72/82, four non-default zombie sizes, eight non-default weather/time modes, and the two implemented forced-spawn modes.

## Firearm reconstruction

Accepted source-map evidence accounts for 744 active released firearm targets. Runtime transforms use contiguous repeated same-name `Item(...)` groups, complete call sequences, `UpgradeLevel(0,0,1,1,2,2,3,3)` marker validation, semantic insertions, and CRLF preservation. Historical line numbers are never runtime targets.

Better Firearms Upgrading accounts for all 157 active targets: 58 existing-call changes plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Better Firearms POV plus matching sway accounts for 177/177 active targets at FOV 62 and 205/205 at FOV 72 and 82.

The corrected recoil audit verifies the camera-FOV repeated-block mapping. For seven shotgun families plus CrowdPleaser, native block 1 contains base recoil and blocks 2/4/6/8 are the released tier-recoil insertion slots. Camera FOV 72/82 candidates and material FOV/Upgrading/POV interactions pass.

## Preset-backed controls

### AI difficulty

Normal is baseline. One Hit, Hard, and Headshot Only are native-candidate validated and mutually exclusive. Hard is reconstructed as 209 named `ParamFloat` edits across 57 members and its native candidate changed all 57 intended members while retaining 3060 entries.

### Zombie size

Complete and native-candidate validated. Linux changes only `m_ForcedBodyScaleMin` / `m_ForcedBodyScaleMax` after validating occurrence counts and baseline value-sequence hashes. No preset file or native value vector is copied into Git.

### Forced spawn

Default matches native. Every non-default preset changes active `m_AIPresets` values in a 165-call vector.

Accepted sanitized evidence proves exact pristine donors exist for **Suicider** and **bandits with guns** only. The private native probe records the pristine 165-value vector SHA-256 `f162dabf233daab2954daf124a673d8beaca2ef92ead2620e9606b00a2dfaebf` without exposing any identifier list.

The public-safe runtime definitions therefore:

- validate exactly 165 active `m_AIPresets` calls and the complete pristine vector digest;
- use native donor ordinal 6 for Suicider and change the other 164 calls;
- use native donor ordinal 119 for armed bandits, preserve ordinals 60 and 119, and change the other 163 calls;
- validate the donor value by SHA-256 before replacement;
- replace only quoted value spans and preserve layout/comments.

These two modes are **candidate-ready**. Butcher, Ram, Bloater, Thug, and bandits with melee have no exact desired-value donor anywhere in the audited native Data0. Their literal identifier lists remain provenance-sensitive and are not embedded in source, so those five choices remain unresolved.

### Weather/time

Vanilla matches native. The accepted structural/detail/probe evidence now proves the full behavior of all eight non-default released choices:

- Rain uses `f_game_weather = 0.8`; Storm uses `1.0`;
- day Rain/Storm insert a commented `f_weather_interior = 0.1` override and leave native time comments untouched;
- ordinary Just Night / Rain Night / Storm Night use active `f_weather_interior = 0.3`;
- Just Night (Darker) uses active `f_weather_interior = 1.0`;
- darker Rain/Storm keep `f_weather_interior = 0.3` commented;
- all night variants activate the native-commented `float time = TIME * 0.1` site as `float time = TIME * 0.0` and change `f_game_time` scale `24.0 -> 8.0`;
- ordinary night sets `f_engine_envprobe_factor 1.0 -> 0.01`;
- darker night sets `f_engine_envprobe_factor 1.0 -> 0.0099` and `f_lighting_indirect_factor 0.45 -> 0.05`.

Linux inserts the logic overrides at named WEATHER-section/interior-calculation anchors rather than historical line numbers, validates the exact native-commented time statements before activation, preserves their trailing explanatory comment, and uses existing strict `VarFloat` value checks for ambient changes.

All eight weather/time modes are **candidate-ready** and mutually exclusive. Native disposable candidate validation is the next gate.

## Transaction safety and native transaction QA

The transaction path provides strict ZIP validation, pristine backup preservation, source-hash binding, candidate/live/backup entry-count checks, exact candidate-hash binding, same-directory temporary writes, a second live-hash check immediately before `os.replace`, installed-hash verification, and expected-backup verification before restore.

Native transaction QA passed. A validated `reduce_sprint_stamina` candidate was atomically installed, its live hash matched exactly, and the retained pristine backup restored the exact original 3060-entry baseline. The live game is pristine after that test.

The retained pristine backup is recovery material and must not be cleaned up or overwritten. The inherited repository `Data0.pak` remains forbidden as a Linux patch source or install payload.

## Validation evidence

Accepted evidence is scoped to the code state that produced it:

- 27 current catalog options pass native disposable candidate construction;
- material FOV/Upgrading/POV interactions and a maximal compatible candidate pass;
- source-map-v2 supplies complete firearm reconstruction data;
- preset-v5 supplies Hard-AI/zombie-size value behavior and preset boundaries;
- FOV-recoil-v2 supplies repeated-block recoil mapping;
- unresolved-preset-v1 proves Hard AI has no hidden structure and maps weather/spawn structure;
- unresolved-detail-v1 proves only Suicider and armed-bandit forced-spawn values have exact pristine donors and confirms ambient weather values;
- weather-probe-v1 supplies the full native spawn-vector digest plus the final whitelisted weather/time statement arguments;
- transaction-QA-v1 passes with exact-original recovery;
- the eight weather and two donor-backed spawn implementations have focused synthetic/native-shape regression coverage but still require the next physical full suite and disposable candidates;
- no GitHub Actions were used.

## Remaining gates

1. Run the full suite/compile on the current branch.
2. Native-candidate validate all eight weather/time modes and both donor-backed forced-spawn modes, their choice-conflict rejection, and one material maximal compatible combination.
3. Keep the five no-donor forced-spawn choices unresolved unless a public-safe derivation is found without embedding proprietary identifier lists.
4. Resolve the upstream unconditional `game.ini` / `menumain_pc.xui` replacement provenance/necessity question.
5. Perform bounded native gameplay/visual QA through the validated transaction/recovery path.
6. Add and validate the Linux-native GUI and packaging when released parity is complete enough to expose safely.

## Cleanup and publication

Cleanup is continuous. Superseded QA generations are removed only after replacement evidence is accepted. Current candidate-v5, Hard-v1, preset-v5, FOV-recoil-v2, source-map-v2, native baseline, transaction-QA-v1, unresolved-preset-v1, unresolved-detail-v1, and weather-probe-v1 evidence remain current until their questions are fully promoted into native candidate evidence. The pristine backup is retained recovery material.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
