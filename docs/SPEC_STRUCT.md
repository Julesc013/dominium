Structures/machines subsystem (stub)
------------------------------------
- `d_struct_instance` stores id, structure proto id, transform, chunk_id, flags, optional entity_id link, and TLV state.
- Instances are created/destroyed via `d_struct_create` / `d_struct_destroy`; registry is a fixed per-world table, chunk inference defaults to (0,0).
- Tick is currently a no-op; model registration is stubbed for future machine models.
- Chunk persistence uses `TAG_SUBSYS_DSTRUCT`: count + instance records (ids, protos, transforms, flags, entity, state blob). Instance-level data is empty.
- Dominium compatibility relies on these TLV tags staying stable; setup/import never mutate structure state outside the engine, keeping determinism intact.
