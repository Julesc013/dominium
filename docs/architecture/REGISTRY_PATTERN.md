Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Registry Pattern (Category B)

This document defines the canonical registry pattern for open-world taxonomies.

## Requirements
- ID type: u32 (0 reserved for INVALID).
- Deterministic mapping from canonical key -> id.
- Ordering: stable sort by canonical key (ASCII, case-sensitive) unless a
  schema explicitly declares a fixed order.
- Runtime lookups: array indexed by id (O(1)).
- String lookups: load/authoring/tools only.
- Serialization stores ids + schema versions (never strings).

## Canonical Registry File Format
File path: `data/registries/<name>.registry`

Rules:
- One key per line.
- Leading/trailing whitespace is ignored.
- Empty lines and lines starting with `#` are ignored.
- Keys must match: `^[A-Z0-9_\\.]+$`

Example:
```
# LAW_TARGETS v1.4.0
AUTH.CAPABILITY_GRANT
AUTH.CAPABILITY_DENY
LIFE.BIRTH
WAR.ENGAGEMENT
```

## ID Assignment
- Read all keys.
- Normalize: trim whitespace; reject duplicates; validate format.
- Sort keys lexicographically (ASCII).
- Assign ids from 1..N in sorted order.
- 0 is reserved for INVALID/UNKNOWN.

## Registry Hash (Change Detection)
- Compute FNV-1a 32-bit over the sorted key list joined by `\n`.
- Store/compare the hash in tests to detect registry drift.

## Adapter Rules
If a legacy registry exists:
- Do NOT refactor all call sites.
- Add adapters that map legacy identifiers -> registry ids.
- Migrate callers incrementally with tests.