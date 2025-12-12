Transport subsystem (splines, stub)
-----------------------------------
- Geometry uses `d_spline_knot` (position + in/out handles) and `d_spline_instance` (id, profile_id, start/end chunk ids, knot array, state TLV).
- Model vtable `dtrans_model_vtable` provides `tick_spline` and registers with family `D_MODEL_FAMILY_TRANS`; dummy model id 1 is installed.
- Splines are created with `d_trans_create_spline`, destroyed with `d_trans_destroy_spline`; per-world registry is a fixed table.
- Chunk serialization under `TAG_SUBSYS_DTRANS` captures splines touching that chunk: count, ids, profile ids, chunk ids, knot_count + knots, and state blob. Instance-level data is empty.
- Tick dispatch walks spline instances for a world and calls the registered model.
- Pack/mod TLVs carry spline profiles; launcher/setup never touch spline guts and rely on `d_tlv_schema_validate` for compatibility during instance selection.
