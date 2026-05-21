Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Result: PASS_WITH_WARNINGS

# WORKBENCH_VALIDATION_SLICE_01

## Scope

Worker 6 implemented the first narrow governed Workbench validation slice for
`dominium.validation.run`.

The slice stays inside command/result/refusal/diagnostic/evidence parity. It
does not implement a full Workbench shell, rendered GUI, workspace runtime,
runtime module loader, provider runtime, package runtime, or broad app behavior.

## Relevant Invariants

- `docs/canon/constitution_v1.md`: A2 process-only mutation, A3 lawful refusal,
  A7 truth/perceived/render separation, A9 pack-driven integration, A10 explicit
  degradation/refusal.
- `docs/canon/glossary_v1.md`: command, capability, diagnostic, evidence,
  refusal, Workbench-facing projection vocabulary remains subordinate to canon.
- `AGENTS.md`: extend over replace, no silent semantic drift, validation honesty,
  contract/schema discipline, protected-area awareness.
- `docs/development/workbench_module_guidelines.md`: Workbench modules bind to
  command/service IDs and present results/evidence without private tool calls.
- `docs/architecture/workbench_workspace_model.md`: validation table binds to
  `dominium.validation.run`, not a validator file path.
- `contracts/workbench/workbench_surface.contract.toml`: Workbench is not
  authority and `workspace_runtime_implemented=false` remains unchanged.

## Changed Artifacts

- `apps/workbench/module/validation/__init__.py`
- `apps/workbench/module/validation/__main__.py`
- `apps/workbench/module/validation/cli.py`
- `apps/workbench/module/validation/command.py`
- `apps/workbench/module/validation/service_adapter.py`
- `apps/workbench/module/validation/workbench_projection.py`
- `contracts/command/validation_run_input.schema.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/module/module_surface.contract.toml`
- `docs/development/workbench_validation_slice.md`
- `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- `tests/app/workbench_validation_slice_tests.py`

## Contract And Schema Impact

Contract/schema impact changed narrowly:

- validation command input now exposes `profile`, `surface`, and `emit_reports`
- Workbench validation module row now points at the skeletal headless module
- diagnostics registry now includes generic validation-run refused/warning codes

No change was made to Workbench workspace runtime status. It remains false.

## Evidence

Validation evidence:

- `py -3 .aide/scripts/aide_lite.py doctor` -> PASS
- `py -3 .aide/scripts/aide_lite.py validate` -> PASS_WITH_WARNINGS,
  existing missing-review-ref warnings
- `py -3 tests/app/workbench_validation_slice_tests.py` -> PASS
- `py -3 -m compileall -q apps/workbench/module/validation tests/app/workbench_validation_slice_tests.py`
  -> PASS
- touched JSON parse for command input, diagnostics registry, refusal registry,
  result schema, and validation result schema -> PASS
- `py -3 tools/validators/contracts/check_command_surface.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`
  -> PASS
- `py -3 -m apps.workbench.module.validation --repo-root . --target unknown.scope --profile FAST`
  -> PASS, expected typed refusal with exit code 1
- `git diff --check` -> PASS

Full repository validation was not run.

## Non-Goals Preserved

- no full Workbench shell
- no rendered GUI
- no workspace runtime
- no runtime module loader
- no provider runtime
- no package runtime
- no renderer UI or native GUI
- no direct Workbench binding to private validator paths
