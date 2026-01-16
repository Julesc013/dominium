--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Blueprints

- Concept: planned structures/edits that generate jobs. `Blueprint { id, name, target_agg, elem_count, elem_capacity, elems[] }` holds `BlueprintElement`s allocated at creation.
- Elements/ops: `BlueprintElement { id, kind (PLACE_ELEMENT/REMOVE_ELEMENT/MODIFY_TERRAIN/PLACE_MACHINE), tile, material, machine_type, required_item/count, deps[] }`. IDs are per-blueprint sequential.
- API: `dblueprint_create(name, capacity)` allocates storage; `dblueprint_add_element` fills next slot; `dblueprint_generate_jobs` creates Jobs (build/deconstruct/custom) with target tiles and requirements, then applies dependencies by mapping element deps to job deps.
- Deterministic storage (bounded arrays per blueprint; no per-tick allocation). Game layer will later consume job completions to mutate world/aggregates.
