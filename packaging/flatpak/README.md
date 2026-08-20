# Flatpak proof of concept

This directory contains the first end-user Flatpak packaging proof for DIRUE Linux.

## Scope

The proof packages only the Linux runtime source under `src/dirue` plus Flatpak desktop metadata. It does not use the repository root as a Flatpak source and does not include the inherited `Data0.pak`, preset archives, replacement assets, Windows helpers, or other provenance-sensitive historical material.

The sandbox intentionally starts without blanket host-filesystem or network access. The existing Qt folder chooser is expected to use the desktop portal. Physical Bazzite QA must prove that a user-selected native DIRDE directory remains readable and writable through that path before any broader filesystem permission is considered.

The application ID is `io.github.Kamui2040.DIRUELinux`. The proof uses `org.kde.Platform` 6.11 with `io.qt.PySide.BaseApp` 6.11 so PySide6 is supplied by the Flatpak base app rather than by the host system.

## Local validation

From the repository root:

```bash
python -m unittest tests.test_flatpak_packaging
```

For the physical Bazzite build, use Flathub's Flatpak Builder package rather than modifying the immutable host:

```bash
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user -y flathub org.flatpak.Builder
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest packaging/flatpak/io.github.Kamui2040.DIRUELinux.json
flatpak run --command=flathub-build org.flatpak.Builder --install packaging/flatpak/io.github.Kamui2040.DIRUELinux.json
flatpak run io.github.Kamui2040.DIRUELinux
```

The proof is not release acceptance. A successful build and launch must still be followed by packaged Bazzite checks for directory selection, native-game validation, candidate Apply, exact Restore, application restart, and artifact-content inspection. A final application icon and full metadata polish belong to the later UI/packaging-polish phase.
