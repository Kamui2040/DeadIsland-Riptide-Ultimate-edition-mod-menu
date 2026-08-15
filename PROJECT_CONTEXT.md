# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Project fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Stable branch: `main`
- Active branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of the released DIRUE behavior. New gameplay tweaks remain deferred until released parity is implemented and validated.

## Verified native Linux baseline

Accepted physical native-Linux evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a permanent compatibility requirement. Read-only audits and disposable candidate work completed so far left the installed archive unchanged.

Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidate archives are not committed to Git.

## Candidate catalog

The catalog contains 26 semantic non-default options. All 26 now pass disposable native candidate construction against the accepted 3060-entry baseline.

The first 20 validated options are:

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
- Better Firearms Upgrading;
- Better Firearms POV 62;
- Better Firearms POV 72;
- Better Firearms POV 82.

The latest native candidate run additionally validated:

- camera FOV 72;
- camera FOV 82;
- zombie size extra-small (`0.3`);
- zombie size midget (`0.6`);
- zombie size large (`2.0`);
- zombie size supersize (`5.0`).

That run also passed:

- camera FOV 72 with Better Firearms Upgrading when supplied in reverse order;
- camera FOV 82 with Better Firearms Upgrading when supplied in reverse order;
- camera FOV 72 with Better Firearms POV 72;
- camera FOV 82 with Better Firearms POV 82;
- one maximal compatible candidate using headshot-only AI, POV 82, camera FOV 82, Better Upgrading, supersize, and the compatible direct options;
- camera-FOV conflict rejection;
- zombie-size conflict rejection.

Every candidate retained 3060 archive entries. Candidate validation did not install any candidate into the game.

Default camera FOV 62.5 and normal zombie size are pristine-baseline states and are represented by absence of a non-default patch rather than no-op definitions.

Choice groups fail closed on conflicting selections: one-hit/headshot-only AI, the three Better Firearms POV variants, camera FOV 72/82, and the four non-default zombie-size variants.

## Firearm reconstruction

Native `inventory_gen.scr` represents audited firearms as contiguous repeated same-name `Item(...)` groups. Runtime firearm transforms therefore:

- require matching same-name blocks to be contiguous;
- reject interleaved groups;
- validate complete call sequences across the ordered group;
- validate `UpgradeLevel(0,0,1,1,2,2,3,3)` before tier-local insertions;
- preserve CRLF;
- never use historical line numbers as runtime targets.

The accepted source-map evidence accounts for 744 active released firearm targets.

Better Firearms Upgrading accounts for all 157 active targets: 58 existing-call changes plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Commented rifle `ShotTime` source lines remain excluded.

Better Firearms POV plus the matching sway handlers account for 177/177 active targets at FOV 62 and 205/205 at FOV 72 and 82. All four firearm options are native-candidate validated.

## Camera FOV

Released choices are 62 default, 72, and 82.

The accepted corrected recoil audit verifies 13 relevant firearm groups with eight repeated `Item(...)` blocks and `UpgradeLevel(0,0,1,1,2,2,3,3)`.

For the seven shotgun families plus CrowdPleaser:

- pristine native has one base `ShootVertRecoil(0.1)` in block 1;
- the four authored tier slots map to blocks 2, 4, 6, and 8;
- FOV 72 produces `0.06, 0.14, 0.14, 0.14, 0.14`;
- FOV 82 produces `0.033, 0.14, 0.14, 0.14, 0.14`.

For the five pistol groups the released camera handlers change only active base recoil calls. FOV 72 changes Desert Eagle, Magnum, M9, and McCall; FOV 82 additionally changes Colt. Commented tier-recoil source lines remain excluded.

Candidate construction deterministically applies Better Upgrading before camera FOV when both are selected. The native interaction candidates for FOV 72/82 with Upgrading and matching POV variants now pass.

## AI and preset-backed controls

Normal AI matches the represented native tree. One-hit changes only the two audited `ParamBool("one_shot", ...)` values. Headshot-only is represented by the complete named-value delta across 20 audited members. Both non-default difficulty modes are native-candidate validated and mutually exclusive.

Hard AI remains unready: 56 of 57 differing members are semantically explained while one custom vessel member still contains unresolved structure. No partial hard-mode transform is exposed.

### Zombie size

The hardened preset comparison shows normal size matches native and every non-default difference is confined to `m_ForcedBodyScaleMin`/`m_ForcedBodyScaleMax` in exactly four members:

- `data/presets/infectedai.pre`;
- `data/presets/infectedai_pre.def`;
- `data/presets/zombieai.pre`;
- `data/presets/zombieai_pre.def`.

Linux validates exact native Min/Max sequences using occurrence counts and SHA-256 digests and changes only those call arguments. No preset file or native value vector is copied into Git. All four non-default size modes now pass native disposable candidates.

### Forced spawn

Default spawn matches native. Non-default variants expose large semantic sets of AI-preset identifier replacements in `aispawnbox_pre.def`. Those identifiers remain provenance-sensitive and no public-safe complete algorithmic transform is proven, so forced spawn remains unready.

### Weather/time

Vanilla matches native. Non-default variants still contain unresolved behavior in `logic_script.scr` and/or `weather.scr`, even where ambient named values are understood. They remain unready.

## Transaction safety

The Linux core now provides:

- strict ZIP validation with CRC, unsafe-path, and duplicate checks;
- safe extraction/rebuild helpers;
- pristine backup creation without silent overwrite;
- in-memory candidate construction from validated source archives;
- same-directory temporary writes followed by atomic replacement;
- pre-replacement verification that live Data0 still matches the candidate source hash;
- verification that the pristine backup matches that same source hash;
- candidate/live/backup entry-count checks before installation;
- optional expected-candidate hash binding;
- expected-backup hash verification before restore;
- recovery that can restore a valid backup even if the live archive is missing;
- CLI commands for backup creation, candidate installation, and backup restore.

Install replacement rechecks the live destination hash after the temporary candidate copy is fully written and fsynced but before `os.replace`. An unexpected live change therefore fails closed before replacement.

Linux patching must start from the validated installed archive or a verified pristine backup derived from it. The inherited repository `Data0.pak` is never a Linux patch source or install payload.

The installed game has still not been modified by the Linux port.

## Validation evidence and next gates

Accepted evidence is scoped to the code state that produced it:

- the earlier 15-option catalog passed native disposable candidates;
- the repeated-item fix and following physical retry passed all 20 then-current options plus compatible combinations and conflicts;
- source-map evidence supplied complete firearm reconstruction data;
- hardened preset evidence supplied the zombie-size and remaining preset boundaries;
- corrected FOV-recoil evidence supplied the repeated-block recoil mapping;
- the latest physical run passed all six newly added individual native candidates, four material FOV interactions, a maximal compatible candidate, and both new conflict checks;
- focused synthetic transaction tests pass for wrong-live, wrong-backup, wrong-candidate, entry-count drift, missing-live restore, and CLI backup/install/restore round-trip behavior;
- no GitHub Actions were used.

Next physical gates:

1. sync the current `linux-port`, run `git diff --check`, the full unit suite, and Python compilation;
2. verify the native ELF, live Data0 baseline, and absence/identity of the intended pristine backup;
3. exercise backup creation without overwriting any existing recovery material;
4. build one disposable candidate from the verified baseline, atomically install it through the hash-bound transaction path, and verify the installed candidate hash;
5. restore the pristine backup through the hash-bound restore path and verify the exact original Data0 hash returns;
6. only after transaction QA succeeds, proceed to native gameplay/visual checks of released features;
7. finish unresolved forced-spawn, hard-AI, and weather/time parity before release work;
8. add and validate the Linux-native GUI and packaging.

## Cleanup and publication

Cleanup is continuous. Superseded versioned QA reports should be removed after replacement evidence is accepted. Current evidence, unresolved diagnostics, pristine backups, hashes, provenance/licensing material, authentic user data, unrelated work, and Git history must be preserved.

The latest successful candidate evidence supersedes failed/older candidate generations. Hardened preset, corrected FOV-recoil, and source-map evidence remain current because unresolved parity decisions still depend on them.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
