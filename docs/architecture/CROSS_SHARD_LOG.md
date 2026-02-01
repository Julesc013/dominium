Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Cross-Shard Log (MMO0)





Status: binding.


Scope: deterministic cross-shard interaction via append-only message logs.





## Core rule





Cross-shard interaction MUST occur via append-only message logs with explicit,


deterministic ordering keys and idempotent semantics.





Messages are inputs to admission control. Messages MUST NOT mutate


authoritative state directly.





## Message model (canonical)





Each cross-shard message is an append-only record that includes, at minimum:





- a global `message_id`


- `origin_shard_id` and `dest_shard_id`


- the relevant `domain_id` or ownership scope


- `origin_tick` and `delivery_tick` (logical simulation ticks)


- a causal ordering key


- a deterministic ordering key


- a message kind namespace





Messages MAY carry:





- intent forwarding


- macro event propagation


- ownership transfer notices


- contract commitments and obligation notices





## Deterministic ordering contract





Each shard MUST process inbound messages in deterministic order using a stable


ordering key. The canonical ordering tuple is:





`(delivery_tick, causal_key, origin_shard_id, message_id, sequence)`





Implementations may add tie-breakers, but they must be deterministic and


derived from message data.





## Idempotent semantics





Message application MUST be idempotent:





- repeated delivery MUST not change outcomes


- duplicate messages MUST be safe


- missing messages MUST refuse or defer explicitly





Idempotence is enforced by deterministic message IDs and idempotency keys.





## Admission and budgets





Message consumption is subject to the same admission rules as local work:





- budgets gate message application


- refusals and deferrals are explicit and logged


- state is unchanged on refusal or deferral





## Ownership transfer notices





Ownership transfer MUST be mediated by the log:





- transfers are messages with explicit provenance


- transfers occur only at commit boundaries


- transfer decisions are replayable and auditable





## Replay and audit requirements





Cross-shard logs MUST be:





- append-only


- replayable without wall-clock assumptions


- sufficient to reproduce distributed outcomes deterministically





## Related invariants





- MMO0-OWNERSHIP-013


- MMO0-LOG-015


- MMO0-TIME-016





## See also





- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`


- `docs/architecture/DISTRIBUTED_TIME_MODEL.md`


- `schema/cross_shard_message.schema`
