Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# RenderModel Contract Baseline (RND-1)

Date: 2026-02-26  
Status: Baseline complete (Perceived->Render contract, deterministic resolver, null-assets behavior)

## 1) Schemas and Registries

### Schemas (v1.0.0)

1. `schema/render/render_model.schema`
2. `schema/render/renderable.schema`
3. `schema/render/render_primitive.schema`
4. `schema/render/procedural_material.schema`
5. `schema/render/representation_rule.schema`
6. `schema/render/material_template.schema`

All six are now in strict canonical schema format with required-shape and invariant sections.

### Registries

1. `data/registries/render_primitive_registry.json`
2. `data/registries/procedural_material_template_registry.json`
3. `data/registries/label_policy_registry.json`
4. `data/registries/lod_policy_registry.json`
5. `data/registries/representation_rule_registry.json`

Registry-driven representation includes:

1. Primitive fallback set (capsule/box/cylinder/sphere/plane/line/glyph)
2. Procedural material templates (`default_by_id_hash`, wood/metal/stone/water-like)
3. View-mode-aware label policy resolution
4. Faction-presence rule (`faction_id=__present__`) for deterministic overlay-style representation metadata

## 2) Runtime Components

1. Adapter: `src/client/render/render_model_adapter.py`
2. Resolver: `src/client/render/representation_resolver.py`
3. Session wrapper: `tools/xstack/sessionx/render_model.py`

Runtime contract guarantees:

1. Render path consumes `PerceivedModel` only (no truth/state imports).
2. Rule selection is deterministic (`priority desc`, `rule_id asc`).
3. Renderables are deterministically sorted (`semantic_id`, `layer_tags`).
4. Renderable IDs are deterministic and hash-stabilized.
5. `render_model_hash` is canonical and replay/audit-safe.

## 3) Null-Assets Behavior

No texture/sound packs are required for valid output.

When optional representation data is missing:

1. resolver chooses deterministic primitive fallback
2. procedural material is generated deterministically from template + semantic/material/type seeds
3. adapter still emits valid renderables/material payloads

## 4) Determinism and Epistemic Boundaries

Determinism:

1. stable rule resolution
2. stable material parameter generation
3. stable ordering and IDs
4. stable `render_model_hash`

Epistemic boundary:

1. adapter/resolver cannot read truth model
2. render derivation is downstream of Perceived filtering and does not open new knowledge channels

## 5) Guardrails

### RepoX

1. `INV-RENDERER-TRUTH-ISOLATION`
2. `INV-REPRESENTATION-RULES-DATA-DRIVEN`

### AuditX

1. `E36_RENDER_TRUTH_LEAK_SMELL` (`RenderTruthLeakSmell`)
2. `E37_HARDCODED_REPRESENTATION_SMELL` (`HardcodedRepresentationSmell`)

### TestX

1. `testx.render.render_model_deterministic_ordering`
2. `testx.render.representation_rule_resolution_deterministic`
3. `testx.render.no_assets_required`
4. `testx.render.no_truth_access`
5. `testx.representation.no_assets_required` (existing fallback coverage retained)

## 6) Gate Execution (RND-1 Final)

1. RepoX PASS
   - command: `py -3 -m tools.xstack.repox.check --profile STRICT`
2. AuditX run PASS
   - command: `py -3 -m tools.xstack.auditx.check --profile STRICT`
3. TestX PASS
   - command: `py -3 tools/xstack/testx/runner.py --profile STRICT --subset testx.render.render_model_deterministic_ordering,testx.render.representation_rule_resolution_deterministic,testx.render.no_assets_required,testx.render.no_truth_access,testx.representation.no_assets_required`
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.rnd1 --cache on --format json`
5. ui_bind PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`

## 7) Extension Points

1. RND-2/3 renderer backends consume `RenderModel` unchanged.
2. MAT/domain visual style can be extended through registry templates/rules without code hardwiring.
3. Additional diegetic overlays remain presentation-only renderables under view-mode/rule policy.
