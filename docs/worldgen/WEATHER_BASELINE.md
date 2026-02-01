Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Weather Baseline (WEATHER0)

Status: binding for T4 baseline.  
Scope: deterministic, event-driven weather overlays on climate envelopes.

## What weather is in T4
- Weather is a set of **scheduled events** that temporarily perturb climate-related fields.
- Events are deterministic, replayable, and bounded by budgets/interest.
- Weather is applied as a provider layer on top of climate envelopes.

## Weather fields (effects)
Required effect fields:
- `climate.temperature_current`
- `climate.precipitation_current`
- `env.surface_wetness`
- `env.wind_current` (symbolic)

All numeric values are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Provider chain (T4 baseline)
1) **Climate envelope provider** (from T3)
2) **Weather event provider**
3) **Cache provider** (disposable)

## Event model
Each weather event has:
- `event_id`, `event_type`
- `affected_domain_ref`
- `start_tick`, `duration_ticks`
- `intensity`
- `RNG_stream_ref` (`noise.stream.weather.<domain>.<event_type>`)

Events apply deterministic deltas to weather effect fields and never exceed
the bounds of the underlying climate envelope unless explicitly configured.

## What is NOT included yet
- No per-tick global simulation.
- No fluid dynamics or storm cell tracking.
- No erosion, flooding, or vegetation growth.

## Collapse/expand compatibility
Weather collapse stores:
- cumulative precipitation and temperature deviation (coarse)
- event counts by type
- intensity histograms
- RNG cursor continuity per event stream

Expand reproduces event schedules deterministically from stored summaries.

## Maturity labels
- Weather events: **BOUNDED** (scheduled, deterministic baseline).
- Weather effects: **BOUNDED** (overlay-only, no global sim).

## See also
- `docs/worldgen/CLIMATE_AND_BIOMES_BASELINE.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`