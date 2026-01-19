--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Provides deterministic primitives; no mod compatibility policy.
GAME:
- Enforces compatibility, safe mode, and refusal-first behavior.
SCHEMA:
- Defines compatibility inputs and refusal codes.
TOOLS:
- Validate packs and explain refusals deterministically.
FORBIDDEN:
- No silent fallback from incompatible sim mods.
- No runtime schema mutation.
DEPENDENCIES:
- Engine -> none outside engine.
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> engine/game public APIs + schema.
--------------------------------
# SPEC_MOD_COMPATIBILITY - Compatibility Negotiation (MOD0)

Status: draft  
Version: 1

## Purpose
Define deterministic compatibility negotiation and safe-mode behavior.

## Compatibility checks
For each mod, evaluate:
- Schema versions (min/max).
- Feature epoch requirements.
- Required capabilities.
- Render feature requirements.
- Performance budget class.

Results:
- `ACCEPT`
- `ACCEPT_WITH_WARNINGS`
- `REFUSE`

## Safe mode rules
Safe mode is explicit and deterministic:
- `NONE`: refuse any incompatible mod.
- `NON_SIM_ONLY`: disable sim-affecting mods; disable incompatible non-sim mods.
- `BASE_ONLY`: disable all mods.

Rules:
- Incompatible sim-affecting mods are refused when safe mode is `NONE`.
- Safe mode must be explicit and is never auto-selected.

## Refusal codes
- `SCHEMA_MISSING`
- `SCHEMA_RANGE`
- `EPOCH_MISSING`
- `EPOCH_RANGE`
- `CAPABILITY_MISSING`
- `RENDER_FEATURE_MISSING`
- `PERF_BUDGET`

## Prohibitions
- No silent enable/disable.
- No privileged access or bypass of epistemics.

## Test plan (spec-level)
- Compatibility result determinism.
- Safe mode outcomes deterministic for identical inputs.
- Refusal on missing schema and feature epochs.
