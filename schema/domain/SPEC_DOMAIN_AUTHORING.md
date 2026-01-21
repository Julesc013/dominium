# SPEC_DOMAIN_AUTHORING (DOMAIN0)

Schema ID: DOMAIN_AUTHORING
Schema Version: 1.0.0
Status: binding.
Scope: authoring formats and deterministic baking to runtime SDF.

## Purpose
Define flexible authoring formats that are compiled into the canonical SDF
runtime representation without ambiguity or best-effort fixes.

## Allowed Authoring Formats
- Primitive SDFs: sphere, box, cylinder, torus, capsule.
- CSG trees: union, intersection, difference.
- Curved surfaces: spline/NURBS (authoring only).
- Mesh volumes: closed, validated meshes.

## Baking Rules
- Authoring formats MUST be converted to SDF deterministically.
- Baking parameters are explicit and versioned.
- Validation errors are fatal (no best-effort mesh repair).
- No runtime dependency on authoring meshes or splines.

## Determinism Requirements
- Authoring inputs must be normalized deterministically.
- Baking output is stable given identical inputs and parameters.

## Versioning
- Baking parameter sets must be versioned.
- Changes require schema version bump and migration notes.

## References
- `schema/domain/SPEC_DOMAIN_RUNTIME_SDF.md`
