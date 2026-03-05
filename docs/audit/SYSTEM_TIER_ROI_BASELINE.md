Status: CANONICAL
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-3 tier/ROI baseline.

# System Tier + ROI Baseline

## Scope
SYS-3 integrates Systems into deterministic tier scheduling (`micro|meso|macro`) with ROI-driven desired fidelity, CTRL budget arbitration, explicit transition logging, and invariant-preserving collapse/expand process usage.

## Tier Policy Summary
- Supported system modes:
  - `tier.micro` (full internal graph)
  - `tier.meso` (optional lowered-fidelity internal networks)
  - `tier.macro` (MacroCapsule)
- Deterministic degradation order is declared per `tier_contract` and applied as `micro -> meso -> macro`.
- Upward fidelity transitions are explicit expands and never silent.

## ROI Scheduler Behavior
- Process: `process.system_roi_tick`.
- Enumeration order: `system_id` ascending.
- Desired tier rules:
  - within ROI, inspection, hazard, or explicit fidelity request => `micro`
  - otherwise => `macro`
- Transition execution is budgeted and deterministic:
  - `max_expands_per_tick`
  - `max_collapses_per_tick`
  - priority ordering (`inspection`, `hazard`, `roi`, `background`) then `system_id`.
- Every decision (approve/deny/no-op) writes DecisionLog rows.

## Transition Guarantees
- Collapse path (`process.system_collapse`) enforces:
  - unresolved hazard refusal
  - open scheduled internal task refusal
  - boundary invariant validation before capsule replacement.
- Expand path (`process.system_expand`) enforces:
  - state-vector/provenance-anchor validation
  - interface-signature consistency validation.
- Refusals emit explain artifacts (`explain.system_tier_transition_refusal`).

## Proof + Replay
- Hash chains extended:
  - `system_tier_change_hash_chain`
  - `collapse_expand_event_hash_chain`
- Replay verifier:
  - `tools/system/tool_replay_tier_transitions`

## Validation Snapshot (2026-03-05)
- RepoX STRICT: PASS
- AuditX STRICT: PASS
- TestX SYS-3 subset: PASS
  - `test_roi_expand_on_interest`
  - `test_macro_outside_roi`
  - `test_transition_deterministic`
  - `test_refusal_on_invalid_transition`
  - `test_cross_platform_tier_hash_match`
- Stress harness (SYS-3 dedicated deterministic ROI movement run): PASS
  - 1024 systems, 24 ticks
  - expand cap respected (`max_expand_per_tick=64`)
  - collapse cap respected (`max_collapse_per_tick=96`)
  - deterministic digest stable across equivalent runs.
- Strict build: PASS
- Topology map update: PASS

## Readiness
SYS-3 is ready for SYS-4 template-library integration with deterministic tier transitions, logged ROI arbitration, control-plane budget mediation, replay-safe proofs, and invariant-safe collapse/expand enforcement.
