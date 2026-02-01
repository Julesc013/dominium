Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Identity Across Time (LIFE0+)





Status: binding.


Scope: identity continuity across refinement, collapse, archival, and forks.





## Invariants


- Identity persists across refinement and collapse.


- Archived identity is immutable unless forked.


- Instance details do not define identity.





## Identity vs instance


- Identity persists across time.


- Instance is a micro realization and can appear/disappear with refinement.





Identity survives refinement and collapse; instance details do not.





## What persists


Persists across refinement/collapse:


- life_id


- lineage_refs


- provenance_refs


- identity_state





Persists across archival:


- identity and lineage are immutable.


- history can only change via fork.





## What does not persist


- Embodiment state (location, health, inventory).


- Controller/session bindings.


- Ephemeral perception/epistemic cache.





## Forking rules


- Forking creates a new identity lineage root.


- Parent identity remains immutable and archived.


- Forked identity records must reference the parent lineage.





## Dependencies


- Existence and archival: `schema/existence/README.md`


- Identity and lineage: `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`


- Reality layer: `docs/architecture/REALITY_LAYER.md`





## Forbidden assumptions


- Identity can be overwritten by refinement details.


- Archived history can be edited without a fork.





## See also


- `docs/architecture/DEATH_AND_CONTINUITY.md`


- `docs/architecture/LIFE_AND_POPULATION.md`
