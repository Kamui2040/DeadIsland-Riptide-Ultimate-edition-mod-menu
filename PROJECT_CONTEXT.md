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

The catalog contains **27 semantic non-default options**, and all 27 pass disposable native candidate construction against the accepted 3060-entry baseline.

Validated families include direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, vehicle noclip, One Hit / Hard / Headshot Only AI, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, and four non-default zombie-size modes.

Hard AI is reconstructed as 209 named `ParamFloat` edits across 57 members. Sanitized structural evidence proves the formerly suspicious custom vessel member has no non-value structural delta. The native Hard candidate changed all 57 intended members, retained 3060 entries, and conflict rejection passed against both One Hit and Headshot Only.

Default camera FOV 62.5, normal zombie size, and normal AI are pristine-baseline states represented by absence of a non-default patch.

Choice groups fail closed on conflicting selections: One Hit / Hard / Headshot Only AI, the three Better Firearms POV variants, camera FOV 72/82, and the four non-default zombie-size variants.

## Firearm reconstruction

Accepted source-map evidence accounts for 744 active released firearm targets. Runtime transforms use contiguous repeated same-name `Item(...)` groups, complete call sequences, `UpgradeLevel(0,0,1,1,2,2,3,3)` marker validation, semantic insertions, and CRLF preservation. Historical line numbers are never runtime targets.

Better Firearms Upgrading accounts for all 157 active targets: 58 existing-call changes plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Better Firearms POV plus matching sway accounts for 177/177 active targets at FOV 62 and 205/205 at FOV 72 and 82.

The corrected recoil audit verifies the camera-FOV repeated-block mapping. For seven shotgun families plus CrowdPleaser, native block 1 contains base recoil and blocks 2/4/6/8 are the released tier-recoil insertion slots. Camera FOV 72/82 candidates and material FOV/Upgrading/POV interactions pass.

## Preset-backed controls

### AI difficulty

Normal is baseline. One Hit, Hard, and Headshot Only are native-candidate validated and mutually exclusive.

### Zombie size

Complete and native-candidate validated. Linux changes only `m_ForcedBodyScaleMin` / `m_ForcedBodyScaleMax` after validating occurrence counts and baseline value-sequence hashes. No preset file or native value vector is copied into Git.

### Forced spawn

Default matches native. Every non-default preset changes active `m_AIPresets` values across a 165-call vector.

Accepted sanitized evidence proves exact pristine donors exist for **Suicider** and **bandits with guns**. The desired values for Butcher, Ram, Bloater, Thug, and bandits with melee have no exact quoted donor anywhere in the audited native Data0. Their literal identifier lists remain provenance-sensitive and are not embedded in source.

A narrow private-QA probe now records only the SHA-256 of the pristine 165-value vector. Combined with the already accepted desired-value digests and semantic ordinals, that is sufficient to implement the two donor-backed modes without storing their identifier lists.

### Weather/time

Vanilla matches native. Sanitized structural evidence maps the behavior without copying preset scripts:

- rain/storm variants add a recognized `set("f_game_weather", ...)` call in `logic_script.scr`;
- day variants preserve a commented `f_weather_interior` site while night variants activate it;
- night variants activate the native-commented `time = ...` and `Set("f_game_time", ...)` sites in `weather.scr`;
- day rain/storm leave `weather.scr` unchanged;
- ordinary night sets `f_engine_envprobe_factor -> 0.01`;
- darker night sets `f_engine_envprobe_factor -> 0.0099` and `f_lighting_indirect_factor 0.45 -> 0.05`.

The first detail audit proved those ambient values but its simple single-line call parser could not recover the argument tails of the recognized logic/time calls. A new research-only `weather_probe` parser handles nested arguments, comments, and CRLF and emits only those four whitelisted statement arguments plus the spawn-vector digest. Weather/time remains research until that private probe is collected.

## Transaction safety and native transaction QA

The transaction path provides strict ZIP validation, pristine backup preservation, source-hash binding, candidate/live/backup entry-count checks, exact candidate-hash binding, same-directory temporary writes, a second live-hash check immediately before `os.replace`, installed-hash verification, and expected-backup verification before restore.

Native transaction QA passed. A validated `reduce_sprint_stamina` candidate was atomically installed, its live hash matched exactly, and the retained pristine backup restored the exact original 3060-entry baseline. The live game is pristine after that test.

The retained pristine backup is recovery material and must not be cleaned up or overwritten. The inherited repository `Data0.pak` remains forbidden as a Linux patch source or install payload.

## Validation evidence

Accepted evidence is scoped to the code state that produced it:

- all 27 current catalog options pass native disposable candidate construction;
- material FOV/Upgrading/POV interactions and a maximal compatible candidate pass;
- source-map-v2 supplies complete firearm reconstruction data;
- preset-v5 supplies Hard-AI/zombie-size value behavior and preset boundaries;
- FOV-recoil-v2 supplies repeated-block recoil mapping;
- unresolved-preset-v1 proves Hard AI has no hidden structure and maps weather/spawn structure;
- unresolved-detail-v1 proves only Suicider and armed-bandit forced-spawn values have exact pristine donors and confirms all ambient weather values;
- transaction-QA-v1 passes with exact-original recovery;
- the full physical suite passed before Hard/detail candidate collection; the later research-only weather-probe commits have focused synthetic parser coverage and still need the next physical suite;
- no GitHub Actions were used.

## Remaining gates

1. Run the narrow private weather/spawn-vector probe on the pristine native baseline.
2. Implement the eight non-default weather/time choices only after all whitelisted statement arguments are proven.
3. Implement the two donor-backed forced-spawn modes with full-vector digest/ordinal validation; keep the five no-donor modes unresolved unless a public-safe derivation is found.
4. Native-candidate validate any newly implemented weather/spawn choices and material conflicts/interactions.
5. Resolve the upstream unconditional `game.ini` / `menumain_pc.xui` replacement provenance/necessity question.
6. Perform bounded native gameplay/visual QA through the validated transaction/recovery path.
7. Add and validate the Linux-native GUI and packaging when released parity is complete enough to expose safely.

## Cleanup and publication

Cleanup is continuous. Superseded QA generations are removed only after replacement evidence is accepted. Current candidate-v5, Hard-v1, preset-v5, FOV-recoil-v2, source-map-v2, native baseline, transaction-QA-v1, unresolved-preset-v1, and unresolved-detail-v1 evidence remain current. The pristine backup is retained recovery material.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
