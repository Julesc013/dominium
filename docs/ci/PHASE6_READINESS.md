# Phase 6 Readiness (LIFE/CIV)

This declaration defines what Phase 6 can safely assume and what it must not assume.
It is constrained by Phase-1 enforcement and Phase 2–5 audit outcomes.

## Phase 6 MAY assume (safe foundations)
- ACT is the only authoritative timebase; all scheduling uses ACT.
- Event-driven stepping exists and is required for macro systems.
- Fidelity projection and interest sets are the only refinement/collapse pathways.
- Rendering never affects simulation state or authoritative hashes.
- UI uses epistemic capability snapshots only; no authoritative reads.
- Ledger primitives are deterministic and event-driven.
- Provenance is required across fidelity tiers.

## Phase 6 MUST NOT assume
- That all Phase 2–5 data structures already have schema/versioning or migrations.
- That static architectural scans (arch_checks) are wired into CI everywhere.
- That determinism gates (DET-G1..G6) are implemented and enforced in CI.
- That render canon enforcement (REND-*) exists in CI.
- That macro subsystems expose `next_due_tick` unless specified in their specs.

## Phase 6 constraints for LIFE/CIV

1) Determinism
- Use fixed-point or integer math only in authoritative paths.
- No wall-clock time; ACT is the sole authoritative clock.
- No unordered iteration without normalization.

2) Event-driven scalability
- Every LIFE/CIV subsystem MUST provide `next_due_tick`.
- No “update all population/cities/markets” patterns.
- Interest sets must bound processing for refinement and UI projections.

3) Epistemic boundary
- All UI-visible LIFE/CIV data must flow through BeliefStores and capability snapshots.
- Market, population, and governance info must be expressed as InfoRecords or capability snapshots.

4) Schema governance
- LIFE/CIV data definitions MUST be schema-versioned with explicit migration rules.
- Mods must declare compatible schema versions; unknown fields preserved.

5) Provenance & continuity
- Birth/death, inheritance, and institutional continuity must preserve provenance hashes.
- Fidelity transitions may not fabricate population or institutions.

## Readiness blockers to resolve before Phase 6
- Missing schema governance for Phase 2–5 data-defined structures.
- Legacy knowledge/economy scaffolding conflicting with event-driven and epistemic rules.
- CI not wiring static scans and determinism gates.
