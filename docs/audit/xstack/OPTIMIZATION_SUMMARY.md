Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# XStack Optimization Summary

## Before vs After

Primary comparison source:
- Baseline: `docs/audit/xstack/PROFILE_BASELINE.json` (STRICT cold cache)
- After: `docs/audit/xstack/PROFILE_AFTER_OPTIMIZATION.json` (STRICT warm cache)

| Metric | Baseline | After |
| --- | ---: | ---: |
| STRICT total runtime | 781.240s | 1.243s |
| STRICT cache hits / misses | 0 / 4 | 4 / 0 |
| Dominant phase | `subprocess.repox_runner` (769.057s) | `plan.generate` (1.200s) |

Observed lane timings after optimization (same repo state):
- `gate.py verify`: ~0.003s (FAST, all cache hits)
- `gate.py strict`: ~0.044s warm / ~780s cold (RepoX miss dominates)
- `gate.py full`: ~123s with sharded runners and impacted-group selection

## Implemented Optimizations

1. Added deterministic profiling across planner, impact graph, Merkle hashing, cache lookup/store, scheduler, and runners.
2. Added lightweight TestX group runner (`scripts/dev/run_xstack_group_tests.py`) and migrated strict/full XStack groups away from monolithic suite calls.
3. Added cache-stability exclusions for derived/run-meta churn:
   - `docs/audit/**`
   - `.xstack_cache/**`
   - `tools/*/cache/**`
4. Added cross-profile cache sharing for stable runner commands:
   - `repox_runner`
   - `auditx.group.core.policy`
   - `testx.group.core.invariants`
   - `testx.group.runtime.verify`
5. Updated FULL scheduling:
   - continues across shard failures to collect deterministic diagnostics
   - uses impacted groups by default; exhaustive all-groups mode is opt-in (`DOM_GATE_FULL_ALL=1`)
6. Added optional refusal coercion for `compatx_runner` when refusal is explicit non-gating (`refuse.bundle_optional_flag`).

## Remaining Heavy Operation

- Cold `RepoX` remains the dominant cost for any new repo-state hash.
- This is structural and safe (no bypass introduced), but still the main limiter for cold STRICT runs.

## Structural Bound Going Forward

- Repeated verify/strict calls on unchanged state are cache hits and near-instant.
- FULL no longer relies on a single monolithic TestX runner in default mode.
- FULL runtime is bounded by shard count and impacted runner set; not by a sequential all-suite loop.
