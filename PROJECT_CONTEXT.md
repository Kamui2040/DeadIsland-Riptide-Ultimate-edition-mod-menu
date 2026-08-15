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

The catalog contains 26 semantic non-default options. All 26 pass disposable native candidate construction against the accepted 3060-entry baseline.

Validated families include:

- direct movement/stamina/ammo/durability/penetration controls;
- Deeper Pockets, Improved Loot, intro skipping, and reverb removal;
- vehicle noclip;
- one-hit and headshot-only AI;
- Better Firearms Upgrading;
- Better Firearms POV 62/72/82 with matching sway behavior;
- camera FOV 72/82 with released recoil behavior;
- zombie size extra-small, midget, large, and supersize.

Default camera FOV 62.5, normal zombie size, and normal AI are pristine-baseline states and are represented by absence of a non-default patch.

Choice groups fail closed on conflicting selections: one-hit/headshot-only AI, the three Better Firearms POV variants, camera FOV 72/82, and the four non-default zombie-size variants.

The latest native candidate run also passed FOV 72/82 with Better Upgrading in reverse selection order, FOV 72/82 with matching POV variants, one maximal compatible candidate, and camera-FOV/zombie-size conflict rejection. Every candidate retained 3060 archive entries.

## Firearm reconstruction

The accepted source-map evidence accounts for 744 active released firearm targets. Runtime transforms use contiguous repeated same-name `Item(...)` groups, complete call sequences, `UpgradeLevel(0,0,1,1,2,2,3,3)` marker validation, semantic insertions, and CRLF preservation. Historical line numbers are never runtime targets.

Better Firearms Upgrading accounts for all 157 active targets: 58 existing-call changes plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Better Firearms POV plus matching sway accounts for 177/177 active targets at FOV 62 and 205/205 at FOV 72 and 82.

The corrected recoil audit verifies the camera-FOV repeated-block mapping. For the seven shotgun families plus CrowdPleaser, native block 1 contains the base recoil and blocks 2/4/6/8 are the released tier-recoil insertion slots. Camera FOV 72/82 native candidates and their material interactions now pass.

## AI and preset-backed controls

Normal AI is baseline. One-hit and headshot-only AI are native-candidate validated.

Hard AI remains unresolved: hardened preset evidence identifies named semantic changes in all 57 differing members, but `data/ai/zombie/vessel_data_preset_custom_31.scr` still has a non-value structural difference that must be identified before a complete transform is exposed.

Zombie size is complete and native-candidate validated. Linux changes only `m_ForcedBodyScaleMin`/`m_ForcedBodyScaleMax` arguments after verifying occurrence counts and baseline value-sequence hashes; no preset file or native value vector is copied into Git.

Forced-spawn default matches native. Non-default variants are value changes to `m_AIPresets`, but their identifier lists remain provenance-sensitive. A new read-only unresolved-preset audit reports only desired-value digests, changed semantic ordinals, and whether each desired value already exists in pristine native data as a donor. This is intended to prove a public-safe donor-based reconstruction without embedding the lists.

Vanilla weather/time matches native. Non-default variants still contain structural changes in `logic_script.scr` and/or `weather.scr`. The unresolved-preset audit now reports sanitized call/assignment/comment-state structural identities and hashes unknown line shapes while omitting argument values.

## Transaction safety and native transaction QA

The transaction path provides:

- strict ZIP validation with CRC, unsafe-path, and duplicate checks;
- pristine backup creation without silent overwrite;
- same-directory temporary writes followed by atomic replacement;
- source-hash binding between live Data0, pristine backup, and candidate source;
- entry-count checks before installation;
- optional exact candidate-hash binding;
- a second live-hash check immediately before `os.replace`;
- installed-hash verification;
- expected-backup hash verification before restore;
- restore support even if the live archive is missing.

Native transaction QA has now passed. The physical run:

- created and retained a pristine backup;
- verified the backup hash equals the accepted baseline;
- built a `reduce_sprint_stamina` candidate from that verified source;
- atomically installed candidate SHA-256 `c0dbe019243ae9cb1cb64e27aea176e58d6757ce5afe76f84e3a3b2772f1e748`;
- verified the live installed hash exactly matched the candidate;
- atomically restored the pristine backup;
- verified the restored live archive exactly returned to baseline SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991` with 3060 entries.

The retained pristine backup is recovery material and must not be cleaned up or overwritten. The live game is currently restored to the exact accepted pristine Data0. The Linux port has therefore performed one controlled live mutation for transaction QA, not a retained gameplay installation.

The inherited repository `Data0.pak` remains forbidden as a Linux patch source or install payload.

## Validation evidence

Accepted evidence is scoped to the code state that produced it:

- all 26 catalog options pass native disposable candidate construction;
- material FOV/Upgrading/POV interactions and a maximal compatible candidate pass;
- source-map evidence supplies complete firearm reconstruction data;
- hardened preset evidence supplies zombie-size behavior and remaining preset boundaries;
- corrected FOV-recoil evidence supplies repeated-block camera-recoil mapping;
- native backup/install/restore transaction QA passes with exact-original recovery;
- focused synthetic transaction tests cover wrong-live, wrong-backup, wrong-candidate, entry-count drift, missing-live restore, and CLI round-trip behavior;
- no GitHub Actions were used.

## Remaining gates

Repository-side parity work continues before broad gameplay QA:

1. run the sanitized unresolved-preset audit on the native baseline and inherited preset set;
2. use that evidence to finish hard AI if its structural delta is safely reconstructible;
3. use native donor evidence to finish forced-spawn modes if every desired value is derivable without embedding proprietary lists;
4. reconstruct weather/time only where sanitized structural evidence proves complete semantic behavior;
5. native-candidate validate any newly completed options and material interactions;
6. then perform bounded native gameplay/visual QA using the validated transaction/recovery path;
7. add and validate the Linux-native GUI and packaging after released parity is complete enough to expose safely.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports should be removed after replacement evidence is accepted. Current evidence, unresolved diagnostics, the validated pristine backup, hashes, provenance/licensing material, authentic user data, unrelated work, and Git history must be preserved.

The successful candidate-v5 report supersedes older candidate generations. Hardened preset-v5, corrected FOV-recoil-v2, source-map-v2, native baseline evidence, and transaction-QA-v1 remain current evidence for ongoing work.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
