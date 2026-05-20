Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Engine API Spine

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/archive/audit/CANON_MAP.md` and `docs/archive/audit/DOC_DRIFT_MATRIX.md`.






Status: draft (implementation gaps noted).


Scope: public engine C ABI and header hygiene.


Authority: canonical for required contract; blockers listed below.





## Required contract


- Public headers MUST be C17 C-compatible and C++17-consumable.


- Public ABI MUST be flat, versioned, and C-only.


- Public headers MUST NOT expose STL, templates, C++ ABI, exceptions, RTTI, or platform types.


- Public handles MUST be opaque; layout is private.


- Error handling MUST use explicit error codes; no hidden globals.


- Ownership, lifetime, and alignment MUST be documented per API.





## Current public surface (as-is)


- Root: `engine/include/domino/` and `engine/include/render/`.


- UI/platform/render headers are exposed in the public surface (e.g., `ui*.h`,


  `gfx.h`, `platform.h`, `render/`), which violates boundary hygiene.


- Prior baseline checks indicate public-header ABI and promotion-blocker debt.





## Blockers to resolve in Phase 2


- Split public vs private headers; move UI/render/platform to private surfaces.


- Replace exposed structs with opaque handles where feasible without behavior change.


- Remove C++ ABI leakage and platform leakage from public headers.


- Define canonical error codes and ownership rules in public headers.





## References


- `docs/architecture/INVARIANTS.md`


- `docs/architecture/EXECUTION_MODEL.md`
