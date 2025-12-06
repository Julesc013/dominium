# Dominium — Milestones (Engine v0)

## v0 — Deterministic core bootstrap
- Build `dom_engine` as a C89 static library with fixed-point-only math and explicit RNG.
- Surface/world layout implemented (2²⁴ m torus, 4096 m vertical), chunk hashing, deterministic `SimPos` ↔ chunk mapping.
- Simple heightfield geometry sampling and scalar field stubs.
- ECS present with deterministic ordering; per-surface tick order fixed (input → ecs → networks → fluids → climate → thermal → edits).
- Save/load for `universe.meta`, `surface.meta`, region/chunk TLV containers; caches are regenerable.
- Headless runtime (`dom_cli`) can create/load a universe, tick N times, and save.

## Next steps (post-v0)
- Flesh out field sampling (atmo/hydro/thermal) and procedural registries.
- Add edit operations and region chunk persistence beyond stubs.
- Expand runtime frontends (renderer/UI) while preserving fixed-point boundaries.
- Extend tools for inspection/validation/migration using shared IO modules.
