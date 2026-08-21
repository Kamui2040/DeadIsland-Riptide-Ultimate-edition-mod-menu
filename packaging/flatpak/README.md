# Flatpak packaging

This directory contains the first-class Flatpak packaging for DIRUE Linux. The initial bounded proof was accepted on physical Bazzite; current work hardens it for a release candidate while preserving the accepted portal-first permission model.

## Scope

The Flatpak packages only the Linux runtime source under `src/dirue` plus public-safe shared metadata from `packaging/common`. It does not use the repository root as a Flatpak source and does not include the inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, or other provenance-sensitive historical material.

The sandbox has no blanket host-filesystem or network access. The Qt folder chooser uses the desktop portal to grant scoped access to the user-selected native DIRDE directory.

The application ID is `io.github.Kamui2040.DIRUELinux`. The package uses `org.kde.Platform` 6.11 with `io.qt.PySide.BaseApp` 6.11 so PySide6 is supplied by the Flatpak base app rather than the host system. Flatpak and AppImage now share the same desktop entry, AppStream metadata, icon identity, and `dirue-linux` launcher name.

For desktop integration the package keeps the shared scalable SVG icon and also installs 64×64 and 128×128 PNG versions under the standard hicolor paths. The raster sizes allow a single-file `.flatpak` bundle to carry direct icon metadata for package frontends such as Bazaar instead of relying only on the scalable icon.

## Accepted Bazzite proof

Physical Bazzite QA on 2026-08-20 accepted the initial proof at commit `92bed2cab98d6ecc5c2255a28a5f11bdd7024bab`:

- six static packaging checks passed;
- Flatpak Builder completed and installed the app;
- packaged imports reported DIRUE `0.1.0.dev0` and PySide6 `6.11.1`;
- permission inspection confirmed no blanket host-filesystem access;
- Browse selected the native DIRDE directory without extra permissions;
- native game validation passed against the accepted pristine Data0 baseline;
- `Reduce sprint stamina` Apply completed successfully;
- Restore completed successfully and final status confirmed the live Data0 matched the retained pristine backup;
- the GUI exited normally.

KDE/UDisks D-Bus disconnect warnings were printed during the GUI run but did not block Browse, Validate, Apply, Restore, or clean exit. They are not an initial proof blocker.

## Local validation

From the repository root:

```bash
python3 -m unittest tests.test_flatpak_packaging tests.test_appimage_packaging
```

For a physical Bazzite build, use Flathub's Flatpak Builder package rather than modifying the immutable host:

```bash
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user -y flathub org.flatpak.Builder
flatpak run org.flatpak.Builder \
  --user \
  --install \
  --install-deps-from=flathub \
  --force-clean \
  --disable-rofiles-fuse \
  .flatpak-build \
  packaging/flatpak/io.github.Kamui2040.DIRUELinux.json
flatpak run io.github.Kamui2040.DIRUELinux
```

The package is not a Flathub submission yet. The maintainer-approved custom icon and packaged UI presentation are accepted. Physical checks confirm the SVG and 64×64/128×128 PNG exports are valid and GTK resolves the application ID to the exported icon. Bazaar's remaining generic icon for the locally installed package is treated as an external sideload/display limitation. The next package step is the release-candidate build from one exact frozen source commit shared with the AppImage build.
