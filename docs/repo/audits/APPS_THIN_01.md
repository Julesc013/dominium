Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: APPS-THIN-01

# APPS-THIN-01 Audit

## Scope

Audit app-local directories that may violate the thin-product rule. This pass does not perform broad runtime API redesign.

Starting commit: `5f0f44fe4`

Branch: `main`

## Paths Inspected

- `apps/client/local_server/`
- `apps/client/model/`
- `apps/client/presentation/`
- `apps/server/authority/`
- `apps/server/persistence/`
- `apps/server/shard/`
- `apps/launcher/lifecycle/`
- `apps/setup/lifecycle/`
- `apps/launcher/include/launcher/_internal/`
- `apps/setup/include/dsu/_internal/`

## Classification

- `apps/client/local_server/` is retained as client-local orchestration glue over runtime network/process APIs. It imports runtime networking and shell pieces rather than owning them.
- `apps/client/model/` and `apps/client/presentation/` are retained as client-specific presentation and render-prep binding. They should be revisited if the same abstractions become shared by Workbench or other products.
- `apps/server/authority/` is retained as server invocation/gating around authority contracts. Shared law remains outside this app path.
- `apps/server/persistence/` is retained as server persistence binding/checkpoint integration. Shared storage substrate remains a follow-up if reuse appears.
- `apps/server/shard/` is retained as server-product sharding implementation.
- `apps/launcher/lifecycle/` and `apps/setup/lifecycle/` are retained as product-specific lifecycle wrappers and stubs.
- Product `_internal` include trees are retained as product-private headers. They are not promoted to runtime until a shared API boundary is explicit.

## Moves

No files were moved. The inspected files are product-specific enough to retain without inventing new runtime APIs during this narrow pass.

## Validation Results

No code moved. Final combined validation for the cleanup wave covers app build and smoke tests.

## Follow-Up Work

- If Workbench or another product starts importing client presentation/model internals, split shared view/model contracts into `contracts/view/` or `runtime/ui/`.
- If server persistence or authority becomes shared runtime service behavior, route it to `runtime/storage`, `runtime/capability`, or `game/law` with focused tests.
