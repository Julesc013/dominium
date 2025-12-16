# DOMINIUM & DOMINO

**Domino** is the deterministic, fixed-point simulation engine.  
**Dominium** is the product layer (game, launcher, setup, tools) that hosts UI,
platform integration, and content workflows on top of Domino.

## Non-negotiable invariants
- Deterministic simulation uses integer ticks, fixed-point math, canonical
  ordering, replay, and world hashing (`docs/SPEC_DETERMINISM.md`).
- Authoritative placement/editing uses anchors + quantized poses
  (`docs/SPEC_POSE_AND_ANCHORS.md`).
- Baked world-space geometry is never authoritative; compiled artifacts are
  derived caches and rebuildable (`docs/SPEC_TRANS_STRUCT_DECOR.md`).
- In the refactor SIM pipeline, authoritative mutation occurs via deltas at
  commit (`docs/SPEC_SIM_SCHEDULER.md`, `docs/SPEC_ACTIONS.md`).

## Repository map
`docs/DIRECTORY_CONTEXT.md` is the authoritative directory/layout contract.
`docs/README.md` is the documentation index.

Key roots:
- `source/domino/` – engine implementation
- `source/dominium/` – products (common, game, launcher, setup, tools)
- `include/` – public headers (`include/domino/**`, `include/dominium/**`)
- `docs/` – specs and policy docs
- `data/` – in-tree content source; `repo/` – runtime repo layout under `DOMINIUM_HOME`

## Specs (entry points)
Determinism + SIM:
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_AGENT.md`
- `docs/SPEC_VM.md`

Placement and structure:
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/SPEC_TRANS.md`
- `docs/SPEC_STRUCT.md`
- `docs/SPEC_BUILD.md`

Policy/build:
- `docs/DETERMINISM_REGRESSION_RULES.md`
- `docs/ARCHITECTURE.md`
- `docs/DEPENDENCIES.md`
- `docs/LANGUAGE_POLICY.md`
- `docs/CONTRACTS.md`
- `docs/STYLE.md`
- `docs/BUILDING.md`

## Building and tests
- Build instructions: `docs/BUILDING.md`
- Run tests after building: `ctest --test-dir build`

## Contributing
See `CONTRIBUTING.md`.

## License
See `LICENSE`.
