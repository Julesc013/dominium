Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Distributed Time Model (MMO0)





Status: binding.


Scope: logical time, causal ordering, and deterministic outcomes across shards.





## Time rules (canonical)





Simulation time is logical, not wall-clock.





Each shard:





- advances time for the domains it owns


- does so independently within policy bounds


- advances only through deterministic commit boundaries





Cross-shard events and messages MUST include:





- `origin_tick` (the originating logical tick)


- a causal ordering key


- a deterministic ordering key





## Ordering guarantee (critical)





Given:





- the same initial world


- the same intent stream


- the same shard partitioning


- the same capability baselines and policies





The final world MUST be identical regardless of physical execution order,


thread scheduling, or server placement.





## Deterministic ordering requirements





To satisfy the ordering guarantee:





- shard-local scheduling MUST be deterministic


- cross-shard message ordering MUST be deterministic


- ownership transfers MUST occur only at commit boundaries


- macro-time evolution MUST remain event-driven and deterministic





No system may rely on wall-clock time for authoritative ordering.





## Causality and bounded independence





Shards may advance independently, but causal links are explicit:





- causal links are expressed through cross-shard messages


- causal ordering keys are carried with messages


- delivery ticks and ordering keys determine deterministic application order





## Replay model





Replay MUST be possible from:





- snapshots or macro capsules


- deterministic event logs


- cross-shard message logs





Replay MUST not require synchronized wall-clock capture.





## Related invariants





- MMO0-TIME-016


- MMO0-LOG-015


- SCALE0-DETERMINISM-004





## See also





- `docs/architecture/MACRO_TIME_MODEL.md`


- `docs/architecture/CROSS_SHARD_LOG.md`


- `docs/architecture/DISTRIBUTED_SIM_MODEL.md`
