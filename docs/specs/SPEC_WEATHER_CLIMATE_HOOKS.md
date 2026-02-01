Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
# SPEC_WEATHER_CLIMATE_HOOKS - Weather and Climate Hooks (v1)

This spec defines deterministic hooks for weather and climate modulation of
media samples. v1 implements stubs only.

## 1. Purpose
Weather/climate providers can modulate local media samples:
- density/pressure/temperature deltas
- wind vector (future)

These hooks exist to avoid future format changes; they do not introduce global
simulation.

## 2. Provider contract
Weather providers expose:
- `api_version`
- `validate(body_id, params)`
- `sample_modifiers(body_id, pos_body_fixed, altitude_m, tick, out_mods)`

Modifiers are scaled integers and must be deterministic. Default provider
returns zero deltas and zero wind.

## 3. Determinism and scope
- Weather hooks are **local-only** and **non-blocking**.
- Sampling uses only deterministic inputs; no external time or I/O.
- Weather changes never alter authoritative time or command ordering.

## 4. Related specs
- `docs/specs/SPEC_MEDIA_FRAMEWORK.md`
- `docs/specs/SPEC_ATMOSPHERE.md`