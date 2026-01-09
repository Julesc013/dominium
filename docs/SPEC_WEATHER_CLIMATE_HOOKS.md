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
- `docs/SPEC_MEDIA_FRAMEWORK.md`
- `docs/SPEC_ATMOSPHERE.md`
