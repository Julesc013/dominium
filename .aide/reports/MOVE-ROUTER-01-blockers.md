Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-01

# MOVE-ROUTER-01 Blockers

No MOVE-ROUTER-01 structural move blocker remains.

## Cleared

- Target collisions: 0.
- Skipped moves: 0.
- Tracked bad-root files after apply: 0.
- Empty bad roots: 24 of 24 configured roots.
- Active root exceptions retired: 23.

## Remaining Warnings

These are assigned to `MOVE-ROUTER-02` and later proof tasks:

- Old bad-root path references remain in active code, docs, tools, validators,
  AIDE evidence, audit reports, and historical material.
- Imports and CMake paths may be stale after physical relocation.
- Quarantined files are intentionally inactive pending later owner review.
- Existing proof tasks may fail until reference/import/build repair runs.

## Non-Goals

MOVE-ROUTER-01 did not repair imports, references, build files, product boot,
projection, release, or semantic lint behavior.
