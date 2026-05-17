Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-A-PLAN Import Consumers

## Summary

| Group | Import Consumers | Apply Rewrites | Temporary Old-Import Callers |
| --- | ---: | ---: | ---: |
| `validation` | 8 | 6 | 2 |
| `meta.identity` | 20 | 14 | 6 |
| `meta.stability` | 16 | 14 | 2 |

## Apply Rewrites

Apply-phase rewrites are limited to active tools, tests, validators, and moved-module internal imports recorded in `.aide/refactors/MOVE-FAMILY-00C-A.import_rewrite_plan.json`.

## Temporary Old-Import Callers

Temporary old-import callers are allowlisted only because they are runtime, compatibility, release/security/lib, or deferred governance surfaces. They must not grow after apply.

## Path References

Bulk path references in docs, audits, AIDE evidence, and generated evidence stay historical. Embedded active metadata strings in moved modules require review during apply before any path-string rewrite.
