Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: audit
Task: CANON-TASK-STATUS-RECONCILE-01

# CANON-TASK-STATUS-RECONCILE-01

## Verdict

CLEAN WITH WARNINGS.

The current tracked tree does not contain the exact active stale path prefixes
that appeared in the uploaded directory export critique. RepoX STRICT, AIDE
doctor/validate, root/layout validators, docs/tools/content/app/workbench
validators, CMake verify/build, smoke CTest, and focused TestX/worldgen/schema
checks passed during this reconciliation.

The repo is not FULL-gate clean. Full CTest was attempted and took 3227.41
seconds, which is about 53 minutes 47 seconds. It failed 63 of 503 tests. That
runtime is too expensive for normal feature iteration and should be treated as
a rare full-certainty lane until a tiered sub-10-minute gate is formalized.

Feature work status: LIMITED.

## Source Of Truth

- Branch: main
- Starting commit: 17e35302327dff31141ae7541ac0d5fe7205ff3d
- Starting worktree: clean
- Source mode: git-tracked local tree
- Structure tool: tools/repo/dirfiles/repo-dirfiles-v19.ps1 with `-TrackedOnly`
- Local evidence path: `.dominium.local/canon-task-status-reconcile-01/`
- Tracked files: 17,493
- Tracked directories: 2,426
- Structure export warnings: 0

The uploaded tree concern was reconciled against `git ls-files` and the
tracked-only dirfiles export. Active source is the current local tracked tree,
not prior audit prose and not old generated reports.

## Root Model

Allowed top-level source and tooling roots are present. No unclassified active
top-level root was found. Generated/local roots such as `.dominium.local/`,
`build/`, `dist/`, `tmp/`, and reports remain ignored or generated-local.

The root layout validator still reports finite existing exceptions for root
files and the absent optional `external/` root. Those are not new findings from
this task.

## Task Status Matrix

| Task | Status | Evidence | Next action |
| --- | --- | --- | --- |
| RUNTIME-NAME-01 | COMPLETE | No active `runtime/render/soft`, `runtime/render/stub`, `runtime/render/client/renderers`, `runtime/shell/commands`, `runtime/shell/ui_backends`, `runtime/capability/capability`, or `runtime/ui/core` prefixes. Canonical runtime paths exist. | None for exact stale prefixes. |
| GAME-RULE-01 | COMPLETE | No active `game/rules` or `game/include/dominium/rules`. Canonical `game/rule`, `game/law`, `game/domain`, and `game/include/dominium` paths exist. | None for exact stale prefixes. |
| ENGINE-INCLUDE-BOUNDARY-01 | COMPLETE WITH EXCEPTIONS | Retired include subdirs such as `engine/include/domino/render` and `engine/include/domino/world` are absent. Some broad flat `engine/include/domino/*.h` public headers remain documented in `ENGINE_INCLUDE_BOUNDARY_01.md`. | Follow up with `ENGINE-INCLUDE-BOUNDARY-02` for remaining flat public header ownership. |
| PACK-AUTHORITY-01 | COMPLETE WITH EXCEPTIONS | `contracts/package/packs/` contains only `README.md`, which reserves the guard/contract location and points authored payloads to `content/packs/`. | Keep guard-only README; do not add payloads there. |
| SCHEMA-CANON-01 | COMPLETE WITH EXCEPTIONS | Named old schema bucket directories are absent. Canonical domain/runtime/package/tool/validation schema roots exist. Root-level and broad schema artifacts remain by identity-preservation policy. | Do not migrate schema identity without a dedicated schema prompt. |
| CONTENT-PACK-CANON-01 | COMPLETE | `content/packs/` uses documented category-plus-pack layout. No active `content/domain-data`, `content/data`, `content/domains/game/core`, or `content/domains/**/content` wrapper was found. | None. |
| APPS-THIN-01 | COMPLETE WITH EXCEPTIONS | Retained app-local paths are limited product glue documented in `APPS_THIN_01.md`. App thinness validator passes. | Revisit only if app code becomes shared runtime/platform code. |
| WORKBENCH-NAME-01 | COMPLETE | No active `apps/workbench/module/game/edit`, `tool/editor`, `ui/editor/gen`, or `ui/native` paths. Workbench module name validator passes. | None. |
| AIDE-SCAN-BOUNDARY-01 | COMPLETE WITH EXCEPTIONS | Active scans pass and do not treat archive/generated nested `.aide` snapshots as active authority. Tracked `.aide/cache`, `.aide/queue`, `.aide/reports`, `.aide/evals/runs`, and `.aide/ledgers` remain retained evidence/fixture surfaces. | Keep scan-boundary proof; classify retained AIDE fixture surfaces explicitly in future AIDE cleanup. |
| TOOLS-FOLD-01 | COMPLETE | Suspicious first-level tools roots from the reconciliation set are absent. Tools taxonomy validator passes. | None for this reconciliation. |
| DOCS-CANON-01 | COMPLETE | Suspicious first-level docs roots from the reconciliation set are absent. Docs taxonomy and docs sanity pass. | None for this reconciliation. |
| REPOX-TESTX-CANON-PATHS-01 | COMPLETE | RepoX STRICT passes. TestX fast dry-run and survival invariants pass. No current `data/registries/law_profiles.json` requirement was found. | None. |
| CANON-REMEDIATION-FULL-PROOF-01 | COMPLETE WITH EXCEPTIONS | The remediation proof lanes are green, but full CTest remains failing and expensive. | Dedicated FULL CTest debt triage. |
| REPOX-STRICT-DEBT-01 | COMPLETE | RepoX STRICT passes from the current tracked tree. | None. |

## Active Old-Path Sweep

Exact active stale-prefix checks found no current tracked matches for the
requested runtime, game, engine include, schema bucket, content wrapper,
Workbench, tools, docs, old registry, or stale helper path classes.

The remaining grep hits are classified as:

- `game/rules`: archive/legacy only.
- `runtime/render/soft`: false positive in `runtime/render/software` and
  software-renderer prose.
- `runtime/shell/commands`: prose/title false positive, not an active directory.
- `contracts/schema/geo`, `contracts/schema/fluid`, `contracts/schema/civ`:
  false positives in root-level schema filenames, not old bucket directories.
- `contracts/package/packs`: guard-only README exception.
- `content/data`: docs or validator code terms, not active `content/data/`.
- `tools/validator`: canonical `tools/validators/**` substring.
- `tools/validation`: docs prose, not active `tools/validation/`.

## Archive And Generated Exceptions

The following are intentionally ignored in active-source mode:

- `archive/legacy/**/game/rules`
- `archive/generated/aide/export/**/files/.aide`
- `archive/generated/aide/queue/**/evidence`
- archive/historical `src` and `source` paths
- generated audit/proof outputs emitted by full CTest

Full CTest rewrote several generated audit artifacts and created new
`docs/audit/**` outputs during the run. Those side effects were reverted or
removed because they were not intentional reconciliation artifacts.

## Remediation

No active source path remediation was performed. The tracked source tree already
matched the path-level reconciliation acceptance checks. This commit records the
audit only.

## Proof Results

| Command | Result |
| --- | --- |
| `git status --short --untracked-files=all` | PASS, clean before audit work |
| `tools/repo/dirfiles/repo-dirfiles-v19.ps1 -TrackedOnly -NoZip -NoColor -NoConsoleTheme -PauseMode Never -StatusMode Quiet` | PASS |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS with existing review-packet warning for missing `.aide/verification/review-decision-policy.yaml` |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS |
| `python tools/validators/check_repo_layout.py --repo-root . --strict --no-write` | PASS |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_bad_root_absence.py --repo-root .` | PASS |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .` | PASS with archive/historical warnings only |
| `python tools/validators/repo/check_forbidden_root_names.py --repo-root .` | PASS with archive/material warnings only |
| `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_content_layout.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_app_thinness.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_workbench_module_names.py --repo-root . --strict` | PASS |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS |
| `python scripts/verify_includes_sanity.py --repo-root .` | PASS |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS |
| `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...` | PASS |
| `python scripts/dev/testx_proof_engine.py --repo-root . --suite testx_fast --dry-run ...` | PASS |
| `python tools/domain/worldgen/tool_verify_worldgen_lock.py --repo-root . ...` | PASS |
| `python tests/schema/schema_taxonomy_validator_tests.py --repo-root .` | PASS |
| `python tests/schema/schema_reference_integrity_tests.py --repo-root .` | PASS |
| `python tools/package/pack/pack_validate.py --repo-root . --pack-root content/packs/core/org.dominium.core.units --format json` | PASS |
| `python tools/validators/check_distribution_layout.py --repo-root .` | PASS |
| `python tools/validators/check_component_matrices.py --repo-root .` | PASS |
| `python tests/invariant/test_survival_no_console.py --repo-root .` | PASS |
| `python tests/invariant/test_survival_no_freecam.py --repo-root .` | PASS |
| `python tests/invariant/test_survival_diegetic_only.py --repo-root .` | PASS |
| `cmake --preset verify` | PASS with existing CMake/SDL/PkgConfig warnings |
| `cmake --build --preset verify --target ALL_BUILD` | PASS with known duplicate-symbol linker warnings |
| `ctest --preset verify -L smoke --output-on-failure` | PASS, 57/57 |
| `ctest --preset verify --output-on-failure` | FAIL, 440/503 passed, 63 failed, 3227.41 seconds |

## Full CTest Failure Summary

Full CTest failures are broad FULL-gate debt, not small reconciliation fixes.
Primary failure clusters:

- stale or missing docs/contracts: `phase6_audit`,
  `universe_complexity_contract_tests`, `perf_budget_regression`
- hardcoded identity/defaults and invariant debt:
  `slice0_hardcoded_ids`, `slice1_hardcoded_constants`,
  process-only mutation checks, capability-scope checks, RNG/SRZ checks
- stale tool routes after tools fold: missing `tools/securex/securex.py`,
  `tools/setup/setup_cli.py`, `tools/launcher/launcher_cli.py`,
  `tools/ops/ops_cli.py`, `tools/bugreport/ingest.py`
- stale old path/test assumptions: distribution profile tests,
  `integration_meta`, `schema_migration_contracts`,
  `test_xstack_removal_builds_runtime`
- FAB/package validation debt: `fab_determinism`, FAB cycle/recursion/safety,
  contentlib/data1 FAB validators, and the previously known 14 current
  pack-reference/FAB validation failures in `docs/archive/audit/PACK_AUDIT.txt`
- portability/workspace and generated-output behavior:
  workspace isolation, gate no-tracked-writes tests, artifact hash separator
  behavior, release preset policy mismatch
- future-case stress suite: undeclared optional chemistry micro domain and
  direct `ctest` invocations in `scripts/test_tier.py` and
  `scripts/test_timing_report.py`

The full run duration confirms that full CTest must not be the default
developer gate. The current practical gate is the passing smoke/STRICT/focused
validation set. A separate proof-system task should define a sub-10-minute
FAST/STRICT gate and reserve full CTest for rare release or ultra-certainty
runs.

## Remaining Blockers

- Full CTest is not clean: 63 failures remain.
- Full CTest is too slow for routine use: 3227.41 seconds.
- `docs/archive/audit/PACK_AUDIT.txt` still records 14 current
  pack-reference/FAB validation failures.
- Engine include cleanup has residual flat public-header ownership debt.
- Schema canon intentionally preserved root-level and identity-sensitive schema
  artifacts; any deeper migration needs a schema-specific review.
- Retained tracked AIDE cache/queue/report surfaces need future fixture/evidence
  classification if the project wants a visually cleaner `.aide/`.

## Recommendation

Feature work may resume only in LIMITED mode. The next task should be:

`FAST-STRICT-TEST-TIER-01`

Goal: make the normal proof command finish in less than 10 minutes by separating
FAST, STRICT, FULL, release, portability, and historical-blocker lanes; forbid
routine direct full-CTest use outside release/ultra-certainty workflows; and
triage the 63 full-CTest failures into explicit owners.
