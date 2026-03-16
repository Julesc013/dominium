Status: CANONICAL
Last Reviewed: 2026-03-06
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: SYS-8 shard-boundary rules for collapsed/expanded systems.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# SYS Shard Boundary Rules

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic shard-boundary constraints for system collapse/expand behavior so SYS scaling does not bypass interface, invariant, or proof contracts.

## Rule Set
1. Collapsed systems may span shard topology only through declared boundary interfaces.
2. Boundary exchange across shards must use artifactized channels:
- flow exchanges (`process.flow_adjust`/flow artifacts)
- signal exchanges (declared signal channels)
- field-boundary exchanges where applicable (field boundary artifacts)
3. Direct cross-shard expand/collapse triggers are forbidden.
4. Cross-shard fidelity transition requests must arrive as boundary requests and be routed through CTRL + `process.system_roi_tick`.
5. Boundary invariant checks are mandatory regardless of shard placement and are never skipped by budget degradation.

## Deterministic Validation Expectations
- Transition ordering remains deterministic (`priority_class` then `system_id`).
- Expand/collapse decisions are logged in `control_decision_log`.
- Tier transition events are logged in `system_tier_change_event_rows`.
- Combined collapse/expand proof chain remains stable (`collapse_expand_event_hash_chain` / `system_collapse_expand_hash_chain`).

## Failure/Refusal Semantics
When shard-boundary requirements are not satisfied:
- Transition request is denied with explicit refusal reason.
- No silent fallback to direct state mutation is permitted.
- Explain pathway must remain available through system forensics contracts.

## Validation Surfaces
- Stress harness: `tools/system/tool_run_sys_stress.py`
- Replay verifier: `tools/system/tool_replay_sys_window.py`
- Invariants:
  - `INV-SYS-INVARIANTS-ALWAYS-CHECKED`
  - `INV-NO-SILENT-TIER-TRANSITION`
  - `INV-SYS-BUDGETED`
- AuditX smells:
  - `UnboundedExpandSmell`
  - `SilentCollapseSmell`
  - `InvariantCheckSkippedSmell`
