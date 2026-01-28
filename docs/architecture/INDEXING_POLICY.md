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
- `docs/arch/CONTENT_AND_STORAGE_MODEL.md`
