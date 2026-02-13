Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Gate Throughput Policy

## Objective

Gate throughput is optimized through incremental planning, content-addressed caching, and parallel execution.  
Invariants, determinism, and canonical enforcement remain mandatory.

## Profiles

- `FAST` (default for `verify` and `exitcheck`)
  - Runs minimal structural checks and impacted fast groups.
  - Skips full suites and heavy runners unless escalation rules require promotion.
- `STRICT` (explicit `gate.py strict` or escalated)
  - Split into `STRICT_LIGHT` and `STRICT_DEEP`.
  - `STRICT_LIGHT`: impacted structural and runtime verification.
  - `STRICT_DEEP`: includes schema/governance-depth checks and full semantic AuditX group.
- `FULL` (explicit `gate.py full` or `gate.py dist`)
  - Runs all sharded groups and heavy runners with parallel scheduling and caching.
  - Default `full` is impacted-group based; set `DOM_GATE_FULL_ALL=1` for exhaustive all-group execution.

## Escalation Rules

Escalation is data-defined in `data/registries/gate_policy.json`.

- `FAST -> STRICT` when changed paths include:
  - `schema/**`
  - `data/registries/**`
  - `repo/repox/**`
  - `scripts/ci/**`
- `STRICT -> FULL` only for explicit `full`/`dist` intent.
- Packaging changes do not force FULL unless `full` or `dist` is requested.

## Incremental Planning Model

Planner inputs:

- subtree Merkle roots (`.xstack_cache/merkle/roots.json`)
- changed-path impact graph
- profile policy
- group registries

Planner output:

- deterministic node DAG
- parallelizable node sets
- expected artifacts
- plan hash and persisted plan file (`.xstack_cache/plans/<plan_hash>.json`)

## Caching Model

Each runner result is content-addressed by:

- `runner_id`
- `input_hash`
- `profile_id`
- optional tool version key

Cache path:

- `.xstack_cache/<runner_id>/<entry_hash>.json`

Cache safety guarantees:

- cache hit requires exact key/input match
- mismatched profile or input hash cannot return success
- cache stores artifacts and exit code for deterministic replay of runner decisions
- selected runners use cross-profile shared cache keys when command and input contract are identical (`repox_runner`, core AuditX/TestX groups)

## Parallel Scheduling

Scheduler behavior:

- executes independent nodes in parallel
- preserves deterministic result ordering in aggregated outputs
- fails fast on first hard failure
- records per-runner duration and cache hit/miss

FULL behavior:

- runs all impacted shards even if one shard fails, then returns aggregate exit status
- improves diagnostics without sacrificing deterministic ordering

Safety rules:

- `repox_runner` is always first
- codegen-sensitive operations remain serialized by dependencies
- test/audit groups are sharded and parallelized when independent

## Observability

`gate.py` supports:

- `--trace` for structured live event logs
- `--profile-report` for scheduler runtime summary

Live events include:

- plan summary
- runner start/end
- cache hit/miss
- duration per runner
- profile summary with total runtime

## Structural Bounding

FULL mode is bounded by architecture, not timeouts:

- group sharding (`testx_groups.json`, `auditx_groups.json`)
- parallel execution
- selective heavy runner inclusion via impact
- plan-size estimator warnings (`docs/audit/xstack/FULL_PLAN_TOO_LARGE.md`)

## Key Files

- `scripts/dev/gate.py`
- `tools/xstack/core/plan.py`
- `tools/xstack/core/scheduler.py`
- `tools/xstack/core/cache_store.py`
- `tools/xstack/core/impact_graph.py`
- `tools/xstack/core/merkle_tree.py`
- `data/registries/gate_policy.json`
- `data/registries/testx_groups.json`
- `data/registries/auditx_groups.json`
- `data/registries/xstack_components.json`
