--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Secrecy policy evaluation and diffusion gating rules.
SCHEMA:
- Secrecy policy record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit diffusion bypasses.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_SECRECY - Secrecy Policies (CIV3)

Status: draft  
Version: 1

## Purpose
Define deterministic secrecy policies that gate knowledge diffusion.

## SecrecyPolicy schema
Required fields:
- policy_id
- allow_diffusion (0/1)
- min_fidelity (integer threshold)

Rules:
- allow_diffusion MUST be explicit.
- min_fidelity is a deterministic integer threshold.

## Determinism requirements
- Policy evaluation is pure and deterministic.
- No wall-clock or random inputs.

## Integration points
- Diffusion: `schema/knowledge/SPEC_DIFFUSION.md`
- Knowledge items: `schema/knowledge/SPEC_KNOWLEDGE_ITEMS.md`

## Prohibitions
- No policy-based global unlocks.
- No silent overrides without explicit policy entries.
