Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: WORKBENCH-NAME-01

# WORKBENCH-NAME-01 Audit

## Starting State

- Starting commit: `29c064993cadb8c2de46a52f15bef5d2cf6be591`
- Branch: `main`
- Preflight worktree: clean
- Source of truth: active tracked tree

## Task Scope

Normalize Workbench module names and route Workbench-adjacent generated/tooling/runtime material to canonical owners. This pass is intentionally scoped to `apps/workbench/` naming/routing plus the validator and references required to keep the naming from regressing.

## Workbench Paths Inspected

- `apps/workbench/module/game/edit/`
- `apps/workbench/module/game/editor/`
- `apps/workbench/module/tool/editor/`
- `apps/workbench/module/tooling/editor/`
- `apps/workbench/module/ui/editor/gen/`
- `apps/workbench/module/ui/editor/generated/`
- `apps/workbench/module/ui/editor/user/`
- `apps/workbench/module/ui/native/`
- `apps/workbench/module/ui/preview/`
- `apps/workbench/module/ui/preview/native/`
- `apps/workbench/module/ui/preview/service/`
- `apps/workbench/module/domain/`
- `apps/workbench/module/schema/`
- `apps/workbench/module/save/`
- `apps/workbench/module/replay/`
- `apps/workbench/module/world/`

## Routing Decisions

- `apps/workbench/module/game/edit/` is already absent from active tracked source. The game editor module is retained at `apps/workbench/module/game/editor/`.
- `apps/workbench/module/tool/editor/` is already absent from active tracked source. The user-facing tool-definition editor is retained at `apps/workbench/module/tooling/editor/`.
- Checked-in generated tool-editor binding sources were moved out of Workbench to `tools/codegen/ui/tool_editor/gen/`.
- Stale generated `.bak` files under the Workbench editor tree were moved to `archive/generated/workbench/tool_editor/`.
- `apps/workbench/module/ui/preview/native/` is retained because it is the Workbench-specific native preview/editor aggregate, not a reusable runtime UI backend.
- `apps/workbench/module/ui/preview/service/` is retained because it is shared only by the Workbench preview hosts; reusable runtime UI IR remains under `runtime/ui/`.
- `apps/workbench/module/domain/{item,technology,transport,universe}/` are retained as user-facing subject modules. They are not runtime UI substrate, codegen, or validators.

## Files And Directories Moved

- `apps/workbench/module/ui/editor/generated/ui_tool_editor_actions_gen.cpp` -> `tools/codegen/ui/tool_editor/gen/ui_tool_editor_actions_gen.cpp`
- `apps/workbench/module/ui/editor/generated/ui_tool_editor_actions_gen.h` -> `tools/codegen/ui/tool_editor/gen/ui_tool_editor_actions_gen.h`
- `apps/workbench/module/ui/editor/generated/*.bak*` -> `archive/generated/workbench/tool_editor/generated/`
- `apps/workbench/module/ui/editor/user/*.bak*` -> `archive/generated/workbench/tool_editor/user/`

## Paths Intentionally Retained Under Workbench

- `apps/workbench/module/tooling/editor/`: user-facing tool-definition editor host and product-specific binding.
- `apps/workbench/module/ui/editor/`: user-facing UI editor host and user-owned action stubs.
- `apps/workbench/module/ui/preview/native/`: Workbench-specific native preview/editor aggregate.
- `apps/workbench/module/ui/preview/service/`: preview-host service helpers scoped to Workbench preview.
- `apps/workbench/module/domain/`: user-facing domain editor modules.

## Generated/Historical References Skipped

- `.aide/**` generated context, install/uninstall plans, and tool classification maps still contain historical paths from earlier snapshots and were not hand-edited.
- `docs/audit/**`, `docs/ci/HYGIENE_QUEUE.md`, and old refactor/change history retain stale historical paths and were not rewritten by this task.
- `archive/generated/**`, `archive/legacy/**`, and `archive/historical/**` were not scanned as current Workbench blockers.

## Validator Updates

- Added `tools/validators/repo/check_workbench_module_names.py`.
- Added focused validator regression tests in `tests/app/workbench_module_names_validator_tests.py`.
- Registered `workbench_module_names_validator_tests` in `tests/app/CMakeLists.txt`.
- Updated `tools/validators/repo/check_path_terms.py` so both retired `ui/editor/gen` and `ui/editor/generated` Workbench binding paths point to `tools/codegen/ui/<area>/gen`.

## Validation Commands And Results

- `py -3 -m py_compile tools/validators/repo/check_workbench_module_names.py tests/app/workbench_module_names_validator_tests.py tools/validators/repo/check_path_terms.py`: PASS.
- `python tools/validators/repo/check_workbench_module_names.py --repo-root . --strict --json --max-findings 50`: PASS.
- `python tests/app/workbench_module_names_validator_tests.py --repo-root .`: PASS.
- `git diff --check`: PASS.
- `git ls-files apps/workbench/module/game/edit apps/workbench/module/tool/editor apps/workbench/module/ui/editor/gen apps/workbench/module/ui/editor/generated apps/workbench/module/ui/native`: PASS, no active tracked files.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with pre-existing AIDE warnings for a missing review-decision-policy reference and stale repo-map source snapshot hash.
- Strict repo/root/distribution/component validators:
  - `python tools/validators/check_repo_layout.py --repo-root .`: PASS with pre-existing TOML fallback/applied-exception warnings.
  - `python tools/validators/check_root_allowlist.py --repo-root .`: PASS with pre-existing TOML fallback/applied-exception warnings.
  - `python tools/validators/check_distribution_layout.py --repo-root .`: PASS.
  - `python tools/validators/check_component_matrices.py --repo-root .`: PASS.
- Root and naming validators:
  - `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict --json`: PASS.
  - `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict --json --max-findings 50`: PASS_WITH_WARNINGS; blockers 0; findings are archive/historical `src`/`source` paths.
  - `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict --json --max-findings 50`: PASS_WITH_WARNINGS; blockers 0; findings are existing archive/.aide naming debt.
  - `python tools/validators/repo/check_app_thinness.py --repo-root . --strict --json --max-findings 50`: PASS.
  - `python tools/validators/repo/check_workbench_module_names.py --repo-root . --strict --json --max-findings 50`: PASS.
  - `python tools/validators/repo/check_directory_naming.py --repo-root . --strict --json --max-findings 80`: PASS_WITH_WARNINGS; blockers 0; existing evidence/archive warnings.
  - `python tools/validators/repo/check_file_naming.py --repo-root . --strict --json --max-findings 80`: PASS_WITH_WARNINGS; blockers 0; existing evidence/archive warnings.
  - `python tools/validators/repo/check_path_terms.py --repo-root . --strict --json --max-findings 80`: FAIL on 8 pre-existing `runtime/render/client` blockers unrelated to Workbench module naming.
- Boundary and sanity checks:
  - `python scripts/verify_build_target_boundaries.py`: PASS.
  - `python scripts/verify_includes_sanity.py`: PASS.
  - `python scripts/verify_docs_sanity.py`: PASS.
  - `python scripts/verify_ui_shell_purity.py`: PASS.
  - `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.
- CMake:
  - `cmake --preset verify`: PASS; existing SDL deprecation and missing PkgConfig warnings.
  - `cmake --build --preset verify --target ALL_BUILD`: PASS; existing duplicate `LNK4006` warnings in `domino_engine`.
- CTest:
  - `ctest --preset verify -L smoke --output-on-failure`: PASS, 57/57.
  - `ctest --preset verify -R workbench_module_names_validator_tests --output-on-failure`: PASS, 1/1.
  - `ctest --preset verify -R "workbench|ui_editor|tool_editor|codegen|ui" --output-on-failure`: FAIL, 30/34 passed. The 4 failures are unrelated pre-existing proof debts: `test_xstack_removal_builds_runtime`, `test_session_spec_required_for_launch`, `securex_reproducible_build_tests`, and `test_future_case_stress_suite`.
  - `ctest --preset verify --output-on-failure`: FAIL, 438/499 passed. The 61 failures are unrelated stale canonical-path/proof debts, including old `data/registries`, `contracts/schemas`, `docs/app`, `runtime/app`, `tools/auditx`, `tools/securex`, `game/rules`, frozen-contract hash, process-only mutation, and workspace-isolation expectations.
- Generated side effects from validators/build/test runs were restored and not committed: `tools/migration/root_inventory.json`, `tools/migration/root_move_map.json`, and generated `docs/audit/**` proof outputs.

## Remaining Follow-Up Work

- Historical `.aide/**` and docs/audit snapshots should be regenerated by their owning tools when those generated-current maps are next refreshed.
- Existing non-Workbench proof debts should be handled by their owning tasks; this task did not change those paths or validator expectations.
