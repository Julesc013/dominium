Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# XStack Incremental Model

## Overview

XStack executes gate verification as a compiler-style incremental pipeline:

1. Impact discovery
2. Merkle state hashing
3. Deterministic plan generation
4. Parallel execution with content-addressed cache
5. Artifact validation and result aggregation

This model removes redundant work while preserving governed invariants.

## Components

- Planner: `tools/xstack/core/plan.py`
- Impact graph: `tools/xstack/core/impact_graph.py`
- Merkle hashing: `tools/xstack/core/merkle_tree.py`
- Cache store: `tools/xstack/core/cache_store.py`
- Scheduler: `tools/xstack/core/scheduler.py`
- Runner adapters: `tools/xstack/core/runners.py`
- Work estimator: `tools/xstack/core/time_estimator.py`
- Artifact classifier: `tools/xstack/core/artifact_contract.py`
- Live logger: `tools/xstack/core/log.py`

## Pipeline

### 1) Impact graph

Changed paths are mapped to:

- impacted subsystems
- impacted TestX groups
- impacted AuditX groups
- required runner families

Inputs:

- `data/registries/testx_groups.json`
- `data/registries/auditx_groups.json`
- `data/registries/xstack_components.json`

### 2) Merkle hashing

Subtree roots are computed for:

- `engine/`, `game/`, `client/`, `server/`, `tools/`, `schema/`, `data/`, `docs/`, `scripts/`, `repo/`, `tests/`

Output:

- `.xstack_cache/merkle/roots.json`
- deterministic `repo_state_hash`

### 3) Plan generation

Planner computes profile-aware DAG:

- FAST
- STRICT (`STRICT_LIGHT`/`STRICT_DEEP`)
- FULL

Plan fields:

- ordered nodes
- dependency edges
- expected artifacts
- estimate summary

Output:

- `.xstack_cache/plans/<plan_hash>.json`

### 4) Scheduler execution

Scheduler runs ready nodes in parallel with deterministic aggregation.

- cache lookup before execution
- only cache-miss nodes execute
- results persisted per runner key

### 5) Artifact class handling

Artifact classes from `data/registries/derived_artifacts.json`:

- `CANONICAL`: deterministic and potentially gating
- `DERIVED_VIEW`: human-facing, regenerable
- `RUN_META`: informational, non-blocking

## Determinism Contracts

- deterministic file ordering in Merkle hashing
- deterministic node ordering in plans
- deterministic dependency level computation
- deterministic result ordering independent of thread completion order

## Operational Notes

- `gate.py verify` defaults to FAST
- `gate.py strict` selects strict profile
- `gate.py full` selects full profile
- `gate.py dist` always full
- `gate.py full` runs impacted groups by default; set `DOM_GATE_FULL_ALL=1` for all-group execution
- `--trace` enables structured live logs
- `--profile-report` includes scheduler metrics

## Debugging

If throughput regresses:

1. inspect latest plan in `.xstack_cache/plans/`
2. inspect cache hit ratio in profile report
3. check group registry granularity
4. review `docs/audit/xstack/FULL_PLAN_TOO_LARGE.md` if present
