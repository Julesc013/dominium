# Lockfile Contracts

Status: PROVISIONAL
Phase: CONVERGE-06

This directory is reserved for deterministic lockfile schemas and lockfile contract definitions.

Concrete lock artifacts belong in install/runtime projections such as `store/locks/`. Process and IPC locks belong under `runtime/locks/`. Setup, update, and rollback transaction state belongs under `ops/transactions/`.

## POST-CONVERGE-04 Note

`contracts/package/locks/pack_lock.mvp_default.json` remains a concrete source lock artifact with embedded identity metadata and distribution copy behavior. Move only lockfile schemas or contract definitions here after protected lock ownership review.

## COMPOSITION-RESOLVER-LAW-01 Note

This directory now owns the provisional schema definitions for derived
composition lockfiles and reports:

- `app_composition_lock.schema.json`
- `pack_mount_lock.schema.json`
- `module_plan_lock.schema.json`
- `provider_selection_lock.schema.json`
- `capability_report.schema.json`
- `refusal_report.schema.json`
- `compatibility_report.schema.json`
- `trust_report.schema.json`

These schemas describe evidence artifacts produced by composition resolution.
They are not source truth and do not implement runtime package mounting,
provider selection, module loading, Workbench runtime behavior, or launch
behavior.
