# Release workflow

Milestone 1 gameplay parity is complete. Release work follows this order:

1. **Flatpak proof** — prove the existing native GUI launches from a bounded, provenance-safe Flatpak and can reach a user-selected native game installation without depending on host Python or PySide6. **Complete on physical Bazzite.**
2. **AppImage proof** — prove a portable one-file AppImage can launch the same application without a user-managed Python/PySide6 environment. **Complete on physical Bazzite.**
3. **Shared packaging hardening** — keep application behavior shared between formats, harden resource/config paths and metadata, pin external build tooling, define the AppImage compatibility baseline, and keep provenance-sensitive inherited content out of both artifacts. **Complete on physical Bazzite.**
4. **UI polish** — improve first-run flow, game-folder selection, hierarchy, spacing, wording, status/error presentation, Apply/Restore affordances, iconography, window behavior, and version/about information. Validate the packaged UI rather than only a development checkout. **Complete with explicit maintainer visual and behavioral approval on physical Bazzite.**
5. **Release candidate** — freeze one source commit and build both end-user formats from that exact state. **Complete at `c3e3b97494058e8da199658f4f265e3eb84f0201`.**
6. **Packaged Bazzite QA** — test the Flatpak and AppImage as users receive them: launch, select/validate native DIRDE, Apply, exact Restore, restart, and artifact/privacy checks. **Complete for both exact RC artifacts.**
7. **Final rebuild and verification** — rebuild from the unchanged frozen RC source state and repeat package-integrity checks. **Active.**
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

## Accepted release candidate

The frozen RC source commit is:

`c3e3b97494058e8da199658f4f265e3eb84f0201`

Accepted RC artifact identities:

- Flatpak: 56,117,784 bytes, SHA-256 `523e4b0921a09a1c05caa20d67cbcfe7e9090bb416d7d0520848665ced204031`;
- AppImage: 60,262,904 bytes, SHA-256 `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- AppImage maximum required glibc symbol: `GLIBC_2.34`.

The focused RC static suite passed 52 tests. The Flatpak retained the bounded permission model, and the AppImage packaging and finished-artifact ELF checks passed.

Physical Bazzite RC QA accepted both exact artifacts on 2026-08-22. Flatpak and AppImage each passed launch, Browse, explicit Validate, `Reduce sprint stamina` Apply, `Restore original`, clean close, and restart. No RC defect requiring a source fix was found.

## Final verification

Final verification must rebuild from the unchanged frozen RC commit, not from the documentation-only `release/final-verification` branch head. The final rebuild must:

- re-run the focused static/package checks;
- rebuild the Flatpak and AppImage from commit `c3e3b97494058e8da199658f4f265e3eb84f0201`;
- re-run AppImage payload and finished ELF checks;
- verify the AppImage remains byte-identical to the accepted RC AppImage;
- record authoritative host-visible artifact hashes and sizes;
- preserve the already accepted RC artifacts until verification is complete.

Because no RC source fix was required, a second gameplay or visual QA pass is not required unless the final rebuild differs unexpectedly or a new finding appears.

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
- final rebuild/verification passes from the accepted frozen source state;
- publication receives explicit approval.

GitHub Actions are not part of this workflow unless separately approved.
