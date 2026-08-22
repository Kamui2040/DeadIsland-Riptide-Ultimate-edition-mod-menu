# DIRDE UE Linux 0.1.0.dev0

First public pre-release candidate for the native Linux port of FireEyeEian's Dead Island Riptide Ultimate Edition (DIRUE) mod menu for *Dead Island: Riptide Definitive Edition*.

## Highlights

- Native Linux PySide6 application; no Wine or Proton wrapper.
- All 42 released non-default DIRUE gameplay options.
- Semantic, fail-closed patch targeting with explicit validation.
- Pristine backup preservation before the first modification.
- Candidate construction and validation in temporary storage.
- Live-source recheck and atomic `Data0.pak` replacement.
- **Restore original** workflow for exact pristine recovery.
- Flatpak and AppImage end-user packages.
- Shared desktop/AppStream identity and maintainer-approved custom icon.

## Validation

The frozen validated source commit is `c3e3b97494058e8da199658f4f265e3eb84f0201`.

On physical Bazzite, the exact recommended Flatpak and AppImage artifacts passed launch, Browse, explicit Validate, representative Apply, exact Restore, close, and restart. The Flatpak also passed bounded permission inspection. The AppImage final rebuild was byte-identical to the tested RC AppImage and its finished ELF audit reported maximum required `GLIBC_2.34`.

## Compatibility

- Native Linux *Dead Island: Riptide Definitive Edition* installation required.
- x86-64 Linux.
- AppImage compatibility floor: glibc `2.34`.
- Compatibility with older pre-x86-64-v2 processors is not established by current evidence.
- Bazzite validation is complete. SteamOS is an operating-system target, but no Steam Deck- or Steam Machine-specific hardware validation is claimed.

## Known presentation limitation

Bazaar may show a generic icon for a locally installed/sideloaded Flatpak. The Flatpak exports valid scalable SVG plus 64x64 and 128x128 PNG icons, and direct GTK icon-theme lookup resolves the application ID correctly. This is treated as a Bazaar sideload/display limitation rather than a package defect.

## Credits and licensing

FireEyeEian created the original Ultimate Edition mod. Kamui2040 authors and maintains the Linux port.

The project is licensed under GPLv3. Dead Island and Techland game content are not licensed by this project's GPL notice and are not redistributed by the Linux packages. Users need their own legitimate native Linux game installation.
