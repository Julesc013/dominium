Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# SEMANTIC-LINTS Blockers

Current blocker count: 0.

`slice0_hardcoded_ids` and `slice1_hardcoded_constants` now pass with a narrow exact-match allowlist for doctrine-backed identifiers, fixture literals, protocol literals, and schema vocabulary.

Remaining non-blocking cautions:

- The allowlist is intentionally large because the previous validators had no disposition model and flagged many legitimate Sol/Earth/Milky Way and field-vocabulary surfaces.
- New or moved literals will fail unless they are fixed, moved to a contract/registry, or added as a reviewed exact allowlist entry.
- Full CTest still depends on the TEST-PERF-01 sharded execution model; this task did not run full monolithic CTest.
