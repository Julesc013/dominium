# RenderModel Contract

Status: normative
Version: 1.0.0

## Scope
- `RenderModel` is a schema-versioned derived artifact.
- Input source is `PerceivedModel` only.
- `RenderModel` never contains hidden truth.

## Contract
- `RenderModel` contains renderer-consumable presentation data only:
  - primitives
  - procedural materials
  - transforms
  - labels
  - overlay/layer tags
- Render backends (null/software/hardware) consume `RenderModel` and must not reach into truth.
- The adapter/resolver path is data-driven from compiled registries.

## Determinism
- Stable renderable identity:
  - `renderable_id` derived deterministically from semantic identity.
- Stable ordering:
  - renderables sorted by semantic identity, then layer tags.
- Stable material mapping:
  - semantic IDs map to procedural material params deterministically.
- Stable hashing:
  - canonical hash over the final `RenderModel` payload.

## Null-Assets Doctrine
- External textures/sounds are optional.
- With zero asset packs, render output remains valid via primitive + procedural defaults.
- Missing representation inputs deterministically degrade to default primitive/material paths.

## Separation
- Truth mutation is forbidden in renderer/adapter/resolver paths.
- Observation/law/epistemic gating occurs before render derivation.
- Render behavior does not alter simulation semantics.
