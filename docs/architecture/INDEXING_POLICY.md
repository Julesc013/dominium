Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Indexing Policy (INDEX0)





Status: binding.


Scope: indexes and caches for performance.





## Rules


- Indexes are optional caches.


- Indexes are safe to delete.


- Indexes never define authoritative state.


- Rebuilds must be deterministic.





## Location


- `data/index/`





## See also


- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
