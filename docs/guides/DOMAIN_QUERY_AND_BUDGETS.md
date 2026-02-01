Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Domain Query and Budgets (DOMAIN1)





Status: draft.


Scope: runtime query semantics, caching, and budgeted degradation for domain volumes.





## Purpose


Domain queries provide a deterministic, conservative way to answer:


- "Is this point inside a domain?"


- "How far is this point from the domain boundary?"


- "Where is the closest known point?"


- "Does a ray intersect the domain?"





All runtime spatial checks must go through this API.





## Invariants


- Domain queries are deterministic and conservative.


- Budgets degrade resolution explicitly; no silent fallback.


- Domain queries are the only spatial authority.





## Public API


Headers:


- `engine/include/domino/world/domain_volume.h`


- `engine/include/domino/world/domain_query.h`


- `engine/include/domino/world/domain_cache.h`





Core queries:


- `dom_domain_contains(...)`


- `dom_domain_distance(...)`


- `dom_domain_closest_point(...)`


- `dom_domain_ray_intersect(...)`





Each query returns metadata:


- `resolution` (FULL/MEDIUM/COARSE/ANALYTIC/REFUSED)


- `confidence` (EXACT/LOWER_BOUND/UNKNOWN)


- `status` (OK/REFUSED)


- `refusal_reason` when refused





## Deterministic Semantics


- All inputs and outputs are fixed-point (`q16_16`).


- No wall-clock or benchmarking inputs are used.


- If a query is uncertain, results are conservative:


  - `contains` returns false when confidence is not exact.


  - `distance` returns a lower bound.


  - `closest_point` returns the nearest known sample point.


  - `ray_intersect` reports hits only on exact confirmation.





## Budget Model


Queries consume budget units from `dom_domain_budget`:


- `dom_domain_budget_init(&budget, max_units)`


- `dom_domain_budget_consume(&budget, cost_units)`





If a query cannot afford a higher resolution, it degrades deterministically:


1) FULL (exact eval)


2) MEDIUM (tile sample lower bound)


3) COARSE (tile sample lower bound)


4) ANALYTIC (primitive fallback if available)


5) REFUSED (explicit refusal)





Degradation is policy-driven via `dom_domain_policy`:


- `max_resolution`


- per-level costs


- tile build costs


- tile size and sample dimensions





## Caching


`dom_domain_cache` stores SDF tiles deterministically:


- Key: `domain_id + tile_id + resolution + authoring_version`


- Eviction: LRU with stable insert-order tie-break


- Invalidation:


  - authoring version changes


  - policy changes


  - existence/archival state changes





Usage:


1) `dom_domain_cache_init`


2) `dom_domain_cache_reserve` (fixed capacity)


3) bind cache to volume via `dom_domain_volume_set_cache`





If no cache is bound, the volume uses a small local tile reuse slot.





## Dependencies


Runtime systems must treat domain queries as the only spatial authority:


- INTEREST: bounds checks for interest sampling


- TRAVEL: path feasibility and reachability tests


- REFINEMENT: visitability checks


- LAW: jurisdiction lookup by point


- SHARDING: partition hints by domain





## Notes


- Domain queries never fabricate “inside” results.


- Correctness does not depend on resolution level.


- All downgrades are explicit and auditable via query metadata.





## Forbidden assumptions


- Direct spatial checks outside the domain API are acceptable.


- Higher resolution is always available regardless of budget.





## See also


- `docs/architecture/DOMAIN_VOLUMES.md`


- `schema/domain/README.md`
