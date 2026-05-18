Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# TEST-PERF-01 Blockers

## Blocking

- `slice0_hardcoded_ids` fails and remains assigned to semantic lint repair.
- `slice1_hardcoded_constants` fails and remains assigned to semantic lint repair.
- Full unfiltered CTest remains not green until those semantic lint blockers are resolved.

## Not Blocking TEST-PERF-01

- `tools_auditx` no longer blocks fast feedback. It passes in the explicit slow AuditX shard with a 1200-second timeout.
- Smoke and fast labels pass after the XStack impact fallback fix.

Next task: `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS - Hardcoded Identifier and Constant Disposition`.
