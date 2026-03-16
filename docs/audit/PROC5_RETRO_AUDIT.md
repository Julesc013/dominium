Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PROC5 Retro-Consistency Audit

Status: AUDIT
Last Updated: 2026-03-06
Scope: PROC-5 process capsule generation/execution readiness.

## Existing Macro Shortcut Patterns

- No canonical `process.process_capsule_generate` or `process.process_capsule_execute` runtime process exists yet.
- Existing process abstraction is currently implied through:
  - deterministic maturity state (`process_capsule_eligible`) in `src/process/process_run_engine.py`
  - COMPILE-0 compiled model usage in `src/meta/compile/compile_engine.py`
  - SYS macro capsule execution patterns in `src/system/macro/macro_capsule_engine.py`
- No direct "instant craft" shortcut was identified in `src/process/`; process outputs still route through run/QC artifacts.

## Candidate Macro Shortcuts To Convert To ProcessCapsules

- Repeated deterministic process runs that already produce low-variance quality:
  - standardized transform workflows driven by `process_definition` + `yield_model` + `defect_model`
  - recurring QC-evaluated runs with stable metrics state.
- Existing compiled reduced-graph artifacts from COMPILE-0 can be attached to capsule execution for low-cost evaluation.

## Reusable SYS Patterns

SYS macro pattern reuse candidates:

- Canonical macro artifact rows:
  - deterministic row builder + normalize + hash-chain model
- Validity checks:
  - tolerance/error policy references
  - forced-expand behavior on out-of-domain inputs
- Runtime integration:
  - process-mediated execution only
  - canonical RECORD outputs plus derived explain artifacts.

## Migration Notes

1. Add process capsule schemas and registry:
   - `process_capsule`
   - `capsule_execution_record`
2. Implement capsule builder/executor in `src/process/capsules/`.
3. Integrate optional COMPILE-0 compiled model execution path with validity/proof checks.
4. Emit canonical execution/invalidation records and process run linkage.
5. Add replay/proof tooling for deterministic hash verification.
