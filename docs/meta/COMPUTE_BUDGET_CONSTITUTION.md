Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Compute Budget Constitution

Status: CANONICAL-DERIVED
Series: META-COMPUTE-0
Version: 1.0.0

## 1) Purpose
Define deterministic compute resource budgeting for executable simulation logic (controllers, compiled models, process pipeline compute steps) so compute is explicit, profile-driven, auditable, and replay-stable.

## 2) Compute Units

Canonical compute unit axes:

- `instruction_units`
  - budgeted per canonical tick
  - consumed by executable evaluations
- `memory_units`
  - persistent state footprint budget
  - consumed by active controller/model state
- `io_units` (optional)
  - declarative budget for signal/port I/O pressure
  - non-authoritative unless explicitly promoted by profile

Compute accounting must be deterministic and independent of wall-clock execution time.

## 3) ComputeBudgetProfile

`ComputeBudgetProfile` declares deterministic limits and degradation policy:

- per session and authority binding via profile architecture
- per subsystem class usage (`controller`, `system`, `process`, `compiled_model`)
- deterministic fields:
  - instruction budget per tick
  - total memory budget
  - evaluation cap per tick
  - degrade policy id
  - optional power coupling enable

## 4) Deterministic Throttling Order

When requested compute exceeds available budget, apply this deterministic order:

1. Reduce evaluation frequency via deterministic tick buckets.
2. Degrade to simpler compiled representation if available.
3. Cap number of evaluated owners per tick using stable ordering.
4. Refuse non-critical executions.
5. Trigger fail-safe shutdown when safety policy requires.

Ordering key:

- `(priority asc, owner_id asc)` for owner selection
- stable tie-break only; no unordered iteration

All throttles/refusals/shutdowns must produce canonical or decision-log records.

## 5) Runtime Requirements

- No hidden compute shortcuts.
- No unmetered loops in authoritative execution.
- Budget outcomes must be explicit (`approved`, `throttled`, `deferred`, `refused`, `shutdown`).
- Deterministic fingerprints and hash chains must include compute records when they affect authoritative behavior.

## 6) Physics Coupling Hooks

Profile-gated coupling from compute to physical domains:

- compute draw can request electrical energy via ledger transform
- inefficiency emitted as thermal loss via ledger transform
- canonical transform path only (no direct state mutation)

Recommended transform mapping:

- `transform.electrical_to_thermal`

If electrical availability is insufficient (policy-gated):

- deterministic throttle/refusal/shutdown path applies.

## 7) Integration Contract

Minimum integration points in this series:

- SYS macro capsule execution requests compute units per capsule evaluation.
- COMPILE runtime execution requests compute units for compiled model execute calls.
- PROC software pipeline compile/test steps request compute units.

Future integration:

- LOGIC evaluator and programmable controller runtime must consume this same budget engine.

## 8) Explainability

Required explain contracts for compute degradation outcomes:

- `explain.compute_throttle`
- `explain.compute_refusal`
- `explain.compute_shutdown`

## 9) Governance

- No runtime mode flags; behavior comes from explicit profile + policy rows.
- Overrides that materially alter invariant behavior must remain profile-gated and auditable.
- FAST profile may warn; STRICT/FULL enforce refusal on unmetered execution paths.
