Building subsystem (stub)
-------------------------
- Instances are `d_building_instance` (id, proto id, position/orientation, chunk_id, flags, TLV state).
- Instances are created/destroyed via `d_build_create` / `d_build_destroy`; creation currently pins to chunk (0,0) if available.
- Per-world registry is a simple fixed table; tick is a no-op placeholder.
- Chunk save/load under `TAG_SUBSYS_DBULD` writes count + instance records (ids, protos, transforms, flags, state blob). Instance-level data is empty.
- No model family is registered yet; protos/load hooks are stubs.
- Dominium products lean on these TLV payloads for compatibility: launcher/setup never patch building data directly, they only route validated TLVs from selected packs/mods into the engine.
