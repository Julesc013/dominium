Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Result: PASS_WITH_WARNINGS

# WORKBENCH_VALIDATION_SLICE_01

## Scope

This slice implements the first narrow governed Workbench validation proof for
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
- `apps/workbench/workspace/validation/validation_workspace.json`
- `contracts/command/validation_run_input.schema.json`
- `contracts/command/validation_run_result.schema.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/module/module_surface.contract.toml`
- `docs/development/workbench_validation_slice.md`
- `docs/workbench/WORKBENCH_VALIDATION_SLICE.md`
- `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- `tests/contract/module/fixtures/valid_workbench_module.json`
- `tests/contract/workbench/fixtures/valid_view_binding.json`
- `tests/app/workbench_validation_slice_tests.py`

## Contract And Schema Impact

Contract/schema impact changed narrowly:

- validation command input now exposes `profile`, `surface`, and `emit_reports`
- validation command input now also exposes `target_kind`, `target_path`,
  `artifact_ref`, `suite_id`, `mode`, `capabilities`, and
  `required_capabilities`
- validation command result now has the dedicated typed schema
  `contracts/command/validation_run_result.schema.json`
- Workbench validation module row now points at the skeletal headless module
- diagnostics and refusal registries now include typed target unknown, target
  kind unsupported, and target outside allowed root surfaces

No change was made to Workbench workspace runtime status. It remains false.

Chosen validation target:

- target kind: `contract_schema`
- target path: `contracts/command/validation_run_input.schema.json`
- suite ID: `validate.contract_schema_artifact`

## Evidence

Validation evidence:

- `py -3 .aide/scripts/aide_lite.py doctor` -> PASS
- `py -3 .aide/scripts/aide_lite.py validate` -> PASS_WITH_WARNINGS,
  existing missing-review-ref warnings
- `py -3 tests/app/workbench_validation_slice_tests.py` -> PASS
- `py -3 -m compileall -q apps/workbench/module/validation tests/app/workbench_validation_slice_tests.py`
  -> PASS
- touched JSON parse for command input, diagnostics registry, refusal registry,
  result schema, validation-run result schema, and validation result schema -> PASS
- `py -3 tools/validators/contracts/check_command_surface.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_provider_model.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/contracts/check_app_descriptors.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/repo/check_public_surface.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
  -> PASS, 0 violations, 68 existing warnings
- `py -3 tools/validators/check_component_matrices.py --repo-root . --strict`
  -> PASS
- `py -3 tools/validators/platform/check_portability_matrix.py --repo-root . --strict`
  -> PASS
- `py -3 scripts/verify_docs_sanity.py --repo-root .` -> PASS
- `py -3 scripts/verify_build_target_boundaries.py --repo-root .` -> PASS
- `py -3 scripts/verify_ui_shell_purity.py --repo-root .` -> PASS
- `py -3 scripts/verify_abi_boundaries.py --repo-root .` -> PASS
- `py -3 -m apps.workbench.module.validation --repo-root . --target unknown.scope --profile FAST`
  -> PASS, expected typed refusal with exit code 1
- `py -3 -m apps.workbench.module.validation --repo-root . --target-kind contract_schema --target-path contracts/command/validation_run_input.schema.json --suite-id validate.contract_schema_artifact --profile FAST`
  -> PASS, contract-schema artifact validated through typed command result
- `py -3 -c "<parse touched JSON/TOML artifacts>"` -> PASS, 9 artifacts parsed
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/WORKBENCH-VALIDATION-SLICE-01-fast-strict.json --md-out .aide/reports/WORKBENCH-VALIDATION-SLICE-01-fast-strict.md`
  -> PASS, T0/T1/T2 selected, 33 commands, smoke CTest 57/57 passed
- `git diff --check` -> PASS

Full T4 CTest and release-promotion gates were not run.

## Non-Goals Preserved

- no full Workbench shell
- no rendered GUI
- no workspace runtime
- no runtime module loader
- no provider runtime
- no package runtime
- no renderer UI or native GUI
- no direct Workbench binding to private validator paths
