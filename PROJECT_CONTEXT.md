# PROJECT_CONTEXT.md

## Repository and milestone

- Upstream: `Fireeyeeian/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Fork: `Kamui2040/DeadIsland-Riptide-Ultimate-edition-mod-menu`
- Stable branch: `main`
- Active branch: `linux-port`
- License: GNU GPLv3, inherited and preserved

Milestone 1 is a faithful native-Linux port of released DIRUE behavior. New gameplay tweaks remain deferred until released parity is implemented and validated.

## Verified native Linux baseline

Accepted physical evidence:

- native ELF `DeadIslandRiptideGame`;
- ZIP-compatible `DIR/Data0.pak`;
- 3060 archive entries;
- archive size 7,932,941 bytes;
- SHA-256 `0afeadca8fb84147cc2c815ec37d1f3c940d40fab6c0a343b7b84e7f41d3c991`.

The hash is evidence for the audited installation, not a permanent compatibility requirement. The current GUI application layer intentionally uses it as the only first-backup compatibility baseline until additional native baselines are independently validated. Raw local reports, machine-specific paths, extracted game content, authentic backups, and temporary candidates are not committed to Git.

## Candidate catalog

The catalog contains **38 semantic non-default options**, and all 38 pass disposable native candidate construction against the accepted 3060-entry baseline.

Native-validated families include direct gameplay controls, Deeper Pockets, Improved Loot, intro skipping, reverb removal, vehicle noclip, One Hit / Hard / Headshot Only AI, Better Firearms Upgrading, Better Firearms POV 62/72/82, camera FOV 72/82, four non-default zombie-size modes, all eight non-default weather/time choices, forced Suiciders, forced bandits with guns, and forced bandits with melee.

Default camera FOV 62.5, normal zombie size, normal AI, default spawns, and vanilla weather/time are pristine-baseline states represented by absence of a non-default patch.

Choice groups fail closed on conflicting selections: One Hit / Hard / Headshot Only AI, the three Better Firearms POV variants, camera FOV 72/82, four non-default zombie sizes, eight non-default weather/time modes, and the three implemented forced-spawn modes.

A material maximal compatible candidate including Hard AI, Better Firearms Upgrading/POV82, camera FOV82, supersize zombies, armed-bandit spawn forcing, darker storm night, and the compatible direct options also passes while retaining 3060 entries.

## Firearm reconstruction

Accepted source-map evidence accounts for 744 active released firearm targets. Runtime transforms use contiguous repeated same-name `Item(...)` groups, complete call sequences, `UpgradeLevel(0,0,1,1,2,2,3,3)` marker validation, semantic insertions, and CRLF preservation. Historical line numbers are never runtime targets.

Better Firearms Upgrading accounts for all 157 active targets: 58 existing-call changes plus 99 tier-local `ShotTime`/`ReloadTime` insertions. Better Firearms POV plus matching sway accounts for 177/177 active targets at FOV 62 and 205/205 at FOV 72 and 82.

Corrected recoil evidence maps the four authored shotgun/Crowd tier calls to blocks 2/4/6/8 of each eight-block item group. Camera FOV 72/82 candidates and material FOV/Upgrading/POV interactions pass.

## Preset-backed controls

### AI difficulty

Normal is baseline. One Hit, Hard, and Headshot Only are native-candidate validated and mutually exclusive. Hard is reconstructed as 209 named `ParamFloat` edits across 57 members and its native candidate changed all 57 intended members while retaining 3060 entries.

### Zombie size

Complete and native-candidate validated. Linux changes only `m_ForcedBodyScaleMin` / `m_ForcedBodyScaleMax` after validating occurrence counts and baseline value-sequence hashes. No preset file or native value vector is copied into Git.

Isolated supersize gameplay QA validates released parity for the affected AI path. The Linux supersize candidate changes exactly the four upstream preset members (`infectedai.pre`, `infectedai_pre.def`, `zombieai.pre`, `zombieai_pre.def`), sets the audited scale fields to `5.0`, and is semantically equivalent to the released four-member supersize preset. Native gameplay showed fast infected and some ordinary walkers clearly enlarged. Some ground actors that imitate corpses remained normal-sized, while some actual corpses were enlarged. Because the released preset contains no additional members and the Linux candidate matches its semantics, this entity-state variation is treated as native/upstream behavior rather than a Linux-port defect. A read-only installed-content precedence audit also found no later PAK or loose-file override for these targets.

### Forced spawn

Default matches native. Every non-default preset changes active `m_AIPresets` values in a 165-call vector.

Accepted sanitized evidence proves exact pristine donors exist for **Suicider** and **bandits with guns** only. Those runtime definitions validate exactly 165 active calls and the complete pristine-vector digest, validate the selected donor value by SHA-256, replace only quoted value spans, and preserve layout/comments.

- Suicider uses native donor ordinal 6, preserves ordinal 6, and changes the other 164 calls. **Native-validated.**
- Armed bandits use native donor ordinal 119, preserve ordinals 60 and 119, and change the other 163 calls. **Native-validated.**

Accepted sanitized reconstruction evidence proves **bandits with melee** can be derived entirely from the user's pristine vector without embedding its game-derived target identifier. Runtime starts from native ordinal 40, validates that source by SHA-256, copies six whole alphanumeric tokens from audited positions within native ordinal 37, validates the reconstructed target SHA-256, preserves ordinal 60, and replaces the other 164 quoted values. Separators/punctuation are inherited from the pristine base identifier and cannot be rewritten by the recipe. Its native disposable candidate retained 3060 entries, changed only `data/presets/aispawnbox_pre.def`, changed exactly 164 of 165 active spawn calls, preserved ordinal 60, and rejected combination with either other implemented forced-spawn mode. **Native-validated.**

Butcher, Ram, Bloater, and Thug remain a hard provenance boundary. Accepted sanitized audits establish that each preserves ordinal 60 and changes the other 164 calls, but no acceptable whole-token reconstruction exists from the pristine 165-value spawn vector, from any of the 1,573 quoted strings in native `aispawnbox_pre.def`, or from the bounded six-member native AI/preset source set (`aispawnbox_pre.def`, `zombieai.pre`, `zombieai_pre.def`, `infectedai.pre`, `infectedai_pre.def`, `bestiary.scr`). The project will not widen this into arbitrary whole-archive string assembly or character-level encoding. Those four choices remain unresolved unless new provenance/rights evidence or a comparably narrow semantic derivation appears.

### Weather/time

Vanilla matches native. Accepted structural, ambient, and private value-probe evidence established the full behavior of all eight non-default released choices. Linux reconstructs them semantically using named WEATHER-section/interior anchors, exact native-commented time priors, and strict named `VarFloat` value checks.

All eight non-default weather/time choices now pass native disposable candidate construction with the expected member scopes. The native regression also proved that semantic anchor matching must tolerate the observed blank line between the two WEATHER declarations without weakening the named/order preconditions.

## Upstream unconditional replacements

The Windows script unconditionally copied bundled replacements over `data/game.ini` and `data/menu/scr/menumain_pc.xui`. A sanitized read-only comparison against the accepted native baseline closes their Linux provenance/necessity gate:

- `game.ini` has the same 25 parsed calls in native and replacement form, with no native-only or replacement-only call identities; the only changed call is active `GameName#1`;
- `menumain_pc.xui` has no native-only component, exactly one replacement-only `MyText:T_Mylogo`, and becomes structurally equivalent to native after removing that component; no existing component property differs independently of the inserted child.

The replacement files therefore serve upstream branding/cosmetic behavior rather than released gameplay behavior. The Linux runtime and packaging will **not** copy or redistribute either replacement. The inherited files remain provenance-sensitive historical upstream material and are not treated as Linux payloads.

## Native application / GUI

A GUI-independent application service wraps the validated transaction path. It validates selections against the exact ready catalog and exclusivity groups, refuses a first backup from an unknown Data0 hash, creates the retained pristine backup only from the currently validated compatibility baseline, builds candidates in temporary storage, installs only over the exact candidate source hash, and requires pristine restore before a different selection can be applied over a DIRUE-modified live archive.

The initial PySide6 GUI is present behind the optional `gui` dependency and `dirue-gui` entry point. Its metadata accounts for all 38 ready options exactly once. The four unresolved spawn choices remain visible but disabled. Qt code delegates validation/build/install/restore to the GUI-independent application service and asks for explicit confirmation before mutation.

Physical Bazzite smoke QA passes for the application/package layer: the full unit suite and compile checks pass, an isolated optional-GUI installation succeeds, PySide6 imports, `MainWindow` constructs with the offscreen Qt backend, all 38 ready options are represented exactly once, all four unresolved spawn choices remain disabled, the real native installation is accepted by the application service, entry points install, and a wheel builds successfully. The smoke run was read-only for the game and left the accepted Data0 hash unchanged.

Real on-screen Bazzite visual QA passes for layout, scrolling, selector behavior, option grouping, status/log readability, and visibility of the four intentionally unavailable forced-spawn choices. The first capture exposed low contrast for disabled dropdown entries; the GUI launcher was corrected to use a readable disabled-text palette while keeping those entries non-selectable, and a focused second native-theme capture verified the result. Both visual runs blocked mutation controls/functions and left Data0 pristine.

The confirmation-driven Qt/application transaction also passes on Bazzite. Using `reduce_sprint_stamina`, the real `MainWindow` Apply handler created the application pristine backup from the audited baseline, installed the exact previously validated candidate hash, and then disabled Apply while the live archive differed from the retained backup. A second application-service apply was rejected until restore. The real `MainWindow` Restore handler then restored the exact original 3060-entry baseline, re-enabled the expected controls, and retained the pristine backup. Apply and restore confirmation paths both executed successfully, and no fallback recovery path was needed.

A first representative gameplay/visual QA attempt is **invalid and supplies no gameplay evidence**. The candidate installation itself succeeded, but the interactive handoff ran under `bash -s <<'EOF'` and plain `read` commands consumed heredoc stdin instead of the terminal, so the script advanced without human input and then failed on an unset observation variable. Its recovery trap restored the exact pristine Data0 hash successfully. Repository QA rules now require interactive heredoc handoffs to read explicitly from `/dev/tty` and verify native game process start/exit before accepting observations.

The corrected representative gameplay/visual run is valid. It installed the exact four-option candidate for camera FOV82, Better Firearms POV82, supersize zombies, and darker storm night; verified the native game process started and exited; and restored the exact pristine archive afterward. Camera FOV82, Better Firearms POV82, darker storm night, and a stable playable session were all observed as passing. The supersize observation was initially recorded as inconclusive, then an isolated supersize-only run established that the Linux candidate is semantically equivalent to the released four-member preset and visibly enlarges fast infected plus at least some ordinary walkers. Ground fake-corpse actors may remain normal-sized; that is retained as an upstream/native entity-state caveat rather than expanded beyond released preset behavior.

A subsequent bounded native gameplay run validates two additional families together without ambiguity. The exact candidate changed only `data/skills/default_levels.xml`, `data/ai/infected/infected_data.scr`, and `data/ai/zombie/vessel_data.scr`; the native game process start/exit checks passed; and both **Run with weapons** and **One Hit AI** were observed working in a stable playable session. The transaction then restored the exact pristine 3060-entry Data0 and retained the pristine backup.

An isolated **Forced Suiciders** gameplay run also passes. The exact candidate changed only `data/presets/aispawnbox_pre.def`; a bounded automatic wait verified the native game process started and later exited; fresh ambient spawn-box enemies were observed repeatedly appearing as Suiciders; and the session remained stable. The transaction restored the exact pristine 3060-entry Data0 and retained the pristine backup. A prior attempt that relied on a one-shot keypress-timed process check is not accepted gameplay evidence, although its recovery path also restored the pristine archive; gameplay QA rules now prefer bounded automatic process-start polling.

An isolated **Better Firearms Upgrading** gameplay run also passes after correcting the QA expectation for derived UI stats. The exact candidate changed only `data/inventory_gen.scr`, the native process start/exit checks passed, and the session remained stable. On the same fully upgraded revolver, the pristine inventory UI showed reload time `4.5` and the candidate showed `3.6`. Accepted source-map evidence for the released Magnum/revolver path gives raw reload time `4.0`, while the released level-3 edit is `3.2`; both UI observations preserve the same `1.125` multiplier (`4.5/4.0 == 3.6/3.2`). The initial assertion that the UI itself should literally display raw `3.2` is therefore rejected as a QA-model error, not a port defect. The transaction restored the exact pristine 3060-entry Data0 and retained the pristine backup.

## Packaging and distribution validation

Physical Bazzite packaging QA now passes for the real repository state. The build system pins `setuptools==83.0.0`, uses a repo-local PEP 517 backend wrapper, disables implicit package-data inclusion, and explicitly excludes provenance-sensitive inherited payloads from the source distribution. The distribution checker validates both wheel and sdist contents without extracting them.

Two clean builds under the same commit-derived `SOURCE_DATE_EPOCH` produced byte-identical artifacts after deterministic sdist normalization. Accepted hashes are:

- wheel `dirue_linux-0.1.0.dev0-py3-none-any.whl`: SHA-256 `062feed8162f67c23877e20bbb7588bc0cda17edb49f79c0fba902d3c0c9f076`;
- sdist `dirue_linux-0.1.0.dev0.tar.gz`: SHA-256 `47732086c7f078750be956f239b26c58cd2d6cdd6eb84862e2b48565c34ea06f`.

The sdist backend normalizes gzip timestamp plus tar member order, ownership, timestamps, and modes. The resulting wheel installs in an isolated environment, `pip check` passes, CLI help works, and both CLI and GUI entry-point metadata are present. The packaging run left the repository clean and did not mutate Data0 or the retained pristine backup.

## Transaction safety and native transaction QA

The transaction path provides strict ZIP validation, pristine backup preservation, source-hash binding, candidate/live/backup entry-count checks, exact candidate-hash binding, same-directory temporary writes, a second live-hash check immediately before `os.replace`, installed-hash verification, and expected-backup verification before restore.

Native transaction QA passed independently at engine level: a validated candidate was atomically installed, its live hash matched exactly, and the retained pristine backup restored the exact original 3060-entry baseline. The Qt/application integration now passes the same install/lock/reject/restore lifecycle through the real GUI handlers. The live game is pristine after accepted transaction/gameplay tests, and the application pristine backup is retained as recovery material.

The retained pristine backup is recovery material and must not be cleaned up or overwritten. The inherited repository `Data0.pak` remains forbidden as a Linux patch source or install payload.

## Validation evidence

Accepted evidence is scoped to the code state that produced it:

- all 38 current catalog options pass native disposable candidate construction;
- all native-tested choice conflicts reject incompatible selections, including the three implemented forced-spawn modes;
- material FOV/Upgrading/POV interactions and a maximal compatible multi-family candidate pass;
- accepted firearm source-map evidence supplies complete firearm reconstruction data;
- hardened preset evidence supplies Hard-AI/zombie-size behavior and preset boundaries;
- corrected recoil evidence supplies repeated-block camera-recoil mapping;
- sanitized unresolved/detail evidence supplies the public-safe spawn donor boundary and weather structure;
- sanitized spawn-recipe evidence proves the melee-bandit target can be reconstructed from native whole tokens;
- sanitized same-member and bounded-AI-source evidence closes further whole-token derivation for Butcher/Ram/Bloater/Thug without widening to arbitrary archive strings;
- private native weather/spawn evidence supplies the pristine spawn-vector digest and final whitelisted weather/time statement arguments;
- sanitized replacement comparison proves the inherited `game.ini` / `menumain_pc.xui` copies are branding/cosmetic only and unnecessary for Linux gameplay parity;
- native engine transaction evidence passes with exact-original recovery;
- isolated physical Bazzite GUI/package smoke passes offscreen, including PySide6 installation/import, real-install application validation, exact UI catalog accounting, disabled unresolved choices, entry points, and wheel construction, with no Data0 mutation;
- physical on-screen GUI visual QA passes after one focused disabled-text contrast correction, with unavailable spawn choices still non-selectable and no Data0 mutation;
- physical Qt/application transaction QA passes through the real Apply and Restore handlers with confirmations, exact candidate installation, apply-lock/reapply rejection while modified, exact-original restore, and retained pristine backup; fallback recovery was not needed;
- the first representative gameplay attempt is rejected as QA-harness failure, not accepted gameplay evidence; exact pristine recovery passed;
- corrected representative gameplay QA validates camera FOV82, Better Firearms POV82, darker storm night, and session stability;
- isolated supersize gameplay QA proves semantic equivalence to the released four-member preset and observes supersizing on fast infected plus some ordinary walkers; ground fake-corpse actors can remain normal-sized without implying a port delta;
- bounded direct/AI gameplay QA validates Run with weapons and One Hit AI in a stable native session, followed by exact pristine restore;
- isolated Forced Suiciders gameplay QA validates the implemented spawn override with automatically verified native process start/exit and exact pristine restore;
- isolated Better Firearms Upgrading gameplay QA validates the released Magnum/revolver reload change through an objective same-weapon UI comparison, with the pristine and modified UI values preserving the exact multiplier implied by the accepted raw values, followed by exact pristine restore;
- the installed-content precedence audit found no other PAK or loose file carrying the audited FOV/POV/weather/zombie-size target members, ruling out archive shadowing;
- physical packaging QA builds the real wheel and sdist twice, validates the provenance-sensitive payload boundary, verifies deterministic sdist metadata, proves both artifacts byte-identical, installs the wheel in isolation, and leaves the repository/game state unchanged;
- no GitHub Actions were used.

## Remaining gates

1. Treat Butcher, Ram, Bloater, and Thug as intentionally unavailable under the current provenance boundary; do not broaden derivation without materially new provenance/rights evidence.
2. Keep additional gameplay QA bounded and evidence-driven only where a specific unresolved risk justifies it; representative gameplay coverage is sufficient for the current Milestone-1 implementation set.
3. Release, public binaries, Nexus publication, main integration, upstream submission, and other external publication remain explicit approval gates.

## Cleanup and publication

Cleanup is continuous. Superseded failed weather/provenance/catalog-count diagnostics and the first low-contrast GUI capture are obsolete after accepted successful evidence and the corrected focused contrast capture. Invalid gameplay harness attempts are not accepted gameplay evidence; only their successful exact-original recovery remains relevant safety evidence. The corrected representative gameplay report, isolated supersize report, direct/One-Hit gameplay report, accepted Forced Suiciders report, Better Firearms Upgrading gameplay report, negative installed-content precedence report, and reproducible packaging report are current private QA evidence. The incorrect raw-value-equals-UI expectation from the first firearm-upgrading assertion is superseded by the accepted proportional UI evidence and is not a runtime failure. The first spawn-recipe audit remains because it documents the accepted melee derivation. The broader same-member and bounded-AI exploratory audit modules/tests were removed after their accepted negative results closed that research path. Current accepted native-candidate, preset, recoil, source-map, native-baseline, engine transaction, unresolved/detail, replacement-provenance, spawn-recipe, final negative spawn evidence, GUI/package smoke, corrected GUI visual evidence, Qt/application transaction evidence, representative gameplay evidence, supersize gameplay evidence, direct/AI gameplay evidence, Forced Suiciders gameplay evidence, Better Firearms Upgrading gameplay evidence, precedence evidence, reproducible packaging evidence, and private value-probe evidence remain preserved while relevant. The pristine backup is retained recovery material.

No main integration, release, public binary, Nexus publication, upstream submission, GitHub Actions use, or other external publication has been authorized. `linux-port` remains the active development branch.
