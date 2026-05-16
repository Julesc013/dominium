# POST-CONVERGE-10J Next Family Recommendation

## Decision

POST-CONVERGE-11 must not proceed yet. Focused tuple `inv_repox_rules` still fails with 60 failures and 5 warnings.

## Recommended Next Task

`POST-CONVERGE-10K - Contract Registry Acceptance Backlog Remediation`

## Why

The largest remaining family is `INV-NEW-CONTRACT-REQUIRES-ENTRY` with 9 failures. These failures are concentrated around architecture contract tokens such as `contract.arch.graph.v1`, `contract.arch.module_boundaries.v1`, `contract.arch.module_registry.v1`, and `contract.arch.single_engine_registry.v1`.

## Not Recommended Yet

- POST-CONVERGE-11 remains blocked by focused RepoX semantic failures.
- TEST-PERF-00 remains useful later, but wall-time is not the current primary blocker while focused RepoX still fails.
- Distribution descriptor/product proof blockers should wait until contract registry and remaining governance-family failures are smaller or separately gated.
