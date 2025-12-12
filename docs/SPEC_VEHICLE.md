Vehicle subsystem (stub)
------------------------
- `d_vehicle_instance` captures id, vehicle proto id, position/velocity, rotation, chunk_id, flags, entity_id, and TLV state.
- Model vtable `dveh_model_vtable` (`tick_vehicle`) registers under family `D_MODEL_FAMILY_VEH`; a dummy model id 1 is provided.
- Instances are created/destroyed with `d_vehicle_create` / `d_vehicle_destroy`; registry is a fixed table keyed by world.
- Chunk save/load under `TAG_SUBSYS_DVEH` writes count + instance records (ids, protos, transforms, velocity, flags, entity, state blob). Instance-level data is empty.
- Tick walks vehicles for a world and dispatches to the registered model tick.
- Vehicle protos ship inside pack/mod TLVs chosen by the launcher; compatibility checks ensure vehicle schema versions track suite/core revisions so older products degrade safely to read-only.
