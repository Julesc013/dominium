# SPEC_PERF_BUDGETS — Runtime Performance Budgets

## Scope
This spec defines **non-authoritative** performance budgets for the Dominium
runtime and presentation pipeline. Budgets are enforced to preserve responsiveness
and "no modal loading" guarantees without changing simulation semantics.

## Principles
- Budgets MUST affect **derived/presentation** work only (fidelity, cadence, caches).
- Budget enforcement MUST NOT change authoritative simulation results.
- Over-budget conditions MUST trigger deterministic degrade or refusal behavior,
  never blocking or best-effort "fixups".

## Budget tiers
Budgets are keyed by performance tier (see `docs/SPEC_TIERS.md`). Values are
upper bounds; callers SHOULD treat `0` as "no limit configured".

### Baseline (2010-era)
- `sim_tick_cost_ms_max`: 12
- `derived_jobs_ms_per_frame_max`: 2
- `derived_io_bytes_per_frame_max`: 256 KiB
- `derived_jobs_per_frame_max`: 4
- `render_submit_ms_max`: 8
- `max_active_bubbles`: 1
- `max_surface_chunks_active`: 256
- `max_entities_per_bubble`: 2048
- `max_ai_ops_per_tick`: 8
- `max_ai_factions_per_tick`: 4
- `max_cosmo_entities_iterated_per_tick`: 4096

### Modern
- `sim_tick_cost_ms_max`: 12
- `derived_jobs_ms_per_frame_max`: 4
- `derived_io_bytes_per_frame_max`: 512 KiB
- `derived_jobs_per_frame_max`: 8
- `render_submit_ms_max`: 10
- `max_active_bubbles`: 1
- `max_surface_chunks_active`: 512
- `max_entities_per_bubble`: 4096
- `max_ai_ops_per_tick`: 16
- `max_ai_factions_per_tick`: 8
- `max_cosmo_entities_iterated_per_tick`: 8192

### Server
- `sim_tick_cost_ms_max`: 16
- `derived_jobs_ms_per_frame_max`: 8
- `derived_io_bytes_per_frame_max`: 2048 KiB
- `derived_jobs_per_frame_max`: 16
- `render_submit_ms_max`: 0
- `max_active_bubbles`: 1
- `max_surface_chunks_active`: 1024
- `max_entities_per_bubble`: 8192
- `max_ai_ops_per_tick`: 32
- `max_ai_factions_per_tick`: 16
- `max_cosmo_entities_iterated_per_tick`: 16384

## Enforcement behavior
- **Time overruns** MUST reduce derived cadence and/or fidelity for subsequent frames.
- **Capacity overruns** MUST evict or refuse new derived activations deterministically.
- **Sim budgets** MUST NOT delay or alter authoritative ticks; they only inform
  presentation degradation and refusal policies.

## Related specs
- `docs/SPEC_PROFILING.md`
- `docs/SPEC_NO_MODAL_LOADING.md`
- `docs/SPEC_STREAMING_BUDGETS.md`
- `docs/SPEC_FIDELITY_DEGRADATION.md`
- `docs/SPEC_TIERS.md`
