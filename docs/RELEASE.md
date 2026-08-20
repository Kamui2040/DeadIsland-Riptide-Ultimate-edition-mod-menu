# Release workflow

Milestone 1 gameplay parity is complete. Release work follows this order:

1. **Flatpak proof** — prove the existing native GUI launches from a bounded, provenance-safe Flatpak and can reach a user-selected native game installation without depending on host Python or PySide6. **Complete on physical Bazzite.**
2. **AppImage proof** — prove a portable one-file AppImage can launch the same application without a user-managed Python/PySide6 environment. **Complete on physical Bazzite.**
3. **Shared packaging hardening** — keep application behavior shared between formats, harden resource/config paths and metadata, pin external build tooling, define the AppImage compatibility baseline, and keep provenance-sensitive inherited content out of both artifacts. **Complete on physical Bazzite.**
4. **UI polish** — improve first-run flow, game-folder selection, hierarchy, spacing, wording, status/error presentation, Apply/Restore affordances, iconography, window behavior, and version/about information. Validate the packaged UI rather than only a development checkout. **In progress on `release/ui-polish`.**
5. **Release candidate** — freeze one source commit and build both end-user formats from that exact state.
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

Packaging QA established the intended user flow for game selection:

- **Browse** selects a directory only and does not auto-validate;
- **Validate** performs the explicit native-game validation once;
- Apply remains disabled until validation succeeds;
- changing the selected path invalidates the prior validation and disables Apply until the new path is validated.

The GUI must still revalidate inside Apply/Restore transactions for safety; that service-level validation is not a replacement for the explicit user-facing Validate step.

## Release gates

A public release requires all of the following:

- Flatpak and AppImage launch without user-managed Python/PySide6 setup;
- both artifacts exclude inherited game archives, preset payloads, replacement assets, private QA, backups, and other non-redistributable or sensitive material;
- packaged game-folder access is validated without unnecessarily broad permissions;
- AppImage build tooling is pinned and its compatibility baseline is deliberate rather than inherited accidentally from the developer host;
- UI polish is complete enough for a normal first-time user;
- packaged Bazzite Apply/Restore behavior passes with the existing transaction safeguards;
- final artifacts are tied to the accepted release commit and version;
- publication receives explicit approval.

GitHub Actions are not part of this workflow unless separately approved.
