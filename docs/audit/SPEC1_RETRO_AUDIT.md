Status: DERIVED
Last Reviewed: 2026-03-01
Supersedes: none
Superseded By: none
Version: 1.0.0
Owner: Core Engineering
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SPEC1 Retro Audit

## Scope
- Prompt: `SPEC-1 — SpecSheet & Standards Substrate`
- Audit target: temporary and hardcoded engineering spec logic that should move to data-driven `SpecSheet` contracts.
- Relevant invariants:
- `INV-MODE-AS-PROFILES`
- `INV-CONTROL-PLANE-ONLY-DISPATCH`
- `INV-NO-ADHOC-TEMP-MODIFIERS`
- `INV-DERIVED-ARTIFACT-CONTRACT`
- `INV-NO-WALLCLOCK-IN-PERFORMANCE`

## Findings

### 1) Hardcoded gauge/width/speed-like constants and policy values
- File: `src/control/control_plane_engine.py`
- Evidence: control/effect integration currently uses fixed parameter keys such as `max_speed_permille` in inline modifier queries.
- Impact: operational limits exist, but there is no unified spec binding layer for target-specific standards/tolerances.
- Migration: move process-level limits to `SpecSheet` parameter keys and compliance checks, then allow effects to modulate those parameters.

### 2) Domain-local tolerance thresholds in inspection presentation
- File: `src/client/interaction/inspection_overlays.py`
- Evidence: pressure/flood/smoke threshold bands are currently expressed as inline constants.
- Impact: tolerance semantics are split between inspection presentation and domain logic.
- Migration: route tolerance bands through `tolerance_policy_registry` and include spec compliance summaries in inspection payloads.

### 3) Domain-specific tolerance logic duplicated outside a spec substrate
- File: `src/materials/composition_engine.py`
- Evidence: material-fraction tolerance checks use local tolerance handling.
- File: `src/reality/ledger/ledger_engine.py`
- Evidence: tolerance-based accounting exception thresholds use local validation.
- Impact: no shared, typed tolerance policy contract for reusable engineering checks.
- Migration: preserve current behavior, then map checks into generic `compliance_check` evaluation with explicit `tolerance_policy_id`.

### 4) Spec-like semantics embedded in process/runtime without explicit spec bindings
- File: `tools/xstack/sessionx/process_runtime.py`
- Evidence: process behavior gates and derived checks do not currently use a target-bound spec contract.
- Impact: plan/execution can run without a single reusable standard acceptance contract.
- Migration: add process family:
- `process.spec_apply_to_target`
- `process.spec_check_compliance`
- and feed compliance outcomes into control decision extensions and inspection summaries.

## No-Conflict Check
- No direct canonical conflict found with `docs/canon/constitution_v1.md` or `docs/canon/glossary_v1.md`.
- Planned implementation keeps:
- process-only mutation,
- deterministic tick ordering,
- optional pack operation for null boot.

## Migration Plan

### Phase A: Introduce SpecSheet substrate (non-breaking)
- Add strict schemas and registries:
- `spec_sheet`, `spec_type`, `tolerance_policy`, `compliance_check`, `compliance_result`.
- Add runtime engine for deterministic evaluation and fingerprinted results.

### Phase B: Integrate with process runtime and control/inspection
- Add process handlers:
- `process.spec_apply_to_target`
- `process.spec_check_compliance`
- Persist spec bindings and compliance artifacts in state through deterministic normalization.
- Inject compliance summary into inspection section data.
- Record compliance outcomes in control decision extensions during plan execution when requested by policy.

### Phase C: Harden and migrate
- Add RepoX rule for hardcoded gauge/width/spec constants outside registries.
- Add AuditX analyzers:
- `SpecHardcodeSmell`
- `SpecBypassSmell`
- Migrate ad hoc constants incrementally to registry-driven spec parameters/tolerance policies.

## Deprecation Entries Required
- Pending explicit deprecation registration after code migration:
- inline inspection tolerance constants in presentation overlays (non-authoritative but semantically spec-like),
- domain-local duplicated tolerance checks where equivalent `compliance_check` is introduced.

## Acceptance Criteria for Audit Closure
- SpecSheets remain optional (null boot with zero spec packs succeeds).
- No wall-clock timing introduced.
- No direct mutation bypasses process runtime.
- Deterministic compliance fingerprints stable for identical inputs.
