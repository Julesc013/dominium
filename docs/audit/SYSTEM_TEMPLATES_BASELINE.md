Status: DERIVED
Last Reviewed: 2026-03-06
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: SYS-4 System Template Library
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# System Templates Baseline

## Summary
SYS-4 establishes deterministic, pack-driven `SystemTemplate` compilation and instantiation workflows without introducing bespoke gameplay object classes.

Delivered capabilities:
- data-defined template schema and canonical instance record schema,
- deterministic template compiler with nested-template topological resolution,
- process-only instantiation (`process.template_instantiate`) routed through CTRL planning and MAT commitments,
- optional starter template pack for engines/generators/pumps/heat exchangers/boilers,
- policy-gated developer UX tooling and reproducibility verifier,
- RepoX/AuditX enforcement and TestX coverage for template discipline.

## Template Schema
Primary schema:
- `schema/system/system_template.schema`
  - `template_id`, `version`, `description`
  - `required_domains`
  - `assembly_graph_spec_ref`
  - `interface_signature_template_id`
  - `boundary_invariant_template_ids`
  - `macro_model_set_id`
  - `tier_contract_id`
  - `safety_pattern_instance_templates`
  - `spec_bindings`
  - `nested_template_refs`
  - `deterministic_fingerprint`, `extensions`

Instance record schema:
- `schema/system/template_instance_record.schema`
  - `instance_id`, `template_id`, `instantiation_mode`, `created_tick`
  - `deterministic_fingerprint`, `extensions`

## Starter Templates (Optional Pack)
Pack path:
- `packs/system_templates/base/`

Templates:
- `template.engine.ice_stub`
- `template.generator.diesel_stub`
- `template.pump_basic`
- `template.heat_exchanger_basic`
- `template.boiler_steam_stub`

Starter template pack remains optional; null-boot with no system template packs is preserved.

## Compiler and Instantiation Workflow
Compiler:
- `src/system/templates/template_compiler.py`
- deterministic validation:
  - required domains available,
  - interface/invariant template refs registered,
  - macro model set and tier contract registered.
- deterministic nested resolution via topological ordering by `template_id`.

Instantiation:
- process: `process.template_instantiate`
- integrated in `tools/xstack/sessionx/process_runtime.py`
- generates:
  - plan artifact (CTRL),
  - commitment row (MAT),
  - template instance record (canonical RECORD),
  - template and fingerprint hash-chain entries for replay/proof.

Refusals:
- `refusal.template.missing_domain`
- `refusal.template.forbidden_mode`
- `refusal.template.spec_noncompliant`

## Enforcement and Tests
RepoX invariants:
- `INV-NO-PREFAB-BYPASS`
- `INV-TEMPLATE-HAS-SIGNATURE-INVARIANTS`

AuditX smells:
- `TemplateBypassSmell` (`E267_TEMPLATE_BYPASS_SMELL`)
- `UnversionedTemplateSmell` (`E268_UNVERSIONED_TEMPLATE_SMELL`)

TestX additions:
- `test_template_compile_deterministic`
- `test_template_instantiate_creates_plan_and_commitments`
- `test_macro_instantiation_policy_gated`
- `test_template_reproducible_hash`
- `test_nested_templates_toposort_deterministic`

## Readiness for SYS-5
SYS-4 outputs are structured for SYS-5 certification workflows:
- templates carry explicit interface/invariant/spec/safety references,
- macro-model bindings are explicit and validation-ready,
- instantiation records and proof hashes provide auditable provenance for certification issuance/revocation hooks.
