# SPEC_SHARD_MODEL (DIST0)

This specification defines the canonical shard model used for distributed
execution. Shards are deterministic ownership partitions; game systems remain
unaware of distribution.

## Definitions

Shard
- `shard_id`: stable identifier for the shard.
- `ownership_scope`: deterministic ownership boundary.
- `determinism_domain`: hash partition identifier used for stable placement.

Ownership scopes (minimum set)
- World region scopes (region_id ranges, tiles, or volumes).
- Entity ID ranges (stable ranges or hash buckets).
- System domains (explicit domains like ECONOMY, WAR, AGENTS).

## Invariants

- Every authoritative entity belongs to exactly one shard at any time.
- Ownership changes only via explicit migration events.
- Shard placement is a pure function of task metadata and ownership scope.
- Shard identity is stable across replays and restarts.

## Determinism Domain

The determinism domain defines a stable hash partition. It is a data-defined
parameter that must not depend on runtime timing or network order. Any placement
rule that uses hashing must use this domain as a stable input.

## Ownership Migration (Preview)

Ownership changes must be:
- explicit (migration events with stable IDs),
- scheduled (ACT time),
- auditable,
- reversible only via a new event (never implicit rollback).

Implementation details are deferred, but the schema requires migration events
to be modeled and logged deterministically.
