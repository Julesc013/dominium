Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: COMMAND-RESULT-VIEW-SLICE-01

# Workbench Command Result View Projection

Workbench validation now has a narrow semantic summary projection for
`dominium.validation.run`.

The projection helper:

```text
apps/workbench/module/validation/workbench_projection.py
```

adds `project_validation_summary(command_result)`. It consumes an existing
command result and emits Workbench-facing projection data for:

- summary
- status
- counts
- diagnostics
- evidence
- target
- refusal
- declared actions

It does not invoke validators, scan file paths, mutate state, implement a
workspace runtime, or implement a rendered/native UI.

The Workbench workspace fixture keeps:

```text
workspace_runtime_implemented = false
private_tool_calls = false
```

Workbench remains a projection host over command/result/evidence contracts.
