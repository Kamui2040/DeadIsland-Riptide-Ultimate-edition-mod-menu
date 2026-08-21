# Flatpak packaging

This directory contains the first-class Flatpak packaging for DIRDE UE Linux. The proof, release-candidate, packaged Bazzite QA, and final rebuild stages are complete for the frozen source state.

## Scope

The Flatpak packages only the Linux runtime source under `src/dirue` plus public-safe shared metadata from `packaging/common`. It does not use the repository root as a Flatpak source and does not include the inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, authentic backups, private QA material, or other provenance-sensitive historical content.

The sandbox has no blanket host-filesystem or network access. The Qt folder chooser uses the desktop portal to grant scoped access to the user-selected DIRDE game directory.

The application ID is `io.github.Kamui2040.DIRUELinux`. The package uses `org.kde.Platform` 6.11 with `io.qt.PySide.BaseApp` 6.11 so PySide6 is supplied by the Flatpak base app rather than the host system.

Flatpak and AppImage share the desktop entry, AppStream metadata, icon identity, and `dirue-linux` launcher name. The Flatpak installs the scalable SVG plus 64x64 and 128x128 PNG icon variants under standard hicolor paths.

## Accepted Bazzite proof

Physical Bazzite QA on 2026-08-20 accepted the initial proof at commit `92bed2cab98d6ecc5c2255a28a5f11bdd7024bab`.

Accepted checks included the bounded source list, successful Flatpak Builder output, packaged PySide6 runtime, permission inspection, portal-based Browse, native-game Validate, representative Apply, exact Restore, and clean exit.

KDE/UDisks D-Bus disconnect warnings observed during the proof did not block Browse, Validate, Apply, Restore, or clean exit and were not a release blocker.

## Release-candidate evidence

The frozen release-candidate source commit is:

`c3e3b97494058e8da199658f4f265e3eb84f0201`

The exact Flatpak bundle exercised during packaged Bazzite RC QA was:

- size: `56,117,784` bytes;
- SHA-256: `523e4b0921a09a1c05caa20d67cbcfe7e9090bb416d7d0520848665ced204031`.

That exact bundle passed hash recheck, per-user install, bounded permission inspection, launch, Browse, explicit Validate, `Reduce sprint stamina` Apply, `Restore original`, close, and restart on physical Bazzite on 2026-08-22.

No RC defect required a source change.

## Final rebuild/verification

Final verification rebuilt the Flatpak from the unchanged frozen source commit on 2026-08-22.

The final-verification bundle was:

- size: `56,114,672` bytes;
- SHA-256: `1eec07e171303cf55b2ce4cfd944e543ced05a7ff05ef74a82368560c1bdc073`.

The final bundle differs in container bytes from the earlier RC bundle. Flatpak bundle byte reproducibility was not a release requirement. The final rebuild passed the focused static/package checks and package build/integrity path, and no source change occurred between the physically exercised RC bundle and the final rebuild.

The exact-artifact distinction is intentional: physical Apply/Restore/restart QA was performed on the RC Flatpak hash above, while the later Flatpak hash records the final rebuild from the same frozen source state.

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

## Desktop integration note

Physical checks confirmed the SVG and 64x64/128x128 PNG exports are valid and GTK resolves the application ID to the exported icon. Bazaar still shows a generic icon for the locally installed package in the tested host and Flatpak Bazaar builds. Because the exported assets, paths, dimensions, application ID, and direct GTK lookup all pass, this remains classified as an external Bazaar sideload/display limitation rather than a DIRDE packaging defect.

## Publication state

This is not a Flathub submission and no public Flatpak binary has been authorized for release. Technical validation of the frozen source state is complete; publication or integration still requires explicit approval.
