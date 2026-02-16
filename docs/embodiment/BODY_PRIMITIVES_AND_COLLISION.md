Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0, `docs/canon/glossary_v1.md` v1.0.0, and `schemas/body_primitive.schema.json` v1.0.0.

# Body Primitives And Collision

## Purpose
Define deterministic body primitives and the minimal collision/contact substrate for embodiment-ready simulation.

## Primitive Types
- `body.shape.capsule`
- `body.shape.aabb`
- `body.shape.convex_hull` (stub; shape token supported, narrowphase deferred)

## Canonical Body Fields
- `body.shape_id`
- `body.transform`
  - `position_mm`
  - `orientation_mdeg`
- `body.collision_layer`
- `body.mass` (optional numeric stub for future physics)
- `body.flags`
  - `dynamic`
  - `ghost`

## TruthModel Integration
- Bodies are represented as standalone assemblies (`assembly.body.*`) in `UniverseState.body_assemblies`.
- Agents may exist without bodies.
- Bodies may exist without controllers.
- Sessions remain valid with zero bodies.

## Deterministic Collision Contract
- `dom.contract.no_penetration`
- `dom.contract.deterministic_contact_resolution`

### No-Penetration Rule
- Overlaps are resolved deterministically during process execution.
- Resolution uses stable ordering and deterministic integer arithmetic.
- In strict contract mode, unresolved overlap yields `refusal.contract.no_penetration_violation`.

### Contact Manifold Ordering
- Candidate pair order is stable by `(body_id_a, body_id_b)`.
- Contact rows and resolution rows are also emitted in stable pair order.

## Broadphase
- Deterministic spatial hash grid (fixed cell size).
- Bodies sorted by `assembly_id` before cell insertion.
- Candidate pairs deduplicated and sorted by `(body_id_a, body_id_b)`.

## Narrowphase + Resolution (v1)
- Supported overlap checks:
  - capsule-capsule
  - capsule-aabb
  - aabb-aabb
- Resolution:
  - minimal translation vector (MTV)
  - both dynamic: split correction 50/50
  - one static: move dynamic body only
  - ghost bodies are ignored by default in contact solve path
- Single-pass per process execution (no iterative stack solver in v1).

## Process Surface
- `process.body_move_attempt`
  - Proposes a body transform delta.
  - Executes deterministic collision resolution before commit.
  - Records deterministic process log entries.

## Multiplayer Constraints
- Lockstep: all peers run same collision math from ordered tick intents.
- Server-authoritative: server resolves contacts; client receives PerceivedModel deltas.
- SRZ hybrid v1: cross-shard body-body collision resolution is refused unless explicitly enabled.
  - refusal code: `refusal.control.cross_shard_collision_forbidden`

## Known Limitations
- No continuous collision detection.
- No stacking/iterative solver.
- `convex_hull` is declared but narrowphase remains stubbed.
- No joints, constraints, or force integration yet.

## Cross-References
- `docs/embodiment/CONTROL_SUBSTRATE_DOCTRINE.md`
- `docs/scale/CONTRACTS_AND_CONSERVATION.md`
- `docs/contracts/refusal_contract.md`
- `schemas/body_primitive.schema.json`
- `schemas/universe_state.schema.json`
