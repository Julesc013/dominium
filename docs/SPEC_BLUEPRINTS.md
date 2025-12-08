# Blueprints

- Concept: planned structures/edits that generate jobs. `Blueprint { id, name, target_agg, elem_count, elem_capacity, elems[] }` holds `BlueprintElement`s allocated at creation.
- Elements/ops: `BlueprintElement { id, kind (PLACE_ELEMENT/REMOVE_ELEMENT/MODIFY_TERRAIN/PLACE_MACHINE), tile, material, machine_type, required_item/count, deps[] }`. IDs are per-blueprint sequential.
- API: `dblueprint_create(name, capacity)` allocates storage; `dblueprint_add_element` fills next slot; `dblueprint_generate_jobs` creates Jobs (build/deconstruct/custom) with target tiles and requirements, then applies dependencies by mapping element deps to job deps.
- Deterministic storage (bounded arrays per blueprint; no per-tick allocation). Game layer will later consume job completions to mutate world/aggregates.
