Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Domain Sharding and Streaming (DOMAIN3)





Status: draft.


Scope: shard ownership, streaming boundaries, and domain-driven placement.





## Purpose


Define how authoritative shards own space by domain volumes and how streaming


is constrained to those volumes. Domains replace grids and region IDs as the


fundamental unit of distribution.





## Domain-Driven Ownership


- Each shard owns one or more domain volumes or sub-volumes.


- Ownership is exclusive for authoritative writes.


- Domains may be partitioned only when explicitly allowed.


- Partitioning is deterministic given domain_id, parameters, and seed.





## Deterministic Partitioning


Partitioning inputs:


- domain_id


- domain volume definition (SDF bounds)


- partition parameters (tile size, resolution, limits)


- global seed





Outputs:


- stable mapping of domain sub-volumes to shard_id


- audit-friendly assignment records





## Streaming Constraints


Streaming requests are allowed only when:


- the domain existence_state is spatially active


- the archival_state is LIVE (not FROZEN or ARCHIVED)


- the domain policy allows simulation/streaming





No streaming occurs outside any active domain.





## Non-Authoritative Hints


The engine may emit advisory hints:


- refine-soon (interest escalation)


- collapse-ok (low interest)





Hints are budgeted and never authoritative.





## Migration and Resharding Preview


Future reshards must be explicit effects with audit:


- no silent migration


- no state teleportation


- causal order preserved by shard handoff events





## References


- `docs/architecture/DOMAIN_VOLUMES.md`


- `engine/include/domino/world/domain_streaming_hints.h`


- `server/shard/domain_shard_mapper.h`
