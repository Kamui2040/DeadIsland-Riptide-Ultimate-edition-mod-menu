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

Released forced-spawn presets contain game-derived identifiers that must not be copied into Linux source merely because they are present in inherited upstream ZIPs. Public-safe runtime transforms therefore derive values only from the user's own validated native Data0 and bind every derivation to audited hashes and semantic structure.

Suicider and bandits-with-guns use exact native donors. Bandits-with-melee uses an accepted whole-token reconstruction from the pristine 165-value spawn vector; the target identifier and substituted token text are not stored in source.

Butcher, Ram, Bloater, and Thug remain intentionally unresolved. Accepted sanitized audits establish that each changes 164 of the 165 active spawn calls while preserving ordinal 60, but no acceptable whole-token recipe exists from:

1. the pristine 165-value `m_AIPresets` vector;
2. any quoted string in native `data/presets/aispawnbox_pre.def`; or
3. the bounded native AI/preset source set consisting of `aispawnbox_pre.def`, `zombieai.pre`, `zombieai_pre.def`, `infectedai.pre`, `infectedai_pre.def`, and `bestiary.scr`.

The project will not widen this into arbitrary whole-archive string assembly or character-level encoding. Those four modes stay unavailable unless new rights/provenance evidence or a comparably narrow semantic derivation is established. Ongoing resolution work is tracked in Issue #2.

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
