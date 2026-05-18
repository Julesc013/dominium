Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# SEMANTIC-LINTS Next Readiness

Readiness: ready with warnings.

Ready conditions:

- `slice0_hardcoded_ids`: PASS.
- `slice1_hardcoded_constants`: PASS.
- No remaining semantic lint blockers are known.

Next task:

`MOVE-SCRIPT-00 - Generate Deterministic Bad-Root Router and Dry-Run Move Plan`

Warnings:

- Full CTest still follows the TEST-PERF-01 sharded execution policy.
- The semantic lint allowlist is exact-match; future literals must be fixed, moved to contracts/registries, or justified with a narrow entry.
