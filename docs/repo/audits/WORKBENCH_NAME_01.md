Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: WORKBENCH-NAME-01

# WORKBENCH-NAME-01 Audit

## Scope

Verify Workbench module naming and Workbench-adjacent ownership after the source-spine cleanup.

Starting commit: `5f0f44fe4`

Branch: `main`

## Paths Inspected

- `apps/workbench/module/game/edit/`
- `apps/workbench/module/tool/editor/`
- `apps/workbench/module/ui/editor/gen/`
- `apps/workbench/module/ui/native/`
- `apps/workbench/module/ui/preview/support/`

## Result

The retired Workbench paths are already absent from active tracked source.

Existing path-term validator guards already reject:

- `apps/workbench/module/game/edit`
- `apps/workbench/module/tool/editor`
- `apps/workbench/module/ui/editor/gen`
- `apps/workbench/module/ui/native`
- `apps/workbench/module/ui/preview/support`

## Moves

No files were moved in this pass.

## Validation Results

Final combined validation for the cleanup wave covers path-term guards, docs sanity, build, and smoke tests.

## Follow-Up Work

- Continue to route user-facing editors/viewers/inspectors to `apps/workbench/module/*`.
- Route reusable runtime UI/platform code to `runtime/ui` or `runtime/platform`, and non-interactive generation to `tools/codegen`.
