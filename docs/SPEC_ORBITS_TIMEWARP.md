# SPEC_ORBITS_TIMEWARP - Orbit Lanes and Warp Pacing

This spec defines the deterministic orbit lane model and time-warp pacing used
by the runtime. v1 implements patched-conic, on-rails orbits (no physics
integration).

## 1. Orbit model (patched conics)
- Orbits are patched-conic elements in fixed-point (no floats).
- Orbital state is defined relative to a reference frame and a primary body.
- Epoch is expressed as `epoch_tick` in the authoritative timebase.
- Updates are analytic and deterministic; no integration by wall-clock.

Canonical orbital state fields:
- `primary_body_id` (u64)
- `semi_major_axis_m` (Q48.16 meters)
- `eccentricity` (Q16.16 in [0, 1))
- `inclination` (Turn, Q16.16)
- `longitude_of_ascending_node` (Turn, Q16.16)
- `argument_of_periapsis` (Turn, Q16.16)
- `mean_anomaly_at_epoch` (Turn, Q16.16)
- `epoch_tick` (u64)

Normalization rules:
- Angles are normalized to `[0, 1)` turns via deterministic normalization.
- `eccentricity` outside `[0, 1)` is invalid and must refuse.
- `semi_major_axis_m <= 0` is invalid and must refuse.

## 2. Orbit lane modes (runtime)
- `ORBITAL`: vessel follows orbital elements.
- `LOCAL_PHYS`: vessel is simulated in local space (surface/air/etc).
- `DOCKED` / `LANDED`: vessel is constrained to a parent body or structure.

## 3. Warp pacing (tick-first)
- Warp is a pacing policy that advances ticks faster than real time.
- Warp never changes canonical time or authoritative state directly.
- In multiplayer, the host/server is authoritative for warp changes and schedules.
- Event ticks are computed analytically from orbital elements and epoch tick.

## 4. Analytic event scheduling (v1 API)
Event queries are deterministic and purely analytic:
- `orbit_next_event(orbit, tick, event_kind, out_tick)`
- `event_kind` includes periapsis, apoapsis, SOI entry/exit, and node crossings.
- Periapsis/apoapsis are computed analytically from mean anomaly and period.
- SOI entry/exit is supported only when a primary SOI radius is known; otherwise
  the API must return `NOT_IMPLEMENTED`.

## 5. Deterministic math requirements
- All math must use deterministic fixed-point utilities (see
  `source/domino/core/dom_deterministic_math.h`).
- Iterative solves must use fixed iteration counts or deterministic bounds.
- No floating-point in authoritative paths.

## Related specs
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_ORBITS.md`
