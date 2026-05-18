Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-01

# MOVE-ROUTER-01 Apply Result

MOVE-ROUTER-01 applied the deterministic route table from MOVE-ROUTER-00.

## Summary

- Bad-root tracked files before: 1,765.
- Bad-root tracked files after: 0.
- Files moved by `git mv`: 1,765.
- Semantic moves: 1,694.
- Quarantine moves: 71.
- Skipped moves: 0.
- Target collisions: 0.
- Former bad roots emptied: 24.
- Active root exceptions retired: 23.

## Quarantine Rule

Unknown or ambiguous files were not left in bad roots. They moved to:

```text
archive/quarantine/<root>/
```

Quarantine is inactive evidence/holding space. Promotion out of quarantine
requires later owner review.

## Remaining Work

`MOVE-ROUTER-02` must repair references, imports, CMake/build paths, projection
metadata, and any proof surfaces that still point to the former bad roots.

Feature work remains blocked.
