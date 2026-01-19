--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

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
# Vehicles and Poses

- VehicleComponent (see `include/domino/dvehicle.h`): `{ VehicleId id, AggregateId agg, EnvironmentKind env, throttle, yaw_cmd, pitch_cmd, roll_cmd, flags }`. All controls are Q16.16 in `[-1 .. +1]`.
- VehiclePose unions per environment: surface/air use `WPosExact + Orientation`; water uses the same; high-atmo uses `{ body, alt_m, lat, lon, Orientation }`; orbit holds an `OrbitComponent`; vacuum-local uses `SpacePos`. Orientation is `{ yaw, pitch, roll }` in `Turn` (Q16.16 turns).
- Registry: `dvehicle_register` allocates a component/pose pair for an Aggregate. Lookup via `dvehicle_get` / `dvehicle_get_pose`; setters for pose, controls, and flags stay integer-only.

## Integrators (stub)
- Per-env steps live in `source/domino/dvehicle.c`: `dvehicle_step_surface`, `dvehicle_step_water_surface`, `dvehicle_step_water_submerged`, `dvehicle_step_air_local`, `dvehicle_step_high_atmo`, `dvehicle_step_orbit`, `dvehicle_step_vacuum_local`. Dispatcher: `dvehicle_step`.
- Motion uses Q16.16 (surface/air/water) and Q48.16 (vacuum/orbit) only—no floats. Heading is quadrant-based from yaw; throttle drives acceleration, friction clamps speed; positions integrate via `g_domino_dt_s`.
- Orbit step currently advances `M0` only; vacuum-local uses a simple linear velocity in `SpacePos`.

## Environment transitions (stub rules)
- `dvehicle_try_switch_surface_to_air`: throttle + ground speed lift into `ENV_AIR_LOCAL`.
- `dvehicle_try_switch_air_to_high_atmo`: crosses a fixed altitude threshold, converts to `lat/lon/alt`.
- `dvehicle_try_switch_high_atmo_to_orbit`: altitude gate to `ENV_ORBIT` with a stub orbit component.
- `dvehicle_try_switch_orbit_to_high_atmo`: drops back when semi-major axis falls below a floor.
- `dvehicle_try_switch_high_atmo_to_air`: re-entries when altitude drops; `dvehicle_try_switch_air_to_surface` lands when z <= build band.
- All thresholds are integer constants for now; replace with body/vehicle-specific criteria later.

## Numeric policy
- Only fixed-point math: Q16.16 for local motion, `Turn` for attitude, Q48.16 for space motion. No private floating-point state.
- Positions stay wrapped/clamped via `dworld` helpers; speeds clamp to prevent runaway values in stub integrators.
