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

## Repository safety and privacy

Treat every tracked file, commit, Issue, pull request, review comment, and other repository submission as future-public.

Before submitting anything to the repository, check it for credentials, tokens, private identifiers, private URLs, personal or machine-specific paths, storage topology, raw private QA, signing or recovery material, authentic game backups, proprietary game binaries, extracted game assets, and maintainer-only workflow. Remove or sanitize private material before submission; keep it private when sanitizing would remove its value.

The inherited upstream `Data0.pak` is historical upstream material. Linux-port code must not use it as an installation payload or treat it as the source archive for patching.

## Autonomy and communication

- Work autonomously on routine safe repository inspection, implementation, tests, documentation, Issues, branches, commits, pull requests, validation, maintenance, and cleanup.
- Do not hand routine repository work to the user when connected tools can do it safely.
- Ask for manual execution only when work genuinely requires the user's physical Bazzite/game machine and that machine is unavailable to tools, such as native-game execution, local filesystem state, or visual/gameplay QA.
- Keep manual handoffs minimal and deterministic.
- Terminal handoffs must start with `clear`, suppress routine command/build/test output, and print only the final concise PASS/FAIL result block. On failure, include only the bounded diagnostics needed to act.
- For interactive handoffs run as `bash -s <<'EOF'`, read human responses explicitly from `/dev/tty`, never inherited stdin, and verify any required external process actually starts and exits before accepting observations.
- When embedded Python in a shell handoff reads `os.environ`, pass every required shell value explicitly on that Python invocation; do not rely on unexported shell variables.
- Before comparing filesystem paths, canonicalize existing paths and compare the canonical values; symlink or mount aliases are not evidence of different locations.
- Parse command output by fields or delimiters instead of relying on exact whitespace formatting.
- For containerized packaging, do not infer host artifact paths from container paths. The wrapper must verify the artifact is visible on the host and emit an authoritative host path/hash for handoffs to consume.
- When a container command reads a here-document or other stdin-driven script, attach stdin explicitly and verify the intended side effect before treating a zero exit as success.
- When a handoff invokes a Python CLI module, verify that the invocation executes the CLI entrypoint and produces the expected output or artifact; a zero exit from an import-only module is not evidence of execution.
- For gameplay QA after candidate installation, use a bounded automatic process-start wait rather than a one-shot keypress-gated start check; accept observations only after verified native-game start and exit.
- Use simple, natural, direct language in repository submissions and project chat. Avoid needless jargon, robotic phrasing, and long explanations.

## Data0 transaction rules

The Linux port must operate on the user's installed `DIR/Data0.pak`:

1. Discover or accept the game root.
2. Validate the native Linux installation and input archive.
3. Preserve a recoverable pristine original before the first write.
4. Work only in temporary storage.
5. Apply selected transformations with explicit preconditions.
6. Rebuild and validate the candidate archive.
7. Before replacement, require the live archive and pristine backup to match the candidate source identity and reject entry-count drift.
8. Recheck the live source hash immediately before atomic replacement.
9. Replace the live archive atomically only after validation passes.
10. Retain recovery material and clean proven-obsolete temporary files.

Never perform an in-place partial rewrite of the live archive. Never install over an unexpected live state. A failed validation must leave the live archive unchanged. Validate backup identity before restore, while still permitting recovery when the live archive is missing or corrupt.

## Patch-engine standards

- Keep the patch engine independent from the GUI and callable deterministically from tests/CLI code.
- Prefer semantic targeting (property/key/block identity plus expected old value) over hard-coded line numbers.
- Require unambiguous matches. Zero or multiple matches are failures unless the patch definition explicitly permits them.
- Validate expected source state before mutation and expected result after mutation.
- Preserve file encoding, newline conventions, and archive paths unless a tested transformation requires otherwise.
- Preserve observed native whitespace/layout variants in semantic-anchor regression fixtures; do not normalize them away when spacing is part of the accepted source shape.
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

- Keep `main` stable and review changes before integration.
- Perform Linux-port work on `linux-port` or focused branches derived from the current validated base.
- Do not force-push or rewrite shared/default history.
- Preserve unrelated work.
- Do not add, trigger, query, monitor, or depend on GitHub Actions for the PC workflow unless explicitly approved.
- Public releases, Nexus publication, upstream submissions, main integration, and other external publication require explicit approval.

## QA

- The installed Steam game is a QA target, not a development workspace.
- Never copy test-game content into the repository.
- Before any QA write to the installed game, verify the target archive and backup state and use the transaction path implemented by the project.
- When validating numeric gameplay changes through an in-game UI, do not assume a raw data value is displayed directly; establish the pristine-to-UI relationship or use an A/B comparison before asserting an exact displayed value.
- Reproducible distribution QA must build the wheel and sdist twice from the same head with a fixed `SOURCE_DATE_EPOCH`; source archives must normalize member order, ownership, timestamps, and gzip metadata before byte comparison.
- Packaging handoffs must provision required non-project build tooling in a disposable isolated environment with an explicit version instead of assuming it exists in the host Python environment.
- Before adopting a PyInstaller container baseline, pin the image by digest and verify its glibc floor, exact Python version, shared `libpython`, required extension modules, and pip; prefer a verified packaged interpreter over an ad hoc source build.
- When a new runtime module is added, distribution validation must require that module in both wheel and sdist payload checks before packaging can be accepted.
- Record sanitized validation evidence where useful; do not record personal paths or identifiers in tracked files.

## Maintenance and cleanup

Cleanup is continuous maintenance, not an end-of-task step.

- At the start, during, and end of each meaningful work unit, classify residue and remove only items proven obsolete when safe.
- Regularly maintain repository worktrees, the local mirror, project docs, private evidence, temporary extracts, fixtures, build outputs, and QA artifacts.
- Remove stale temporary data, duplicate notes, redundant evidence, and superseded scripts when their replacement is verified.
- For versioned QA report files, delete superseded local report generations in the same work unit once replacement evidence is accepted and no unresolved work still depends on them; manual QA handoffs must clean prior report outputs, not only `/tmp` files.
- Preserve accepted evidence, unresolved diagnostics, provenance and licensing material, pristine backups, hashes and manifests, authentic user data, unrelated work, and Git history.
- Never delete uncertain material or keep extracted game contents longer than needed.

## Project state

`PROJECT_CONTEXT.md` is the canonical concise record of current milestone, verified compatibility state, implementation status, and remaining gates. Update it when verified project state materially changes.
