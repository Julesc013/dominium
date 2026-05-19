Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/embodiment/BODY_PRIMITIVES_AND_COLLISION.md` v1.0.0 and deterministic Process-only mutation invariants.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Body Collision Baseline

## Supported Shapes
- `capsule`
- `aabb`
- `convex_hull` (schema + registry declared, runtime narrowphase stubbed)

## Deterministic Ordering Rules
- Bodies are normalized and sorted by `assembly_id`.
- Broadphase candidate pairs are sorted by `(body_id_a, body_id_b)`.
- Contact/resolution rows preserve this order.

## Resolution Rules
- Capsule-capsule, capsule-aabb, and aabb-aabb overlap checks are deterministic.
- MTV correction:
  - both dynamic: split correction equally
  - one static: move dynamic only
  - ghost: ignored by default in solver path
- Single-pass per `process.body_move_attempt`.

## Contract Enforcement
- `dom.contract.no_penetration`
- `dom.contract.deterministic_contact_resolution`
- Strict mode unresolved overlap refusal:
  - `refusal.contract.no_penetration_violation`

## Multiplayer Limitation (v1)
- Cross-shard body-body collision is refused in SRZ hybrid when bodies resolve to different shard owners:
  - `refusal.control.cross_shard_collision_forbidden`

## Extension Points
- Continuous collision detection (CCD)
- Convex hull narrowphase
- Iterative manifold solver / stacking stability
- Joint and constraint primitives
