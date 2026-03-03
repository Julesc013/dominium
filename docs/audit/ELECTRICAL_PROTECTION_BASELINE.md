# Electrical Protection Baseline

Status: BASELINE  
Series: ELEC-2  
Date: 2026-03-03

## Scope

ELEC-2 hardens electrical safety behavior around deterministic faults, protection trips, grounding policy, co-ordination, LOTO, and proof/replay hooks.

Implemented substrate paths:

- `src/electric/fault/fault_engine.py` for deterministic fault state detection.
- `src/electric/protection/protection_engine.py` for deterministic trip planning and co-ordination ordering.
- `tools/xstack/sessionx/process_runtime.py` for process-only orchestration (`process.elec.network_tick`, `process.elec_apply_loto`, `process.elec_remove_loto`).
- `src/control/proof/control_proof_bundle.py` for electrical fault/trip proof hash integration.
- `tools/xstack/repox/check.py` + AuditX analyzers for enforcement.

## Fault Kinds and Detection Rules

Canonical fault classes in ELEC-2:

- `fault.overcurrent`
- `fault.short_circuit`
- `fault.ground_fault`
- `fault.open_circuit`
- hook-only: insulation/under/over voltage classes

Detection behavior (E1 meso):

- Overcurrent from apparent power (`S`) against deterministic thresholds/settings.
- Short/open from channel/device state and connectivity hints.
- Ground fault from deterministic imbalance proxy gated by grounding policy.
- Deterministic ordering by `(graph_id, edge_id)` with bounded evaluation and `budget_outcome`.

Outputs:

- canonical `elec_fault_states`
- `fault_state_hash_chain`
- deterministic safety fault events

## Protection Devices and Coordination

Protection devices remain state-machine + safety-pattern mediated:

- breaker/fuse/relay/gfci/isolator device rows
- threshold settings (`trip_threshold_*`, `gfci_threshold`, `trip_delay_ticks`)
- co-ordination policy tables:
  - `coord.downstream_first`
  - `coord.upstream_first`
  - `coord.strict_table`

Trip orchestration:

- fault -> trip plan -> SAFETY instance (`safety.breaker_trip`) -> flow disconnect action
- deterministic group ordering by `coordination_group_id` and policy sort key
- tie-breaks by `device_id`/fault deterministic keys

Proof/replay additions:

- `trip_event_hash_chain`
- deterministic trip cascade rows (`elec_trip_cascade_rows`)

## LOTO Workflow

LOTO process paths:

- `process.elec_apply_loto`
- `process.elec_remove_loto`

Behavior:

- lockout rows tracked in `safety_lockouts`
- breaker reclose (`closed|reset`) refused when active lockout targets match channel/device
- lock metadata mirrored onto protection device extensions for deterministic inspection/tooling views

## Thermal/Pollution Hooks

Fault-triggered hooks are process-mediated and deterministic:

- apply `effect.temperature_increase_local` on active fault targets
- increment `hazard.elec.insulation_breakdown`
- attach deterministic hook metadata for replay/provenance

No THERM/POLL solver semantics are introduced in ELEC-2.

## Enforcement

RepoX invariants added:

- `INV-ELEC-PROTECTION-THROUGH-SAFETY`
- `INV-NO-ADHOC-FAULT-TRIP`
- `INV-LOTO-STATE_MACHINE-ONLY`

AuditX analyzers added:

- `E187_INLINE_TRIP_SMELL` (`InlineTripSmell`)
- `E188_FAULT_BYPASS_SMELL` (`FaultBypassSmell`)
- `E189_UNLOGGED_TRIP_SMELL` (`UnloggedTripSmell`)

## TestX Coverage (ELEC-2)

Added/verified tests:

1. `test_fault_detection_deterministic`
2. `test_breaker_trip_deterministic`
3. `test_coordination_downstream_first`
4. `test_loto_prevents_reclose`
5. `test_proof_hashes_include_faults`
6. `test_budget_degrade_fault_eval_stable`

## Gate Summary

Execution date: 2026-03-03

- RepoX: `python tools/xstack/repox/check.py --profile FAST`
  - `status=fail` (global pre-existing fail remains):
    - `INV-NO-RANKED-FLAGS` in `tools/signals/tool_run_sig_stress.py`
  - ELEC-2 diegetic channel registry fail removed by surfacing:
    - `ch.diegetic.elec.test_lamp`
    - `ch.diegetic.elec.breaker_panel`
    - `ch.diegetic.elec.ground_fault`
- AuditX: `python tools/auditx/auditx.py scan --repo-root . --changed-only --format both`
  - `result=scan_complete`
  - new analyzers present in run: `E187`, `E188`, `E189`
- TestX: `python tools/xstack/testx/runner.py --profile FAST --cache off --subset ...`
  - `status=pass` for all six ELEC-2 tests listed above
- strict build: `python tools/xstack/run.py strict --repo-root . --cache on`
  - `result=refusal` with pre-existing global pipeline findings outside ELEC-2 scope (CompatX/registry/session/TestX/packaging)
- topology map: `python tools/governance/tool_topology_generate.py --repo-root .`
  - `result=complete`
  - fingerprint: `a2cc2d8a00424f53f2f6c6f3e18b38653634af07ffb5014d090bb4788e99c553`

## Extension Notes

ELEC-3 readiness:

- advanced PF/load response models can remain model-bound without altering protection process paths.
- transformer/selective protection expansion can reuse current co-ordination registry + safety pattern dispatch.

LOGIC integration readiness:

- relay/control policies can bind to existing state machine and process hooks.
- no new mutation path is required; process-only + deterministic proof surfaces are already in place.

