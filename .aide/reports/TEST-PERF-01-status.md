Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# TEST-PERF-01 Status

Result: PASS_WITH_WARNINGS.

## Applied

- Added `fast` to existing smoke CTest tests.
- Added `audit`, `slow`, and `nightly` labels to the existing AuditX CTest shard.
- Kept the `auditx` label for compatibility.
- Preserved the AuditX 1200-second timeout.
- Added an impact-graph fallback so unmapped dirty paths still select core TestX/AuditX groups.

## Measured

- Focused RepoX: PASS, 128.978 seconds.
- Smoke CTest: PASS, 55.829 seconds.
- Fast CTest: PASS, 48.821 seconds.
- AuditX shard: PASS, 824.573 seconds.
- `slice0_hardcoded_ids`: FAIL, semantic lint blocker.
- `slice1_hardcoded_constants`: FAIL, semantic lint blocker.

## Disposition

Full CTest remains not green, but it is now honestly blocked by semantic lint failures rather than by an unclassified AuditX wall-time lane.
