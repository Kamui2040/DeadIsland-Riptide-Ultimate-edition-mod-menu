# Publication preparation

This document prepares the first public DIRDE UE Linux package release for manual publication. It does not authorize or perform publication.

## Release identity

- Package version: `0.1.0.dev0`
- Frozen validated source commit: `c3e3b97494058e8da199658f4f265e3eb84f0201`
- Main integration merge: `cc62b1d2874ad571e2c17370dca5d43a75adc477`
- Current project is a native-Linux port of FireEyeEian's DIRUE for Dead Island: Riptide Definitive Edition.

## Recommended publication artifacts

Use the exact physically exercised RC Flatpak together with the AppImage that is byte-identical between RC and final verification:

- `DIRDE-UE-Linux-0.1.0.dev0-c3e3b974-x86_64.flatpak`
  - size: `56,117,784` bytes
  - SHA-256: `523e4b0921a09a1c05caa20d67cbcfe7e9090bb416d7d0520848665ced204031`
  - evidence: exact hash passed Bazzite install, permission inspection, launch, Browse, Validate, representative Apply, exact Restore, close, and restart.
- `DIRUE-Linux-0.1.0.dev0-x86_64.AppImage`
  - size: `60,262,904` bytes
  - SHA-256: `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`
  - evidence: exact hash passed Bazzite launch, Browse, Validate, representative Apply, exact Restore, close, and restart; the final rebuild was byte-identical and the finished ELF audit reported maximum required `GLIBC_2.34`.

A later final-verification Flatpak was also produced from the same frozen source:

- size: `56,114,672` bytes
- SHA-256: `1eec07e171303cf55b2ce4cfd944e543ced05a7ff05ef74a82368560c1bdc073`

That later Flatpak passed final static/package build-integrity checks but did not receive a second exact-artifact Apply/Restore/restart pass. Do not substitute it for the recommended Flatpak while claiming the stronger RC exact-artifact QA evidence.

## Pre-upload verification

Before uploading, verify the selected files locally and compare both hash and size against the values above. Do not upload any inherited `Data0.pak`, preset archive, replacement asset, extracted game content, authentic backup, QA report, local path record, credential, token, private URL, or recovery/signing material.

The release must preserve GPLv3 and FireEyeEian attribution and must clearly identify this as the Linux port. Techland game content is not redistributed.

## End-user installation text

### Flatpak

Install the downloaded bundle:

```bash
flatpak install --user ./DIRDE-UE-Linux-0.1.0.dev0-c3e3b974-x86_64.flatpak
```

Launch **DIRDE UE Linux** from the desktop application menu, or run:

```bash
flatpak run io.github.Kamui2040.DIRUELinux
```

Use **Browse** to select the native Linux Dead Island: Riptide Definitive Edition game folder, then **Validate**. Select the wanted options and use **Apply changes**. Use **Restore original** to return to the retained pristine state.

### AppImage

If necessary, make the downloaded AppImage executable:

```bash
chmod +x DIRUE-Linux-0.1.0.dev0-x86_64.AppImage
```

Then launch it directly:

```bash
./DIRUE-Linux-0.1.0.dev0-x86_64.AppImage
```

Use **Browse**, **Validate**, select options, and then **Apply changes**. Use **Restore original** to return to the retained pristine state.

## Requirements and compatibility copy

- A legitimate native Linux installation of *Dead Island: Riptide Definitive Edition*.
- x86-64 Linux.
- The AppImage compatibility floor is glibc `2.34`; compatibility with older pre-x86-64-v2 processors is not established by current evidence.
- Bazzite package and gameplay-adjacent validation is complete. SteamOS is an operating-system target, but Steam Deck- or Steam Machine-specific hardware validation is not claimed.
- This project is not a Wine wrapper, Proton frontend, Windows launcher, or general mod manager.

## Nexus Mods copy

### Short description

Native Linux port of FireEyeEian's Dead Island Riptide Ultimate Edition mod menu, with all 42 released non-default gameplay options, transactional Data0 patching, exact restore, and Flatpak/AppImage packages.

### Main description

**DIRDE UE Linux** is a native-Linux port of FireEyeEian's **Dead Island Riptide Ultimate Edition (DIRUE)** mod menu for *Dead Island: Riptide Definitive Edition*.

It implements all 42 released non-default gameplay options from the original DIRUE release while replacing the Windows-only implementation with a native Linux application. It is not a Wine or Proton wrapper.

The application patches your own validated installed `DIR/Data0.pak`. Before the first modification it preserves a pristine backup, builds and validates candidates in temporary storage, rechecks the live source before replacement, installs atomically, and provides **Restore original** for recovery. The Linux packages do not include Techland game files, inherited preset archives, or replacement assets.

**Available packages**

- Flatpak — recommended first-class package for Bazzite, SteamOS, and other Flatpak-friendly Linux systems.
- AppImage — portable x86-64 Linux alternative.

Normal packaged users do not need to install Python or PySide6.

**Basic use**

1. Launch DIRDE UE Linux.
2. Browse to your native Linux game folder.
3. Select **Validate**.
4. Choose the gameplay options you want.
5. Select **Apply changes**.
6. Use **Restore original** when you want to return to the pristine game archive.

**Credits and license**

FireEyeEian created the original Ultimate Edition mod. Kamui2040 authors and maintains the Linux port. The project is GPLv3. Dead Island and Techland game content are not covered by this project's GPL notice and are not redistributed.

### Suggested Nexus changelog

Initial public Linux pre-release:

- native Linux PySide6 GUI;
- all 42 released DIRUE non-default gameplay controls;
- semantic fail-closed patch targeting;
- pristine backup preservation, validated candidate construction, atomic replacement, and exact restore;
- Flatpak and AppImage package paths;
- packaged Bazzite Validate/Apply/Restore/restart QA;
- AppImage finished-artifact audit bounded to `GLIBC_2.34`;
- maintainer-approved UI and custom application icon.

Known presentation limitation: Bazaar may show a generic icon for a locally installed/sideloaded Flatpak even though the package exports valid SVG/PNG icons and GTK resolves the application ID correctly.

## Ko-fi announcement copy

DIRDE UE Linux is ready for its first public pre-release.

This is the native Linux port of FireEyeEian's Dead Island Riptide Ultimate Edition mod menu for Dead Island: Riptide Definitive Edition. The Linux version now covers all 42 released gameplay options and includes a native GUI, safe transactional Data0 patching, pristine restore, and both Flatpak and AppImage packages.

The release was validated on Bazzite through install/launch, game-folder validation, representative Apply/Restore, restart, packaging checks, and an AppImage `GLIBC_2.34` compatibility audit.

Credit to FireEyeEian for the original DIRUE project. The Linux port remains GPLv3 and does not redistribute Techland game content.

## Manual publication checklist

1. Verify the two recommended files against `docs/RELEASE_CHECKSUMS_0.1.0.dev0.txt` and the byte sizes above.
2. Upload only those end-user package files; do not upload repository-inherited game content or private QA/recovery material.
3. Mark the release as a pre-release/development version where the destination supports that distinction because the package version is `0.1.0.dev0`.
4. Use the Nexus description, install text, changelog, credits, and compatibility boundaries from this document.
5. Include the checksum file or publish the two SHA-256 values alongside the downloads.
6. Publish the Ko-fi announcement only after the download destination is live and verified.
7. After publication, verify both public download files still match the accepted hashes.
8. Record the public URLs and publication date in project state only after they actually exist. Do not store account credentials or private management links in Git.
