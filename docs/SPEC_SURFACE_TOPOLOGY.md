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
# SPEC_SURFACE_TOPOLOGY - Deterministic Surface Topology Providers

This spec defines deterministic surface topology providers for body surfaces.
Topology is authoritative and must be bound, hashed, and versioned.

## 1. Scope
- Topology defines altitude, lat/long mapping, surface normals, and the local
  tangent basis used for surface projections.
- Topology providers are deterministic and fixed-point only.
- Topology selection is part of universe identity and must be hashed.

## 2. Provider kinds
Canonical provider kinds:
- `SPHERE` (implemented in v1)
- `ELLIPSOID` (stub allowed)
- `TORUS` (allowed only for special surfaces; never default for Earth)

## 3. Inputs and outputs
Inputs:
- Body-fixed position in segmented Q16.16 meters (`dom_posseg_q16`).
- Lat/long in turns (`Q16.16`) for inverse mapping where supported.

Outputs:
- `altitude_m` (Q48.16 meters)
- `lat_turns` (Q16.16 turns; range [-0.25, 0.25] for latitude)
- `lon_turns` (Q16.16 turns; range [0, 1) or [-0.5, 0.5])
- `surface_normal` (Q16.16 unit vector in body-fixed coordinates)
- `tangent_frame` (ENU basis vectors in Q16.16)

Notes:
- Segmented inputs are supported via a deterministic segment size defined by
  the surface runtime (see `docs/SPEC_SURFACE_STREAMING.md`).

## 4. Sphere provider rules (v1)
- Altitude = `|pos| - radius`.
- Latitude/longitude are derived deterministically from position.
- Surface normal is the normalized position vector.
- Lat/long + altitude must map back to a deterministic body-fixed position.

## 5. Binding and defaults
- Every body has a topology binding (`body_id -> provider + params`).
- Earth MUST bind to `SPHERE` or `ELLIPSOID` by default.
- `TORUS` is permitted only with explicit override for non-Earth bodies.

## 6. Determinism and refusal
- Any invalid binding or unsupported provider must refuse deterministically.
- Unknown provider bindings must be preserved during bundle round-trips.

## Related specs
- `docs/SPEC_SYSTEMS_BODIES.md`
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_SURFACE_STREAMING.md`
