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

## Preferred Linux distribution model

Where practical, represent gameplay changes as semantic transformations and compact project-authored patch definitions rather than replacement copies of game files. If a feature cannot be reproduced without bundled replacement content, its provenance and redistribution status must be resolved before packaging.

## Attribution requirements

Public documentation and distributed builds should clearly state that:

- DIRUE was created by FireEyeEian;
- this project is a modified native-Linux port;
- the project is GPLv3;
- Dead Island and Techland game assets are not licensed by this project's GPL notice; and
- users need their own legitimate native Linux game installation.
