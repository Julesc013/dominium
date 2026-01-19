--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Provides IDs, hashes, and scheduling primitives only.
GAME:
- Defines mod rules, compatibility policy, and safe-mode behavior.
SCHEMA:
- Owns mod manifest format, versioning, and validation rules.
TOOLS:
- Build/validate mod packs and report refusals deterministically.
FORBIDDEN:
- No runtime logic in schema specs.
- No code injection or executable payloads in mods.
DEPENDENCIES:
- Engine -> none outside engine.
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> engine/game public APIs + schema.
--------------------------------
# SPEC_MOD_MANIFEST - Mod Manifest Format (MOD0)

Status: draft  
Version: 1

## Purpose
Define the deterministic, schema-governed manifest format used by all mods.
Manifests are data-only and must not embed executable logic.

## Format (v1)
Line-based key/value pairs:

```
mod_id=example.mod
mod_version=1.2.0
schema_dep=world@1.0.0-2.0.0
feature_epoch=war@3-5
sim_affecting=1
perf_budget_class=2
dependency=base.assets@1.0.0-2.0.0
conflict=other.mod@1.0.0-1.1.0
required_capability=ui
render_feature=dgfx_soft
payload_hash=fnv1a64:0123456789abcdef
```

Rules:
- Keys are ASCII, one per line.
- Lines beginning with `#` or `;` are comments.
- Unknown keys are rejected (refusal-first).
- `payload_hash` is required and must be deterministic.

## Required fields
- `mod_id`
- `mod_version`
- `payload_hash`
- `sim_affecting`

## Optional fields
- `schema_dep` (repeatable): `schema_id@min-max`
- `feature_epoch` (repeatable): `epoch_id@min-max`
- `dependency` (repeatable): `mod_id@min-max`
- `conflict` (repeatable): `mod_id@min-max`
- `required_capability` (repeatable)
- `render_feature` (repeatable)
- `perf_budget_class`

## Version range rules
- `min-max` may omit either side: `1.0.0-` or `-2.0.0`.
- `*` or `any` means unbounded.
- Exact version may be specified without `-` (treated as min=max).

## Determinism rules
- Parsing is order-preserving and deterministic.
- Manifest hashing is computed from sorted file lists and byte content.
- No OS time or randomness is permitted.

## Prohibitions
- No embedded code or scripts.
- No runtime schema mutation.
- No silent fallback if manifest fields are invalid.

## Test plan (spec-level)
- Parse deterministically with identical input.
- Reject unknown keys and malformed version ranges.
- Require `payload_hash` and `mod_id`.
