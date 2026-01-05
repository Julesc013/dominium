# SPEC_ORBITS_TIMEWARP - Orbit Lanes and Warp Pacing

This spec defines the deterministic orbit lane model and time-warp pacing used
by the runtime. It is scaffolding-only in v1; no physical solvers are required.

## 1. Orbit model (patched conics)
- Orbits are patched-conic elements in fixed-point (no floats).
- Orbital state is defined relative to a reference frame.
- Epoch is expressed as `tick_index` in the authoritative timebase.
- Updates are analytic and deterministic; no integration by wall-clock.

## 2. Orbit lane modes (runtime)
- `ORBITAL`: vessel follows orbital elements.
- `LOCAL_PHYS`: vessel is simulated in local space (surface/air/etc).
- `DOCKED` / `LANDED`: vessel is constrained to a parent body or structure.

## 3. Warp pacing (tick-first)
- Warp is a pacing policy that advances ticks faster than real time.
- Warp never changes canonical time or authoritative state directly.
- In multiplayer, the host is authoritative for warp changes and schedules.

## 4. Analytic event scheduling (v1 API)
Event queries are deterministic and purely analytic:
- `orbit_next_event(orbit, tick, event_kind, out_tick)`
- `event_kind` includes periapsis, apoapsis, SOI entry/exit, and node crossings.
- v1 returns `NOT_IMPLEMENTED` for non-trivial events; identity cases may be
  supported for tests.

## Related specs
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_ORBITS.md`
