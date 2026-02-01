Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Global ID Model (MMO0)





Status: binding.


Scope: deterministic, collision-free identifier rules across shards.





## Purpose





Define a global identifier contract that is:





- deterministic


- collision-free without coordination


- reproducible on replay


- stable across ownership transfers





## ID rules (canonical)





All entities, domains, and events MUST have a globally unique identifier that:





- is derived deterministically


- encodes namespace, shard-of-origin, and a local identifier


- does not require cross-shard coordination to remain unique





## Canonical ID shape





Global IDs are structured values. Implementations may choose the physical


encoding (string, integer tuple, packed bits), but the logical fields are


binding:





- namespace


  - A stable, namespaced classification for the ID family.





- shard_of_origin


  - The shard that first minted the ID.


  - This field never changes, even if domain ownership transfers.





- local_id


  - A shard-local deterministic identifier.


  - Local IDs must be derived from deterministic seeds and sequences.





Example logical form:





`<namespace>:<shard_of_origin>:<local_id>`





## Deterministic derivation contract





ID generation MUST be:





- seeded from deterministic inputs (for example: world seed, shard id,


  namespace, and a local sequence)


- invariant under thread count and physical scheduling


- reproducible during save/replay for the same input streams





## Ownership transfer rules





Ownership transfer MUST NOT mint new IDs for existing entities or domains.





- IDs remain stable across shard handoff.


- Shard handoff is recorded as an event, not an identity rewrite.





## Event identifiers





Events MUST also be globally identifiable.





Event IDs MUST encode:





- event namespace


- shard_of_origin


- a shard-local sequence or deterministic event key





Global ordering is handled by deterministic ordering keys and logs, not by


assuming a single global counter.





## Related invariants





- MMO0-ID-014


- MMO0-LOG-015


- MMO0-COMPAT-018





## See also





- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`


- `docs/architecture/CROSS_SHARD_LOG.md`


- `docs/architecture/DISTRIBUTED_TIME_MODEL.md`
