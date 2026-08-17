# Provenance and redistribution policy

## Original project

Dead Island Riptide Ultimate Edition (DIRUE) was created by FireEyeEian.

Primary upstream sources:

- GitHub: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Nexus Mods: `https://www.nexusmods.com/deadislandriptide/mods/3`

The upstream repository declares GNU General Public License v3.0 (GPLv3). The Linux-port project preserves that license and original attribution.

## Linux-port modifications

This fork is creating a native Linux implementation for the native Linux build of Dead Island: Riptide Definitive Edition. Linux-port changes are identified through Git history, branch history, documentation, and source attribution where appropriate.

Source distributed by this project remains subject to GPLv3 unless a file clearly states another compatible provenance/license.

## Game content is separate

The GPLv3 license of the DIRUE source repository does not by itself establish permission to redistribute Techland game binaries, archives, scripts, textures, audio, or other copyrighted game content.

Therefore the Linux implementation must not depend on redistributing extracted game content. It should patch the user's own validated installed `DIR/Data0.pak` transactionally.

## Inherited upstream `Data0.pak`

The fork inherits a committed upstream `Data0.pak` of 7,647,523 bytes. A validated native Linux Steam installation uses a different `Data0.pak` (7,932,941 bytes in the current compatibility baseline).

The inherited archive is historical upstream material and is **not** an approved Linux-port installation payload. Linux code must not copy it over the user's installation, use it as the pristine source for patching, or package it into Linux releases.

Removal or retention of inherited historical files will be handled separately so provenance is preserved and no unique upstream history is rewritten.

## Bundled presets and replacement files

The upstream repository contains ZIP presets, replacement files, UI assets, sounds, and helper executables. Before any such file is reused or redistributed in a Linux release, it must be classified as one of:

1. original GPL-covered project source/content with adequate provenance;
2. generated patch data that contains no redistributable game content;
3. third-party material with an identified compatible license/permission; or
4. game-derived/proprietary/unclear material that must not be redistributed without explicit rights.

Unknown provenance is not treated as permission.

Accepted sanitized native comparison resolves the two unconditional Windows replacement files:

- `Required_files_and_scripts/game.ini` differs from the accepted native `data/game.ini` only at the active `GameName#1` call; native and replacement each contain the same 25 parsed call identities and no call is added or removed;
- `Required_files_and_scripts/menumain_pc.xui_version` adds one replacement-only `MyText:T_Mylogo` component; after removing that component, the replacement XUI is structurally equivalent to the accepted native menu.

These replacements therefore implement upstream branding/cosmetic behavior rather than gameplay behavior. They are **not required for Milestone-1 Linux parity** and must not be copied into the user's Data0 or packaged as Linux runtime content. Their inherited repository copies remain provenance-sensitive historical upstream material; this decision does not assert redistribution rights over them.

## Forced-spawn provenance boundary

Forced-spawn transforms must not use inherited preset ZIPs as runtime payloads or replacement files. The Linux runtime always patches the user's own validated native Data0 and validates the complete pristine 165-call `m_AIPresets` vector before mutation.

Suicider and bandits-with-guns use exact native donors. Bandits-with-melee uses an accepted whole-token reconstruction from the pristine 165-value spawn vector; the target identifier and substituted token text are not stored in source.

For Butcher, Ram, Bloater, and Thug, earlier accepted audits found no exact pristine donor and no acceptable bounded whole-token reconstruction from:

1. the pristine 165-value `m_AIPresets` vector;
2. any quoted string in native `data/presets/aispawnbox_pre.def`; or
3. the bounded native AI/preset source set consisting of `aispawnbox_pre.def`, `zombieai.pre`, `zombieai_pre.def`, `infectedai.pre`, `infectedai_pre.def`, and `bestiary.scr`.

A later focused audit established a narrower compatibility path. The four released upstream preset blobs were read without extracting or reusing their files as runtime content. For each preset, the audit verified the expected inherited Git blob identity, ZIP integrity, the single expected `aispawnbox_pre.def` member, 165 active `m_AIPresets` calls, one dominant target value used in exactly 164 calls, and preservation of ordinal 60. The target values are machine-facing preset identifier lists rather than replacement game files.

The integrated Linux implementation therefore carries only those minimum compatibility identifier lists plus pinned SHA-256, syntax, identifier-count, pristine-vector, preserved-ordinal, changed-call-count, and post-transform validation. The Linux runtime does **not** copy, extract, install, or package the inherited preset ZIPs.

Accepted physical candidate QA confirms all four transforms against the pristine native baseline: each candidate keeps all 3060 archive entries and member order, changes only `data/presets/aispawnbox_pre.def`, preserves ordinal 60, replaces exactly the other 164 active calls, validates archive integrity and reported hashes, and leaves the live Data0 unchanged.

Accepted bounded native gameplay QA then applied Butchers, Rams, Bloaters, and Thugs one at a time through the normal application transaction path. Each mode produced the intended forced-spawn behavior in the native game. After the native ELF process exited, the exact pristine Data0 was restored before the observation was accepted. The retained pristine backup remained valid and unchanged throughout.

This is a narrow project compatibility treatment for the minimum machine identifiers required to reproduce released behavior. It does not assert that the inherited preset ZIPs, Data0 archives, replacement files, or other Techland-derived content are GPL-covered or otherwise redistributable. Those files remain provenance-sensitive historical material and are excluded from Linux runtime/distribution payloads.

The project will not widen this exception into arbitrary whole-archive string assembly, character-level encoding, asset extraction, or general reuse of bundled preset content. Issue #2 records the completed provenance and native-game acceptance path for these four released choices.

## Preferred Linux distribution model

Where practical, represent gameplay changes as semantic transformations and compact project-authored patch definitions rather than replacement copies of game files. If a feature cannot be reproduced without bundled replacement content, its provenance and redistribution status must be resolved before packaging.

The Linux runtime specifically avoids the upstream unconditional `game.ini` / `menumain_pc.xui` copies because accepted native evidence proves they are unnecessary for gameplay parity.

## Attribution requirements

Public documentation and distributed builds should clearly state that:

- DIRUE was created by FireEyeEian;
- this project is a modified native-Linux port;
- the project is GPLv3;
- Dead Island and Techland game assets are not licensed by this project's GPL notice; and
- users need their own legitimate native Linux game installation.
