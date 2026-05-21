Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Workbench Validation Slice

`WORKBENCH-VALIDATION-SLICE-01` adds the first skeletal Workbench projection for
the registered `dominium.validation.run` command.

The slice is intentionally headless. It provides:

- a command boundary in `apps/workbench/module/validation/command.py`
- a service adapter in `apps/workbench/module/validation/service_adapter.py`
- a Workbench projection facade in `apps/workbench/module/validation/workbench_projection.py`
- a CLI entrypoint in `apps/workbench/module/validation/cli.py`

It does not add a Workbench shell, GUI, workspace runtime, runtime module loader,
provider runtime, package runtime, renderer UI, or native GUI.

## Boundary

Workbench code consumes `dominium.validation.run` results. It does not call
private validators directly.

The adapter boundary is:

1. CLI, headless tests, or Workbench projection submit a typed command request.
2. `run_validation_command` normalizes profile, surface, and aggregate target.
3. `ValidationServiceAdapter` calls the public unified validation suite export.
4. The command boundary returns `contracts/result/result.schema.json` shape with
   validation payload, typed diagnostics, typed refusals, and evidence refs.
5. Workbench projection turns the command result into table rows without
   inventing new meanings.

The actual validation report payload remains governed by
`contracts/schema/validation_result.schema.json`.

## CLI

The headless CLI path is:

```text
py -3 apps/workbench/module/validation/cli.py --repo-root . --profile FAST --target all
```

For import-style invocation:

```text
py -3 -m apps.workbench.module.validation --repo-root . --profile FAST --target all
```

By default the service returns inline command evidence and does not write report
artifacts. `--write-reports` explicitly asks the service adapter to write the
governed validation report outputs.

## Refusal Semantics

The skeletal slice supports the aggregate validation target only:

- `all`
- `validate.all`
- `validation`
- `dominium.validation`
- `dominium.validation.run`

Unsupported targets refuse with
`dominium.refusal.validation.invalid_target` and `DOM-CMD-INVALID-INPUT`.
Unsupported caller surfaces refuse with
`dominium.refusal.command.unsupported_surface` and
`DOM-CMD-UNSUPPORTED-SURFACE`.

Validation-suite blocking findings are projected as
`DOM-VALIDATION-RUN-REFUSED`. Non-blocking validation warnings are projected as
`DOM-VALIDATION-RUN-WARNING`.

## Contract Impact

Changed contract surfaces:

- `contracts/command/validation_run_input.schema.json` now declares `profile`,
  `surface`, and `emit_reports`.
- `contracts/module/module_surface.contract.toml` now records the skeletal
  headless implementation path.
- `contracts/diagnostics/diagnostic_code.registry.json` now includes the two
  generic validation-run diagnostic display codes used by the command boundary.

Unchanged contract posture:

- `contracts/workbench/workbench_surface.contract.toml` keeps
  `workspace_runtime_implemented=false`.
- `dominium.validation.run` remains provisional.
- Provider runtime, Workbench runtime, and GUI behavior remain out of scope.

## Tests

Targeted proof:

```text
py -3 tests/app/workbench_validation_slice_tests.py
```

The test uses a fake validation service for command/projection parity so it does
not broaden into full repository validation during unit-level proof.
