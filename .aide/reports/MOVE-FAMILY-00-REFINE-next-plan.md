# MOVE-FAMILY-00-REFINE Next Plan

Status: DERIVED
Last Reviewed: 2026-05-17

## Recommended Next Task

```text
MOVE-FAMILY-00B-PLAN - IDE Manifest Contract/Projection Ownership Plan
```

## Why This Comes Next

The IDE manifest group is the smallest refined group and has the clearest target owner: `contracts/projections`.

Active Python roots remain higher risk:

- `validation/**`, `meta/identity/**`, and `meta/stability/**` need a temporary shim and validator namespace plan.
- `governance/**` needs release/tool import proof and a shimmed governance-tooling namespace plan.
- most `meta/**` files are semantic/runtime/domain support and must not be moved as tooling.
- `performance/**` has product/client/game consumers and should not be forced into `tools/performance`.

## Expected MOVE-FAMILY-00B Scope

MOVE-FAMILY-00B should remain planning-only unless a later gate expands scope. It should decide the contract path, schema validator, reference rewrite list, rollback path, and exception update conditions for `ide/manifests/**`.

## Not Recommended

Do not proceed directly to `MOVE-FAMILY-00-GATE`. No apply-ready move set exists yet.
