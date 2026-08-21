# Release workflow

Milestone 1 gameplay parity is complete. Release work follows this order:

1. **Flatpak proof** — complete on physical Bazzite.
2. **AppImage proof** — complete on physical Bazzite.
3. **Shared packaging hardening** — complete on physical Bazzite.
4. **UI polish** — complete with explicit maintainer visual and behavioral approval on physical Bazzite.
5. **Release candidate** — complete at frozen source commit `c3e3b97494058e8da199658f4f265e3eb84f0201`.
6. **Packaged Bazzite QA** — complete for both exact RC artifacts.
7. **Final rebuild and verification** — complete from the unchanged frozen RC source commit.
8. **Release** — publication or integration requires explicit approval.

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

Final verification rebuilt both end-user formats from the unchanged frozen RC commit `c3e3b97494058e8da199658f4f265e3eb84f0201` on physical Bazzite on 2026-08-22.

Accepted final-verification results:

- focused static/package tests: PASS;
- final Flatpak: 56,114,672 bytes, SHA-256 `1eec07e171303cf55b2ce4cfd944e543ced05a7ff05ef74a82368560c1bdc073`;
- final AppImage: 60,262,904 bytes, SHA-256 `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- final AppImage is byte-identical to the accepted RC AppImage;
- finished AppImage GLIBC audit: PASS with maximum required `GLIBC_2.34`.

The final Flatpak bundle differs in container hash/size from the earlier RC bundle. Flatpak bundle byte reproducibility was not a release gate; both were built from the same frozen source state and passed the required package checks. No source fix occurred between RC acceptance and final verification, so no second gameplay or visual QA pass was required.

## Release gates

All technical gates are complete. The accepted release state has:

- Flatpak and AppImage launch without user-managed Python/PySide6 setup;
- packaging excludes inherited game archives, preset payloads, replacement assets, private QA, backups, and other non-redistributable or sensitive material from the end-user artifacts;
- packaged game-folder access works without unnecessarily broad Flatpak permissions;
- AppImage build tooling and compatibility baseline are pinned and validated;
- maintainer-approved custom icon and packaged UI presentation;
- both RC artifacts tied to one exact frozen source commit with recorded identities;
- packaged Bazzite Validate/Apply/Restore/restart acceptance for both formats;
- final rebuild/verification from the unchanged frozen source state;
- final AppImage byte identity with the accepted RC and `GLIBC_2.34` finished-artifact audit.

The remaining gate is **explicit approval** before main integration, public release/binaries, Nexus publication, upstream submission, announcements, distribution/visibility changes, or GitHub Actions use.

GitHub Actions are not part of this workflow unless separately approved.
