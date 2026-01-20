# SPEC_CROSS_SHARD_MESSAGES (DIST0)

This specification defines cross-shard message contracts and ordering.

## CrossShardMessage

Fields (minimum):
- `source_shard`
- `target_shard`
- `message_id` (stable)
- `task_id` or `event_id` (stable)
- `arrival_tick` (ACT)
- `payload` (deterministic serialization)

## Rules

- No synchronous reads across shards.
- All cross-shard interaction is modeled as messages.
- `arrival_tick` is the earliest observation time.
- Ordering is deterministic by `(arrival_tick, message_id)`.

## Serialization

- Payload encoding must be deterministic and platform-independent.
- Byte order must be explicit.
- Field order must be stable and documented.

## Replay & Recovery

- Cross-shard message logs are authoritative for replay.
- Replay must reconstruct identical message ordering and arrival ticks.
- Message IDs must be stable across runs.
