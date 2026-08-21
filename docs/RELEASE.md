# Release workflow

Milestone 1 gameplay parity is complete. Release work follows this order:

1. **Flatpak proof** — prove the existing native GUI launches from a bounded, provenance-safe Flatpak and can reach a user-selected native game installation without depending on host Python or PySide6. **Complete on physical Bazzite.**
2. **AppImage proof** — prove a portable one-file AppImage can launch the same application without a user-managed Python/PySide6 environment. **Complete on physical Bazzite.**
3. **Shared packaging hardening** — keep application behavior shared between formats, harden resource/config paths and metadata, pin external build tooling, define the AppImage compatibility baseline, and keep provenance-sensitive inherited content out of both artifacts. **Complete on physical Bazzite.**
4. **UI polish** — improve first-run flow, game-folder selection, hierarchy, spacing, wording, status/error presentation, Apply/Restore affordances, iconography, window behavior, and version/about information. Validate the packaged UI rather than only a development checkout. **Complete with explicit maintainer visual and behavioral approval on physical Bazzite.**
5. **Release candidate** — freeze one source commit and build both end-user formats from that exact state. **Active on `release/rc-0.1.0-dev0`.**
6. **Packaged Bazzite QA** — test the Flatpak and AppImage as users receive them: launch, select/validate native DIRDE, Apply, native-game check where required, exact Restore, restart, and artifact-content/privacy checks.
7. **Final rebuild and verification** — rebuild final-version artifacts from the accepted source state and repeat package-integrity and smoke checks affected by any RC fixes.
8. **Release** — publish only after explicit approval.

## End-user acceptance

The primary release is not considered complete if normal users must install Python, create a virtual environment, install PySide6, or use development commands to run the GUI.

- **Flatpak** is the first-class target for SteamOS, Bazzite, and other Flatpak-friendly Linux systems.
- **AppImage** is the portable Linux alternative.
- Wheel and sdist artifacts may remain available for source/developer use but are not the primary one-click user path.

SteamOS is treated as an operating-system target rather than as a Steam Deck-only target. Hardware-specific claims such as Steam Deck- or Steam Machine-specific validation require evidence from that hardware and are not implied by Bazzite testing.

## UI validation flow

The accepted user flow for game selection is:

- **Browse** selects a directory only and does not auto-validate;
- **Validate** performs the explicit native-game validation once;
- Apply remains disabled until validation succeeds;
- changing the selected path invalidates the prior validation and disables Apply until the new path is validated.

The GUI still revalidates inside Apply/Restore transactions for safety; that service-level validation is not a replacement for the explicit user-facing Validate step.

Packaged Bazzite review accepted first-run clarity, hierarchy/spacing, status/error presentation, Apply/Restore affordances, iconography, window behavior, and version/About presentation. The main window and About dialog received explicit maintainer visual approval, and the required validation-state behavior was confirmed.

The shared Flatpak icon export also passed direct checks: the scalable SVG and 64x64/128x128 PNGs are present, the raster dimensions are correct, and GTK resolves the application ID to the exported 128x128 PNG. Bazaar still displays a generic icon for the locally installed Flatpak in both tested Bazaar packaging forms; this is treated as an external Bazaar sideload/display limitation rather than a DIRDE packaging defect.

## Release-candidate freeze

The release-candidate branch is `release/rc-0.1.0-dev0`. Build both primary artifacts from the same exact branch-head commit. Do not mix commits between the Flatpak and AppImage builds.

If an RC defect requires a source change, record the finding, apply only the accepted fix, rerun the affected validation, and establish a new exact RC commit before rebuilding both formats as required by the change.

## Release gates

A public release requires all of the following:

- Flatpak and AppImage launch without user-managed Python/PySide6 setup;
- both artifacts exclude inherited game archives, preset payloads, replacement assets, private QA, backups, and other non-redistributable or sensitive material;
- packaged game-folder access is validated without unnecessarily broad permissions;
- AppImage build tooling is pinned and its compatibility baseline is deliberate rather than inherited accidentally from the developer host;
- the custom application icon has maintainer-approved artwork;
- UI polish has passed functional packaged QA and received explicit maintainer visual approval;
- both RC artifacts are built from one exact source commit and their authoritative identities/hashes/sizes are recorded;
- packaged Bazzite Apply/Restore behavior passes with the existing transaction safeguards;
- final artifacts are tied to the accepted release commit and version;
- publication receives explicit approval.

GitHub Actions are not part of this workflow unless separately approved.
