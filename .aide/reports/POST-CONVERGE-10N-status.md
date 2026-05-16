# POST-CONVERGE-10N Status

Status: DERIVED
Last Reviewed: 2026-05-17

## Result

PARTIAL.

Focused RepoX improved from 23 failures / 5 warnings to 20 failures / 5 warnings.

## Scope

- Tool hash and audit evidence staleness only.
- No root moves, deletes, renames, aliases, move maps, or salvage maps.
- No product boot proof, portable projection proof, package proof, or release generation.
- No product/runtime/source behavior changes.
- No RepoX weakening.

## Fixed

- `INV-IDENTITY-FINGERPRINT`: 1 to 0.
- `INV-TOOL-VERSION-MISMATCH`: 2 to 0.
- RepoX group cache now includes explicit docs/audit evidence dependencies for groups that read tracked audit evidence skipped by Merkle roots.

## Deferred

- `INV-AUDITX-OUTPUT-STALE` warning remains; AuditX findings are 199 commits behind HEAD.
- Four glossary warnings in generated/historical audit evidence remain.
- Remaining 20 hard failures are outside the narrow 10N tool-hash/audit-staleness scope.

## Readiness

POST-CONVERGE-11 is not ready because non-proof RepoX governance/source-policy failures remain.
