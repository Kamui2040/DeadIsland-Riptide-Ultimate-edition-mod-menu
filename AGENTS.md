# AGENTS.md

## Scope

These rules apply to the entire repository.

## Project purpose

This repository is the Linux-native port of FireEyeEian's Dead Island Riptide Ultimate Edition mod menu (DIRUE), targeting the native Linux build of Dead Island: Riptide Definitive Edition.

Milestone 1 is feature parity with the existing DIRUE release. Do not add or redesign gameplay tweaks until parity is implemented and validated.

## Compatibility boundary

- Target the native Linux game executable and data layout.
- Do not build a Wine wrapper, Proton frontend, Windows launcher, or general-purpose mod manager.
- Treat `DIRUE.ahk` as the behavioral specification for Milestone 1.
- Replace Windows-only implementation details rather than emulating them.

## Licensing and provenance

- Preserve GNU GPLv3 and original FireEyeEian attribution.
- Keep source available for distributed builds.
- Clearly identify Linux-port modifications.
- Do not assume the GPL license of this repository grants redistribution rights for Techland game content.
- Keep provenance and redistribution decisions documented in `docs/PROVENANCE.md`.

## Repository safety

Tracked content must remain suitable for a future public repository. Never commit credentials, tokens, private URLs, personal information, machine-specific personal paths, device identifiers, sensitive logs, authentic game backups, proprietary game binaries, or extracted game assets unless redistribution rights are explicitly established.

The inherited upstream `Data0.pak` is historical upstream material. Linux-port code must not use it as an installation payload or treat it as the source archive for patching.

## Data0 transaction rules

The Linux port must operate on the user's installed `DIR/Data0.pak`:

1. Discover or accept the game root.
2. Validate the native Linux installation and input archive.
3. Preserve a recoverable pristine original before the first write.
4. Work only in temporary storage.
5. Apply selected transformations with explicit preconditions.
6. Rebuild and validate the candidate archive.
7. Replace the live archive atomically only after validation passes.
8. Retain recovery material and clean proven-obsolete temporary files.

Never perform an in-place partial rewrite of the live archive. A failed validation must leave the live archive unchanged.

## Patch-engine standards

- Keep the patch engine independent from the GUI and callable deterministically from tests/CLI code.
- Prefer semantic targeting (property/key/block identity plus expected old value) over hard-coded line numbers.
- Require unambiguous matches. Zero or multiple matches are failures unless the patch definition explicitly permits them.
- Validate expected source state before mutation and expected result after mutation.
- Preserve file encoding, newline conventions, and archive paths unless a tested transformation requires otherwise.
- Keep gameplay values faithful to upstream during Milestone 1.
- Record every user-facing option with target file(s), upstream/default state, modified state, and any replacement/preset dependency.

## Architecture

Keep responsibilities separated:

- game discovery and compatibility validation
- archive extraction/rebuild/validation
- declarative patch definitions
- patch engine
- backup/restore and transactional replacement
- CLI/test surface
- Linux-native GUI (currently expected to use Python and PySide6)
- packaging, only after parity validation

## Git workflow

- Keep `main` stable and close to the inherited upstream state until changes are reviewed.
- Perform Linux-port work on `linux-port` or focused branches derived from it.
- Do not force-push or rewrite shared/default history.
- Preserve unrelated work.
- Do not add GitHub Actions or other cloud CI for the PC workflow; validation is local and deterministic.
- Public releases, Nexus publication, upstream submissions, and other external publication require an explicit project decision.

## QA

- The installed Steam game is a QA target, not a development workspace.
- Never copy test-game content into the repository.
- Before any QA write to the installed game, verify the target archive and backup state and use the transaction path implemented by the project.
- Record sanitized validation evidence where useful; do not record personal paths or identifiers in tracked files.

## Project state

`PROJECT_CONTEXT.md` is the canonical concise record of current milestone, verified compatibility state, implementation status, and remaining gates. Update it when verified project state materially changes.
