Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Shard policy, authority boundaries, and simulation orchestration.
- Implementation lives under `game/` (rules/content/server logic).

TOOLS:
- Inspection and verification utilities only.

SCHEMA:
- Message/schema definitions for shard metadata if needed.

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_SHARDING_AUTHORITY — Sharding & Authority Partition Canon

Status: draft
Version: 1

## Purpose
Define the authoritative sharding model for Dominium / Domino. Sharding MUST NOT
change simulation semantics, determinism, or provenance. All partitions are
logical authority domains; deployment is a separate concern.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Every authoritative object has exactly one shard that can mutate it.
2) Cross-shard interaction is explicit, scheduled, and deterministic.
3) No shard reads or writes authoritative state owned by another shard directly.
4) All shards share ACT; no per-shard clocks or drift.
5) Sharding changes placement, not rules or outcomes.

## Definitions (mandatory)

### SHARD
An authority domain with:
- unique `shard_id`
- defined spatial/scope boundary
- single authoritative writer
- local deterministic event queue

### SHARD KEY
A deterministic mapping from world identity to `shard_id`.
Examples: `galaxy_id`, `system_id`, `body_id`, `region_id`, `local_bubble_id`.

### AUTHORITY DOMAIN
The set of objects whose authoritative state may be mutated by a shard.

### SHARD OWNER
The process or machine currently responsible for the shard's authoritative writes.

## Sharding axes (mandatory)

### 1) Spatial
Partition boundaries may follow:
`galaxy -> system -> body -> region -> local bubble`.

### 2) Functional
Partition layers may follow:
- MACRO (economy, population)
- MESO (cities, factories)
- MICRO (entities, vehicles)

### 3) Temporal (single clock)
All shards share ACT.
Pacing differs only via batching; clocks MUST NOT diverge.

## Authority rules (locked)

**MUST**
- A shard MUST NOT mutate state outside its authority domain.
- A shard MUST NOT read or write authoritative state owned by another shard directly.
- Cross-shard interaction MUST occur ONLY via scheduled messages delivered at ACT `arrival_tick`.
- Message delivery order MUST be deterministic and stable.

**MUST NOT**
- Use distributed shared state.
- Use cross-shard locks or synchronous RPC.
- Use speculative simulation for authoritative state.

**Rationale**
Single-writer authority ensures determinism, replayability, and auditability.

## Singleplayer and Local MP mapping

### Singleplayer
- All shards MAY run in one process.
- Shards are still treated as separate authority domains logically.
- Cross-shard messages are still scheduled and ordered; no direct state access.

### Local MP
- Same as singleplayer, with multiple controllers.
- Controller inputs are routed to the authoritative shard only.

**Rationale**
Keeping the model identical prevents divergence between SP and MMO logic.

## Server-auth MMO mapping

**MUST**
- The server owns authoritative shards.
- Clients MUST NOT own shards or mutate authoritative state.
- Shard placement (single machine vs cluster) is a deployment concern only.

**Rationale**
Authority remains centralized and deterministic regardless of deployment topology.

## Rebalancing and migration (mandatory)

**MUST**
- Shard migration occurs only at safe ACT boundaries.
- Migration MUST be explicit via handoff events.
- Migration MUST freeze the shard, transfer state, then resume at the same ACT.

**MUST NOT**
- Migrate mid-tick.
- Perform partial or lazy transfers of authoritative state.

**Rationale**
Handoff boundaries preserve determinism and replay equivalence.

## Integration with other systems (mandatory)
- Event-driven stepping: `docs/specs/SPEC_EVENT_DRIVEN_STEPPING.md`
- Interest sets: `docs/specs/SPEC_INTEREST_SETS.md`
- Fidelity projection: `docs/specs/SPEC_FIDELITY_PROJECTION.md`
- Provenance: `docs/specs/SPEC_PROVENANCE.md`
- Communication model: `docs/specs/SPEC_COMMUNICATION.md`
- Command intent: `docs/specs/SPEC_COMMAND_MODEL.md`
- Time warp: `docs/specs/SPEC_TIME_WARP.md`

## Prohibitions (absolute)
- Best-effort shard synchronization.
- Eventual consistency for authoritative state.
- Hidden cross-shard reads.
- Per-shard clocks or drift.

## ASCII diagram

  [Shard A] --(scheduled messages)--> [Shard B]
     |                                      |
     v                                      v
  Authority Domain A                    Authority Domain B

## Test and validation requirements (spec-only)
Implementations MUST provide:
- shard ownership invariant tests
- cross-shard message ordering determinism tests
- migration boundary tests (freeze/transfer/resume)
- SP vs MMO equivalence tests across shard boundaries