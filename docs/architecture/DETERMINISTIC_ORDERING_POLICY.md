# Deterministic Ordering Policy (ORDER0)

Status: binding.
Scope: a single, global ordering policy used across engine, game, schemas, and tools.

This policy is subordinate to:
- `docs/architecture/EXECUTION_REORDERING_POLICY.md`
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`
- `docs/architecture/CROSS_SHARD_LOG.md`

## Core rule
When an order matters, it MUST be produced by sorting a deterministic key
derived only from stable data. Ordering MUST be:
- deterministic
- platform-independent
- independent of thread scheduling and hash map iteration order

## Canonical comparison rules
- Integers: compare as unsigned integers in natural ascending order.
- Identifiers: compare lowercase ASCII bytes (case-insensitive, locale-free).
- Tuples: compare lexicographically from left to right.
- Missing fields: treat as the lowest value for that field.
- Floating point: MUST NOT be part of authoritative ordering keys.

## The canonical ordering key pattern
Authoritative systems should construct ordering keys in this shape:

`(time_key, scope_key, kind_key, id_key, tie_break_key)`

Where each element is itself a deterministic integer or identifier. The exact
fields differ by domain but MUST follow the domain-specific rules below.

## Domain-specific ordering contracts

### Entities
Order authoritative entities by:
`(shard_id, topology_node_id)`

If `shard_id` is not present, use:
`(topology_node_id)`

### Components
Order component work and serialization by:
`(component_schema_id, shard_id, topology_node_id)`

If a component is not shard-scoped, omit `shard_id` but keep the remaining
fields in the same order.

### Partitions and shards
Order partitions and shards by:
`(partition_id, shard_id)`

If only shards exist in a context, order by:
`(shard_id)`

### Domains and topology nodes
Order domains and topology nodes by:
`(domain_id, topology_node_id)`

### Events (tick and sequence)
Order authoritative events by:
`(act_tick, event_seq, event_id)`

Rules:
- `act_tick` is the primary time key.
- `event_seq` MUST be a deterministic per-tick sequence.
- `event_id` is the final tie-breaker.

### Cross-shard messages
Order inbound cross-shard messages using the canonical tuple from MMO0:

`(delivery_tick, causal_key, origin_shard_id, message_id, sequence)`

### Packs and providers (tie-break rules)
When multiple providers satisfy the same capability, the canonical order is:
`(pack_version_major_desc, pack_version_minor_desc, pack_version_patch_desc, pack_id, provider_id, manifest_relpath)`

Rules:
- Version precedence is descending by semver components.
- `pack_id` and `provider_id` are stable identifiers.
- `manifest_relpath` is the final tie-breaker and MUST be relative to the
  selected data root, never an absolute path.

### Macro events
Order macro events by:
`(macro_tick, macro_phase, macro_event_id, domain_id)`

Rules:
- `macro_tick` is an authoritative time key.
- `macro_phase` is a small integer phase barrier within a macro step.
- `macro_event_id` is stable and required.

## Execution and commit ordering
This document does not replace execution ordering. Execution backends MUST
still honor the canonical commit ordering key:

`(phase_id, task_id, sub_index)`

## Forbidden ordering sources
- Hash map iteration order.
- Thread completion order.
- Wall-clock time.
- Floating point values.
- Absolute file paths.

## See also
- `docs/architecture/GLOBAL_ID_MODEL.md`
- `docs/architecture/MACRO_TIME_MODEL.md`
- `docs/architecture/PACK_FORMAT.md`
- `docs/architecture/ID_AND_NAMESPACE_RULES.md`
