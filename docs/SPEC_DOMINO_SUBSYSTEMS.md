# Domino Subsystems

Domino subsystem descriptors let the engine enumerate and orchestrate major domains (world, res, env, build, transport, etc.) without wiring bespoke code for each one.

## d_subsystem_desc
- `subsystem_id` (`u16`): stable id; engine-reserved range starts at 1, mods use 1000+ later.
- `name`: short label (`"world"`, `"env"`, …).
- `version` (`u32`): subsystem ABI/schema guard.
- `register_models()`: optional global init hook to populate model registries.
- `load_protos(blob)`: optional content/proto ingest hook (TLV-packaged).
- `init_instance(world)`: optional per-world initialization after creation/load.
- `tick(world, ticks)`: optional fixed-timestep hook after core ECS tick.
- `save_chunk/load_chunk(world, chunk, blob)`: optional chunk-level serializers.
- `save_instance/load_instance(world, blob)`: optional world/global serializers.

## Registry usage
- Call `d_subsystem_register(&desc)` during startup; duplicate ids are rejected.
- Lookups: `d_subsystem_count()`, `d_subsystem_get_by_index()`, `d_subsystem_get_by_id()`.
- Implementation uses a fixed-size table (static, deterministic; no heap churn).

## Save/load orchestration
- The serializer iterates registered subsystems and wraps each payload in a TLV tagged with `TAG_SUBSYS_*`.
- Subsystem callbacks are optional; absent hooks are skipped cleanly.
- Chunk and instance/global data share the same framing so new subsystems can plug in without changing the orchestrator.

## Rationale
- Central registry keeps lifecycle hooks discoverable and deterministic.
- New domains (e.g. chemistry, biology, EM fields) register once and ride the same init/tick/save pipeline.
- Mod/third-party subsystems can claim ids in the reserved range without patching core serialization.
