# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Primary branch: `main`
- Development branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. On 2026-08-16, the validated Linux-port implementation was explicitly approved for main integration and fast-forwarded into `main` without rewriting history. `linux-port` is retained as the development branch and should remain aligned unless new work intentionally diverges.

Focused branch `agent/forced-spawn-identifiers` resolves the four previously blocked Butcher, Ram, Bloater, and Thug forced-spawn choices using narrowly scoped machine-facing compatibility identifiers extracted read-only from the inherited upstream preset blobs. The preset archives themselves remain excluded from Linux runtime/distribution use. All four new transforms pass disposable native candidate validation and bounded native gameplay QA with exact pristine restore after every mutation. Released-option gameplay parity is therefore complete on the focused branch. `main` remains unchanged until explicit integration approval.

New gameplay tweaks remain deferred until this validated parity branch is reviewed and integrated.

## Verified native Linux baseline

Accepted physical evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a permanent compatibility requirement. The current application layer intentionally uses it as the only first-backup compatibility baseline until additional native baselines are independently validated. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Current implementation state

Integrated `main` contains **38 semantic non-default options**. Focused branch `agent/forced-spawn-identifiers` contains **42 semantic non-default options** after adding Butcher, Ram, Bloater, and Thug forced spawning. All 42 branch options pass disposable native candidate construction against the accepted 3060-entry baseline.

Native-validated families include:

- direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, and vehicle noclip;
- One Hit, Hard, and Headshot Only AI;
- Better Firearms Upgrading and Better Firearms POV 62/72/82;
- camera FOV 72/82;
- extra-small, midget, large, and supersize zombie modes;
- all eight non-default weather/time choices;
- forced Suiciders, bandits with guns, bandits with melee, Butchers, Rams, Bloaters, and Thugs on the focused branch.

Choice groups fail closed on incompatible selections. Runtime transforms are semantic and validate expected source state, match counts, archive identity, and result state rather than using historical line numbers.

A material maximal compatible candidate spanning direct controls, Hard AI, Better Firearms Upgrading/POV82, camera FOV82, supersize zombies, armed-bandit spawning, and darker storm night also passes with all 3060 entries retained.

## Forced-spawn provenance boundary

Default spawning matches native behavior. Implemented forced-spawn modes validate the complete pristine 165-call `m_AIPresets` vector before mutation.

- **Suiciders**: derived from a validated pristine donor; Native-validated and gameplay-validated.
- **Bandits with guns**: derived from a validated pristine donor; Native-validated.
- **Bandits with melee**: reconstructed entirely from validated whole tokens already present in the pristine native vector; Native-validated.
- **Butcher, Ram, Bloater, and Thug**: focused-branch implementations use only the minimal machine-facing compatibility identifier lists required to reproduce the released transforms. The identifiers are pinned by digest and syntax/count validation; each released mode preserves ordinal 60 and replaces the other 164 active calls. No preset archive or replacement file is reused by the Linux runtime.

Accepted physical candidate QA for the four new modes proves that each candidate retains all 3060 entries, changes only `data/presets/aispawnbox_pre.def`, preserves the released ordinal-60 exception, replaces exactly the other 164 active calls, validates ZIP integrity/member order and candidate hashes, and leaves the live pristine Data0 unchanged.

Accepted bounded native gameplay QA then installed each of Butchers, Rams, Bloaters, and Thugs through the normal application transaction path, verified the intended forced-spawn behavior in the native game, exited the native ELF process, and restored the exact pristine Data0 before recording each observation. The retained pristine backup remained valid and unchanged throughout.

This narrow compatibility treatment does not establish or claim redistribution rights over the inherited preset ZIPs or other game-derived assets. Those remain provenance-sensitive historical material and stay excluded from Linux runtime/distribution payloads.

## Replacement and redistribution boundary

The released Windows workflow unconditionally copied bundled `data/game.ini` and `data/menu/scr/menumain_pc.xui` replacements. Sanitized native comparison established that those files only add branding/cosmetic behavior and are not required for gameplay parity. The Linux runtime and distributions therefore do not copy or redistribute them.

The inherited upstream `Data0.pak`, preset ZIPs, replacement assets, and other provenance-sensitive historical material are not Linux installation payloads. The installed native game archive is always the patch source.

## Application, GUI, and transaction safety

The GUI-independent application service validates selections, compatibility, archive identity, and exclusivity before any mutation. It creates a retained pristine backup only from a recognized baseline, builds candidates in isolated temporary storage, validates them before installation, rechecks the live source immediately before atomic replacement, and requires pristine restore before applying a different selection over an already modified live archive.

The integrated GUI exposes all 38 `main` options exactly once. On `agent/forced-spawn-identifiers`, the four new spawn choices are enabled, raising the ready catalog to 42. UI/catalog tests verify all released spawn choices are available and the ready UI catalog matches the semantic catalog exactly. Existing real on-screen Bazzite QA passes for layout, scrolling, grouping, selector behavior, readability, and the confirmation-driven Apply/Restore workflow.

Native transaction QA passes at both engine and GUI/application levels. Accepted tests prove exact candidate installation, apply lock/reapply rejection while modified, exact-original restore, and retained pristine backup recovery. The four new forced-spawn gameplay runs also passed the same transaction path with exact pristine restore after each mode. The live game is pristine after accepted transaction and gameplay tests.

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
- Better Firearms Upgrading;
- Forced Butchers;
- Forced Rams;
- Forced Bloaters;
- Forced Thugs.

Sessions remained playable and each bounded mutation test ended with exact pristine restore.

Supersize behavior matches the released four-member preset semantics. Some corpse-decoy/ground actors may remain normal-sized even though active infected and walkers can be supersized; that observed entity-state variation is treated as upstream/native behavior rather than expanded beyond released parity.

Better Firearms Upgrading was validated on the same fully upgraded Magnum/revolver path before and after mutation. The pristine UI reload value `4.5` and modified value `3.6` preserve the same `1.125` multiplier implied by accepted raw values `4.0 -> 3.2`; the earlier expectation that the UI would display raw `3.2` directly was a QA-model error, not a runtime defect.

## Packaging and distribution validation

Physical Bazzite packaging QA passes for the integrated 38-option state. The build system pins `setuptools==83.0.0`, uses a repo-local deterministic PEP 517 backend wrapper, disables implicit package-data inclusion, and explicitly excludes provenance-sensitive inherited payloads from the source distribution.

Two clean builds under the same commit-derived `SOURCE_DATE_EPOCH` produced byte-identical artifacts:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `062feed8162f67c23877e20bbb7588bc0cda17edb49f79c0fba902d3c0c9f076`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `47732086c7f078750be956f239b26c58cd2d6cdd6eb84862e2b48565c34ea06f`.

The distribution checker passes, deterministic sdist metadata normalization passes, the wheel installs in isolation, `pip check` passes, CLI help works, and both CLI and GUI entry-point metadata are present. Packaging QA left the repository clean and did not mutate the game archive or pristine backup.

The focused 42-option branch adds a new packaged Python module and fixes direct `python -m dirue.cli` execution. Candidate/gameplay validation proves the runtime behavior, and a CLI subprocess regression test proves direct module invocation now executes. A fresh distribution build has not yet been accepted for this branch, so the earlier reproducible artifact hashes remain evidence only for the integrated 38-option state.

## Validation and QA rules

- All 38 integrated catalog options pass native disposable candidate construction; all 42 focused-branch options pass it as well.
- Native-tested choice conflicts reject incompatible selections.
- Material multi-family interactions pass for the integrated state.
- Engine and GUI/application transaction QA pass with exact-original recovery.
- Representative gameplay QA covers direct controls, AI, camera/POV, firearm upgrading, zombie size, weather/time, and all released forced-spawn families, including the four newly resolved modes.
- Reproducible wheel/sdist packaging and artifact payload-safety checks pass for the integrated state; the focused 42-option branch still needs a bounded packaging refresh before integration because it adds a packaged module and CLI-entry behavior.
- No GitHub Actions were used.

Interactive `bash -s <<'EOF'` handoffs must read human input from `/dev/tty`; gameplay handoffs should automatically poll for the native game process rather than relying on a keypress-timed start check. Embedded Python must receive required shell values explicitly through its invocation environment. Numeric gameplay QA must distinguish raw data values from derived UI values. Existing filesystem paths must be canonicalized before comparison, command output must be parsed structurally rather than by exact whitespace, and a CLI handoff must verify its expected output or artifact instead of treating exit status alone as proof of execution.

## Remaining gates

1. Run a bounded packaging refresh for the focused 42-option branch to verify the new module is present in built distributions and direct CLI execution works from the installed wheel; do not repeat unrelated gameplay QA.
2. After that validation, request explicit approval before integrating `agent/forced-spawn-identifiers` into `main` and realigning `linux-port`.
3. Public releases/binaries, Nexus publication, upstream submission, announcements, and other publication or visibility changes still require explicit approval.

## Cleanup and publication

Accepted evidence, provenance material, reproducible-build hashes, and the pristine recovery backup remain preserved. Superseded failed QA harness outputs and temporary build/extraction residue are obsolete and should be removed when safe; authentic game content and backups must never be committed.

Main integration was explicitly approved and completed by fast-forward on 2026-08-16. No public release, binary publication, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized.