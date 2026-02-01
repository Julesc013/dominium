Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Space and Bounds (DOMAIN0)





Status: draft.


Scope: define what "space" means in terms of domain volumes and boundaries.





## Principles


- Space exists only inside explicit domains; outside is non-simulated.


- Domain membership is explicit and query-based, never inferred.


- Existence and archival states gate whether domains are active.


- Overlaps resolve deterministically with no ambiguity.





## Spatial Semantics


- A point may be inside multiple domains.


- Resolution order: explicit reference, smallest containing domain, higher


  precedence, then parent chain.


- Runtime boundaries are SDF-evaluated and deterministic.


- Inputs must be quantized or fixed-point to avoid float nondeterminism.





## Query Contract


- Required queries: Contains, Distance, ClosestPoint, RayIntersect, AABB, Sample.


- Queries are side-effect free and budgeted.


- Degradation lowers resolution only; correctness does not change.


- Caches are allowed with deterministic invalidation.





## Integration


- Travel edges reference domains only.


- Refinement requests are allowed or refused by domain policy.


- Law jurisdiction binds to domains, not implied geography.


- Sharding and interest sampling are constrained by domains.





## Prohibitions


- No implicit world bounds or rectangular assumptions.


- No mesh-only runtime queries.


- No probabilistic or heuristic membership tests.





## References


- `docs/architecture/DOMAIN_VOLUMES.md`


- `schema/domain/README.md`


- `docs/architecture/SPACE_TIME_EXISTENCE.md`
