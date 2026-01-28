# Engine API Spine

Status: draft (implementation gaps noted).
Scope: public engine C ABI and header hygiene.
Authority: canonical for required contract; blockers listed below.

## Required contract
- Public headers MUST be C89 and C++98 parseable.
- Public ABI MUST be flat, versioned, and C-only.
- Public headers MUST NOT expose STL, templates, inline logic, or platform types.
- Public handles MUST be opaque; layout is private.
- Error handling MUST use explicit error codes; no hidden globals.
- Ownership, lifetime, and alignment MUST be documented per API.

## Current public surface (as-is)
- Root: `engine/include/domino/` and `engine/include/render/`.
- UI/platform/render headers are exposed in the public surface (e.g., `ui*.h`,
  `gfx.h`, `platform.h`, `render/`), which violates boundary hygiene.
- Prior baseline checks indicate non-C89/C++98 constructs in public headers.

## Blockers to resolve in Phase 2
- Split public vs private headers; move UI/render/platform to private surfaces.
- Replace exposed structs with opaque handles where feasible without behavior change.
- Remove inline logic and C99 constructs from public headers.
- Define canonical error codes and ownership rules in public headers.

## References
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/EXECUTION_MODEL.md`
