Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# XStack Speed Report

## Measured Baseline

Source: `docs/audit/xstack/PROFILE_BASELINE.json` (STRICT cold cache).

- Total: `781.240s`
- Dominant phase: `subprocess.repox_runner` (`769.057s`, 98.44%)
- Remaining shards (TestX/AuditX) were sub-10s each.

## Measured After Optimization

Source: `docs/audit/xstack/PROFILE_AFTER_OPTIMIZATION.json` (STRICT warm cache).

- Total: `1.243s`
- Cache hits: `4/4` strict nodes
- Runtime dominated by planner + Merkle/impact graph setup, not runner execution.

## Current Lane Throughput

- FAST (`gate.py verify`): ~`0.003s` warm (all cache hits)
- STRICT (`gate.py strict`): ~`0.044s` warm; cold still RepoX-bound
- FULL (`gate.py full`): ~`123s` with impacted-group selection + sharded execution

## Throughput Architecture

- Deterministic plan DAG (`tools/xstack/core/plan.py`)
- Impact graph and group routing (`tools/xstack/core/impact_graph.py`)
- Incremental Merkle hashing with derived/run-meta exclusions (`tools/xstack/core/merkle_tree.py`)
- Content-addressed cache (`tools/xstack/core/cache_store.py`)
- Parallel scheduler with deterministic aggregation (`tools/xstack/core/scheduler.py`)

## Operational Guidance

1. Use `--trace --profile-report` on any slow run.
2. Check cache miss reasons first; misses dominate throughput.
3. For exhaustive all-group FULL runs, set `DOM_GATE_FULL_ALL=1`.
4. Keep tool caches and derived artifacts out of planner input hash scope.
