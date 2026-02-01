Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Performance Metrics (PERF1)

Status: binding.
Scope: derived, replayable performance metrics used by PERF-1 fixtures and regression gates.

## Principles

- Metrics are derived from event streams and scheduler counters only.
- Metrics are reproducible from replays and do not influence simulation outcomes.
- Metrics must be deterministic across platforms and thread counts.
- Metrics are reported in fixed units and stable field names.

## Canonical metric set

The following metric keys are mandatory in PERF-1 fixture outputs:

- active_tier2_domains: count of active Tier-2 domains per tick.
- active_tier1_domains: count of active Tier-1 domains per tick.
- processes_per_tick: total Process executions per tick.
- macro_events_per_tick: macro events executed per tick.
- macro_time_steps_per_tick: macro time steps executed per tick.
- collapse_expand_ops_per_tick: collapse or expand operations per tick.
- agent_planning_steps_per_tick: agent planning steps per tick.
- snapshot_ops_per_tick: snapshot operations per tick.
- serialization_ops_per_tick: serialization operations per tick.
- refusal_counts_total: total refusals observed per tick.
- refusal_counts_budget: refusals attributed to budgets.
- refusal_counts_capability: refusals attributed to missing capabilities.
- refusal_counts_validation: refusals attributed to validation failures.
- refusal_counts_unknown: refusals attributed to unknown or uncategorized causes.
- memory_peak_kb: peak memory observed for the fixture (kilobytes).
- memory_plateau_kb: post-warmup memory plateau (kilobytes).
- cross_shard_msgs_per_tick: cross-shard messages per tick.
- cross_shard_bytes_per_tick: cross-shard bytes per tick.
- event_hash: deterministic hash of the canonical event stream.
- metrics_hash: deterministic hash of the canonical metric payload.
- replay_hash: deterministic hash of the replay input.

## Hashing and identity

- event_hash, metrics_hash, and replay_hash MUST be stable across platforms.
- Hashes are recorded as lowercase hex strings.
- Hashes are derived from canonical, deterministic serialization.

## Serialization and storage

- PERF-1 fixture metrics are stored as JSON under `tests/fixtures/perf/*/metrics/`.
- Budget regression reports are stored under `run_root/perf/budgets/`.
- Non-authoritative metadata MAY appear in metrics payloads.
- Allowed metadata keys include thread_count, platform, run_id, observed_at.
- Non-authoritative metadata MUST NOT alter metric equality or determinism checks.

## Related contracts

- `docs/architecture/CONSTANT_COST_GUARANTEE.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/BUDGET_POLICY.md`
- `docs/policies/PERF_BUDGETS.md`