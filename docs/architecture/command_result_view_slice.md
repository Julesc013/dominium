Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: COMMAND-RESULT-VIEW-SLICE-01

# Command Result View Slice

COMMAND-RESULT-VIEW-SLICE-01 proves a narrow semantic presentation path for
`dominium.validation.run`:

```text
command
-> typed result/refusal/diagnostic/evidence
-> semantic view
-> declared actions
-> projection fixtures
-> Workbench-facing projection data
```

This is not a runtime projection engine and not broad UI work.

## Model

- Command: `dominium.validation.run`
- Result schema: `contracts/command/validation_run_result.schema.json`
- Semantic view: `dominium.validation.summary.v1`
- Action registry: `contracts/action/validation_actions.registry.json`
- Projection kind registry: `contracts/presentation/projection_kind.registry.json`
- Projection set: `contracts/presentation/validation_summary.projections.json`

The view presents command output. It is not authority and does not mutate truth.
The actions are semantic operations available from the view. Only rerun is
command-backed by the existing validation command; open report and export
evidence are contract-only descriptors in this slice.

## Projection Kinds

`cli`, `text`, `rendered`, `native`, and `headless` are projection kinds. They
are not separate semantic authorities.

This slice proves fixture-level projections for:

- headless JSON/report shape
- CLI table/structured shape
- text/TUI-style panel stub
- Workbench-facing projection data

Rendered and native projections are descriptor-only placeholders and explicitly
do not claim runtime implementation.

## Result, Document, Snapshot, Patch

This slice is result-focused:

- A result is command output.
- A document is persistent/editable logical state.
- A snapshot is a read-only state projection.
- A patch is a lawful mutation proposal.

The validation summary view accepts the validation result schema. It does not
claim document or snapshot ownership.

## Boundaries

This slice does not implement:

- full Workbench shell
- rendered GUI
- native GUI
- TUI runtime
- runtime view/projection engine
- runtime module loader
- provider runtime
- package runtime
- gameplay/domain work
- release publication

Workbench remains a shell host for projection data. It does not call private
validators directly and does not become authority.
