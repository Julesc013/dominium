# SPEC_TRANS_STRUCT_DECOR — TRANS / STRUCT / DECOR Responsibilities

This spec defines the responsibilities and boundaries of TRANS, STRUCT, and
DECOR in the strict layer stack:

`BUILD / TRANS / STRUCT / DECOR / SIM / RES / ENV / JOB / AGENT`

## Scope
Applies to:
- separation of concerns between TRANS/STRUCT/DECOR
- authoring vs compiled artifacts
- deterministic compilation constraints
- explicit prohibitions (no solvers, no baked geometry truth)

## TRANS (Transform/Topology)
**Responsibilities**
- Own transform/topology representations used to connect structures and anchors.
- Provide deterministic, canonical representations suitable for SIM consumption.
- Provide deterministic compilation from authored inputs (see `compile/`).

**Non-responsibilities**
- No rendering integration.
- No platform APIs.
- No tolerance/epsilon solvers.

## STRUCT (Structures)
**Responsibilities**
- Own structure semantic models (authoring-time) and compiled structure artifacts.
- Support deterministic slot-based packing (e.g., corridor packing) as a discrete
  compile step (no tolerance fitting).
- Expose structure state to SIM only through stable IDs and deltas.

**Non-responsibilities**
- No baked world-space geometry as authoritative truth.
- No solver-based fitting.

## DECOR (Decoration)
**Responsibilities**
- Own decoration rulepacks and deterministic compilation to runtime artifacts.
- Provide derived decoration outputs only; decor is non-authoritative.

**Non-responsibilities**
- Decor MUST NOT become gameplay truth.
- No platform rendering dependencies.

## Authoring vs compiled artifacts
- Authoring artifacts are for tools only; they MUST NOT be required in
  determinism paths.
- Compiled artifacts are the only acceptable deterministic inputs to SIM.
- Compilation MUST be deterministic, TLV-versioned, and canonically ordered
  (`docs/SPEC_PACKETS.md`, `docs/SPEC_DETERMINISM.md`).

## Explicit prohibitions
TRANS/STRUCT/DECOR MUST forbid:
- tolerance/epsilon solvers
- world-space baked geometry as authoritative state
- global grids as logic dependencies (grids may be derived caches only)
- unordered iteration in determinism paths
- platform-dependent behavior

## Source of truth vs derived cache
**Source of truth:**
- compiled artifacts (TLV-versioned)
- anchors/poses referenced by stable IDs

**Derived cache:**
- render geometry
- visualization geometry
- any occupancy grids or spatial accelerators (regenerable)

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`

