Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Timing and Clock Domains

This document defines clock domains and timing modes used by application
entrypoints.

## Clock domains
- Platform monotonic clock: `dsys_time_now_us()` (owned by platform runtime).
- Application logical clock: per-app logical time advanced in app loops.
- Simulation clock: server-only authoritative simulation time (MP0 ticks in
  current CLI demos).

Only the server advances authoritative simulation time. Client/launcher/setup
and tools advance their own logical clocks only.

## Timing modes
### Deterministic mode
- Fixed timestep: `D_APP_FIXED_TIMESTEP_US` in `domino/app/runtime.h`.
- No wall-clock sleeps.
- Stable ordering and outputs given identical inputs.
- Used by `--smoke`/`--selftest` tests.

### Interactive mode
- Variable timestep based on platform monotonic clock.
- Optional frame cap via `--frame-cap-ms` (client/tools).
- Vsync preference is configuration-only; no dependency in tests.

## Mode selection
- `--deterministic` or `--interactive` select a mode explicitly.
- If no explicit mode is given, CLI-only commands default to deterministic;
  windowed/TUI loops default to interactive.
- `--smoke`/`--selftest` enforce deterministic mode.

## Minimized / occluded behavior
Current loops do not auto-throttle on minimize/occlusion. Frame caps (if set)
remain the only throttling mechanism. Deterministic mode is unaffected.