Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Performance Budgets (PERF0)

This document defines hard performance targets and regression budgets.
All budgets are measurable and must be tied to PERF3 fixtures.

## Tiers

- Baseline tier (2010 hardware)
- Modern tier (2020 hardware)
- Server tier

## Budgets (authoritative)

### Baseline tier
- Sim tick cost: <= 8.0 ms/tick
- Event queue processing: <= 1.0 ms/tick
- Macro events processed: <= 512 events/tick
- Event queue depth: <= 2048 events
- Interest set size: <= 4096 volumes
- Derived job queue depth: <= 64 jobs
- Derived jobs: <= 2.0 ms/frame
- Rendering submit: <= 4.0 ms/frame
- Memory budget: <= 2.0 GB
- IO budget: <= 256 KB/frame
- Network messages: <= 2048 msgs/tick
- Network bytes: <= 1.0 MB/tick

### Modern tier
- Sim tick cost: <= 4.0 ms/tick
- Event queue processing: <= 0.5 ms/tick
- Macro events processed: <= 1024 events/tick
- Event queue depth: <= 4096 events
- Interest set size: <= 8192 volumes
- Derived job queue depth: <= 128 jobs
- Derived jobs: <= 4.0 ms/frame
- Rendering submit: <= 2.0 ms/frame
- Memory budget: <= 4.0 GB
- IO budget: <= 1.0 MB/frame
- Network messages: <= 4096 msgs/tick
- Network bytes: <= 2.0 MB/tick

### Server tier
- Sim tick cost: <= 6.0 ms/tick
- Event queue processing: <= 0.5 ms/tick
- Macro events processed: <= 1024 events/tick
- Event queue depth: <= 4096 events
- Interest set size: <= 8192 volumes
- Derived job queue depth: <= 64 jobs
- Derived jobs: <= 1.0 ms/tick
- Rendering submit: <= 0.0 ms (no render)
- Memory budget: <= 8.0 GB
- IO budget: <= 128 KB/tick
- Network messages: <= 8192 msgs/tick
- Network bytes: <= 4.0 MB/tick

## Measurement requirements

Each budget MUST be measured by a PERF3 regression fixture:
- Fixture defines workload and world size.
- Fixture records per-tick and per-frame timing.
- Fixture emits structured results under `run_root/perf/budgets/`.
- Reports are validated by `tools/ci/perf_budget_check.py` (PERF-BUDGET-002).

## Budget Data (machine-readable)

```perf-budgets
[baseline]
macro_sim_tick_us_max=8000
macro_macro_sched_us_max=1000
macro_macro_events_max=512
macro_event_queue_depth_max=2048
meso_interest_set_size_max=4096
local_derived_queue_depth_max=64
local_derived_job_us_max=2000
local_render_submit_us_max=4000
local_stream_bytes_max=262144
macro_net_msg_sent_max=2048
macro_net_msg_recv_max=2048
macro_net_bytes_sent_max=1048576
macro_net_bytes_recv_max=1048576

[modern]
macro_sim_tick_us_max=4000
macro_macro_sched_us_max=500
macro_macro_events_max=1024
macro_event_queue_depth_max=4096
meso_interest_set_size_max=8192
local_derived_queue_depth_max=128
local_derived_job_us_max=4000
local_render_submit_us_max=2000
local_stream_bytes_max=1048576
macro_net_msg_sent_max=4096
macro_net_msg_recv_max=4096
macro_net_bytes_sent_max=2097152
macro_net_bytes_recv_max=2097152

[server]
macro_sim_tick_us_max=6000
macro_macro_sched_us_max=500
macro_macro_events_max=1024
macro_event_queue_depth_max=4096
meso_interest_set_size_max=8192
local_derived_queue_depth_max=64
local_derived_job_us_max=1000
local_render_submit_us_max=0
local_stream_bytes_max=131072
macro_net_msg_sent_max=8192
macro_net_msg_recv_max=8192
macro_net_bytes_sent_max=4194304
macro_net_bytes_recv_max=4194304
```

## Fixture bindings (EXEC-AUDIT1)

These fixtures exercise the budgets above. Each fixture declares per-tier
caps in `game/tests/fixtures/**/fixture.cfg`.

| Fixture | Budget profile | Primary focus |
| --- | --- | --- |
| fixture_earth_only | baseline | Minimal world cost and determinism baseline |
| fixture_10k_systems_latent | baseline | Latent scaling, no global iteration |
| fixture_war_campaign | baseline | War workloads and degradation |
| fixture_market_crisis | modern | Economy burst amortization |
| fixture_timewarp_1000y | baseline | Long-horizon batch stepping |

## Failure artifacts

On violation, emit a report with:
- tier
- budget name
- threshold
- observed value
- fixture name and run parameters