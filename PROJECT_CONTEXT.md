# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. On 2026-08-16, the validated Linux-port implementation was explicitly approved for main integration and fast-forwarded into `main` without rewriting history. `linux-port` is retained as the development branch and should remain aligned unless new work intentionally diverges.

New gameplay tweaks remain deferred until released parity is fully resolved. Four released forced-spawn choices remain intentionally unavailable because their required target identifiers cannot currently be reconstructed or redistributed under the accepted provenance boundary. This durable unresolved gate is tracked in Issue #2.

## Verified native Linux baseline

Accepted physical evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a permanent compatibility requirement. The current application layer intentionally uses it as the only first-backup compatibility baseline until additional native baselines are independently validated. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Current implementation state

The catalog contains **38 semantic non-default options**, and all 38 pass disposable native candidate construction against the accepted 3060-entry baseline.

Native-validated families include:

- direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, and vehicle noclip;
- One Hit, Hard, and Headshot Only AI;
- Better Firearms Upgrading and Better Firearms POV 62/72/82;
- camera FOV 72/82;
- extra-small, midget, large, and supersize zombie modes;
- all eight non-default weather/time choices;
- forced Suiciders, bandits with guns, and bandits with melee.

Choice groups fail closed on incompatible selections. Runtime transforms are semantic and validate expected source state, match counts, archive identity, and result state rather than using historical line numbers.

A material maximal compatible candidate spanning direct controls, Hard AI, Better Firearms Upgrading/POV82, camera FOV82, supersize zombies, armed-bandit spawning, and darker storm night also passes with all 3060 entries retained.

## Forced-spawn provenance boundary

Default spawning matches native behavior. Implemented forced-spawn modes validate the complete pristine 165-call `m_AIPresets` vector before mutation.

- **Suiciders**: derived from a validated pristine donor; Native-validated and gameplay-validated.
- **Bandits with guns**: derived from a validated pristine donor; Native-validated.
- **Bandits with melee**: reconstructed entirely from validated whole tokens already present in the pristine native vector; Native-validated.

**Butcher, Ram, Bloater, and Thug remain unavailable.** Accepted audits found no exact pristine donor and no acceptable bounded whole-token reconstruction from the audited native spawn vector or bounded AI/preset source set. The project will not widen this into arbitrary archive-string assembly, character-level encoding, or embedding provenance-sensitive target identifiers. Revisit only if materially new provenance/rights evidence or an equally narrow semantic derivation appears.

## Replacement and redistribution boundary

The released Windows workflow unconditionally copied bundled `data/game.ini` and `data/menu/scr/menumain_pc.xui` replacements. Sanitized native comparison established that those files only add branding/cosmetic behavior and are not required for gameplay parity. The Linux runtime and distributions therefore do not copy or redistribute them.

The inherited upstream `Data0.pak`, preset ZIPs, replacement assets, and other provenance-sensitive historical material are not Linux installation payloads. The installed native game archive is always the patch source.

## Application, GUI, and transaction safety

The GUI-independent application service validates selections, compatibility, archive identity, and exclusivity before any mutation. It creates a retained pristine backup only from a recognized baseline, builds candidates in isolated temporary storage, validates them before installation, rechecks the live source immediately before atomic replacement, and requires pristine restore before applying a different selection over an already modified live archive.

The PySide6 GUI exposes all 38 ready options exactly once. The four unresolved forced-spawn choices are visible but disabled. Real on-screen Bazzite QA passes for layout, scrolling, grouping, selector behavior, readability, disabled-state clarity, and the confirmation-driven Apply/Restore workflow.

Native transaction QA passes at both engine and GUI/application levels. Accepted tests prove exact candidate installation, apply lock/reapply rejection while modified, exact-original restore, and retained pristine backup recovery. The live game is pristine after accepted transaction and gameplay tests.

The retained pristine backup is recovery material and must not be deleted or overwritten.

## Accepted native gameplay evidence

Representative physical Bazzite gameplay QA validates:

- camera FOV82;
- Better Firearms POV82;
- darker storm/night;
- Run with weapons;
- One Hit AI;
- supersize behavior on active infected and walker AI;
- Forced Suiciders;
- Better Firearms Upgrading.

Sessions remained playable and each bounded mutation test ended with exact pristine restore.

Supersize behavior matches the released four-member preset semantics. Some corpse-decoy/ground actors may remain normal-sized even though active infected and walkers can be supersized; that observed entity-state variation is treated as upstream/native behavior rather than expanded beyond released parity.

Better Firearms Upgrading was validated on the same fully upgraded Magnum/revolver path before and after mutation. The pristine UI reload value `4.5` and modified value `3.6` preserve the same `1.125` multiplier implied by accepted raw values `4.0 -> 3.2`; the earlier expectation that the UI would display raw `3.2` directly was a QA-model error, not a runtime defect.

## Packaging and distribution validation

Physical Bazzite packaging QA passes for the real repository state. The build system pins `setuptools==83.0.0`, uses a repo-local deterministic PEP 517 backend wrapper, disables implicit package-data inclusion, and explicitly excludes provenance-sensitive inherited payloads from the source distribution.

Two clean builds under the same commit-derived `SOURCE_DATE_EPOCH` produced byte-identical artifacts:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `062feed8162f67c23877e20bbb7588bc0cda17edb49f79c0fba902d3c0c9f076`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `47732086c7f078750be956f239b26c58cd2d6cdd6eb84862e2b48565c34ea06f`.

The distribution checker passes, deterministic sdist metadata normalization passes, the wheel installs in isolation, `pip check` passes, CLI help works, and both CLI and GUI entry-point metadata are present. Packaging QA left the repository clean and did not mutate the game archive or pristine backup.

## Validation and QA rules

- All 38 current catalog options pass native disposable candidate construction.
- Native-tested choice conflicts reject incompatible selections.
- Material multi-family interactions pass.
- Engine and GUI/application transaction QA pass with exact-original recovery.
- Representative gameplay QA covers direct controls, AI, camera/POV, firearm upgrading, zombie size, weather/time, and forced spawning.
- Reproducible wheel/sdist packaging and artifact payload-safety checks pass.
- No GitHub Actions were used.

Interactive `bash -s <<'EOF'` handoffs must read human input from `/dev/tty`; gameplay handoffs should automatically poll for the native game process rather than relying on a keypress-timed start check. Embedded Python must receive required shell values explicitly through its invocation environment. Numeric gameplay QA must distinguish raw data values from derived UI values.

## Remaining gates

1. Keep Butcher, Ram, Bloater, and Thug unavailable under the current provenance boundary unless materially new evidence changes that boundary.
2. Additional gameplay QA should be bounded to a specific newly identified risk; representative coverage is sufficient for the current implementation set.
3. Public releases/binaries, Nexus publication, upstream submission, announcements, and other publication or visibility changes still require explicit approval.

## Cleanup and publication

Accepted evidence, provenance material, reproducible-build hashes, and the pristine recovery backup remain preserved. Superseded failed QA harness outputs and temporary build/extraction residue are obsolete and should be removed when safe; authentic game content and backups must never be committed.

Main integration was explicitly approved and completed by fast-forward on 2026-08-16. No public release, binary publication, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized.
