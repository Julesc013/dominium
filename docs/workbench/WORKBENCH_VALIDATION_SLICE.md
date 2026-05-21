Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Workbench Validation Slice

`WORKBENCH-VALIDATION-SLICE-01` proves the first governed validation loop for
Workbench without adding a rendered shell, runtime module loader, provider
runtime, package runtime, renderer, native GUI, or gameplay behavior.

## Proven Loop

The slice uses one command identity across CLI/headless and Workbench projection:

- command ID: `dominium.validation.run`
- input schema: `contracts/command/validation_run_input.schema.json`
- result schema: `contracts/command/validation_run_result.schema.json`
- validation payload schema: `contracts/schema/validation_result.schema.json`
- evidence schema: `contracts/evidence/evidence_packet.schema.json`
- module ID: `dominium.workbench.validation`
- static workspace projection:
  `apps/workbench/workspace/validation/validation_workspace.json`

The chosen validation target is the real contract artifact
`contracts/command/validation_run_input.schema.json`, validated with:

```text
target_kind = contract_schema
target_path = contracts/command/validation_run_input.schema.json
suite_id = validate.contract_schema_artifact
mode = strict
profile = FAST
```

The older aggregate `validate.all` names remain recognized by the command
surface, but aggregate execution is not bound in this slice. It refuses with
`dominium.refusal.validation.tool_unavailable` until a later service-conformance
task defines that broader service boundary.

## Parity Rule

CLI/headless and Workbench projection use the same command boundary. Workbench
does not call private validators directly and does not own validation truth. It
projects the command result into a table-shaped document only after the command
returns typed diagnostics, typed refusal payloads, and evidence references.

The result payload carries:

- `validation_status`: `pass`, `pass_with_warnings`, `fail`, or `refused`
- `summary_counts`
- `validated_artifact_ref`
- `validation_report`
- `evidence_packet`

## Refusals And Diagnostics

Required refusal cases are typed:

- unknown target:
  `dominium.refusal.validation.target_unknown` /
  `DOM-VALIDATION-TARGET-UNKNOWN`
- unsupported target kind:
  `dominium.refusal.validation.target_kind_unsupported` /
  `DOM-VALIDATION-TARGET-KIND-UNSUPPORTED`
- missing capability:
  `dominium.refusal.command.capability_missing` /
  `DOM-CAPABILITY-MISSING`
- target outside allowed root:
  `dominium.refusal.validation.target_outside_allowed_root` /
  `DOM-VALIDATION-TARGET-OUTSIDE-ROOT`
- invalid input before execution:
  `dominium.refusal.command.invalid_input` /
  `DOM-CMD-INVALID-INPUT`

Validation execution warnings and refusals remain:

- `DOM-VALIDATION-RUN-WARNING`
- `DOM-VALIDATION-RUN-REFUSED`

## Runtime Gaps

Still not implemented:

- Workbench shell
- rendered UI
- workspace runtime
- runtime module loading
- provider runtime
- package/mod runtime loading
- broad app composition runtime

## Next Slice

The next useful slice is `SERVICE-CONFORMANCE-LAW-01` unless a later
coordinator chooses `DOCUMENT-PATCH-TRANSACTION-RUNTIME-01` or
`PROJECT-GRAPH-SERVICE-01` first.
