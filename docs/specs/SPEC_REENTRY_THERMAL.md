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
# SPEC_REENTRY_THERMAL - Atmospheric Drag and Heating (v1)

This spec defines deterministic drag and heating proxies used during
atmospheric flight in local lanes.

## 1. Inputs (authoritative)
The reentry model uses:
- `density_q16` from the atmosphere sample (Q16.16 kg/m^3)
- `velocity` in body-fixed or local frame (Q48.16 m/s)
- `mass_kg_q16` (Q16.16 kg)
- `drag_area_cda_q16` (Q16.16, Cd*A in m^2)
- `heat_coeff_q16` (Q16.16, dimensionless scaling)

## 2. Drag proxy (v1)
Acceleration magnitude:
- `a = (density * v^2 * CdA) / mass`

Rules:
- All math uses fixed-point.
- Apply along `-velocity` direction (if `v > 0`).
- This is a kinematic modifier, not a physics integrator.

## 3. Heating proxy (v1)
Heating rate:
- `h = density * v^3 * heat_coeff`

Heat accumulation:
- `heat += h * dt`
- `dt` is exactly one tick; no wall-clock scaling.

Optional thresholds:
- If `heat > max_heat`, emit a warning or refusal event (damage not required in v1).

## 4. Warp rules
- In atmosphere (density > 0), warp is capped or forces collapse to ORBITAL.
- Warp does not change `dt`; it only changes tick pacing.

## 5. Determinism
- All operations are fixed-point.
- Iterations (if any) are fixed-count.
- Results must be invariant under tick batching and warp.

## 6. Related specs
- `docs/SPEC_MEDIA_FRAMEWORK.md`
- `docs/SPEC_ATMOSPHERE.md`
- `docs/SPEC_LANES_AND_BUBBLES.md`
