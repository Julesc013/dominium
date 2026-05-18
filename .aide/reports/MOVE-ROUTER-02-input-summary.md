Status: DERIVED
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-02

# MOVE-ROUTER-02 Input Summary

## MOVE-ROUTER-01 Result

| Metric | Count |
| --- | ---: |
| Moved files | 1765 |
| Semantic moves | 1694 |
| Quarantine moves | 71 |
| Skipped moves | 0 |
| Target collisions | 0 |
| Former bad roots with tracked files after apply | 0 |
| Former bad roots emptied | 24 |
| Active exceptions retired | 23 |

## Expected Repair Areas

MOVE-ROUTER-01 intentionally did not repair active imports, current path strings,
CMake/source lists, projection/release proof paths, or runtime/tooling references.
The stale-reference scan was intentionally broad and truncated after recording
5,000 findings, so MOVE-ROUTER-02 uses the full moved-item map as the source of
truth for active repairs.

| Stale-reference class | Count |
| --- | ---: |
| `active_docs_current` | 29340 |
| `active_source` | 35757 |
| `active_tool` | 3385 |
| `active_validator` | 106 |
| `unknown` | 129 |

## Repair Policy

- Active exact old paths may be rewritten to their routed targets.
- Active Python imports may be rewritten to routed package/module names.
- Historical/audit/generated evidence remains preserved unless it is a current
  authority surface.
- Imports or references to quarantined files are blockers unless they are
  archival references.
- Broad feature behavior changes are out of scope.
