--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (engine primitives are not modified by tech effects).
GAME:
- Effect activation rules and enforcement.
SCHEMA:
- Effect record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No tech effects that modify engine primitives.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_TECH_EFFECTS - Technology Effects (CIV3)

Status: draft  
Version: 1

## Purpose
Define deterministic technology effects that unlock game-layer content.

## TechEffect schema
Required fields:
- tech_id
- effect_type (unlock_recipe/unlock_policy/unlock_research)
- target_id
- flags (optional)

Rules:
- Effects only unlock game-layer content.
- Effects MUST NOT modify engine primitives or determinism gates.

## Determinism requirements
- Effect ordering is stable (tech_id, target_id).
- Activation is explicit and acknowledged by the actor/org.

## Integration points
- Tech prerequisites: `schema/technology/SPEC_TECH_PREREQUISITES.md`
- Production recipes: `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- Policy system: `schema/governance/SPEC_POLICY_SYSTEM.md`

## Prohibitions
- No omniscient tech unlocks.
- No direct simulation rule changes without explicit effects.
