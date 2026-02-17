# Procedural Rendering Defaults

Status: normative
Version: 1.0.0

## Deterministic Color Mapping
- Default color rule:
  - `base_color = hash(material_id or semantic_id) -> HSL -> RGB`
- Hash source precedence:
  1. resolved `material_id`
  2. resolved semantic/entity ID
- Category clamps:
  - saturation/value ranges are fixed by category and policy.

## Deterministic Primitive Selection
- Selection precedence:
  1. explicit representation rule match
  2. body-shape-derived primitive
  3. semantic fallback by entity kind
  4. global fallback (`prim.box.default`)
- Missing shape/material data does not refuse; it degrades deterministically.

## Labels
- Labels are policy-driven and optional.
- Player-default diegetic profiles may hide labels.
- Debug/spectator/observer profiles may enable label expansion by entitlement/law.

## LOD and Highlighting
- LOD hints are presentation-only and deterministic from:
  - policy
  - view mode
  - distance bands (quantized inputs)
- Highlight layers are presentation-only:
  - no authority changes
  - no truth channel expansion

## Null-Asset Baseline
- Primitive geometry + procedural material parameters are sufficient for valid output.
- Texture/sound packs are optional extensions, not runtime assumptions.
