# Generated Code Policy (REPOX)

Status: binding.
Scope: generated outputs, overrides, and review expectations.

## What may be generated
- IDE projections under `/ide/**`.
- Codegen outputs under existing `gen/` or `generated/` patterns.
- Deterministic lookup tables derived from data (Category D).

## What must never be generated
- Authoritative logic that replaces engine/game sources.
- Silent rewrites of canon documents or schemas.
- Output that hides provenance or determinism assumptions.

## Overrides and hand-written code
Use a clear split:
- `gen/` for generated code (overwritten).
- `user/` for hand-written code (never overwritten).
- `doc/` for generator specs and contracts.

## Editing rules
- Generated outputs are NEVER edited directly.
- Edits go to the source template or generator inputs.
- Generated outputs must include “GENERATED DO NOT EDIT” headers when applicable.

## Review expectations
- Generated changes must be reproducible by scripts.
- Reviews focus on generator input, not output.

## Cross-references
- `docs/arch/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/arch/PROJECTION_LIFECYCLE.md`
