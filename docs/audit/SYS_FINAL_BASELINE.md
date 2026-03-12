Status: BASELINE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-8 stress/proof/regression envelope for system collapse/expand at scale.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SYS Final Baseline

## Stress Results Summary
Deterministic SYS-8 regression lock established at `data/regression/sys_full_baseline.json`.

Scenarios (fixed seeds):
- `nested_plant` (`seed=88017`) -> `result=complete`
- `roi_movement` (`seed=88027`) -> `result=complete`
- `forced_expand` (`seed=88037`) -> `result=complete`
- `degradation` (`seed=88047`) -> `result=complete`

Composite anchor:
- `composite_sys_hash_anchor = 0c9eace420fb20ced978703238bb8c00fecff5966d218093ed368ace9e52c446`

Regression lock update control:
- `required_commit_tag = SYS-REGRESSION-UPDATE`

## Degradation Behavior
Deterministic degrade sequence enforced and logged:
1. `degrade.system.expand_cap`
2. `degrade.system.defer_noncritical_expand`
3. `degrade.system.force_macro_failsafe_on_expand_denied`
4. `degrade.system.inspect_refusal_when_expand_denied`
5. `degrade.system.keep_invariant_checks_mandatory`

Harness assertions for each baseline scenario:
- bounded expands per tick
- no silent tier transitions
- invariant preservation across roundtrip
- replay hash stability
- degradation policy logging

## Shard Rules
Shard boundary doctrine added:
- `docs/system/SYS_SHARD_BOUNDARY_RULES.md`

Validated constraints:
- collapsed systems interact across shards only through boundary interfaces
- boundary exchange remains artifactized (flows/signals/field boundary artifacts)
- no silent direct cross-shard tier mutation path

## Proof + Replay Guarantees
Proof surfaces verified by `tools/system/tool_replay_sys_window.py`:
- `system_collapse_expand_hash_chain`
- `macro_output_record_hash_chain`
- `forced_expand_event_hash_chain`
- `certification_hash_chain`
- `system_health_hash_chain`

Runtime aliases and deterministic hashing are aligned with replay ordering.

## Gate Snapshot
- RepoX STRICT: PASS (`status=pass`; warnings only)
- AuditX STRICT: PASS (`status=pass`; `promoted_blockers=0`)
- TestX (SYS-8 required subset): PASS
  - `test_stress_scenario_deterministic_sys8`
  - `test_invariant_preserved_roundtrip_sys8`
  - `test_expand_cap_enforced_sys8`
  - `test_proof_hash_chain_stable_sys8`
  - `test_replay_window_hash_match_sys8`
- Stress harness PASS: `build/system/sys8_degradation_report_gate.json` (`result=complete`)
- strict build: REFUSAL in repository-wide strict lane due pre-existing non-SYS8 blockers (CompatX/pack/session/TestX/securex/packaging); no SYS-8-specific canon regression surfaced
- topology map updated: PASS (`docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md`)

## Readiness Checklist for LOGIC-0
- deterministic stress generation and execution: complete
- deterministic degrade ordering with DecisionLog traces: complete
- shard boundary doctrine + validation hooks: complete
- unified SYS replay/hash verification: complete
- regression lock with update-tag governance: complete
- SYS-8 enforcement and TestX coverage: complete
