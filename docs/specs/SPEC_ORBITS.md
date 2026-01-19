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
# Orbit and Space Model (Deterministic, Fixed-Point)

## OrbitComponent
- Fields (see `include/domino/dorbit.h`):
  - `central`: `BodyId` of central body.
  - `a`: semi-major axis, Q48.16 metres.
  - `e`: eccentricity Q16.16 (0..1).
  - `i`, `Omega`, `omega`, `M0`: angles in `Turn` (1.0 turn = 2π).
  - `t0`: epoch in simulation **seconds** (integer seconds in simulation time, not wall-clock).
  - Drifts per second: `dOmega_dt`, `domega_dt`, `da_dt`, `de_dt`, `di_dt`.
- No floating point; Kepler solving uses fixed-point integers with bounded iterations.
- Mean anomaly uses a coarse mean-motion estimate from `mu` (gravitational parameter) and drifted `a`; elements are adjusted linearly by drifts before solving.

## Kepler pipeline (fixed-point)
1. Apply linear drifts to `a/e/i/Omega/omega` for time `t`.
2. Compute mean anomaly `M(t)` = `M0 + n * (t - t0)`.
3. Solve Kepler for eccentric anomaly `E` via integer Newton iterations.
4. Derive true anomaly `v` and radius `r` in orbital plane.
5. Rotate by `Omega`, `i`, `omega` to inertial `SpacePos` (Q48.16 metres).
- Trig uses bounded integer approximations (no floats) and MUST remain deterministic
  across platforms. Any change in approximation semantics is a determinism contract change.

## Bodies
- `Body` (see `include/domino/dbody.h`):
  - `id`, `name`, `mass`, `radius_m`, `base_temp_K`, `axial_tilt`, `spin_phase0`, `spin_rate_turns_per_s`, `mu`, and `orbit`.
  - `mu` is stored as Q48.16 (m³/s²). Orbits with `central==0` or `central==self` are roots at the origin.
- Registry helpers:
  - `dbody_register`, `dbody_get`, `dbody_get_mu`, `dbody_get_space_pos`.
  - Solar helpers: `dbody_sun_direction` (rough normalised vector), `dbody_solar_flux_at_body` (stub constant for now).

## Space sites and Lagrange points
- `SpaceSite` (registry via `dspace_site_register`):
  - `id`, `name`, `attached_body` (0 if free), `orbit` (optional), `offset` (local frame).
  - Use to represent stations, Lagrange points (L1–L5 co-rotating with a body), rings, and reference frames.
- `dspace_site_pos` resolves site position by combining attached-body offset and/or its own orbit.

## Belts, rings, radiation (stubs)
- `dspace_env.h` defines `BeltField` and `MagneticField` placeholders; registry and query stubs:
  - `dspace_env_radiation_intensity(pos)` (stub constant).
  - `dspace_env_belt_density(pos)` (checks radial shell membership).
- Radiation/fields are stubbed in this pass: queries are deterministic but not physically derived.

## Determinism
- All math is integer/fixed-point; no floats or doubles in orbit code.
- Iteration counts are fixed; clamping guards against invalid eccentricities or negative semi-major axes.
- Positions are recomputed from elements each query; no stateful N-body integration.
