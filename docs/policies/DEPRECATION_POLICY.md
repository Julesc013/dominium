# DEPRECATION_POLICY (FINAL0)

Status: draft  
Version: 1

## Purpose
Define deterministic deprecation rules for APIs, schemas, and render backends.

## Deprecation stages
1) **Announce**: document the deprecation with rationale and replacement path.
2) **Warn**: emit explicit warnings in tooling and documentation.
3) **Support window**: minimum two minor releases before removal.
4) **Retire**: removal only after lifecycle doc update and migration notes.

## Render backends
- Backends follow `docs/RENDER_BACKEND_LIFECYCLE.md`.
- Removal requires explicit lifecycle update and compatibility notes.

## Schemas
- Deprecated schemas must declare migration or refusal behavior.
- Major version removals are forbidden without migration coverage.

## Enforcement
- CI gates require policy docs to be updated for deprecations.
- Deprecated paths must be labeled explicitly in documentation.

## Prohibitions
- Silent removal of deprecated systems.
- Skipping support windows.
