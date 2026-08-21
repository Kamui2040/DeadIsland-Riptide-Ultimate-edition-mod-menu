# Release workflow

Milestone 1 gameplay parity is complete. Release work follows this order:

1. **Flatpak proof** — complete on physical Bazzite.
2. **AppImage proof** — complete on physical Bazzite.
3. **Shared packaging hardening** — complete on physical Bazzite.
4. **UI polish** — complete with explicit maintainer visual and behavioral approval on physical Bazzite.
5. **Release candidate** — complete at frozen source commit `c3e3b97494058e8da199658f4f265e3eb84f0201`.
6. **Packaged Bazzite QA** — complete for both exact RC artifacts.
7. **Final rebuild and verification** — complete from the unchanged frozen RC source commit.
8. **Release** — integration or publication requires explicit approval.

## End-user acceptance

Normal packaged users must not need to install Python, create a virtual environment, install PySide6, or use development commands to run the GUI.

- **Flatpak** is the first-class target for Bazzite, SteamOS, and other Flatpak-friendly Linux systems.
- **AppImage** is the portable x86-64 Linux alternative.
- Wheel and sdist artifacts remain source/developer distribution formats, not the primary one-click user path.

SteamOS is treated as an operating-system target rather than as a Steam Deck-only target. Bazzite testing does not establish Steam Deck- or Steam Machine-specific hardware validation.

## Accepted UI flow

The accepted game-selection flow is:

- **Browse** selects a directory only and does not auto-validate;
- **Validate** performs explicit native-game validation;
- Apply remains disabled until validation succeeds;
- changing the selected path invalidates prior validation and disables Apply until the new path is validated.

The GUI still revalidates inside Apply/Restore transactions for safety. Service-level validation does not replace the explicit user-facing Validate step.

Packaged Bazzite review accepted first-run clarity, hierarchy/spacing, status/error presentation, Apply/Restore affordances, iconography, window behavior, and version/About presentation. The main window and About dialog received explicit maintainer visual approval.

The Flatpak icon export also passed direct checks: scalable SVG and 64x64/128x128 PNG variants are present, raster dimensions are correct, and GTK resolves the application ID to the exported icon. Bazaar's remaining generic icon for the locally installed Flatpak is treated as an external sideload/display limitation rather than a DIRDE packaging defect.

## Frozen release source

The frozen release source commit is:

`c3e3b97494058e8da199658f4f265e3eb84f0201`

No RC defect required a source fix, so this source state remained unchanged through final verification.

## RC artifacts and physical QA

The exact RC artifacts were:

- Flatpak: 56,117,784 bytes, SHA-256 `523e4b0921a09a1c05caa20d67cbcfe7e9090bb416d7d0520848665ced204031`;
- AppImage: 60,262,904 bytes, SHA-256 `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- AppImage maximum required glibc symbol: `GLIBC_2.34`.

The focused RC static suite passed 52 tests before packaging.

Physical Bazzite RC QA on 2026-08-22 exercised those exact hashes. Both formats passed launch, Browse, explicit Validate, `Reduce sprint stamina` Apply, `Restore original`, close, and restart. The Flatpak also passed bounded permission inspection before launch.

## Final rebuild and verification

Final verification rebuilt both formats from the same unchanged frozen source commit on physical Bazzite on 2026-08-22.

Results:

- focused static/package tests: PASS;
- final-verification Flatpak: 56,114,672 bytes, SHA-256 `1eec07e171303cf55b2ce4cfd944e543ced05a7ff05ef74a82368560c1bdc073`;
- final AppImage: 60,262,904 bytes, SHA-256 `0484d85e33707d3ab8701a6c05fc96ad2a980c299a3de1374097b8b6f57bf6a5`;
- final AppImage is byte-identical to the exact AppImage already exercised during packaged Bazzite RC QA;
- finished AppImage GLIBC audit: PASS with maximum required `GLIBC_2.34`.

The final-verification Flatpak differs in bundle bytes from the earlier RC Flatpak. Flatpak bundle byte reproducibility was not a release gate, so that difference is recorded rather than treated as a source regression.

The exact-artifact boundary must remain clear:

- physical Apply/Restore/restart QA applies directly to Flatpak SHA-256 `523e4b0921a09a1c05caa20d67cbcfe7e9090bb416d7d0520848665ced204031`;
- Flatpak SHA-256 `1eec07e171303cf55b2ce4cfd944e543ced05a7ff05ef74a82368560c1bdc073` is the later final-verification rebuild from the same frozen source state and passed the final static/package build-integrity checks;
- the final AppImage requires no such distinction because its final rebuild is byte-identical to the physically exercised RC AppImage.

No second gameplay or visual pass was required because no source fix occurred after RC acceptance. This does not make the two Flatpak hashes identical evidence; documentation and release handoff must continue to identify which bundle received which validation.

## Release gate

Technical validation of the frozen release source state is complete. The remaining gate is **explicit approval** before any of the following:

- main integration;
- public Flatpak or AppImage publication;
- Nexus publication;
- upstream submission;
- announcements;
- distribution or repository visibility changes;
- GitHub Actions use.

No release artifact should be described as published or generally available until that approval and publication actually occur. Artifact selection for an approved release must use the recorded hashes above and preserve the exact-artifact QA distinction.

GitHub Actions are not part of this workflow unless separately approved.
