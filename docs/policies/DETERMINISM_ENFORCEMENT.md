Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Determinism Enforcement Law (ENF0)

This document defines non-negotiable determinism law for the Dominium / Domino repository.
All authoritative simulation code MUST obey these rules. Violations are merge-blocking.

## Scope

Determinism law applies to all authoritative zones and any code paths that influence authoritative state.
No temporary or conditional exception is allowed.

## A. Authoritative Determinism Zones

The following directories are authoritative and MUST be deterministic:

- `engine/modules/core/**`
- `engine/modules/sim/**`
- `engine/modules/world/**`
- `game/rules/**`
- `game/economy/**`
- `game/core/**` (simulation paths only)

**Rationale**
Authoritative zones produce canonical state; nondeterminism here corrupts replayability,
lockstep simulation, and server authority.

## B. Forbidden Constructs in Authoritative Zones

The following constructs are FORBIDDEN in authoritative zones:

- Floating point arithmetic (`float`, `double`, `long double`, SIMD float ops).
- OS time APIs (wall clock, monotonic clock, performance counters).
- Random number generators outside the deterministic RNG approved by engine core.
- Unordered containers without deterministic normalization before any iteration, hashing, or serialization.
- Iteration over global containers or registries without an explicit deterministic ordering.
- Thread races or shared mutable state without deterministic scheduling and ordered reduction.

**MUST NOT**
- Call platform time APIs or external time sources.
- Use non-deterministic seeds or entropy sources.
- Depend on iteration order of hash-based containers.
- Perform cross-thread writes without deterministic synchronization.

**Rationale**
These constructs introduce nondeterministic state divergence that cannot be detected or repaired at runtime.

## C. Determinism Gates

Determinism gates are mandatory CI checks. Any failure blocks merging.

### Gate DET-GATE-STEP-001 — Step vs Batch Equivalence

- **What is tested:** N simulation steps executed individually MUST match a single batch step of N.
- **Failure means:** Update order or state accumulation is nondeterministic.
- **Merge block phase:** Test (determinism suite).

### Gate DET-GATE-REPLAY-002 — Replay Equivalence

- **What is tested:** A recorded input stream MUST reproduce the original authoritative state hash.
- **Failure means:** Replay is non-canonical or uses nondeterministic inputs.
- **Merge block phase:** Test (replay determinism suite).

### Gate DET-GATE-LOCKSTEP-003 — Lockstep vs Server-Auth Equivalence

- **What is tested:** Lockstep simulation and server-authoritative simulation MUST converge to identical hashes.
- **Failure means:** Authority or client prediction diverges from canonical rules.
- **Merge block phase:** Test (network determinism suite).

### Gate DET-GATE-HASH-004 — Hash Partition Invariance

- **What is tested:** Hashes computed across partitioned or sharded state MUST match monolithic hashes.
- **Failure means:** Partitioning changes simulation outcomes or ordering.
- **Merge block phase:** Test (shard invariance suite).

**Rationale**
Determinism gates enforce equivalence across execution modes and prevent drift from authoritative law.