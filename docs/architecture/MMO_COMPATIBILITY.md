Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# MMO Compatibility (MMO0)





Status: binding.


Scope: unified singleplayer and multiplayer semantics plus legacy SKU


behavior under distributed saves.





## Core compatibility rules





- Singleplayer is a single-shard universe.


- Multiplayer is the same deterministic engine distributed across shards.


- Sharding MUST NOT create alternate gameplay semantics.





## Single-shard equivalence





Singleplayer is the reference implementation of the MMO contract:





- shard id `0` MAY be reserved for single-shard operation


- all shard rules still apply, but the partition is trivial


- outcomes must match distributed execution for equivalent partitions





## Unified code paths





Multiplayer MUST use the same authoritative engine code paths as


singleplayer:





- same deterministic reductions


- same budgets and refusal semantics


- same collapse/expand and macro-time rules





No forked "MMO logic" layer is allowed to change authoritative outcomes.





## Legacy SKU behavior





Legacy or capability-limited SKUs:





- MAY load distributed saves in frozen or inspect-only mode


- MAY replay distributed logs deterministically


- MUST refuse live participation explicitly when unsupported





Explicit refusal is preferred over partial, nondeterministic participation.





## Save and replay expectations





Distributed saves and replays must remain valid canon artifacts:





- they are replayable under the same capability baselines


- they are auditable without hidden coordination assumptions


- they do not require real-time wall-clock synchronization





## Related invariants





- MMO0-COMPAT-018


- MMO0-UNIVERSE-012


- SCALE0-REPLAY-008





## See also





- `docs/architecture/DISTRIBUTED_SIM_MODEL.md`


- `docs/architecture/JOIN_RESYNC_CONTRACT.md`


- `docs/architecture/CAPABILITY_BASELINES.md`
