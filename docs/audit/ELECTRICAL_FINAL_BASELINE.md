Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# ELECTRICAL FINAL BASELINE

Status: COMPLETE (ELEC-5 scope)  
Series: ELEC-5  
Date: 2026-03-03

## Scope Summary

ELEC-5 hardening completed for:

- deterministic cascade envelope
- deterministic budget degradation ordering
- shard boundary enforcement and boundary transfer artifacts
- proof-bundle hash-chain integration
- replay-window verification tools
- regression lock baseline for long-term stability

## Implemented Artifacts

- Retro-audit: `docs/audit/ELEC5_RETRO_AUDIT.md`
- Cascade doctrine: `docs/electric/CASCADE_MODEL.md`
- Shard boundary rules: `docs/electric/SHARD_BOUNDARY_RULES.md`
- Stress tools:
  - `tools/electric/tool_generate_elec_stress_scenario.py`
  - `tools/electric/tool_run_elec_stress.py`
  - `tools/electric/tool_replay_elec_window.py`
- Degradation policy:
  - `src/electric/degradation_policy.py`
  - integrated in `process.elec.network_tick` via `tools/xstack/sessionx/process_runtime.py`
- Proof integration:
  - `src/control/proof/control_proof_bundle.py`
  - `schema/control/control_proof_bundle.schema`
  - `schemas/control_proof_bundle.schema.json`
  - network policy surfaces:
    - `src/net/srz/shard_coordinator.py`
    - `src/net/policies/policy_server_authoritative.py`
- Enforcement:
  - RepoX: `tools/xstack/repox/check.py`
  - AuditX analyzers:
    - `tools/auditx/analyzers/e192_infinite_cascade_smell.py`
    - `tools/auditx/analyzers/e193_unbudgeted_solve_smell.py`
    - `tools/auditx/analyzers/e194_silent_degrade_smell.py`
- TestX coverage:
  - `test_stress_scenario_deterministic`
  - `test_cascade_bounded`
  - `test_degradation_logged`
  - `test_shard_boundary_rules`
  - `test_proof_hash_chain_stable`
  - `test_replay_window_hash_match`

## Stress Results

Baseline scenario:

- scenario file: `build/electric/elec5_stress_scenario.json`
- seed: `5705`
- counts: generators=12, loads=96, storage=12, breakers=24, graphs=2, shards=3
- ticks: `48`

Stress report:

- file: `build/electric/elec5_stress_report.json`
- result: `complete`
- ticks_to_steady_state: `2`
- cascaded_trip_count: `218`
- degraded_solve_count: `0`
- trip_event_count: `10385`
- fault_event_count: `464`
- boundary_transfer_count: `192`

Replay verification:

- file: `build/electric/elec5_replay_window_report.json`
- result: `complete`
- window_hashes_match: `true`
- full_proof_summary_match: `true`

## Determinism + Proof Envelope

Proof chains integrated and emitted:

- `power_flow_hash_chain`
- `fault_state_hash_chain`
- `protection_state_hash_chain`
- `degradation_event_hash_chain`
- `trip_event_hash_chain`

Final baseline lock:

- file: `data/regression/elec_full_baseline.json`
- baseline id: `elec.full.baseline.v1`
- composite anchor: `1fb701878cb6905e7608db69ff4cf106be9d676306e927060bc7caa276ef8c5e`
- required tag to modify: `ELEC-REGRESSION-UPDATE`

## Degradation Contract (Deterministic Order)

Applied policy order remains:

1. reduce E1 solve frequency (stride)
2. downgrade selected networks to E0 (logged)
3. defer non-critical model cost budget
4. refuse low-priority connection requests with refusal code

All degradation decisions are logged with deterministic decision IDs.

## Gate Results

Run date: 2026-03-03

- RepoX: `PASS`  
  Command: `python tools/xstack/repox/check.py --profile FAST`  
  Notes: warnings remain in unrelated/global areas; no failing findings.

- AuditX: `RUN COMPLETE`  
  Command: `python tools/auditx/auditx.py scan --repo-root . --format both`

- ELEC-5 TestX subset: `PASS`  
  Command:  
  `python tools/xstack/testx/runner.py --profile FAST --cache off --subset test_stress_scenario_deterministic,test_cascade_bounded,test_degradation_logged,test_shard_boundary_rules,test_proof_hash_chain_stable,test_replay_window_hash_match`

- strict build: `REFUSAL` (global/pre-existing)  
  Command: `python tools/xstack/run.py strict --repo-root . --cache on`  
  Report: `tools/xstack/out/strict/latest/report.json`  
  Blocking causes were outside ELEC-5 scope (global CompatX/TestX/packaging findings).

- topology map: `UPDATED`  
  Command: `python tools/governance/tool_topology_generate.py --repo-root .`  
  Fingerprint: `800f22ffd74730ff6774397fab93f5cb5c520336023a966cd2ea068ce44fb439`

## Readiness

ELEC subsystem is hardened for deterministic MMO-scale stress/cascade/proof/replay workflows and is ready for:

- LOGIC-0 control/automation integration
- THERM-0 thermal-domain coupling expansion
