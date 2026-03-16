Status: DERIVED
Last Reviewed: 2026-03-06
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-4 retro audit for deterministic system template integration.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SYS4 Retro Audit

## Scope
Audit existing template/prefab patterns before introducing canonical `SystemTemplate` schema, compiler, and instantiation process.

## 1) Existing Template/Prefab Patterns
- Existing reusable content is concentrated in blueprint/domain packs and plan artifacts, not in system-template registries.
- Runtime already supports deterministic plan creation/execution and commitment emission:
  - `process.plan_create`
  - `process.plan_execute`
- There is no dedicated `process.template_instantiate` path yet.

## 2) Ad-hoc Blueprint Pack Inventory
- Pack contribution structure already exists and is pack-driven (`pack.json` + contribution payloads).
- Reusable system stubs are currently represented indirectly (blueprints/macros), not as a single canonical `system_template` record type.
- No evidence of a hidden hardcoded "engine object" path in current SYS/POLL runtime branches.

## 3) Migration Targets
- Introduce canonical schema + registry:
  - `schema/system/system_template.schema`
  - `schema/system/template_instance_record.schema`
  - `data/registries/system_template_registry.json` (null-boot safe baseline)
- Add deterministic compiler:
  - `src/system/templates/template_compiler.py`
- Add canonical process:
  - `process.template_instantiate`
- Add optional pack content:
  - `packs/system_templates/base/`

## 4) Migration Plan
1. Keep core registry null-boot safe by default.
2. Add optional starter pack for templates (runtime must remain valid without pack).
3. Enforce process-only instantiation (no direct prefab bypass).
4. Require signature/invariant references per template and deterministic nested-template resolution.
5. Wire proofs/replay and tests before strict gate validation.

## 5) Risks and Controls
- Risk: direct spawn/prefab code path bypassing CTRL/MAT discipline.
  - Control: `process.template_instantiate` as canonical mutation path.
- Risk: nondeterministic nested-template order.
  - Control: deterministic topological sort by `template_id`.
- Risk: template pack becoming mandatory.
  - Control: empty core registry + optional pack policy.
