--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (engine primitives are not modified by tech prerequisites).
GAME:
- Prerequisite evaluation and activation gating.
SCHEMA:
- Prerequisite record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No floating point thresholds.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_TECH_PREREQUISITES - Technology Prerequisites (CIV3)

Status: draft  
Version: 1

## Purpose
Define deterministic prerequisites for technology activation.

## TechPrerequisite schema
Required fields:
- tech_id
- knowledge_id
- min_completeness (integer threshold, 0..1000)

Rules:
- min_completeness uses integer fixed-point.
- Missing knowledge fails the prerequisite check.

## Determinism requirements
- Prerequisite ordering is stable (tech_id, knowledge_id).
- Checks are deterministic and replayable.

## Integration points
- Knowledge items: `schema/knowledge/SPEC_KNOWLEDGE_ITEMS.md`
- Tech effects: `schema/technology/SPEC_TECH_EFFECTS.md`

## Prohibitions
- No implicit prerequisite bypasses.
- No global scans across all knowledge items.
