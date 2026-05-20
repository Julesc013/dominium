Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: audit

# CANON-REMEDIATION-FULL-PROOF-01

## Executive Verdict

- Verdict: PARTIAL
- Feature work may resume: LIMITED
- Reason: active canonical path/layout cleanup is mostly coherent and the CMake build plus smoke CTest pass, but `RepoX` STRICT still fails on residual non-path debt and a focused governance generator run exposes a missing release dist helper path.

## Starting State

- Starting branch: `main`
- Starting commit: `e201f72d6825c5f815f3850692885ed185745b6b`
- Initial worktree: clean
- Active tracked tree was used as the source of truth. Live GitHub state, chat memory, and old generated reports were not used as authority.
- Relevant invariants consulted: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`, `contracts/planning/final_prompt_inventory.json`, and `contracts/planning/dependency_graph_post_pi.json`.
- Contract/schema impact: no semantic IDs, pack IDs, schema IDs, content hashes, lock IDs, manifest IDs, or ABI/API names were intentionally changed. This pass updated stale path constants and regenerated current AIDE/repo/root maps.

## Task Purpose

Perform a final remediation and proof pass after the canonical source-spine cleanup. The task was constrained to small stale-reference, validator, generated-map, and proof hygiene repairs. It did not perform feature work or broad architecture redesign.

## Prior Cleanup Status

| Task | Status | Evidence |
| --- | --- | --- |
| `RUNTIME-NAME-01` | COMPLETE | No active `runtime/render/soft`, `runtime/render/stub`, `runtime/render/client/renderers`, `runtime/shell/commands`, `runtime/shell/ui_backends`, `runtime/capability/capability`, or `runtime/ui/core`. |
| `GAME-RULE-01` | COMPLETE | No active `game/rules` or `game/include/dominium/rules`. |
| `ENGINE-INCLUDE-BOUNDARY-01` | COMPLETE | Old public include leak paths under `engine/include/domino/{app,cli,gui,input,io,pkg,render,tui,world}` and `engine/include/render` are absent. |
| `PACK-AUTHORITY-01` | COMPLETE | `contracts/package/packs` is guard-only (`README.md`); authored pack payloads are under `content/packs`. |
| `SCHEMA-CANON-01` | COMPLETE | Old schema buckets such as `contracts/schema/chem`, `contracts/schema/geo`, `contracts/schema/fluid`, `contracts/schema/civ`, `contracts/schema/net`, and `contracts/schema/tools` are absent. |
| `CONTENT-PACK-CANON-01` | COMPLETE | No active `content/domain-data`, `content/data`, `content/domains/game/core`, or `content/domains/**/content` tautology. |
| `APPS-THIN-01` | COMPLETE WITH JUSTIFIED RETAINED PATHS | Retained app-local paths remain documented by prior audit, including `apps/client/local_server`, `apps/launcher/lifecycle`, and `apps/setup/lifecycle`. |
| `WORKBENCH-NAME-01` | COMPLETE | No active `apps/workbench/module/game/edit`, `apps/workbench/module/tool/editor`, `apps/workbench/module/ui/editor/gen`, or `apps/workbench/module/ui/native`. |
| `AIDE-SCAN-BOUNDARY-01` | COMPLETE AFTER REMEDIATION | `.dominium.local`, `archive/generated`, `archive/legacy`, and `archive/historical` are excluded from active AIDE fallback walking and context ignore rules. |
| `TOOLS-FOLD-01` | COMPLETE | Broad tools mirror roots and root-level tool editor/viewer/inspector paths are absent; tools taxonomy validator passes. |
| `DOCS-CANON-01` | COMPLETE | Old docs first-level mirror roots are absent; docs taxonomy validator passes. |
| `REPOX-TESTX-CANON-PATHS-01` | COMPLETE WITH REMAINING NON-PATH REPOX DEBT | TestX current law-profile path checks pass; RepoX STRICT no longer fails on the targeted stale path lanes but still fails on broader legacy/current proof debt. |

## Structure Reports

Generated review artifacts were written under ignored local evidence path `.dominium.local/canon-remediation-full-proof-01/` and were not committed:

- `metadata.txt`
- `tracked-files.txt`
- `tracked-dirs.txt`
- `tracked-roots.txt`
- `per-root-file-counts.tsv`
- `first-level-by-root.txt`
- `suspicious-active-paths-final.txt`
- `archive-generated-scan-boundary-final.txt`
- `old-path-reference-grep*.txt`
- `validation/testx_fast_summary.json`
- `validation/testx_fast_summary.md`
- `validation/testx_fast_run_meta.json`
- `validation/repox_proof_manifest.json`
- `validation/repox_profile.json`

The final suspicious path report contains only `contracts/package/packs/README.md`, which is the expected guard-only package packs directory.

## Remediation Changes Made

- Updated `.aide/context/ignore.yaml` to exclude `.dominium.local/**`, `archive/generated/**`, `archive/legacy/**`, and `archive/historical/**` from active AIDE context inputs.
- Updated `.aide/scripts/aide_lite.py` fallback scanning so `.dominium.local` is treated like local forbidden state and archive generated/legacy/historical trees are skipped in active-mode walking.
- Regenerated AIDE context, repo intelligence, and roots maps after the scan-boundary fix.
- Updated stale governance generator constants from old `data/governance` and `data/registries` outputs to canonical `contracts/governance` and `contracts/registry` files.
- Updated stale governance audit/report constants from `docs/audit` and `data/audit` to `docs/archive/audit` and `archive/generated/audit` where matching canonical retained files already exist or generated evidence is the correct owner.
- Updated store GC constants from old `docs/audit`, `docs/lib`, and `data/*` paths to existing `docs/archive/audit`, `docs/runtime/storage`, `archive/generated/audit`, and `contracts/registry` targets.
- Refreshed `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` through AIDE roots tooling for the current starting commit.

No tracked files were moved during this remediation pass. No old root was recreated.

## Generated Or Historical References Skipped

The following classes were intentionally not hand-edited in this pass:

- historical AIDE reports under `.aide/reports/**`
- install observations under `.aide/install/**`
- historical docs under `docs/archive/**`
- retained generated evidence under `archive/generated/**`
- retained legacy material under `archive/legacy/**`
- local remediation evidence under `.dominium.local/**`

During focused proof, five untracked old-root outputs were generated and preserved under `.dominium.local/canon-remediation-full-proof-01/generated-noise/` instead of being committed. They were byte-identical to already tracked canonical files under `contracts/registry`, `contracts/governance`, and `docs/archive/audit`.

## Proof Results

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short` | PASS at start | Worktree started clean. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Preflight and later validation succeeded. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS WITH WARNING | Existing warning: missing review-packet ref `.aide/verification/review-decision-policy.yaml`. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test lane passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root maps validate. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo maps validate. |
| `python -m py_compile ...` | PASS | Covered touched Python files and key proof tools. |
| `python scripts/dev/testx_proof_engine.py --repo-root . --suite testx_fast --dry-run ...` | PASS | Selected five proof items and wrote summaries under ignored local evidence. |
| `python tests/invariant/test_survival_no_console.py --repo-root .` | PASS | Survival/profile focused lane. |
| `python tests/invariant/test_survival_no_freecam.py --repo-root .` | PASS | Survival/profile focused lane. |
| `python tests/invariant/test_survival_diegetic_only.py --repo-root .` | PASS | Survival/profile focused lane. |
| `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...` | FAIL | Residual non-path RepoX debt remains; see blockers. |
| `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict` | PASS | Bad-root absence passed. |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict` | PASS WITH WARNINGS | Archive/historical source paths reported as historical info. |
| `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict` | PASS WITH WARNINGS | Finite historical/exception cases. |
| `python tools/validators/check_root_allowlist.py` | PASS WITH WARNINGS | Existing transitional `data` root and finite unknown-root exceptions. |
| `python tools/validators/check_repo_layout.py` | PASS WITH WARNINGS | Existing exceptions, including missing `external` root. |
| `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict` | PASS | Tools taxonomy passed. |
| `python tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict` | PASS | Docs taxonomy passed. |
| `python tools/validators/check_distribution_layout.py` | PASS | Distribution layout passed. |
| `python tools/validators/check_component_matrices.py` | PASS | Component matrices passed. |
| `python tools/validators/repo/check_content_layout.py --repo-root . --strict` | PASS | Content layout passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | `BOUNDARY-OK`. |
| `python scripts/verify_includes_sanity.py --repo-root .` | PASS | Include sanity passed. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI checks passed. |
| `cmake --preset verify` | PASS WITH EXISTING WARNINGS | SDL CMake deprecation and missing `PkgConfig` warnings. |
| `cmake --build --preset verify --target ALL_BUILD` | PASS WITH EXISTING WARNINGS | Existing duplicate-symbol `LNK4006` warnings in stub/sys symbols. |
| `ctest --preset verify -R "^(engine_smoke|test_manifest_selection_logic|test_manifest_fallback_when_missing|tools_auditx|tools_auditx_changed_only|tools_auditx_hash_stability)$" --output-on-failure` | PASS | 6/6 tests passed; focused smoke shard took about 10 minutes. |
| Full `ctest --preset verify` | NOT RUN | Not practical in this turn after the focused smoke shard duration. |
| Focused governance generator write check | BLOCKED AFTER PATH CONSTANT FIX | Old-root outputs were not recreated, but generator failed later because `tools/dist/runtime_compile_helper.py` is missing. |

An earlier PowerShell wrapper attempt using POSIX heredoc syntax failed before execution and was discarded as proof evidence.

## Remaining Blockers

`RepoX` STRICT still fails on broader debt that is not caused by stale canonical path aliases alone. Current categories include:

- `DUPLICATE_LOGIC_PRESSURE`
- `INV-CANON-NO-HIST-REF`
- `INV-CANON-STATE`
- `INV-DOC-STATUS-HEADER`
- `INV-EXTENSIONS-NAMESPACED`
- `INV-IDENTITY-FINGERPRINT`
- release/dist/package artifact requirements such as `INV-MVP-PACKS-MINIMAL`, `INV-NO-ADHOC-MAIN`, `INV-PACK-LOCK-REQUIRED`, and `INV-PROFILE-BUNDLE-REQUIRED`
- `INV-NO-BLOCKING-WORLDGEN-IN-UI`
- `INV-NO-RAW-PATHS`
- `INV-NO-WALLCLOCK-IN-DESCRIPTOR`
- `INV-OFFICIAL-PACKS-HAVE-COMPAT-MANIFEST`
- process guard/runtime checks
- unversioned schema-reference checks
- worldgen lock/baseline checks
- `NO_SILENT_DEFAULTS`

Focused governance output generation also exposes a release helper defect:

- `tools.repo.governance.write_governance_outputs('.', platform_tag='win64')` reaches `tools.release.dist.dist_tree_common._compile_runtime_tree`, which attempts to execute missing `tools/dist/runtime_compile_helper.py`.
- The path fix in this task prevents old-root output recreation before that failure, but creating or relocating the missing helper is release-tool repair work outside this remediation pass.

## Final Recommendation

Feature work may resume only in a limited way. Work that depends on the full strict proof gate remains blocked until a follow-up fixes the residual RepoX debt and the release dist helper path.

Recommended next prompt: `REPOX-STRICT-DEBT-01`, scoped to the remaining strict RepoX categories plus the missing `tools/dist/runtime_compile_helper.py` release helper route.
