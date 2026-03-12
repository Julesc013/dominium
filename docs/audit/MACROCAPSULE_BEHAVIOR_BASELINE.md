Status: CANONICAL
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-2 MacroCapsule behavior baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MacroCapsule Behavior Baseline

## Scope
SYS-2 hardens deterministic macro-tier system behavior for collapsed systems (`MacroCapsule`) using constitutive models and process-only boundary mutation.

## Execution Semantics
- Runtime process: `process.system_macro_tick`.
- Deterministic capsule ordering: `capsule_id` ascending.
- Boundary input collection includes flow/signal/safety/declared field samples.
- Model evaluation is delegated to META-MODEL (`evaluate_model_bindings`) with registered macro model sets.
- Output application is routed through process-governed pathways:
  - `process.flow_adjust`
  - energy transform recording
  - `process.pollution_emit`
  - deferred effect application rows for controlled follow-up.
- Macro runtime state is persisted in `system_macro_runtime_state_rows` and hash chained.

## Error Bounds and Forced Expand Rules
- Error bound policies are resolved through TOL and residual policy registries.
- Forced expand is emitted as canonical `forced_expand_event` when:
  - error bounds are exceeded,
  - inspection/fidelity requests target capsule,
  - hazard/validity constraints require higher fidelity.
- Forced expand is logged in DecisionLog and emitted as canonical RECORD artifact (`artifact.record.system_forced_expand`).
- Macro output records are OBSERVATION artifacts (`artifact.observation.system_macro_output`) and compactable.

## Domain Integration Points
- ELEC/THERM/FLUID/CHEM macro stubs are registered in `macro_model_set_registry`.
- POLL integration uses `process.pollution_emit` from macro outputs.
- Explain contracts integrated:
  - `explain.system_forced_expand`
  - `explain.system_safety_shutdown`
  - `explain.system_output_degradation`.

## Proof and Replay
- Hash chains persisted:
  - `system_forced_expand_event_hash_chain`
  - `system_macro_output_record_hash_chain`
  - `system_macro_runtime_hash_chain`.
- Replay tool added: `tools/system/tool_replay_capsule_window`.

## Validation Snapshot (2026-03-05)
- SYS-2 TestX subset: PASS
  - `test_capsule_execution_deterministic`
  - `test_macro_outputs_match_interface_signature`
  - `test_error_bound_triggers_forced_expand`
  - `test_forced_expand_is_canonical`
  - `test_expand_on_inspection_request`
  - `test_cross_platform_capsule_hash_match`
- Capsule-heavy stress verification (256 capsules, budget cap 64): PASS
  - deterministic digest stable across equivalent runs
  - deterministic defer/processed counts stable (`64/192`)
- Replay window verification (`tool_replay_capsule_window`): PASS
- Strict build target gate (`domino_engine`, `dominium_game`, `dominium_client`): PASS
- Topology map regeneration: PASS

## Gate Notes
- RepoX STRICT and AuditX STRICT were executed but remain failing due pre-existing repository-wide governance drift unrelated to SYS-2 deltas (doc status/header/index and historical tool-version/ruleset mismatches). SYS-2 scoped tests/build/replay/stress validations pass.

## Readiness
SYS-2 is ready for SYS-3 tier-contract/ROI scheduling integration, with deterministic macro behavior execution, forced-expand logging, proof/replay hooks, and process-only boundary mutation preserved.
