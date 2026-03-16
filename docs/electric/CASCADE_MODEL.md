Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Cascade Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: Authoritative (ELEC-5)  
Series: ELEC-5  
Date: 2026-03-03

## 1) Purpose

ELEC-5 defines deterministic cascade handling for large electrical grids without introducing new solver tiers.

## 2) Cascade Sources

- overload -> protection trip -> topology/capacity change -> upstream/downstream stress redistribution
- line/device loss -> delivered power shift -> load stress change
- short/open/ground fault sequences with coordination ordering

## 3) Deterministic Ordering

Within one electrical network tick:

1. Networks sorted by `graph_id`
2. Fault targets sorted by deterministic target key
3. Protection devices sorted by coordination policy + `device_id`
4. Cascade rows sorted by `(coordination_group_id, device_id, fault_id)`

## 4) Cascade Execution Rule

Cascade execution uses bounded fixed-point semantics:

1. Evaluate faults
2. Evaluate protection/trip candidates
3. Apply safety actions for planned trips
4. Re-check for newly activated trip candidates
5. Repeat until fixed point OR iteration cap

Iteration cap contract:

- `cascade_max_iterations` is a fixed deterministic constant (default `4`)
- cap reach is logged in runtime metadata
- cap value does not depend on wall-clock

## 5) Budget / Degradation Interaction

Cascade processing remains deterministic under pressure:

- fault eval budget defers targets deterministically
- trip action budget defers devices deterministically
- deferred rows are logged and reflected in proof surface

## 6) Logging and Proof

Each electrical tick must preserve:

- `fault_state_hash_chain`
- `trip_event_hash_chain`
- `protection_state_hash_chain`
- `degradation_event_hash_chain`
- `power_flow_hash_chain`

Trip cascade investigation rows must retain deterministic IDs and replay references.
