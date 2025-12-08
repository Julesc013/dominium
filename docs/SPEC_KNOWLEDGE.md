# Knowledge / Fog of War

- Knowledge types: tile visibility, entity sightings, market info. Keys are `KnowledgeKey { type, subject_id }`.
- Records: `KnowledgeRecord { key, last_seen_tick, confidence_0_1 }` stored in `KnowledgeBase { id, records[], record_count, record_capacity }`.
- Registry: `dknowledge_create(capacity)` grabs a fixed slice of the global record pool; lookup via `dknowledge_get`; destroy clears handles (pool memory is static).
- Updates: `dknowledge_observe` finds or inserts a record (linear scan). On full capacity, replacement is deterministic: lowest confidence wins; ties broken by oldest `last_seen_tick`. Confidence clamps to 0..1 (Q16.16).
- Queries: `dknowledge_query` returns a record pointer; `dknowledge_mark_tile_visible` hashes tile coords into a subject id and inserts visibility with full confidence.
- All storage is bounded arrays; no dynamic allocation during ticks.
