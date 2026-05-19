Status: DERIVED
Last Reviewed: 2026-05-19
Supersedes: none
Superseded By: none

# RUNTIME-NAME-01 Audit

Result: PASS_WITH_WARNINGS
Starting commit: `f9f74e9ee8bf9f4fab967789c76f3e53bf780bae`

## Scope

This pass is limited to the remaining runtime second-level naming cleanup. It does not start game/rule, schema, content/pack, app-thin, tools-fold, docs-fold, or feature work.

## Preflight

- Branch: `main`
- Worktree before edits: clean
- Tracked old runtime path inventory:
  - `runtime/render/client/__init__.py`
  - `runtime/render/client/render_model_adapter.py`
  - `runtime/render/client/representation_resolver.py`
  - `runtime/render/client/snapshot_capture.py`
- No tracked files were found under:
  - `runtime/render/soft`
  - `runtime/render/stub`
  - `runtime/shell/commands`
  - `runtime/shell/ui_backends`
  - `runtime/capability/capability`
  - `runtime/ui/core`

## Classification

The remaining `runtime/render/client` files are shared runtime render backend/service code, not product-specific client glue:

- `render_model_adapter.py`: deterministic PerceivedModel to RenderModel adapter.
- `representation_resolver.py`: deterministic representation-rule resolver for RenderModel materialization.
- `snapshot_capture.py`: backend selection, fallback, cache, and snapshot capture pipeline.
- `__init__.py`: package export surface for the adapter/resolver API.

## Moves

- `runtime/render/client/render_model_adapter.py` -> `runtime/render/backend/render_model_adapter.py`
- `runtime/render/client/representation_resolver.py` -> `runtime/render/backend/representation_resolver.py`
- `runtime/render/client/snapshot_capture.py` -> `runtime/render/backend/snapshot_capture.py`
- `runtime/render/client/__init__.py` -> `runtime/render/backend/model_api.py`

The existing `runtime/render/backend/__init__.py` now exports the render-model adapter and snapshot capture API alongside renderer backend entrypoints.

## Active Reference Updates

Updated active imports and validator/audit-test path constants from `runtime.render.client` / `runtime/render/client` to `runtime.render.backend` / `runtime/render/backend` in:

- `runtime/ui/client/viewer_shell.py`
- `tools/validators/render/tool_render_capture.py`
- `tools/xstack/sessionx/render_model.py`
- `tools/xstack/sessionx/boundary_debug.py`
- `tools/xstack/repox/check.py`
- `tools/xstack/auditx/analyzers/*render*`
- `tools/xstack/testx/tests/test_render_no_truth_access.py`
- `tools/xstack/testx/tests/test_renderer_truth_isolation.py`
- `tools/xstack/testx/tests/test_renderer_truth_isolation_hardware.py`
- `scripts/ci/check_repox_rules.py`
- `tools/audit/review/xi6_common.py`
- `tools/migration/canon_spine_new.py`
- `tests/app/app_scaffold_contract_tests.py`
- `runtime/shell/bootstrap.py`

The bootstrap import was updated from `runtime.shell.commands` to `runtime.shell.command`
after full CTest exposed the stale import in setup/install lanes.

## Exclusions

Historical and generated inventories still mention old paths and were not hand-edited:

- `.aide/**` generated reports, maps, observations, and repair context
- `docs/archive/audit/**` historical audit reports
- `docs/repo/audits/CANON_DEBT_CLEANUP_01.md` prior audit record
- generated architecture/module registries

These should be refreshed by their owning generators if current proof lanes require fresh snapshots.

## Validation Plan

- `git diff --check`
- import smoke for `runtime.render.backend`, snapshot capture, render validator CLI, and session render wrapper
- `py -3 .aide/scripts/aide_lite.py validate`
- focused TestX render isolation tests
- app scaffold contract test
- include/ABI CTest
- smoke CTest
- CMake configure/build when feasible

## Validation Results

- `git ls-files runtime/render/soft runtime/render/stub runtime/render/client runtime/shell/commands runtime/shell/ui_backends runtime/capability/capability runtime/ui/core`: PASS, no tracked active paths.
- `git diff --check`: PASS.
- Import smoke for `runtime.render.backend`, snapshot capture, render validator CLI, and session render wrapper: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with warnings for missing review policy ref and stale repo map source snapshot hash.
- `py -3 tools/validators/check_root_allowlist.py`: PASS.
- `py -3 tools/validators/check_repo_layout.py`: PASS.
- `py -3 tools/validators/repo/check_bad_root_absence.py --strict --json`: PASS.
- `py -3 tools/validators/repo/check_no_src_source_dirs.py --json`: PASS_WITH_WARNINGS, blocker count 0.
- `py -3 tools/validators/repo/check_path_terms.py --strict --json --max-findings 20`: PASS_WITH_WARNINGS, blocker count 0.
- `py -3 scripts/verify_build_target_boundaries.py`: PASS.
- `py -3 scripts/verify_includes_sanity.py`: PASS.
- `py -3 scripts/verify_docs_sanity.py`: PASS.
- `py -3 scripts/verify_ui_shell_purity.py`: PASS.
- `py -3 scripts/verify_abi_boundaries.py`: PASS.
- `py -3 tests/app/app_scaffold_contract_tests.py --repo-root .`: PASS.
- `cmake --preset verify`: PASS.
- `cmake --build --preset verify --target ALL_BUILD`: PASS with existing duplicate-symbol linker warnings.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS, 57/57.
- Focused CTest `render_prep_work_ir|renderer_backend_contracts|renderer_contract_tests|app_ui_contracts|app_ui_bind_phase|const_product_shell_contracts|capability_runtime_enforcement|sys_caps|build_include_sanity|build_abi_boundaries`: PASS, 10/10.
- Focused setup/install rerun after shell import repair: PASS, 2/2.

## Full CTest

`ctest --preset verify --output-on-failure --timeout 300` was run and failed with
108 failures out of 495. The only runtime-rename failure found was the stale
`runtime.shell.commands` import in `runtime/shell/bootstrap.py`; it was repaired
and the affected setup/install tests were rerun successfully.

The remaining full-suite failures are outside this targeted runtime naming pass.
They are dominated by stale `data/*`, `contracts/schemas/*`, old tool launcher
paths such as `tools/auditx`, `tools/controlx`, `tools/performx`, `tools/compatx`,
and `tools/securex`, legacy `game/rules` test expectations, and broader RepoX
invariant debt.

## Follow-Up Work

- Refresh generated architecture/module registries and historical AIDE/report snapshots through their owning generators if current proof lanes require them.
- Repair broad stale TestX/RepoX expectations for old `data/*`, `contracts/schemas/*`, `game/rules/*`, and old tool launcher paths in a proof-infrastructure task.
- Continue the already-scoped next cleanup waves separately: game rule/domain, schema taxonomy, content/pack taxonomy, app thinness, tools fold, and docs fold.
