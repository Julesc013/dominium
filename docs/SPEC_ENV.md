Environment subsystem (stub)
----------------------------
- Zones are represented by `denv_zone_state` (id, temperature, pressure, humidity, 4-element gas mix, pollution, light_level, extra TLV).
- Portals link zones via `denv_portal` (zone ids, area, permeability, extra).
- Models implement `denv_model_vtable` (`init_chunk`, `tick`) and register with `denv_register_model` (family `D_MODEL_FAMILY_ENV`). A no-op model id 1 is pre-registered.
- Each chunk keeps arrays of zones/portals; `denv_init_chunk` seeds a single outdoor zone.
- `denv_tick` iterates chunk entries and calls model ticks.
- Chunk serialization under `TAG_SUBSYS_DENV` encodes zone_count + portal_count, followed by zone structs (with extra blobs) and portal structs. Instance-level data is empty.
