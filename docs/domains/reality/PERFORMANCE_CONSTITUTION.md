Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Performance Constitution

## Purpose
Define deterministic performance governance for bounded micro simulation work, deterministic arbitration under overload, and inspection as cached derived artifacts.

## A) Performance Envelope
Each authoritative shard must run under explicit policy bounds:
- `max_micro_entities_per_shard`
- `max_micro_regions_per_shard`
- `max_solver_cost_units_per_tick`
- `max_inspection_cost_units_per_tick`

Envelope values are policy artifacts, not hardcoded mode switches.

## B) Deterministic Degradation
When demand exceeds configured capacity, degradation is mandatory and deterministic.

Required degradation order:
1. reduce solver tier
2. collapse least-priority regions
3. reduce inspection resolution/budget
4. refuse additional expansion requests

Runtime must degrade rather than absorb unbounded lag spikes.

## C) Arbitration
Arbitration under contention is deterministic and policy-driven.

Supported constitutional modes:
- equal share per active player
- server-profile weighted allocation

Tie-breaking uses stable deterministic ordering:
- `(player_id, region_id, tick)`

No wall-clock-derived heuristics may participate in arbitration.

## D) Inspection As Derived Artifact
Inspection operations are derived snapshot generation, not solver recomputation triggers.

Requirements:
- Inspection emits deterministic derived `inspection_snapshot` artifacts.
- Snapshots are cacheable by deterministic content hash.
- Cached snapshots are reused until deterministic invalidation.
- Inspection path must not mutate authoritative truth.
- Inspection path must respect epistemic redaction and entitlement gates.

## E) Hysteresis
Transition hysteresis is required to prevent deterministic thrash.

Minimum guarantees:
- deterministic minimum dwell time before re-collapse after expansion
- deterministic thresholds for re-expand after degrade
- thresholds are policy-defined and replay-stable

## Multiplayer Fairness
- Lockstep/authoritative/hybrid policies must all honor deterministic envelope and arbitration rules.
- Ranked profiles may constrain arbitration policy selection for fairness.
- Distributed-player workloads (e.g., sparse factory-planet observers) must resolve identically from identical canonical inputs.
