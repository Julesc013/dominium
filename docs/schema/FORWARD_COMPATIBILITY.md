Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Forward Compatibility Rules

This document is canonical for schema evolution. It defines how readers and
writers MUST preserve data across versions.

## Skip-Unknown Is Mandatory
- Readers MUST preserve unknown fields, tags, and records exactly as read.
- Unknown fields MUST NOT be discarded, reordered, or altered.
- Writers MUST round-trip unknown data without interpretation.

## Open Enums
- Enums MUST be treated as open tag strings.
- Unknown enum values MUST be preserved and emitted unchanged.

## Version Progression
- `schema_version` is semantic (MAJOR.MINOR.PATCH).
- MAJOR bumps are breaking and require an explicit migration plan.
- MINOR bumps add optional fields only and MUST be skip-unknown safe.
- PATCH bumps are corrections only and MUST NOT change meaning.

## Structural Guarantees
- Required fields in v1 MUST remain required in all later versions.
- Fields MUST NOT be renamed or removed without a MAJOR bump.
- New fields MUST be optional and MUST NOT change the meaning of existing fields.

## Preservation Across Engines
- Newer engines MUST read older schema versions.
- Older engines MUST preserve newer fields even if unused.
- Partial reads MUST emit untouched unknown data.

## No Defaults or Coercion
- Readers MUST NOT invent defaults for missing optional fields.
- Writers MUST NOT coerce unknown fields into known ones.