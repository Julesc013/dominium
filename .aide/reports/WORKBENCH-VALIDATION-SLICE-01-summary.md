Status: PASS_WITH_WARNINGS
Task: WORKBENCH-VALIDATION-SLICE-01
Phase: post-foundation-product-slice

# Workbench Validation Slice 01 Summary

## Summary

Implemented the narrow governed validation product loop around
`dominium.validation.run` for one real target:
`contracts/command/validation_run_input.schema.json`.

The slice preserves semantic parity across CLI/headless and static Workbench
projection:

- command ID: `dominium.validation.run`
- module ID: `dominium.workbench.validation`
- workspace projection: `dominium.workbench.workspace.validation`
- target kind: `contract_schema`
- suite ID: `validate.contract_schema_artifact`
- input schema: `contracts/command/validation_run_input.schema.json`
- result schema: `contracts/command/validation_run_result.schema.json`
- evidence schema: `contracts/evidence/evidence_packet.schema.json`

## Changed Files

- `apps/workbench/module/validation/cli.py`
- `apps/workbench/module/validation/command.py`
- `apps/workbench/module/validation/service_adapter.py`
- `apps/workbench/module/validation/workbench_projection.py`
- `apps/workbench/workspace/validation/validation_workspace.json`
- `contracts/command/command_surface.contract.toml`
- `contracts/command/validation_run_input.schema.json`
- `contracts/command/validation_run_result.schema.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/module/module_surface.contract.toml`
- `contracts/refusal/refusal_code.registry.json`
- `docs/development/workbench_validation_slice.md`
- `docs/workbench/WORKBENCH_VALIDATION_SLICE.md`
- `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- `tests/app/workbench_validation_slice_tests.py`
- `tests/contract/module/fixtures/valid_workbench_module.json`
- `tests/contract/workbench/fixtures/valid_view_binding.json`
- `.aide/reports/WORKBENCH-VALIDATION-SLICE-01-fast-strict.json`
- `.aide/reports/WORKBENCH-VALIDATION-SLICE-01-fast-strict.md`
- `.aide/reports/WORKBENCH-VALIDATION-SLICE-01-summary.md`
- `.aide/reports/WORKBENCH-VALIDATION-SLICE-01-validation.json`

## Refusal And Diagnostic IDs

- `dominium.refusal.validation.target_unknown` /
  `DOM-VALIDATION-TARGET-UNKNOWN`
- `dominium.refusal.validation.target_kind_unsupported` /
  `DOM-VALIDATION-TARGET-KIND-UNSUPPORTED`
- `dominium.refusal.validation.target_outside_allowed_root` /
  `DOM-VALIDATION-TARGET-OUTSIDE-ROOT`
- `dominium.refusal.command.capability_missing` /
  `DOM-CAPABILITY-MISSING`
- `dominium.refusal.command.invalid_input` /
  `DOM-CMD-INVALID-INPUT`

## Validation

- Targeted app proof: PASS
- Command, diagnostic, artifact, capability/refusal, provider, module,
  Workbench, app, public-surface, dependency-direction, component-matrix, and
  portability validators: PASS
- AIDE doctor/validate: PASS with known missing-review-ref warnings
- Fast strict: PASS, 33 commands, T0/T1/T2 selected, smoke CTest 57/57 passed
- `git diff --check`: PASS

## Remaining Warnings

- Dependency-direction strict remains PASS with 68 existing warnings and 0
  violations.
- AIDE validate reports existing missing review-packet reference warnings.
- RepoX fast-strict reports the known stale AuditX warning.
- Full T4 CTest and release-promotion gates were not run.
- Workbench shell, rendered UI, runtime workspace loading, runtime module
  loading, provider runtime, and package/mod runtime remain unimplemented.

## Non-Goals

No broad Workbench UI, renderer, native GUI, provider runtime, package runtime,
module loader, gameplay, release publication, or private validator bypass was
implemented.
