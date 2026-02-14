Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# XStack Speed Report

## Measured Baseline (Current Pass)

Source profiles:

- `docs/audit/xstack/PROFILE_FAST.json`
- `docs/audit/xstack/PROFILE_STRICT_COLD.json`
- `docs/audit/xstack/PROFILE_STRICT_WARM.json`
- `docs/audit/xstack/PROFILE_FULL.json`

Measured totals:

- FAST cold: `838.673s`
- FAST warm: `0.003s`
- STRICT cold: `897.040s`
- STRICT warm: `0.053s`
- FULL cold: `1023.451s`

## Bottleneck Summary

- Dominant cold-path cost remains `repox_runner`.
- Warm-path throughput is now near-instant because cache reuse is deterministic and profile-aware.
- Test/Audit shard execution stays parallel and deterministic in FULL.

## Structural Improvements Active

- Deterministic plan DAG (`tools/xstack/core/plan.py`)
- Profile-aware cache input hashing (`tools/xstack/core/scheduler.py`)
- Merkle subtree hashing (`tools/xstack/core/merkle_tree.py`)
- Content-addressed runner cache (`tools/xstack/core/cache_store.py`)
- Parallel shard scheduler (`tools/xstack/core/scheduler.py`)

## Operational Guidance

1. Use `gate.py <profile> --profile-report` for timing snapshots.
2. Run `gate.py strict` twice to separate cold and warm behavior.
3. Use `gate.py full --full-all` only for explicit exhaustive validation.
4. Continue reducing RepoX cold path cost by tightening per-group dependency scopes.
