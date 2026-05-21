Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Lockfile Law

Composition lockfiles and reports are deterministic derived evidence. They
record a resolution result; they do not become the source truth for app,
profile, pack, module, provider, capability, trust, compatibility, or artifact
inputs.

## Required Shape

Each composition lock/report carries:

- `lock_id` or `report_id`
- `source_plan_ref`
- `decision_ref`
- `source_commit` or `source_artifact_refs`
- `schema_version`
- `generated_by`
- optional `generated_at`
- `entries[]`
- `diagnostics[]`
- `evidence_ref`
- optional `content_hash` or `canonical_hash`
- `limitations[]`
- `status`
- `artifact_class = derived_evidence`
- `source_truth = false`

Schemas live in `contracts/lock/`.

## Lock And Report Types

- `app_composition.lock.json`
- `pack_mount.lock.json`
- `module_plan.lock.json`
- `provider_selection.lock.json`
- `capability_report.json`
- `refusal_report.json`
- `compatibility_report.json`
- `trust_report.json`

The checked-in schema filenames use `_schema.json` to describe these future
artifact shapes.

## Source Truth Boundary

Lockfiles cite source plans, decisions, commits, artifacts, diagnostics, and
evidence. They are reproducible records, not authored doctrine or descriptors.
If a lockfile conflicts with a descriptor, manifest, registry, or canonical law,
the stronger source wins and the lock is stale, invalid, refused, or degraded.

Generated lockfiles may help launch, package, inspect, or review a product only
after a resolver or validator proves the underlying inputs. A checked-in fixture
lock proves schema behavior only.

## Determinism

Re-running resolution from the same governed inputs must produce equivalent
canonical lock content. Ordering inputs are declared mount/module/provider/
capability order, stable IDs, policy-declared tie-breakers, and canonical
serialization. Filesystem enumeration, wall-clock timing, thread completion
order, and hidden runtime state are not valid ordering inputs.

Hashes are optional in the first contract slice. When present, `content_hash` or
`canonical_hash` must cover canonical lock content rather than a path or
presentation-only copy.

## Forbidden Claims

Lock IDs and report IDs must not be raw paths. Lockfiles may not claim source
truth. Planned or fixture-only lock rows may not claim runtime support. Stale
locks require a diagnostic and evidence trail.

Silent fallback, silent overlay overwrite, missing diagnostic codes for
refusals, and degraded provider decisions without fallback trace are validation
failures.

## Future Use

Future launcher, setup, Workbench, client, server, package, and release tasks
may consume these locks. This law does not implement those consumers and does
not authorize lockfiles to mutate authoritative truth directly.
