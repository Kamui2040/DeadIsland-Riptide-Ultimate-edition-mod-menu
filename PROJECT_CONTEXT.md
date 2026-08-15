# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Stable branch: `main`
- Active branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. New gameplay tweaks remain deferred until released parity is implemented and validated.

## Verified native Linux baseline

Accepted physical native-Linux evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a permanent compatibility requirement. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Candidate catalog

The catalog contains 27 semantic non-default options.

Twenty-six options pass disposable native candidate construction against the accepted 3060-entry baseline. Validated families include direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, vehicle noclip, one-hit/headshot-only AI, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, and four non-default zombie-size modes.

Hard AI is the twenty-seventh option and is candidate-ready. Hardened preset-v5 evidence contains 209 `ParamFloat` changes across all 57 differing members. The sanitized structural audit proves the formerly suspicious custom vessel member has identical non-value structure, so no hidden structural edit remains. The implementation uses only named-call value edits with accepted prior values and an audited-table digest.

Default camera FOV 62.5, normal zombie size, and normal AI are pristine-baseline states and are represented by absence of a non-default patch.

Choice groups fail closed on conflicting selections: one-hit/Hard/headshot-only AI, the three Better Firearms POV variants, camera FOV 72/82, and the four non-default zombie-size variants.

The latest accepted native candidate run also passed FOV 72/82 with Better Upgrading in reverse selection order, FOV 72/82 with matching POV variants, one maximal compatible candidate, and camera-FOV/zombie-size conflict rejection. Every candidate retained 3060 archive entries.

## Firearm reconstruction

The accepted source-map evidence accounts for 744 active released firearm targets. Runtime transforms use contiguous repeated same-name `Item(...)` groups, complete call sequences, `UpgradeLevel(0,0,1,1,2,2,3,3)` marker validation, semantic insertions, and CRLF preservation. Historical line numbers are never runtime targets.

Better Firearms Upgrading accounts for all 157 active targets: 58 existing-call changes plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Better Firearms POV plus matching sway accounts for 177/177 active targets at FOV 62 and 205/205 at FOV 72 and 82.

The corrected recoil audit verifies the camera-FOV repeated-block mapping. For the seven shotgun families plus CrowdPleaser, native block 1 contains the base recoil and blocks 2/4/6/8 are the released tier-recoil insertion slots. Camera FOV 72/82 native candidates and their material interactions pass.

## AI and preset-backed controls

Normal AI is baseline. One-hit and headshot-only AI are native-candidate validated. Hard AI is candidate-ready as described above; a native disposable candidate remains the validation gate before promotion.

Zombie size is complete and native-candidate validated. Linux changes only `m_ForcedBodyScaleMin`/`m_ForcedBodyScaleMax` arguments after verifying occurrence counts and baseline value-sequence hashes; no preset file or native value vector is copied into Git.

### Forced spawn

Default matches native. Each non-default preset changes active `m_AIPresets` values. The accepted sanitized audit shows each mode converges on one desired whole-list value across almost all 165 calls.

Exact same-member native donors exist for Suicider and bandits-with-guns only. Butcher, Ram, Bloater, Thug, and bandits-with-melee have no donor in the audited `aispawnbox_pre.def`. Their literal identifier lists remain provenance-sensitive and are not embedded in source.

A second read-only detail audit now searches the entire pristine Data0 for exact quoted desired-list donors and emits only value digests, safe member paths, and counts. Forced spawn remains unresolved until a complete public-safe derivation is proven.

### Weather/time

Vanilla matches native. The first sanitized audit maps the remaining non-value structure precisely:

- rain/storm variants insert a recognized `set("f_game_weather", ...)` call in `logic_script.scr`;
- day variants preserve a commented `f_weather_interior` site, while night variants activate it;
- night variants activate the native-commented `time = ...` and `Set("f_game_time", ...)` sites in `weather.scr`;
- day rain/storm leave `weather.scr` text unchanged.

Hardened preset-v5 also proves the ambient behavior: normal night uses `f_engine_envprobe_factor -> 0.01`; darker night uses `0.0099` plus `f_lighting_indirect_factor 0.45 -> 0.05`; day rain/storm do not change those ambient values.

The new detail audit emits only the whitelisted values for these recognized sites plus their active/commented state. Weather/time remains research until those exact constants are physically collected and a complete semantic transform is built.

## Transaction safety and native transaction QA

The transaction path provides strict ZIP validation, pristine backup preservation, source-hash binding, candidate/live/backup entry-count checks, exact candidate-hash binding, same-directory temporary writes, a second live-hash check immediately before `os.replace`, installed-hash verification, and expected-backup verification before restore.

Native transaction QA passed. The physical run created and retained a pristine backup, installed a validated `reduce_sprint_stamina` candidate atomically, verified the installed candidate hash, restored the backup atomically, and verified the live archive returned exactly to the accepted 3060-entry baseline.

The retained pristine backup is recovery material and must not be cleaned up or overwritten. The live game is currently restored to the exact accepted pristine Data0. The Linux port has therefore performed one controlled live mutation for transaction QA, not a retained gameplay installation.

The inherited repository `Data0.pak` remains forbidden as a Linux patch source or install payload.

## Validation evidence

Accepted evidence is scoped to the code state that produced it:

- 26 catalog options pass native disposable candidate construction;
- material FOV/Upgrading/POV interactions and a maximal compatible candidate pass;
- source-map evidence supplies complete firearm reconstruction data;
- hardened preset-v5 supplies Hard-AI/zombie-size value behavior and remaining preset boundaries;
- corrected FOV-recoil evidence supplies repeated-block camera-recoil mapping;
- sanitized unresolved-preset-v1 proves Hard AI has no hidden structural delta and maps forced-spawn/weather structure without exposing proprietary lists;
- a physical checkout at the preceding transaction/documentation state passed 137/137 unit tests;
- native backup/install/restore transaction QA passes with exact-original recovery;
- Hard AI and unresolved-detail additions have focused synthetic coverage but still need the next full physical suite/candidate audit;
- no GitHub Actions were used.

## Remaining gates

1. Run the full suite/compile on the current branch and a disposable native candidate for `hard_ai`, including difficulty conflict rejection.
2. Run the new read-only unresolved-detail audit to collect exact whitelisted weather constants and global exact forced-spawn donors.
3. Promote Hard AI if its native candidate passes.
4. Implement and native-candidate validate weather/time once the detail audit proves all exact constants and preconditions.
5. Finish forced-spawn only if every mode can be derived public-safely without embedding proprietary identifier lists.
6. Resolve the upstream unconditional `game.ini` / `menumain_pc.xui` replacement provenance/necessity question.
7. Then perform bounded native gameplay/visual QA using the validated transaction/recovery path and add the Linux-native GUI/packaging.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports should be removed after replacement evidence is accepted. Current evidence, unresolved diagnostics, the validated pristine backup, hashes, provenance/licensing material, authentic user data, unrelated work, and Git history must be preserved.

Candidate-v5, preset-v5, FOV-recoil-v2, source-map-v2, transaction-QA-v1, and unresolved-preset-v1 remain current evidence. The next unresolved-detail report may supersede only the research questions it explicitly answers; it does not replace preset-v5 or the validated pristine backup.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
