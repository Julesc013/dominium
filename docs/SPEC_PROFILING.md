# SPEC_PROFILING — Runtime Profiling Contract

## Scope
Defines profiling hooks and reporting for the Dominium runtime. Profiling is
**non-authoritative** and MUST NOT influence simulation results.

## Measured zones (minimum)
Profiling MUST expose per-frame measurements for:
- `sim_tick` (authoritative tick step wrapper)
- `lane_update`
- `orbit_update` (if invoked)
- `surface_streaming`
- `derived_pump`
- `ai_scheduler`
- `net_pump`
- `render_submit`
- `input_pump`

## Counters
Profiling MUST provide:
- last-frame duration per zone (microseconds or milliseconds)
- total-frame duration
- invocation counts per zone

## Reporting
- Output format MUST be structured (TLV or JSON) and written under `RUN_ROOT`.
- The profile dump MUST be deterministic in field ordering.
- Profiling output MUST be opt-in (CLI flag or explicit request).

## Overhead control
- Profiling MUST NOT allocate excessively.
- Profiling SHOULD be compilable out for release builds.
- Profiling MUST NOT use wall-clock time for any authoritative decision.

## Related specs
- `docs/SPEC_PERF_BUDGETS.md`
- `docs/SPEC_NO_MODAL_LOADING.md`
