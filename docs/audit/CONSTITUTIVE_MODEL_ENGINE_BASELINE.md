Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Constitutive Model Engine Baseline

Date: 2026-03-03
Series: META-MODEL-1

## Scope

This baseline establishes deterministic constitutive model runtime plumbing without introducing domain-specific ELEC/THERM/FLUID/CHEM implementations.

## Delivered Artifacts

- Schemas:
  - `schema/models/constitutive_model.schema`
  - `schema/models/model_type.schema`
  - `schema/models/model_binding.schema`
  - `schema/models/input_ref.schema`
  - `schema/models/output_ref.schema`
  - `schema/models/cache_policy.schema`
  - `schema/models/model_evaluation_result.schema`
- JSON schema projections:
  - `schemas/constitutive_model.schema.json`
  - `schemas/model_type.schema.json`
  - `schemas/model_binding.schema.json`
  - `schemas/input_ref.schema.json`
  - `schemas/output_ref.schema.json`
  - `schemas/cache_policy.schema.json`
  - `schemas/model_evaluation_result.schema.json`
  - registry schemas for model type/cache/model registries
- Registries:
  - `data/registries/model_type_registry.json`
  - `data/registries/model_cache_policy_registry.json`
  - `data/registries/constitutive_model_registry.json`
- Engine:
  - `src/models/model_engine.py`
  - `src/models/__init__.py`
- Process/runtime integration:
  - `process.model_evaluate_tick`
  - `process.hazard_increment`
  - `process.flow_adjust`
  - model runtime state persistence in `tools/xstack/sessionx/process_runtime.py`
- Inspection:
  - `section.models.summary` in inspection registry and inspection engine.

## Deterministic Evaluation Ordering

- Active bindings are sorted by `(tier, model_id, binding_id)`.
- Input signatures and output signatures are normalized and sorted.
- Inputs hash (`inputs_hash`) and outputs hash (`outputs_hash`) are computed from canonical serialization.
- RNG path is only active for models with `uses_rng_stream=true` and `rng_stream_name` set.

## Cache Rules

- `cache.none`: always evaluate.
- `cache.by_inputs_hash`: cache key is `(model_id, binding_id, tier, inputs_hash)`.
- Optional TTL in ticks controls cache entry expiry.

## Budget and Degradation Rules

- Per-binding evaluation cost is `cost_units` declared by model.
- Budget cap is applied per evaluation tick.
- Deterministic degrade behavior:
  - deferred bindings are returned in stable order with explicit `degrade.*` reasons.
  - optional far-target tick bucketing can skip non-local bindings deterministically.

## Process-Only Output Contract

- Model outputs map to process-backed channels:
  - `effect` -> effect rows/provenance (process-backed effect application path).
  - `hazard_increment` -> `process.hazard_increment`.
  - `flow_adjustment` -> `process.flow_adjust`.
  - `derived_quantity` and `compliance_signal` -> derived observation/report path only.
- Model evaluation emits deterministic observation artifacts (`artifact_family_id=OBSERVATION`) into `info_artifact_rows`.

## Enforcement Hooks

- RepoX:
  - `INV-RESPONSE-CURVES-MUST-BE-MODELS`
  - `INV-MODEL-OUTPUTS-PROCESS-ONLY`
- AuditX:
  - `E179_INLINE_RESPONSE_CURVE_SMELL`
  - `E180_MODEL_BYPASS_SMELL`

## Ready For ELEC-0

The substrate now supports registering and evaluating model stubs for:

- load phasor/power factor
- attenuation-style response models
- fatigue/wear-rate style response models
- pump/curve style flow response models
- conductance-style thermal response models

Specific domain semantics remain deferred to future series.

## Gate Run Status (2026-03-03)

Commands executed:

- `python tools/xstack/testx/runner.py --profile FAST --subset test_model_binding_order_deterministic,test_inputs_hash_deterministic,test_cache_reuse_by_inputs_hash,test_rng_usage_only_when_declared,test_output_processes_emitted,test_budget_degrade_stable,test_constitutive_model_docs_present,test_repox_constitutive_model_invariant_registered`
- `python tools/xstack/repox/check.py --profile FAST`
- `python tools/auditx/auditx.py scan --repo-root . --format both`
- `python tools/xstack/run.py strict --repo-root . --cache on`
- `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`

Results:

- TestX (META-MODEL-1 targeted subset): PASS (8/8).
- RepoX FAST: FAIL due pre-existing cross-series findings; model-related undeclared schema/registry findings were cleared after topology regeneration.
- AuditX scan: RUN complete; canonical artifacts refreshed under `docs/audit/auditx/`.
- strict build: REFUSAL due existing global baseline findings outside META-MODEL-1 scope (CompatX/TestX/packaging pipeline status).
- topology map: UPDATED and deterministic fingerprint refreshed.
