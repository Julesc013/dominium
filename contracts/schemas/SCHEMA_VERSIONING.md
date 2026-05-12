# Schema Versioning Law (DATA0)

All schemas under `schema/**` MUST be versioned and self-describing.
Versioning is enforceable and merge-blocking.

## Required Metadata

Every schema MUST declare:

- `schema_id` (stable, globally unique identifier)
- `schema_version` (semantic version: MAJOR.MINOR.PATCH)
- `stability` (one of: `core`, `extension`, `experimental`)

Schemas without these fields are invalid.

## Semantic Version Rules

- PATCH: bugfix only. MUST NOT change semantics or behavior.
- MINOR: backward-compatible additions only. MUST be skip-unknown safe.
- MAJOR: breaking change. Requires migration or refusal.

**MUST NOT**
- Increase PATCH for semantic changes.
- Increase MINOR without forward compatibility guarantees.
- Change behavior without version bump.

## Forward Compatibility (Skip-Unknown)

- Readers MUST preserve unknown fields and forward them unchanged.
- Unknown fields MUST NOT be discarded, reordered, or altered.
- MINOR changes MUST be readable by prior MINOR readers via skip-unknown.

## Backward Compatibility

- MAJOR changes require an explicit migration or refusal.
- Refusal is mandatory when migration is absent or would be lossy.

## Stability Levels

- `core`: required for runtime and persistent formats. Strictest guarantees.
- `extension`: optional but stable for runtime integration.
- `experimental`: tools-only or non-shipping; MUST NOT be used by runtime.

## Version Progression Rules

- Version numbers MUST be monotonic per schema_id.
- Downgrades are FORBIDDEN.
- Any MAJOR bump MUST list a migration plan in `schema/SCHEMA_MIGRATION.md`.
