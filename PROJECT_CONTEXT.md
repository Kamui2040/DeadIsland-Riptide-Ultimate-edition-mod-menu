# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- Active release branch: `release/ui-polish`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. Released-option parity is integrated on fork `main`; upstream remains untouched. New gameplay tweaks remain deferred until a separate post-parity decision.

Release sequence: Flatpak proof, AppImage proof, shared packaging hardening, UI polish, release candidate, packaged Bazzite QA, final rebuild/verification, then explicitly approved release.

## Verified native Linux baseline

Accepted physical evidence for the audited installation:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a universal requirement. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed.

## Gameplay parity and transaction safety

Integrated `main` contains **42 semantic non-default options** covering released DIRUE gameplay controls. All 42 pass disposable native candidate construction against the accepted baseline, including the formerly blocked forced-spawn modes. Representative native gameplay QA and exact pristine restore are accepted.

Choice groups fail closed. Runtime transforms validate source state, exact match counts, archive identity, and result state rather than relying on line numbers. The inherited preset ZIP payloads are not copied, installed, or packaged.

The GUI-independent application service validates selections, compatibility, archive identity, and exclusivity before mutation. It preserves a pristine backup, builds candidates in isolated temporary storage, validates before install, rechecks the live source immediately before atomic replacement, and requires pristine restore before applying a different selection over a modified live archive.

The retained pristine backup is recovery material and must not be overwritten or deleted. The GUI catalog exposes all 42 ready options and matches the semantic catalog.

## Developer/source distribution evidence

Reproducible Bazzite packaging produced byte-identical artifacts:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `f870e68409fa351caabdacd2566989f2c06b7ca1086658438a1a8105753febd3`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `72d783b2faf73f45346a916490c0bccb0830ff3ea9c0ca56d0cd724bebe7a29a`.

These are developer/source artifacts, not the primary one-click release path.

## End-user packaging

Primary targets are **Flatpak first** for SteamOS/Bazzite/Flatpak-friendly systems and **AppImage second** as the portable Linux alternative. Normal users must not need to install Python or PySide6.

### Flatpak

Physical Bazzite QA accepted the Flatpak proof on 2026-08-20. The package built and installed, imported DIRUE `0.1.0.dev0` with PySide6 `6.11.1`, retained the bounded sandbox without blanket host-filesystem or network permission, reached the selected native game through the Qt folder chooser, validated the pristine baseline, applied `Reduce sprint stamina`, restored pristine Data0 exactly, and exited cleanly.

The KDE/UDisks D-Bus disconnect warning observed during proof QA was harmless and did not block Browse, Validate, Apply, Restore, or exit.

### AppImage hardening

The initial AppImage proof passed on physical Bazzite. Shared hardening stage 1 was accepted at commit `15437a1ee0172cb79092fdc5c230759ff2d3d3bb`.

Shared hardening stage 2 was accepted at commit `f37d39165212b84954cf60c34b0d97bdec313511`:

- digest-pinned UBI 9 Python 3.11 baseline;
- glibc `2.34`, Python `3.11.13`, fixed `PYTHONHASHSEED=1`, and source-derived `SOURCE_DATE_EPOCH`;
- deterministic AppDir SHA-256 `5741e2dab0460061bc5a1d26187a8eb5323ec30a0b6187757c4cd067d5a175ce`;
- byte-identical AppImages;
- final AppImage SHA-256 `07284a312c929cd46bcc191ba9f76f3683d2134f36e912622b77656079376dd4`;
- final size `60,246,520` bytes;
- 179 ELF files audited with maximum required `GLIBC_2.34`;
- incompatible container-collected `libgcc_s.so.1` excluded and checker-enforced;
- direct packaged launch passed.

Issue #5 is closed as resolved. Portability evidence is bounded to x86-64 systems meeting the glibc 2.34 floor and target-system base-library expectations; older pre-x86-64-v2 CPUs are not proven compatible.

## UI polish — active

`release/ui-polish` is based on the accepted packaging-hardening checkpoint. The implementation includes:

- Browse selects a folder only and does not auto-validate;
- Validate performs one explicit inspection;
- editing/changing the selected path invalidates prior validation and disables Apply/Restore;
- Apply and Restore require the currently selected path to be explicitly validated, while the transaction service still revalidates for safety;
- transaction failures invalidate GUI validation state;
- successful Apply leaves Restore enabled and Apply disabled until pristine restore;
- first-run steps, game-installation grouping, clearer status wording, Activity labeling, shorter Apply/Restore labels, tooltips, packaged icon lookup, minimum window size, version display, and About information;
- stale text about unresolved forced-spawn modes is removed;
- source-level regression coverage locks the explicit validation flow without requiring PySide6 during ordinary unit discovery.

Physical packaged AppImage UI QA on 2026-08-21 accepted this flow at commit `fb46e7f9438fb218edd7673ea03621ab0f28dcf2`:

- focused GUI/catalog static tests passed;
- packaged AppImage SHA-256 `90624c9be56b50d39685dc81430a6cebcd99537be774894e557707d6bfb7ea2c`;
- packaged AppImage size `60,246,520` bytes;
- packaged launch passed;
- first-run layout and scrolling were accepted;
- Browse did not auto-validate;
- explicit Validate enabled the appropriate actions;
- editing the selected path invalidated validation immediately without implicit revalidation;
- About/version/attribution information was present;
- no game mutation occurred.

The remaining UI-polish gate is a bounded Flatpak portal-flow check to confirm the same Browse/Validate behavior still works inside the sandbox. No gameplay mutation is required.

## Validation boundary

Verified now:

- all 42 released non-default options pass native candidate construction;
- representative native gameplay QA and exact pristine restore pass;
- UI/catalog accounting passes at 42 options;
- transaction/recovery behavior is validated;
- wheel/sdist reproducibility passes;
- Flatpak build/import/sandbox/portal/Apply/Restore proof passes;
- AppImage build/payload/launch/Apply/Restore/relaunch proof passes;
- shared packaging hardening stages 1 and 2 pass;
- hardened AppImage reproducibility and `GLIBC_2.34` audit pass;
- packaged AppImage UI-polish visual and explicit-validation QA passes;
- no GitHub Actions were used.

## Remaining release gates

1. **Finish UI polish** — run the bounded Flatpak portal-flow check and fix any accepted findings.
2. **Release candidate** — freeze one exact source commit and build both primary formats from it.
3. **Packaged Bazzite QA** — exercise both release-candidate artifacts as users receive them, including launch, validation, Apply, exact Restore, restart, and artifact/privacy checks.
4. **Final rebuild/verification** after accepted RC fixes.
5. **Explicit approval** before public release/binaries, Nexus publication, upstream submission, announcements, distribution/visibility changes, or GitHub Actions use.

## Cleanup and publication

Accepted evidence, provenance material, artifact hashes, and pristine recovery material remain preserved. Disposable worktrees, build environments, temporary candidates, and superseded QA residue are removed when no longer needed. Authentic game content and backups must never be committed.

No public release, binary publication, Nexus publication, upstream submission, announcement, GitHub Actions use, or other external publication has been authorized.
