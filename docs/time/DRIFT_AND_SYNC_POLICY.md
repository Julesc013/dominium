# Drift and Sync Policy

Date: 2026-03-04  
Scope: TEMP-2

## Drift

- Drift is optional and declared per mapping via `drift_policy_id`.
- Drift modifies derived domain-time increment only; canonical tick is unchanged.
- Drift is deterministic and bounded by policy:
  - `base_rate_multiplier`
  - optional `deterministic_rng_stream` (deterministically seeded by mapping/scope/tick)
  - `max_skew_allowed`

## Correction

- Correction is process-driven only: `process.time_adjust`.
- Inputs include remote stamp/receipt context and target domain scope.
- Correction behavior is policy-controlled and logged as `time_adjust_event`.
- No direct canonical tick mutation is permitted.

## Sync Modes

- `sync.none`
  - observe-only behavior; no correction.
- `sync.adjust_on_receipt`
  - bounded adjustment each invocation using `max_adjust_per_tick`.
- `sync.strict_reject`
  - rejects correction when skew exceeds policy bound.

## Determinism Rules

- No wall-clock APIs in authoritative sync logic.
- Deterministic ordering remains canonical tick first, then stable subject ordering.
- Every adjustment attempt emits deterministic artifacts/hashes for replay.
