Status: DERIVED
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Release-pinned engine numeric policy and compiler matrix documentation.

# Numeric Discipline Model

## Truth Numeric Rules

- Canonical state uses integers or fixed-point only.
- Floating-point values must not be persisted in:
  - assemblies
  - fields
  - process outputs
  - law evaluation results
  - proof/replay hashes
- Deterministic rounding must route through the governed helpers in `src/meta/numeric.py`.
- Reviewed approximation bridges are allowed only when they quantize back to canonical integer outputs and are explicitly inventoried by the numeric scans.

## Render Numeric Rules

- Floating-point math is allowed in render-only and UI-only presentation surfaces.
- Render numeric may influence pixels and interaction feel, but it must not feed canonical hashes or authoritative mutation.
- Render tolerances are versioned separately and remain provisional.

## Tolerance Model

- Engine-level tolerances live in `data/registries/tolerance_registry.json`.
- Each tolerance row declares:
  - `tol_id`
  - `domain_id`
  - `allowed_error_bound`
  - `rounding_mode`
- Truth tolerances are frozen contracts.
- Render tolerances are provisional and may evolve without affecting truth semantics.

## Cross-Compiler Stability

- Truth-side compiler flags must not relax float semantics.
- SOL-1 and SOL-2 trig/orbit logic must remain lookup-table or fixed-point based.
- Reviewed approximation bridges must be bounded and documented; they are not a license for general float use in truth paths.

## Deterministic Serialization

- Canonical numeric serialization must not depend on locale.
- Governed manifests and hashes must not use ad hoc float formatting or scientific notation.
- Numeric identity/report/manifests must use canonical serializers and deterministic key ordering.
