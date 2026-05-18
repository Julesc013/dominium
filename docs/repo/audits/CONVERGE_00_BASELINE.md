Status: DERIVED
Last Reviewed: 2026-05-12
Supersedes: prior CONVERGE-00 baseline text merged in `b3d1e62bafbcf48b9760d15ea820c70215b80e41`
Superseded By: none

Stability: provisional
Future Series: REPO-CONVERGENCE
Replacement Target: CONVERGE-01 machine-readable layout contract and generated root inventory

# CONVERGE-00 Baseline Snapshot

## Status

- Task ID: CONVERGE-00
- Result: partial
- Date/time: 2026-05-12T12:33:47.0188288+10:00
- Branch before sync: `main`
- Branch after sync: `main`
- HEAD SHA after sync: `b3d1e62bafbcf48b9760d15ea820c70215b80e41`
- Remote tracked branch: `origin/main`
- Working tree clean before changes: yes
- Working tree clean after changes: yes after the local audit commit; before that commit, only this audit file was modified
- Directory moves performed: none
- Semantic changes performed: none
- Product/build/install/pack/runtime/source-layout changes performed: none
- Contract or schema impact: none; no schema, runtime contract, product identity, install identity, pack identity, executable name, or virtual root was changed
- Relevant invariant documents upheld: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, and `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`

The task result is `partial` because the repository synced and the baseline was recorded, but two lightweight verification-adjacent commands did not pass in this local environment:

- `python scripts/verify_docs_sanity.py --repo-root .` failed under Python 3.8.1 because the script uses `list[...]` type syntax.
- `python .aide/scripts/aide_lite.py pack --task "CONVERGE-00 baseline repository layout audit"` failed with `TypeError: write_text() got an unexpected keyword argument 'newline'`.

## Git Sync Evidence

Initial status:

```text
$ git status --short --branch
## main...origin/main [behind 2]
```

Remote configuration:

```text
$ git remote -v
origin  https://github.com/Julesc013/dominium.git (fetch)
origin  https://github.com/Julesc013/dominium.git (push)
```

Checkout:

```text
$ git checkout main
Your branch is behind 'origin/main' by 2 commits, and can be fast-forwarded.
  (use "git pull" to update your local branch)
Already on 'main'
```

Fetch:

```text
$ git fetch --all --prune
<no output; exit 0>
```

Fast-forward pull:

```text
$ git pull --ff-only origin main
Updating 4daf31c63..b3d1e62ba
Fast-forward
 docs/repo/audits/CONVERGE_00_BASELINE.md | 612 +++++++++++++++++++++++++++++++
 1 file changed, 612 insertions(+)
 create mode 100644 docs/repo/audits/CONVERGE_00_BASELINE.md
From https://github.com/Julesc013/dominium
 * branch                main       -> FETCH_HEAD
```

Post-sync status:

```text
$ git status --short --branch
## main...origin/main
```

HEAD and remote HEAD:

```text
$ git rev-parse HEAD
b3d1e62bafbcf48b9760d15ea820c70215b80e41

$ git rev-parse origin/main
b3d1e62bafbcf48b9760d15ea820c70215b80e41
```

Branch/ref state:

```text
$ git branch --all --verbose --no-abbrev
* main                                  b3d1e62bafbcf48b9760d15ea820c70215b80e41 Merge pull request #3 from Julesc013/converge/converge-00-baseline
  remotes/origin/HEAD                   -> origin/main
  remotes/origin/main                   b3d1e62bafbcf48b9760d15ea820c70215b80e41 Merge pull request #3 from Julesc013/converge/converge-00-baseline
  remotes/origin/recovery/mega-13cb8ca7 13cb8ca7dcd6440c5f605f27f680684b9257153d mega: integrate pending PHYS/FLUID/TEMP/META governance sweeps and baselines
```

## Top-Level Root Inventory

Current top-level entries from repo root, excluding `.git`, sorted by name:

| Entry | Provisional classification | Notes |
| --- | --- | --- |
| `.agentignore` | metadata_or_config | Agent/tool ignore metadata. |
| `.aide/` | metadata_or_config | AIDE Lite context, policy, verification, and adapter files. |
| `.aide.local.example/` | metadata_or_config | Example local AIDE state surface. |
| `.gitattributes` | metadata_or_config | Git metadata. |
| `.github/` | metadata_or_config | CI/workflow configuration. |
| `.gitignore` | metadata_or_config | Git metadata. |
| `.vscode/` | metadata_or_config | Editor configuration. |
| `__init__.py` | unknown_needs_review | Root-level Python package marker or compatibility surface. |
| `AGENTS.md` | metadata_or_config | Canonical agent governance surface. |
| `app/` | current_runtime_root | Runtime/app substrate. |
| `appshell/` | current_runtime_root | AppShell substrate. |
| `archive/` | current_archive_or_quarantine_root | Historical/archive surface. |
| `archive/generated/artifacts/` | generated_or_ephemeral | Generated or evidence-like outputs. |
| `astro/` | current_domain_root | Domain root. |
| `attic/` | current_archive_or_quarantine_root | Historical/quarantine surface. |
| `bundles/` | current_content_or_data_root | Bundle data/content surface. |
| `CHANGELOG.md` | current_docs_root | Human documentation. |
| `chem/` | current_domain_root | Domain root. |
| `CLAUDE.md` | metadata_or_config | Agent/tool guidance surface. |
| `client/` | current_product_root | Product entry/root at top level. |
| `cmake/` | current_tools_root | Build tooling/configuration. |
| `CMakeLists.txt` | metadata_or_config | Root build configuration. |
| `CMakePresets.json` | metadata_or_config | Build preset configuration. |
| `CODE_CHANGE_JUSTIFICATION.md` | current_docs_root | Human documentation/governance note. |
| `compat/` | current_contract_or_schema_root | Compatibility/contract-adjacent root. |
| `CONTRIBUTING.md` | current_docs_root | Human documentation. |
| `control/` | current_runtime_root | Control/runtime substrate. |
| `core/` | current_runtime_root | Core runtime/domain substrate. |
| `data/` | current_content_or_data_root | Data, registries, planning mirrors, and content surfaces. |
| `diag/` | current_runtime_root | Diagnostic substrate. |
| `diegetics/` | current_domain_root | Domain root. |
| `archive/generated/dist/` | current_release_or_dist_root | Distribution output/projection surface. |
| `docs/` | current_docs_root | Documentation and doctrine root. |
| `DOMINIUM.md` | current_docs_root | Human documentation. |
| `electric/` | current_domain_root | Domain root. |
| `embodiment/` | current_domain_root | Domain root. |
| `engine/` | canonical_candidate | Engine/root substrate expected to remain first-class. |
| `epistemics/` | current_domain_root | Domain root. |
| `field/` | current_domain_root | Transitional compatibility facade per ownership review. |
| `fields/` | current_domain_root | Canonical semantic field substrate per ownership review. |
| `fluid/` | current_domain_root | Domain root. |
| `game/` | canonical_candidate | Game/root substrate expected to remain first-class. |
| `geo/` | current_domain_root | Domain root. |
| `governance/` | current_docs_root | Governance documentation or policy surface. |
| `GOVERNANCE.md` | current_docs_root | Human documentation/governance note. |
| `ide/` | metadata_or_config | IDE/projection configuration surface. |
| `infrastructure/` | current_domain_root | Domain root. |
| `inspection/` | current_domain_root | Domain root. |
| `interaction/` | current_domain_root | Domain root. |
| `interior/` | current_domain_root | Domain root. |
| `labs/` | unknown_needs_review | Experimental or lab surface. |
| `launcher/` | current_product_root | Product entry/root at top level. |
| `legacy/` | current_archive_or_quarantine_root | Legacy surface. |
| `lib/` | current_runtime_root | Shared library/root surface; overlaps with `libs/`. |
| `libs/` | current_runtime_root | Shared library/root surface; overlaps with `lib/`. |
| `LICENSE.md` | metadata_or_config | Repository license file. |
| `locks/` | current_content_or_data_root | Lock/artifact surface needing future split review. |
| `logic/` | current_domain_root | Domain root. |
| `logistics/` | current_domain_root | Domain root. |
| `machines/` | current_domain_root | Domain root. |
| `materials/` | current_domain_root | Domain root. |
| `mechanics/` | current_domain_root | Domain root. |
| `meta/` | unknown_needs_review | Meta/runtime/domain-adjacent surface. |
| `meta_extensions_engine.py` | unknown_needs_review | Root-level source file; ownership needs review. |
| `mobility/` | current_domain_root | Domain root. |
| `modding/` | current_content_or_data_root | Modding/content-adjacent root. |
| `MODDING.md` | current_docs_root | Human documentation. |
| `models/` | current_content_or_data_root | Model/data surface. |
| `net/` | current_runtime_root | Network/runtime substrate. |
| `numeric_discipline.py` | unknown_needs_review | Root-level source or policy helper. |
| `packs/` | current_content_or_data_root | Runtime pack substrate per ownership review. |
| `performance/` | current_tools_root | Performance tooling/evidence surface. |
| `physics/` | current_domain_root | Domain root. |
| `pollution/` | current_domain_root | Domain root. |
| `process/` | current_domain_root | Process/domain substrate; ownership-sensitive because process mutation is constitutional. |
| `profiles/` | current_content_or_data_root | Profile data surface. |
| `quarantine/` | current_archive_or_quarantine_root | Quarantine surface. |
| `README.md` | current_docs_root | Human documentation. |
| `reality/` | current_domain_root | Domain/reality substrate. |
| `release/` | current_release_or_dist_root | Release/control-plane surface. |
| `repo/` | current_release_or_dist_root | Repo/control-plane policy surface. |
| `runtime/` | current_runtime_root | Runtime root; caution per planning doctrine. |
| `safety/` | current_contract_or_schema_root | Safety/contract-adjacent surface. |
| `schema/` | current_contract_or_schema_root | Canonical schema law root per ownership review. |
| `schemas/` | current_contract_or_schema_root | Validator-facing schema projection per ownership review. |
| `scripts/` | current_tools_root | Developer and verification scripts. |
| `security/` | current_contract_or_schema_root | Security/trust/policy surface. |
| `SECURITY.md` | metadata_or_config | Security policy file. |
| `server/` | current_product_root | Product entry/root at top level. |
| `setup/` | current_product_root | Product entry/root at top level. |
| `signals/` | current_domain_root | Domain root. |
| `sitecustomize.py` | metadata_or_config | Python startup/config surface. |
| `specs/` | current_contract_or_schema_root | Specification root, including reality doctrine. |
| `system/` | current_domain_root | Domain/root substrate. |
| `templates/` | current_content_or_data_root | Template/content surface. |
| `tests/` | current_tools_root | Verification/test surface. |
| `thermal/` | current_domain_root | Domain root. |
| `tool_ui_bind.cmd` | current_tools_root | Root-level tool launcher. |
| `tool_ui_doc_annotate.cmd` | current_tools_root | Root-level tool launcher. |
| `tool_ui_validate.cmd` | current_tools_root | Root-level tool launcher. |
| `tools/` | current_tools_root | Tooling root. |
| `ui/` | current_runtime_root | UI/runtime presentation surface. |
| `universe/` | current_domain_root | Domain root. |
| `updates/` | current_release_or_dist_root | Update/release surface. |
| `validation/` | current_tools_root | Validation tooling surface. |
| `VERSION_CLIENT` | metadata_or_config | Version identity file. |
| `VERSION_ENGINE` | metadata_or_config | Version identity file. |
| `VERSION_GAME` | metadata_or_config | Version identity file. |
| `VERSION_LAUNCHER` | metadata_or_config | Version identity file. |
| `VERSION_SERVER` | metadata_or_config | Version identity file. |
| `VERSION_SETUP` | metadata_or_config | Version identity file. |
| `VERSION_SUITE` | metadata_or_config | Version identity file. |
| `VERSION_TOOLS` | metadata_or_config | Version identity file. |
| `worldgen/` | current_domain_root | Domain root. |

## Existing Layout Authority Documents

| Document | Present | Status header | Claims canonical or authoritative layout status | Baseline assessment | Notable conflicting path claims |
| --- | --- | --- | --- | --- | --- |
| `README.md` | present | no formal status header; starts with "This readme is likely out of date." | Does not directly claim to be layout authority, but points readers to canonical architecture contracts under `docs/architecture/`. | Stale user-facing orientation. | High-level architecture lists `engine/`, `game/`, `client/`, `server/`, `repo/`, `tests/`, and `tools/*x/`; omits many current roots and still frames product roots at top level. |
| `docs/architecture/ARCH_REPO_LAYOUT.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-02-01`; `Stability: provisional`; `Replacement Target: patched document aligned to current canon ownership and release scope` | Yes. The title says "Canonical Repository Layout and Ownership" and the body includes "Canonical layout (authoritative)." | Stale/conflicting. Its patch notes explicitly say the concrete top-level layout is stale relative to the real repository tree. | Lists top-level `engine/`, `game/`, `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`, `data/`, `schema/`, `sdk/`, `docs/`, and `legacy/`; `sdk/` is not present and many present roots are omitted. |
| `docs/architecture/DIRECTORY_CONTEXT.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-02-01`; `Future Series: DOC-ARCHIVE`; `Replacement Target: legacy reference surface retained without current binding authority` | Yes. It says it is the authoritative directory/layout contract and source of truth if another document disagrees. | Stale/conflicting legacy reference. Header replacement target weakens it, but body still claims authority. | Lists the older tree with `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`, `schema/`, `sdk/`, `scripts/`, `cmake/`, `legacy/`, `build/`, `archive/generated/dist/`, and `.github/`. |
| `docs/restructure/FUTURE_LAYOUT_PROPOSAL.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-13`; `Future Series: RESTRUCTURE`; `Replacement Target: executed post-v0.0.0 layout migration plan with shim retirement after one stable release` | It is marked canonical, but its body says it is a no-move planning artifact for future restructure. | Planning-only input, not current layout authority. | Proposes `/src`, `/tools`, `/data`, `/packs`, and `/docs` layout; mapping table describes `src/...` paths even though current root inventory has many top-level domain roots. |
| `docs/architecture/CANON_INDEX.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-16`; `Future Series: DOC-ARCHIVE`; `Replacement Target: legacy reference surface retained without current binding authority` | Yes. It states that if a document is not listed as canonical, it is not binding. | Conflicting/stale for layout authority because it lists old layout docs as canonical while its replacement target says legacy reference. | Lists both `docs/architecture/ARCH_REPO_LAYOUT.md` and `docs/architecture/DIRECTORY_CONTEXT.md` under `CANONICAL`, preserving competing layout claims. |

CONVERGE-00 does not patch these documents. Later CONVERGE work should supersede or demote stale layout authority explicitly instead of adding another competing layout source.

## Existing Distribution / Install / Storage Documents

| Document | Present | Status header | Main layout roots or physical paths defined | Obvious conflict or convergence need |
| --- | --- | --- | --- | --- |
| `docs/runtime/shell/VIRTUAL_PATHS.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-13`; `Future Series: APPSHELL/LIB`; `Replacement Target: release-pinned install discovery and virtual root contract` | Defines logical roots `VROOT_BIN`, `VROOT_EXPORTS`, `VROOT_INSTALL`, `VROOT_INSTANCES`, `VROOT_IPC`, `VROOT_LOCKS`, `VROOT_LOGS`, `VROOT_PACKS`, `VROOT_PROFILES`, `VROOT_SAVES`, and `VROOT_STORE`; portable defaults include `.`, `exports`, `instances`, `runtime`, `locks`, `logs`, `packs`, `profiles`, and `saves`. | Strong input for future projection contract. Needs alignment with any future split between deterministic store locks, runtime/process locks, and operations transaction state. |
| `docs/architecture/INSTALL_MODEL.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-11`; `Future Series: DOC-CONVERGENCE`; `Replacement Target: canon-aligned documentation set for convergence and release preparation` | Defines portable install layout with `install.manifest.json`, `semantic_contract_registry.json`, `bin/`, `store/`, `instances/`, and `saves/`; references `data/registries/install_registry.json`. | Strong install doctrine; should be consolidated into a distribution/install layout contract without changing install IDs or virtual roots. |
| `docs/architecture/CONTENT_AND_STORAGE_MODEL.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-11`; `Future Series: DOC-CONVERGENCE`; `Replacement Target: canon-aligned documentation set for convergence and release preparation` | Defines canonical storage root layout with `bin/`, `store/`, `instances/`, `saves/`, and `exports/`; `store/` categories include `packs`, `profiles`, `blueprints`, `system_templates`, `process_definitions`, `logic_programs`, `view_presets`, `resource_pack_stubs`, `locks`, `migrations`, and `repro`. | Strong CAS/storage doctrine; needs projection alignment with source repo layout and distribution output layout. |
| `docs/distribution/DIST_TREE_CONTRACT.md` | present | `Status: DERIVED`; `Last Reviewed: 2026-02-08`; `Future Series: DOC-CONVERGENCE`; `Replacement Target: canon-aligned documentation set for convergence and release preparation` | Defines `archive/generated/dist/pkg/<platform>/<arch>/`, `archive/generated/dist/sys/<platform>/<arch>/`, `archive/generated/dist/sym/<platform>/<arch>/`, `archive/generated/dist/res/`, `archive/generated/dist/cfg/`, `archive/generated/dist/rearchive/generated/dist/`, and `archive/generated/dist/meta/`. | Strong derived distribution tree contract; needs promotion or incorporation into a machine-readable distribution projection contract if later tasks require enforcement. |
| `docs/architecture/BUNDLE_MODEL.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-11`; `Future Series: DOC-CONVERGENCE`; `Replacement Target: canon-aligned documentation set for convergence and release preparation` | Defines bundle types and bundle payload locations such as `archive/generated/artifacts/blueprint/<payload>.json`, `archive/generated/artifacts/blueprint/shareable.artifact.manifest.json`, `instance/instance.manifest.json`, and `instance/lockfiles/capabilities.lock`. | Strong share/export doctrine; needs alignment with repo-level `archive/generated/artifacts/` and bundle export projections. |
| `docs/architecture/SAVE_MODEL.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-11`; `Future Series: DOC-CONVERGENCE`; `Replacement Target: canon-aligned documentation set for convergence and release preparation` | Defines save identity through `schema/save.manifest.schema`, `schema/lib/save_manifest.schema`, and related schema roots; optional relative locators include `contract_bundle_ref`, `state_snapshots_ref`, `patches_ref`, and `proofs_ref`. | Strong save doctrine; needs no layout move in CONVERGE-00 but must stay aligned with `saves/` projection contracts later. |
| `docs/architecture/INSTANCE_MODEL.md` | present | `Status: CANONICAL`; `Last Reviewed: 2026-03-11`; `Future Series: DOC-CONVERGENCE`; `Replacement Target: canon-aligned documentation set for convergence and release preparation` | Defines instance manifests through `schema/instance.manifest.schema`, `schema/lib/instance_manifest.schema`, and `schema/lib/instance_settings.schema`; portable instances use `embedded_archive/generated/artifacts/` and optional `embedded_builds`. | Strong instance doctrine; needs alignment with future layout contracts and pack/profile lock projections. |

CONVERGE-00 makes no changes to these documents.

## Build and Verification Surface

Observed verification surface:

- `CMakePresets.json` defines configure, build, and test presets named `verify`.
- `cmake --list-presets` reports configure preset `verify`.
- `cmake --list-presets=build` reports build preset `verify`.
- `ctest --list-presets` reports test preset `verify`.
- `CMakeLists.txt` runs `scripts/verify_build_target_boundaries.py --repo-root ${CMAKE_SOURCE_DIR}` during configure.
- `CMakeLists.txt` defines custom targets including `check_build_boundaries`, `check_ui_shell_purity`, `check_abi_boundaries`, `check_docs_sanity`, `check_all`, `verify_fast`, and `verify_full`.
- `.github/workflows/ci.yml` runs `python scripts/verify_ui_shell_purity.py --repo-root .`, `python scripts/verify_abi_boundaries.py --repo-root .`, and `python3 scripts/verify_docs_sanity.py --repo-root .`.
- `scripts/dev/gate.py` is present.
- `scripts/verify_build_target_boundaries.py` is present.
- `scripts/verify_ui_shell_purity.py` is present.
- `scripts/verify_abi_boundaries.py` is present.
- `scripts/verify_docs_sanity.py` is present.
- `cmake --version` reports CMake 4.2.0.
- `ctest --version` reports CTest 4.2.0.
- `python --version` reports Python 3.8.1.

Requested command availability:

| Command | Availability | Run in CONVERGE-00 | Result |
| --- | --- | --- | --- |
| `cmake --preset verify` | confirmed by configure preset | no | Not run; configure/build is outside this baseline task's lightweight verification scope. |
| `cmake --build --preset verify` | confirmed by build preset | no | Not run; full build target is outside this baseline task's lightweight verification scope. |
| `ctest --preset verify` | confirmed by test preset | no | Not run; full test preset is outside this baseline task's lightweight verification scope. |
| `python scripts/dev/gate.py verify --repo-root .` | script present; README documents this command | no | Not run; may be broader than the lightweight audit checks requested. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | script present and referenced by CMake | yes | PASS: `BOUNDARY-OK: build boundary checks passed`. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | script present and referenced by CMake/CI | no | Not run in CONVERGE-00. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | script present and referenced by CMake/CI | no | Not run in CONVERGE-00. |
| `python scripts/verify_docs_sanity.py --repo-root .` | script present and referenced by CMake/CI | yes | FAIL under Python 3.8.1 with `TypeError: 'type' object is not subscriptable`. |

## Optional Verification Run

Lightweight verification commands actually run:

```text
$ python scripts/verify_docs_sanity.py --repo-root .
Traceback (most recent call last):
  File "scripts\verify_docs_sanity.py", line 39, in <module>
    def _scan_markdown(repo_root: str, rel_path: str, violations: list[tuple[str, str]]) -> None:
TypeError: 'type' object is not subscriptable
```

```text
$ python scripts/verify_build_target_boundaries.py --repo-root .
BOUNDARY-OK: build boundary checks passed
```

AIDE Lite preflight commands were also attempted because `AGENTS.md` carries AIDE adapter guidance:

```text
$ py -3 .aide/scripts/aide_lite.py doctor
py : The term 'py' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

```text
$ python .aide/scripts/aide_lite.py doctor
AIDE Lite doctor
status: PASS
...
PASS validation should be run: no hard validation failures detected
```

```text
$ python .aide/scripts/aide_lite.py validate
AIDE Lite validate
status: PASS
...
PASS no obvious secrets in token-survival files
```

```text
$ python .aide/scripts/aide_lite.py pack --task "CONVERGE-00 baseline repository layout audit"
Traceback (most recent call last):
  File ".aide\scripts\aide_lite.py", line 9033, in <module>
    raise SystemExit(main())
  File ".aide\scripts\aide_lite.py", line 9026, in main
    return int(args.handler(args))
  File ".aide\scripts\aide_lite.py", line 6878, in command_pack
    result, packet = write_task_packet(args.repo_root, args.task)
  File ".aide\scripts\aide_lite.py", line 6298, in write_task_packet
    result = write_text_if_changed(repo_root / LATEST_PACKET_PATH, packet.text)
  File ".aide\scripts\aide_lite.py", line 1283, in write_text_if_changed
    path.write_text(normalized, encoding="utf-8", newline="\n")
TypeError: write_text() got an unexpected keyword argument 'newline'
```

No risky remediation was performed for either failure.

Post-edit whitespace validation:

```text
$ git diff --check
warning: in the working copy of 'docs/repo/audits/CONVERGE_00_BASELINE.md', LF will be replaced by CRLF the next time Git touches it
<exit 0>
```

## Known Baseline Problems

- `README.md` is explicitly likely out of date and still describes a smaller high-level layout.
- `docs/architecture/ARCH_REPO_LAYOUT.md` is marked canonical and says its canonical layout section is authoritative, but its patch notes admit the concrete top-level layout is stale.
- `docs/architecture/DIRECTORY_CONTEXT.md` is marked canonical and says it is the authoritative directory/layout contract, but it describes an older tree and also has a legacy-reference replacement target.
- `docs/architecture/CANON_INDEX.md` lists stale layout documents as canonical, preserving multiple authoritative layout claims.
- `docs/restructure/FUTURE_LAYOUT_PROPOSAL.md` is marked canonical but is planning-only and proposes a future `/src` structure rather than describing current layout.
- Duplicate or overlapping roots are present, including `schema/` and `schemas/`, `lib/` and `libs/`, `field/` and `fields/`, and multiple archive/quarantine surfaces.
- Product roots remain at top level: `client/`, `server/`, `setup/`, and `launcher/`.
- Runtime and AppShell surfaces are split across top-level `app/`, `appshell/`, `runtime/`, `core/`, `control/`, `net/`, `diag/`, and `ui/`.
- Many domain roots are top-level entries, including `astro/`, `chem/`, `electric/`, `embodiment/`, `epistemics/`, `fluid/`, `geo/`, `infrastructure/`, `inspection/`, `interaction/`, `interior/`, `logic/`, `logistics/`, `machines/`, `materials/`, `mechanics/`, `mobility/`, `physics/`, `pollution/`, `process/`, `reality/`, `signals/`, `system/`, `thermal/`, `universe/`, and `worldgen/`.
- Generated or ephemeral roots are present at top level, including `archive/generated/artifacts/` and `archive/generated/dist/`; generated echo handling is not yet mechanically enforced by a layout contract.
- Distribution, install, storage, bundle, save, and instance layout rules are split across several strong docs rather than one enforceable projection contract.
- No machine-readable repository layout contract was found at `contracts/repo/layout.contract.toml`.
- No CONVERGE-01 root inventory was found at `tools/migration/root_inventory.json`.
- No CONVERGE-01 root move map was found at `tools/migration/root_move_map.json`.

## CONVERGE Readiness

The repo is ready for CONVERGE-01 with warnings.

Readiness criteria:

- Local `main` is synced to `origin/main`: yes, at `b3d1e62bafbcf48b9760d15ea820c70215b80e41`.
- Working tree is clean except this audit file before commit, and clean after the local audit commit: yes.
- Baseline root inventory has been recorded: yes, in this document.
- Stale authority docs have been identified: yes.
- Directory moves were performed: no.
- Product/build/install/pack/runtime/source-layout changes were performed: no.

Warnings:

- `python scripts/verify_docs_sanity.py --repo-root .` fails under the local Python 3.8.1 interpreter because the script uses Python 3.9+ generic type syntax.
- `python .aide/scripts/aide_lite.py pack --task "CONVERGE-00 baseline repository layout audit"` fails due a `write_text(..., newline=...)` call unsupported by the local Python runtime.

These warnings do not block CONVERGE-01's audit-only layout contract work, but they should be visible before stronger gates are claimed.

## Next Recommended Task

CONVERGE-01 - Layout Contract and Non-Blocking Audit

Expected future deliverables:

- `contracts/repo/layout.contract.toml`
- `contracts/repo/layout.schema.json`
- `tools/validators/check_repo_layout.py`
- `tools/migration/root_inventory.json`
- `tools/migration/root_move_map.json`
- `docs/repo/REPO_LAYOUT_TARGET.md`
- `docs/repo/OWNERSHIP_RULES.md`
- `docs/repo/DOMAIN_SPLIT_RULES.md`
- `docs/repo/ROOT_FILE_POLICY.md`

This section is only a recommendation. CONVERGE-01 was not implemented by this task.

## CONVERGE-01 Follow-up Note

CONVERGE-01 added the first machine-readable source repository layout contract, contract schema, non-blocking root layout validator, generated root inventory, generated root move map, and concise repo layout documentation for target layout, ownership rules, domain split rules, and root-file policy.

## CONVERGE-02 Follow-up Note

CONVERGE-02 added a root allowlist contract and non-blocking root allowlist validator, marked stale layout authority docs as legacy/planning/reference surfaces for current source-layout purposes, and performed no physical moves.

## CONVERGE-03 Follow-up Note

CONVERGE-03 refined the root inventory and convergence move map into complete migration-planning artifacts, added human-readable inventory and move-map summaries, updated repo layout guidance, and performed no physical moves.

## CONVERGE-04 Follow-up Note

CONVERGE-04 added a distribution layout contract, distribution layout validator, and distribution/install/media/bundle/cache/symbol documentation. It performed no physical moves and generated no package bytes.

## CONVERGE-05 Follow-up Note

CONVERGE-05 completed archive-family convergence. Root-level `attic/`, `legacy/`, and `quarantine/` were moved under `archive/`, `archive/README.md` and `archive/MANIFEST.md` were added, and no non-archive roots were moved.

## CONVERGE-06 Follow-up Note

CONVERGE-06 completed contract-adjacent convergence for root-level `schema/` and `schemas/`, merging retained schema material under `contracts/schema/`. `compat/` and `locks/` remain review roots, `registry/` and `registries/` were confirmed absent, contracts README/MANIFEST were added, and no product, runtime, AppShell, domain, content, archive, or generated-output roots were moved.

## CONVERGE-07 Follow-up Note

CONVERGE-07 completed runtime/AppShell convergence for safe runtime-facing roots. Root-level `appshell/` moved to `runtime/shell/`, `app/` moved to `runtime/shell/lifecycle/`, `ui/` moved to `runtime/ui/`, and `diag/` moved to `runtime/diagnostics/`. Root-level `net/`, `control/`, and `core/` remain review roots because they are mixed and ownership-sensitive. Runtime README/MANIFEST were added, and no product or domain roots were moved.

## CONVERGE-08 Follow-up Note

CONVERGE-08 completed product entrypoint convergence by moving root-level `client/`, `server/`, `setup/`, and `launcher/` under `apps/`. It added `apps/README.md`, `apps/MANIFEST.md`, and `docs/repo/APPS_CONVERGENCE.md`; updated contracts, validators, inventory, move map, and path references required by the move; performed no domain split; and preserved product IDs, executable names, install IDs, pack IDs, virtual-root IDs, and command behavior.

## CONVERGE-09 Follow-up Note

CONVERGE-09 completed the safe portion of the domain-root split by moving root-level Python domain implementation packages under `game/domain/`. It added `game/domain/README.md`, `game/domain/MANIFEST.md`, and `docs/repo/DOMAIN_SPLIT_REPORT.md`; updated contracts, validators, inventory, move map, and path references required by the split; and added no new simulation features.

## CONVERGE-10 Follow-up Note

CONVERGE-10 made strict layout validation available with explicit active exceptions. It added `contracts/repo/layout_exceptions.toml`, `contracts/repo/layout_exceptions.schema.json`, `docs/repo/LAYOUT_ENFORCEMENT.md`, and `docs/repo/LAYOUT_EXCEPTION_LEDGER.md`.

Active exception count: 37. Unexcepted strict layout violation count: 0.

No broad physical moves occurred.

## CONVERGE-11 Follow-up Note

CONVERGE-11 added the release component matrix layer. It added `contracts/release/component_matrix.contract.toml`, `contracts/release/component_matrix.schema.json`, `tools/validators/check_component_matrices.py`, and product/mode/platform/render/native/toolchain/packaging/audio/input/network/storage/support-tier docs under `docs/release/`.

No platform, render, native shell, backend, toolchain, or packaging implementation occurred. No physical moves occurred.

## CONVERGE-12 Follow-up Note

CONVERGE-12 completed the bounded final stale-doc/path audit for the CONVERGE series. It added `docs/repo/audits/CONVERGE_12_FINAL_AUDIT.md`, `docs/repo/audits/STALE_PATH_REFERENCE_AUDIT.md`, `docs/repo/audits/CONVERGE_VALIDATION_SUMMARY.md`, and `docs/repo/POST_CONVERGE_NEXT_STEPS.md`.

High-risk stale layout authority docs were patched with current contract references. No physical moves, platform/render/native implementations, domain features, or package artifacts were added.
