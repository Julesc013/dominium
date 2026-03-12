Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# RenderModel Contract

Status: normative
Version: 1.0.0
Scope: RND-1

## 1) RenderModel Artifact Definition

- `RenderModel` is a schema-versioned derived artifact.
- `RenderModel` input is `PerceivedModel` only.
- `RenderModel` cannot carry hidden truth channels.
- Renderer backends (null/software/hardware) consume `RenderModel` only.

## 2) Allowed Payload Surface

`RenderModel` contains presentation-only data:

1. primitive geometry refs
2. procedural material parameters
3. transforms
4. labels/glyph metadata
5. layer/highlight tags
6. LOD hints (presentation-only)

Forbidden:

1. truth-only fields
2. authority/law mutation commands
3. hidden inventory/state leak channels

## 3) Determinism Rules

- Stable IDs:
  - `renderable_id` is derived deterministically from semantic identity.
- Stable ordering:
  - `renderables` are sorted by `semantic_id` then `layer_tags`.
- Stable material mapping:
  - semantic/material seeds map deterministically to procedural outputs.
- Stable hashing:
  - canonical hash over the final render payload is emitted as `render_model_hash`.

## 4) Null-Assets Doctrine

- Runtime must remain valid with zero texture/sound packs.
- Primitive + procedural material output is sufficient for valid rendering.
- Missing optional representation metadata degrades deterministically to fallback primitive/material paths.

## 5) Separation Contract

- Adapter/resolver paths must not import or access `TruthModel`/universe state.
- Observation/law/epistemic filtering happens upstream in `PerceivedModel`.
- Rendering and render derivation are presentation-only and cannot mutate simulation truth.
