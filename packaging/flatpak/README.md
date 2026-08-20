# Flatpak proof of concept

This directory contains the accepted first end-user Flatpak packaging proof for DIRUE Linux.

## Scope

The proof packages only the Linux runtime source under `src/dirue` plus Flatpak desktop metadata. It does not use the repository root as a Flatpak source and does not include the inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, or other provenance-sensitive historical material.

The sandbox intentionally has no blanket host-filesystem or network access. The existing Qt folder chooser uses the desktop portal to grant scoped access to the user-selected native DIRDE directory.

The application ID is `io.github.Kamui2040.DIRUELinux`. The proof uses `org.kde.Platform` 6.11 with `io.qt.PySide.BaseApp` 6.11 so PySide6 is supplied by the Flatpak base app rather than by the host system.

## Accepted Bazzite proof

Physical Bazzite QA on 2026-08-20 accepted the proof at commit `92bed2cab98d6ecc5c2255a28a5f11bdd7024bab`:

- six static packaging checks passed;
- Flatpak Builder completed and installed the app;
- packaged imports reported DIRUE `0.1.0.dev0` and PySide6 `6.11.1`;
- permission inspection confirmed no blanket host-filesystem access;
- Browse selected the native DIRDE directory without adding extra permissions;
- native game validation passed against the accepted pristine Data0 baseline;
- `Reduce sprint stamina` Apply completed successfully;
- Restore completed successfully and final status confirmed the live Data0 matched the retained pristine backup;
- the GUI exited normally.

KDE/UDisks D-Bus disconnect warnings were printed during the GUI run but did not block Browse, Validate, Apply, Restore, or clean exit. They are not an initial proof blocker.

## Local validation

From the repository root:

```bash
python3 -m unittest tests.test_flatpak_packaging
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
flatpak run --command=python3 io.github.Kamui2040.DIRUELinux \
  -c 'import dirue, PySide6; print(dirue.__version__, PySide6.__version__)'
flatpak info --user --show-permissions io.github.Kamui2040.DIRUELinux
flatpak run io.github.Kamui2040.DIRUELinux
```

The proof is not a Flathub submission yet. Final iconography, screenshots, release metadata, Flathub submission lint, broader packaged QA, and UI polish belong to later release stages.
