# Temporal Semantics Constitution

Status: CANONICAL  
Last Updated: 2026-03-04  
Scope: TEMP-0 constitution for temporal domains, mappings, causality, warp semantics, and timeline branching.

## 1) Purpose

Define a deterministic temporal substrate where authoritative truth mutations remain ordered by canonical ticks while additional notions of time are modeled as explicit, auditable mappings.

## 2) Canonical Engine Time

- `CanonicalTime` is integer tick index (`t_tick`).
- All authoritative truth mutation is ordered by canonical tick.
- Subsystems must not reorder canonical ticks.
- Wall-clock APIs are never authoritative inputs.

## 3) TemporalDomains

`TemporalDomain` is a named interpretation space over canonical ticks.

Baseline domains:
- `time.canonical_tick`
- `time.proper`
- `time.civil`
- `time.warp`
- `time.replay`

Domain scope is explicit (`global`, `per_spatial`, `per_assembly`, `per_session`).

## 4) TimeMappings

`TimeMapping` is a deterministic constitutive-model binding from canonical ticks into a target domain:

`d(domain_time)/d(tick) = f(model_inputs, policy, deterministic parameters)`

Rules:
- `from_domain_id` is `time.canonical_tick`.
- mapping evaluation is deterministic, budgeted, and cacheable.
- mappings must not reorder canonical tick execution.
- mappings are derived semantics and do not mutate canonical tick order.

## 5) Scheduling Semantics

Schedules may target any declared `temporal_domain_id`.

Execution contract:
- schedule intent is evaluated at canonical tick boundaries.
- trigger condition is domain-aware (example: `proper_time >= target_time_value`).
- commit remains anchored to canonical tick ordering.
- schedule evaluation order is deterministic.

Default compatibility:
- missing/legacy schedule domain binds to `time.canonical_tick`.

## 6) Time Warp

Time warp is policy, not clock magic:
- deterministic batching of canonical ticks
- deterministic fixed substeps or closed-form updates
- no adaptive float-error-driven step sizing
- no wall-clock adaptive stepping

## 7) Synchronization

Synchronization emerges from explicit information flow:
- time-stamp artifacts
- delivery receipts
- trust and verification policy

There is no implicit universal clock synchronization beyond canonical tick order.

## 8) Epistemic Time

"When subject S knew X" is represented by:
- receipt acquisition tick (`knowledge_receipt.acquired_tick`)
- memory and belief artifacts

Epistemic time can differ from civil/proper domains due to delay and trust mediation.

## 9) Branching Timelines (Time Travel)

Time travel is explicit branch lineage:
- fork `UniverseState` at canonical tick `T`
- assign explicit `branch_id`
- record authority origin and proof anchors

Forbidden:
- silent in-place canonical truth rewrite
- retroactive mutation of existing lineage

## 10) Sharding

- each shard keeps canonical tick order locally.
- cross-shard temporal coordination is artifact-driven.
- no direct cross-shard temporal mutation or hidden sync.

## 11) Compression and Storage

- canonical ticks and event ordering are canonical persisted truth.
- derived domain times (`proper`, `civil`, `warp`, `replay`) may be recomputed.
- replay/proof invariants use canonical order and deterministic hash chains.

## 12) Non-Goals (TEMP-0)

- no relativity solver
- no waveform clock simulation
- no wall-clock authority coupling
- no change to existing RS canonical tick semantics
