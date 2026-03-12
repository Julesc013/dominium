Status: ACTIVE
Version: 1.0.0
Owner: Core Engineering
Last Updated: 2026-03-01
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FORM1 Retro Audit

## Scope
- Prompt: `FORM-1 — FormalizationState Substrate`
- Audit target: ad hoc infrastructure formalization behavior that should move to deterministic `FormalizationState` lifecycle.
- Relevant invariants:
- `INV-CONTROL-PLANE-ONLY-DISPATCH`
- `INV-INFERENCE-DERIVED-ONLY`
- `INV-FORMALIZATION-THROUGH-CONTROL`
- `INV-NO-ADHOC-TEMP-MODIFIERS`
- `INV-NO-WALLCLOCK-IN-PERFORMANCE`

## Findings

### 1) No canonical formalization substrate exists yet
- Evidence: no `src/infrastructure/formalization` module exists.
- Impact: inference/accept/promote/revert lifecycle is not represented as first-class deterministic state.
- Migration: add `formalization_state`, `inference_candidate`, and `formalization_event` artifacts with process-owned state transitions.

### 2) No explicit auto-snap/auto-track runtime branch found in authoritative process runtime
- File: `tools/xstack/sessionx/process_runtime.py`
- Evidence: no existing process family for infrastructure auto-formalization; no direct "auto track creation" process.
- Impact: behavior gap for raw-to-formal workflow (not a violation), but no explicit policy-governed inference/accept path yet.
- Migration: implement `action.formalize.*` control actions and `process.formalization_*` handlers with deterministic refusals.

### 3) Implicit graph/path persistence is fragmented across unrelated substrates
- Files:
- `src/core/graph/network_graph_engine.py`
- `src/inspection/inspection_engine.py`
- `src/client/interaction/inspection_overlays.py`
- Evidence: network graph and overlay pathways exist, but no lifecycle state linking raw assemblies to inferred/formal/networked infrastructure.
- Impact: impossible to reenact formalization intent chain end-to-end.
- Migration: add event-sourced formalization transitions and connect inspection/overlay summaries to formalization artifacts.

### 4) Domain migration targets for FORM1
- Interior/terrain/path-like hints currently rely on domain-local payloads and overlays rather than unified formalization lifecycle state.
- Planned migration targets:
- `installed_structure_instances` and `construction_steps` as `raw_sources` for inference.
- Network graph attachment through `process.formalization_promote_networked`.
- Event stream/provenance integration for reenactment visibility.

## No-Conflict Check
- No canon conflict found with:
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- Planned implementation keeps inference derived-only and routes all truth mutation through process runtime and control plane.

## Migration Plan

### Phase A: Introduce formalization contracts
- Add strict schemas and registries for state, candidate, event, target, and policy.
- Integrate registry compile/lockfile hashing for formalization registries.

### Phase B: Deterministic inference and process transitions
- Add `src/infrastructure/formalization/inference_engine.py` for deterministic candidate generation.
- Add process family:
- `process.formalization_infer`
- `process.formalization_accept_candidate`
- `process.formalization_promote_networked`
- `process.formalization_revert`

### Phase C: UX + enforcement + tests
- Add control actions and inspection/overlay integration.
- Add RepoX hard rules and AuditX smells for bypass and truth mutation.
- Add TestX coverage for determinism, no-truth-mutation inference, commitments, promote/revert semantics, and epistemic gating.

## Deprecation Entries Required
- None currently mandatory; no existing canonical formalization subsystem to deprecate.
- If future ad hoc formalization helper paths are found, they must be quarantined under the FORM1 enforcement rules.

## Acceptance Criteria for Audit Closure
- Inference remains derived-only (no state mutation).
- Accept/promote/revert mutation only through process runtime via control actions.
- Formalization events are deterministic and reenactable.
- No wall-clock usage introduced.
