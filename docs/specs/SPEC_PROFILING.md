--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
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
