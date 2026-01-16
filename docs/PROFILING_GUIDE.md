# Profiling Guide (PERF3)

This guide defines the mandatory profiling contract and how to use it safely.
Profiling is non-authoritative and MUST NOT influence simulation outcomes.

## Enabling profiling

Profiling is opt-in and disabled by default.

**MUST**
- Call `dsys_perf_set_enabled(1)` before any tick instrumentation.
- Provide a clock via `dsys_perf_set_clock(...)` for performance runs.
- Use the manual clock (`dsys_perf_set_manual_clock` / `dsys_perf_advance_manual_clock`) for deterministic tests.

**MUST NOT**
- Depend on profiling output for authoritative decisions.
- Write telemetry inside render/UI critical paths.

## Lanes (required attribution)

Every metric MUST be attributed to a lane:

- LOCAL: UI, rendering, derived jobs, streaming.
- MESO: interest sets and mid-tier aggregation.
- MACRO: authoritative sim and macro schedulers.
- ORBITAL: long-horizon/logistics (use when applicable).

## Metrics (required minimum)

The following metrics MUST be recorded at minimum:

- `sim_tick_us` (MACRO)
- `macro_sched_us`, `macro_events`, `event_queue_depth` (MACRO)
- `interest_set_size` (MESO)
- `derived_queue_depth`, `derived_job_us` (LOCAL)
- `render_submit_us`, `stream_bytes` (LOCAL)
- `net_msg_sent`, `net_msg_recv`, `net_bytes_sent`, `net_bytes_recv` (MACRO)

## Recording patterns

**Tick lifecycle**
- Call `dsys_perf_tick_begin(act, tick_index)` at the start of a tick.
- Call `dsys_perf_tick_end()` after all metrics are recorded.

**Counters**
- Use `dsys_perf_metric_add` for counts/bytes.
- Use `dsys_perf_metric_set` for one-shot values.
- Use `dsys_perf_metric_max` for queue depths or maxima within a tick.

**Timers**
- Wrap durations with `dsys_perf_timer_begin` / `dsys_perf_timer_end`.
- Timers accumulate into the specified metric.

## Telemetry output

Profiling emits:
- Telemetry: `run_root/perf/telemetry/telemetry_<fixture>_<seq>.jsonl`
- Budgets: `run_root/perf/budgets/PERF-BUDGET-002_<fixture>_<seq>.json`

Telemetry is JSON Lines (one entry per lane per tick). Budget reports use
deterministic keys and are enforced by `tools/ci/perf_budget_check.py`.

## Running PERF3 fixtures locally

From a test-enabled build directory:

```sh
ctest -R engine_perf_budget --output-on-failure
```

## Adding new metrics safely

**MUST**
- Add the metric to `dsys_perf_metric` in `engine/include/domino/system/dsys_perf.h`.
- Update metric names in `engine/modules/system/dsys_perf.c`.
- Update `docs/PERF_BUDGETS.md` if the metric is budgeted.
- Update `docs/CI_ENFORCEMENT_MATRIX.md` if a new gate is introduced.

**MUST NOT**
- Introduce profiling that changes ordering, hashing, or authoritative state.

## Debugging regressions

1) Run PERF3 fixtures to generate budget reports.
2) Inspect `run_root/perf/budgets/*.json` for which metric exceeded its tier.
3) Use telemetry JSONL to identify which lane/tick caused the spike.
4) Optimize or adjust workload; update budgets only with explicit approval.
