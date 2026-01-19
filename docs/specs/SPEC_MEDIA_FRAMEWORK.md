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
# SPEC_MEDIA_FRAMEWORK - Planetary Media Framework (v1)

This spec defines the modular media framework for local-only environments such
as atmosphere and oceans. It is authoritative for runtime behavior and
bindings, but it does not define gameplay features.

## 1. Concepts
- **Medium**: A local environment that affects motion and thermal state inside
  activation bubbles (air, water, vacuum).
- **Media kinds**:
  - `VACUUM` (default)
  - `ATMOSPHERE`
  - `OCEAN` (stub in v1)
- Media sampling is **local-only** and **non-global**. Outside local bubbles,
  vessels remain on rails and only analytic boundary events apply.

## 2. Sampling inputs and outputs
Media sampling is a pure function of:
- `body_id`
- body-fixed position or altitude (meters, fixed-point)
- tick (`tick_index`), used only for deterministic weather modulation

Media sampling outputs (scaled integers; no floats):
- `density_q16` (Q16.16 kg/m^3)
- `pressure_q16` (Q16.16 Pa)
- `temperature_q16` (Q16.16 K)
- `wind_body_q16[3]` (optional; Q16.16 m/s, body-fixed)

All sampling is deterministic and side-effect free.

## 3. Provider model
Providers are pluggable and versioned:
- `AtmosphereProvider`
- `OceanProvider` (stub)
- `GenericMediumProvider` (vacuum)
- `WeatherProvider` (modulates samples; stub in v1)

Each provider exposes:
- `api_version`
- `validate(body_id, params)`
- `sample(body_id, pos_body_fixed, altitude_m, tick, out_sample)`

## 4. Bindings and identity
- A **provider binding** is stored per body:
  - `provider_id`
  - `params` (TLV)
  - `params_hash`
- Bindings are **sim-affecting** and included in universe identity.
- Mismatched bindings must refuse by default.

## 5. Determinism and non-blocking
- Sampling must be O(1) and must not allocate or perform I/O.
- All computation uses fixed-point math; no floats in authoritative paths.
- Derived work (meshes, UI) must use derived job queues and never block.

## 6. Related specs
- `docs/SPEC_ATMOSPHERE.md`
- `docs/SPEC_REENTRY_THERMAL.md`
- `docs/SPEC_WEATHER_CLIMATE_HOOKS.md`
- `docs/SPEC_LANES_AND_BUBBLES.md`
- `docs/SPEC_NO_MODAL_LOADING.md`
