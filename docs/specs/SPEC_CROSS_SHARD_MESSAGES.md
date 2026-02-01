Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives for message queues and ordering.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Message payload definitions and authority policy.
- Implementation lives under `game/` and `server/`.

TOOLS:
- Diagnostics and inspection only.

SCHEMA:
- Message schema definitions and validation formats.

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
# SPEC_CROSS_SHARD_MESSAGES — Deterministic Cross-Shard Messaging Canon

Status: draft
Version: 1

## Purpose
Define the deterministic cross-shard message model. Messages are the ONLY legal
cross-shard interaction mechanism and MUST preserve determinism and authority
boundaries.

This spec is documentation-only. It introduces no runtime logic.

## Definitions (mandatory)

### CROSS-SHARD MESSAGE
A deterministic message representing:
- intent
- event
- information
Delivered via scheduled `arrival_tick` under ACT.

### MESSAGE ORDER KEY
A stable, deterministic ordering key used to resolve delivery order when
multiple messages share the same `arrival_tick`.

## Message envelope (mandatory)
Every cross-shard message MUST include:
- `sender_shard_id`
- `receiver_shard_id`
- `payload_type`
- `arrival_tick` (ACT)
- `order_key` (stable deterministic key)
- `payload` (schema-validated)

**Rationale**
Explicit metadata makes ordering, audit, and replay deterministic.

## Deterministic ordering (mandatory)

Messages MUST be delivered in strict order:
1) `arrival_tick` (ascending)
2) `order_key` (ascending, stable)
3) `message_id` (ascending, deterministic tiebreak)

**MUST NOT**
- Deliver messages based on arrival wall-clock time.
- Use nondeterministic queues or hash iteration order.

## Allowed interactions (mandatory)
- logistics arrival
- command propagation
- economic settlement
- information dissemination

## Forbidden interactions (absolute)
- direct pointer/reference sharing across shards
- synchronous RPC between shards
- shared memory or shared authoritative containers

## Authority boundaries (mandatory)
Messages MUST NOT cause:
- the sender to mutate receiver-owned authoritative state
- the receiver to mutate sender-owned authoritative state

All mutations MUST occur in the receiver shard only.

## Message scheduling rules

**MUST**
- Assign a deterministic `arrival_tick` based on ACT and travel/processing models.
- Use deterministic ordering keys derived from stable IDs (e.g., contract_id, convoy_id).
- Persist message provenance and audit trail.

**MUST NOT**
- Schedule "best-effort" delivery.
- Drop or reorder messages without an explicit, deterministic rule.

## Singleplayer and local MP mapping
- Messages are queued and delivered even when shards share a process.
- No direct cross-shard access is allowed in SP or local MP.

## Server-auth MMO mapping
- Server owns all authoritative message queues.
- Clients never enqueue authoritative cross-shard messages directly.
- Client requests are converted into server-owned messages with deterministic IDs.

## Migration and rebalancing
During shard migration:
- Pending cross-shard messages MUST be transferred as part of shard state.
- Message ordering MUST remain stable across migration boundaries.
- No mid-tick message handoff is permitted.

## Integration points (mandatory)
- Event-driven stepping: `docs/specs/SPEC_EVENT_DRIVEN_STEPPING.md`
- Provenance: `docs/specs/SPEC_PROVENANCE.md`
- Fidelity projection: `docs/specs/SPEC_FIDELITY_PROJECTION.md`
- Command intent: `docs/specs/SPEC_COMMAND_MODEL.md`
- Communication model: `docs/specs/SPEC_COMMUNICATION.md`
- Time warp: `docs/specs/SPEC_TIME_WARP.md`

## Prohibitions (absolute)
- Best-effort shard synchronization.
- Eventual consistency for authoritative state.
- Hidden cross-shard reads.
- Per-shard clocks or drift.

## ASCII diagram

  [Shard A] --(arrival_tick, order_key)--> [Shard B]
           deterministic queue + ordering

## Test and validation requirements (spec-only)
Implementations MUST provide:
- deterministic ordering tests for same-tick messages
- replay equivalence tests for message delivery
- migration transfer tests for in-flight messages