Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Interaction UX Baseline (RND-4)

Date: 2026-02-26  
Status: Baseline complete (affordances, previews, refusal UX, inspection overlays)

## 1) Affordance Schema and Registry

Implemented interaction contract surfaces:

1. `schema/interaction/affordance.schema`
2. `schema/interaction/affordance_list.schema`
3. `schema/interaction/interaction_preview.schema`
4. `data/registries/interaction_action_registry.json`

Runtime behavior:

1. Affordances are derived from `PerceivedModel` + `LawProfile` + `AuthorityContext`.
2. Registry declares UI metadata only; legality remains law/authority gated.
3. Deterministic ordering is stable by display/process/id keys.
4. Disabled affordances are retained with deterministic refusal hints.

## 2) Preview Modes

Implemented preview capabilities:

1. `none`: explicit no-preview response.
2. `cheap`: deterministic predicted summary from `PerceivedModel`.
3. `expensive`: inspection-cache-backed derived preview.

Safety:

1. Preview never mutates truth.
2. Budget pressure yields deterministic refusal (`refusal.preview.budget_exceeded`).
3. Epistemic limits yield deterministic refusal (`refusal.preview.forbidden_by_epistemics`).
4. Ranked profile redacts preview detail while preserving refusal/result contracts.

## 3) Inspection Overlay Behavior

Inspection affordance integration:

1. `process.inspect_generate_snapshot` remains process-driven and entitlement-gated.
2. Interaction dispatch consumes process output and emits RenderModel overlay payloads.
3. Overlays include deterministic highlight/label primitives and procedural materials.
4. Overlays degrade deterministically when budget or entitlement constraints apply.

## 4) Degradation and Caching Rules

Deterministic degradation path:

1. Try requested preview capability.
2. Refuse expensive preview when budget is exceeded.
3. UI can deterministically fall back to cheap/no preview modes.

Caching path:

1. Expensive previews use RS-5 inspection cache keys.
2. Cache reuse is keyed by target + truth hash anchor + policy.
3. No continuous recomputation is triggered by inspection display alone.

## 5) Guardrails

### RepoX invariants

1. `INV-UI-NEVER-MUTATES-TRUTH`
2. `INV-INTERACTION-INTENTS-ONLY`
3. `INV-AFFORDANCES-DERIVED-FROM-LAW`

### AuditX analyzers

1. `E52_INTERACTION_BYPASS_SMELL` (`InteractionBypassSmell`)
2. `E53_PREVIEW_INFO_LEAK_SMELL` (`PreviewInfoLeakSmell`)

### TestX coverage

1. `testx.interaction.affordance_list_deterministic`
2. `testx.interaction.affordance_respects_entitlements`
3. `testx.interaction.dispatch_creates_intent`
4. `testx.interaction.preview_budget_degrades_not_lags`
5. `testx.performance.inspection_cache_reuse`
6. `testx.interaction.refusal_display_consistent`

## 6) Gate Execution (RND-4 Final)

1. RepoX PASS
   - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
2. AuditX run
   - `py -3 tools/auditx/auditx.py scan --repo-root . --format json`
3. TestX PASS (interaction UX suite)
   - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset testx.interaction.affordance_list_deterministic,testx.interaction.affordance_respects_entitlements,testx.interaction.dispatch_creates_intent,testx.interaction.preview_budget_degrades_not_lags,testx.performance.inspection_cache_reuse,testx.interaction.refusal_display_consistent`
4. strict build PASS
   - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.rnd4 --cache on --format json`
5. `ui_bind --check` PASS
   - `py -3 tools/xstack/ui_bind.py --repo-root . --check`

## 7) Extension Points (MAT Integration)

1. `interaction_action_registry` can add material/part-specific actions without client hardcoding.
2. `parameter_schema_id` allows MAT payload contracts once part/material semantics are introduced.
3. Inspection overlays can expand to MAT diagnostics while preserving epistemic redaction and budget policies.
