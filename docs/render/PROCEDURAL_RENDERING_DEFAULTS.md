Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Procedural Rendering Defaults

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: normative
Version: 1.0.0
Scope: RND-1 defaults

## 1) Deterministic Color Mapping

- Default rule: `base_color = hash(material_id or type/semantic id) -> HSL -> RGB`.
- Hash precedence:
  1. resolved `material_id`
  2. semantic/entity id
- Category clamps:
  - saturation/value ranges are fixed by template/category policy.

## 2) Deterministic Primitive Selection

Selection precedence:

1. explicit representation-rule match
2. body-shape-derived primitive
3. semantic fallback by entity kind
4. global fallback (`prim.box.default`)

Missing shape/material metadata must degrade deterministically and must not refuse.

## 3) Label Policy Defaults

- Labels are policy-driven and optional.
- `label.none` for minimal diegetic/player defaults.
- `label.debug_ids` for debug/observer-style visibility.
- `label.player_minimal` for compact player-readable labels when allowed by policy.

## 4) LOD and Highlight Defaults

- LOD hints are presentation-only and deterministic from:
  - selected LOD policy
  - view mode
  - quantized distance bands
- Highlight layers are presentation-only and must not:
  - alter authority
  - reveal hidden truth

## 5) Null-Asset Baseline

- Primitive geometry + procedural material parameters are sufficient for valid output.
- Texture/sound packs are optional extensions.
- No runtime path may assume external assets exist.
