# RenderModel Contract Baseline

Status: baseline
Version: RND-1

## Implemented
- Schema-versioned `RenderModel` contract:
  - `schemas/render_model.schema.json`
  - `schemas/renderable.schema.json`
  - `schemas/render_primitive.schema.json`
  - `schemas/procedural_material.schema.json`
  - `schemas/representation_rule.schema.json`
  - `schemas/material_template.schema.json`
- Data-driven registries for deterministic representation:
  - `data/registries/render_primitive_registry.json`
  - `data/registries/procedural_material_template_registry.json`
  - `data/registries/label_policy_registry.json`
  - `data/registries/lod_policy_registry.json`
  - `data/registries/representation_rule_registry.json`
- Canonical adapter/resolver path:
  - `src/client/render/render_model_adapter.py`
  - `src/client/render/representation_resolver.py`
  - `tools/xstack/sessionx/render_model.py` wrapper

## Determinism Guarantees
- Renderables are generated from `PerceivedModel` only.
- Stable ordering:
  - sorted by `(semantic_id, layer_tags)`.
- Stable rule selection:
  - highest `priority`, tie-break by `rule_id`.
- Procedural material parameters are deterministic from registry template rules and semantic seeds.
- Canonical `render_model_hash` is emitted for replay/audit usage.

## Null-Assets Behavior
- No external texture/sound packs are required.
- Missing asset references do not refuse; representation degrades to primitive + procedural material output.
- Adapter emits valid renderables and procedural material payloads with zero asset packs.

## Guardrails
- RepoX:
  - `INV-RENDERER-TRUTH-ISOLATION`
  - `INV-REPRESENTATION-RULES-DATA-DRIVEN`
- AuditX analyzers:
  - `RenderTruthLeakSmell`
  - `HardcodedRepresentationSmell`
- TestX coverage:
  - deterministic render ordering/hash
  - deterministic rule tie-break resolution
  - no-assets output path
  - static no-truth-access scan

## Extension Points
- RND-2/3 renderer backends consume `RenderModel` without changing contract.
- MAT/domain visuals can extend templates/rules through packs.
- Additional overlay/diegetic styles remain presentation-only and law/epistemic-gated upstream.
