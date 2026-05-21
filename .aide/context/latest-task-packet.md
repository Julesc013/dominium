# AIDE Latest Task Packet

## PHASE

Post-Foundation Lock / post-MATRIX-CLEANUP-00 / post-WORKBENCH-VALIDATION-SLICE-01

## GOAL

COMMAND-RESULT-VIEW-SLICE-01 - define the next narrow Workbench/app projection for command result display without building a broad Workbench shell.

## WHY

Foundation Lock is closed as `PASS_WITH_WARNINGS`. `MATRIX-CLEANUP-00` and `WORKBENCH-VALIDATION-SLICE-01` have both landed. The next useful product-spine step is a narrow command/result/evidence view that consumes existing command surfaces without adding renderer, native GUI, workspace runtime, provider runtime, package runtime, gameplay, or release behavior.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/MATRIX_CLEANUP_00.md`
- `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- `docs/development/workbench_validation_slice.md`
- `contracts/module/module_surface.contract.toml`
- `contracts/command/validation_run_input.schema.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `.aide/queue/current.toml`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `apps/workbench/module/**` only for a narrow command/result projection module or existing validation module integration points
- `contracts/module/module_surface.contract.toml` only for registering the narrow module surface
- `contracts/command/**` only for command/view contract additions directly required by the slice
- `contracts/diagnostics/diagnostic_code.registry.json` only for distinct diagnostic codes required by the slice
- `docs/development/**` for slice documentation
- `docs/repo/audits/**` for task audit evidence
- `tests/app/**` and `tests/contract/**` for targeted tests

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- raw provider credentials, API keys, local caches, raw prompt logs
- `.aide/context/latest-task-packet.md` unless the task is a coordinator queue task
- `.aide/context/latest-review-packet.md` unless the task is a coordinator queue task
- `.aide/reports/latest-dominium-status.md` unless the task is a coordinator queue task
- `.aide/reports/latest-warning-disposition.md` unless the task is a coordinator queue task
- `.aide/queue/current.toml` unless the task is a coordinator queue task
- `docs/repo/FOUNDATION_LOCK.md`
- broad Workbench shell, renderer, native GUI, gameplay, provider runtime, package runtime, runtime module loader, release publication, or product-wide implementation paths

## IMPLEMENTATION

- Keep the slice command-driven and projection-only.
- Consume public command/result/refusal/diagnostic/evidence surfaces; do not call private validators directly from Workbench.
- Do not set `workspace_runtime_implemented=true`.
- Do not implement renderer, native GUI, package runtime, provider runtime, runtime module loading, gameplay, or broad app behavior.
- Preserve `MATRIX-CLEANUP-00` renderer/platform terminology: `software`, `opengl`, `direct3d`, `metal`, `vulkan`, and canvas as drawing layer.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- targeted app tests for the new projection
- touched JSON/TOML parse checks
- `py -3 tools/validators/contracts/check_command_surface.py --repo-root . --strict`
- `py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`
- `py -3 tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
- `py -3 tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`
- `git diff --check`

## COMMITS

- Commit coherent subdeliverables with verbose bodies.
- Do not commit ignored transient validation reports unless the task explicitly promotes them as evidence.

## EVIDENCE

- changed files
- validation commands and results
- result/refusal/diagnostic/evidence parity proof
- unresolved risks and deferrals

## NON_GOALS

- No full Workbench shell.
- No rendered GUI.
- No workspace runtime.
- No runtime module loader.
- No provider runtime.
- No package runtime.
- No renderer backend implementation.
- No native GUI.
- No gameplay, worldgen, release publication, or broad app behavior.

## ACCEPTANCE

- Command/result projection is narrow and service/command mediated.
- CLI/headless semantics remain the source of behavior; Workbench projection is not authority.
- Same result/refusal/diagnostic/evidence packet can be displayed without private tool binding.
- Broad blockers remain explicit.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4990
- approx_tokens: 1248
- budget_status: PASS
- warnings:
  - next task is a narrow product-spine candidate and must remain inside the allowed paths
