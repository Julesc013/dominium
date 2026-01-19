# SIM (Deterministic Simulation Layer)

This directory is the deterministic simulation layer of the Domino engine.
All code here is expected to participate in replay, hashing, and lockstep.

## Boundaries (non-negotiable)
- C89 only in determinism paths; fixed-point only (Q formats); no floats.
- No OS/platform/UI/render/audio/input APIs or wall-clock time sources.
- No tolerance/epsilon solvers; no unordered iteration; no pointer-order logic.
- No hardcoded gameplay semantics; this layer provides generic mechanisms.
- Global grids and world-space baked geometry must not be authoritative state.

## Submodules (scaffold)
- `execution/` authoritative Work IR + scheduler lives in engine/modules/execution.
- `pkt/` TLV-versioned packet families (intent/delta/event/etc.).
- `bus/` deterministic routing of fields/events/messages (no cross-calls).
- `lod/` representation ladder selection and budgeted promotion/demotion.
- `act/` intent → action → delta pipeline interfaces.
- `sense/` deterministic sensing/sampling scaffolding.
- `know/` belief/knowledge state scaffolding (derived cache only).
- `vis/` visibility/occlusion/comms scaffolding (derived cache only).
- `prop/` propagators and bounded incremental updates.

## Specs
See `docs/SPEC_DETERMINISM.md`, `docs/SPEC_SIM_SCHEDULER.md`, `docs/SPEC_PACKETS.md`,
`docs/SPEC_FIELDS_EVENTS.md`, `docs/SPEC_ACTIONS.md`, `docs/SPEC_LOD.md`,
`docs/SPEC_DOMAINS_FRAMES_PROP.md`, `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`.
