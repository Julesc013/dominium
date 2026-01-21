# SPEC_DOMAIN_RUNTIME_SDF (DOMAIN0)

Schema ID: DOMAIN_RUNTIME_SDF
Schema Version: 1.0.0
Status: binding.
Scope: canonical runtime representation of domain volumes.

## Purpose
Define the deterministic, backend-agnostic runtime representation for domain
volumes using Signed Distance Fields (SDF).

## Canonical Runtime Representation
DomainVolumeRuntime is an SDF:
- f(x,y,z) -> signed distance
- Inside if f <= 0
- Outside if f > 0

The runtime representation does not depend on meshes, splines, or authoring
formats. It is stable and deterministic.

## Determinism and Numeric Rules
- Evaluation must be deterministic across platforms.
- Use fixed-point or explicitly quantized representation (no nondeterministic
  floating-point dependence).
- All numeric encodings are explicit and versioned.

## Multi-Resolution Tiles
- Sparse tiles are allowed for large volumes.
- Coarse checks must be performed before fine checks.
- Resolution changes must not alter correctness (only precision).
- Deterministic cache invalidation is required.

## Required Queries
All queries must be deterministic, side-effect free, and budgetable:
- Contains(point)
- Distance(point)
- ClosestPoint(point)
- RayIntersect(ray)
- AABB(bounds)
- Sample(tile_id, resolution)

## Budget and Degradation
- Coarse checks first; fine checks only when necessary.
- Degrade under budget pressure by lowering resolution or deferring noncritical
  queries.
- Correctness must not depend on resolution.

## References
- `schema/domain/SPEC_DOMAIN_AUTHORING.md`
- `schema/domain/SPEC_DOMAIN_NESTING.md`
