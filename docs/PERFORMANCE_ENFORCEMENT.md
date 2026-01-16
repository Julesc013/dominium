# Performance Enforcement Law (ENF0)

This document defines non-negotiable performance law for the Dominium / Domino repository.
All runtime code MUST comply. Violations are merge-blocking.

## Scope

Performance law applies to engine, game, client, server, and runtime tooling paths.
It does not grant permission to alter gameplay systems.

## A. No-Global-Iteration Rule

The following patterns are FORBIDDEN:

- “update all entities”
- “tick all cities”
- “iterate all markets”
- Any unbounded traversal over global registries in runtime updates

Runtime stepping MUST be event-driven and bounded by interest sets.

**MUST NOT**
- Iterate over all world entities in a frame or tick.
- Traverse all domain objects without a bounded interest set.
- Use global sweeps as a fallback when event routing fails.

**Rationale**
Global iteration scales poorly and undermines deterministic scheduling and throughput budgets.

## B. No-Modal-Loading Rule

The following behaviors are FORBIDDEN:

- Blocking IO on render or UI threads
- Shader compilation on demand
- Synchronous asset decoding on render or UI threads

**Derived job requirements**
- All IO, decode, and compilation work MUST run in background job systems.
- Shader compilation MUST be performed at build time or explicit preload phases.
- Asset decode MUST be streamed and cached before use by render or UI threads.
- Runtime fallback assets MUST exist when streaming is incomplete.

**Stall watchdog thresholds**
- Any render-thread stall caused by IO or decode exceeding 2 ms in a frame is a failure.
- Any UI-thread stall caused by IO or decode exceeding 1 ms in a frame is a failure.
- Any blocking file or network call on render or UI threads is a failure regardless of duration.

**Rationale**
Modal loading introduces frame hitches and nondeterministic stalls that defeat scalability budgets.

## C. Fidelity Degradation Law

Acceptable degradation mechanisms are strictly limited to:

- Aggregation
- Resolution reduction
- Update cadence reduction

Forbidden degradation mechanisms include:

- Entity despawn without provenance
- State reset or rollback for performance reasons
- Visual-driven simulation changes

**MUST NOT**
- Remove authoritative entities solely to reduce load.
- Reset simulation state to recover performance.
- Change simulation outcomes based on renderer or visual fidelity.

**Rationale**
Degradation must preserve authoritative state and provenance while scaling performance costs.
