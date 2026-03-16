Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Process Final Baseline

Status: BASELINE (PROC-9)  
Date: 2026-03-07  
Scope: stress, deterministic degradation, proof/replay, compaction safety, and regression lock for the PROC subsystem.

## 1) Stress Results Summary

Deterministic PROC stress scenario and harness completed.

- scenario id: `scenario.proc.stress.c4e1059473a4`
- scenario fingerprint: `a43343a69e0a55b05323f2133cc879f2a5520fa0248ad04e6a6dfb747a05e3d7`
- harness fingerprint: `fca92ab6499eddb36791b0f3ca7a42118aae3ca4da5d36686c38a5d9a2263d90`

Harness assertions:

- deterministic ordering: `true`
- bounded micro execution: `true`
- no silent capsule execution: `true`
- no hidden state drift: `true`
- compaction replay anchor match: `true`

Primary stress metrics:

- micro process runs: `840`
- capsule executions: `1467`
- forced expands: `133`
- invalid capsule usage refusals: `133`
- QC sampled count: `360`
- QC fail rate: `0.0`
- drift warnings: `142`
- drift critical events: `15`
- revalidation success/failure: `7 / 8`
- compiled model cache hit rate: `0.11944444444444445`

## 2) Deterministic Degradation Rules

Enforced degrade order under budget pressure:

1. `degrade.proc.cap_micro_steps`
2. `degrade.proc.prefer_capsules`
3. `degrade.proc.defer_research_inference`
4. `degrade.proc.reduce_low_risk_qc_sampling`
5. `degrade.proc.never_defer_safety_checks`

All degrade decisions are written through deterministic decision/event rows in the harness state.

## 3) Proof and Replay Guarantees

Replay verification (`tools/process/tool_replay_proc_window.py`) completed with zero violations.

Verified chains:

- `process_run_record_hash_chain`: `45c14a579ab95bbe8ea7f4e76bd311935c935df2cdadb70bc28523d7a63c5df5`
- `process_step_record_hash_chain`: `89b1384d0295c699292ab60ae5597fb01ea5ea7fb9bd1c78e8b13576a4755b49`
- `process_quality_hash_chain`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `qc_result_hash_chain`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `process_maturity_hash_chain`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `drift_event_hash_chain`: `2bdb74f30e1f87d8dc45a2af84cffc87d14fd62e05f3c9de4d0667b11f4a9970`
- `capsule_execution_hash_chain`: `fc147134b0942f54cb1c9b35c32a918dfbeb6320f8f792a19e7e687a22838997`
- `compiled_model_hash_chain`: `2f88354d583daed4e77b86211b126980dc005b81edf1197bf091203e8accfad7`
- `candidate_promotion_hash_chain`: `baa7d6280bdb2ad141b1b4a9f6429d05bb71fef88b278ae36133c5c320adf2e0`
- `deployment_hash_chain`: `661e27888b05af3927883c87fc1890bd443c7706e0c876d08fa69fbd31e6415d`

## 4) Compaction Guarantees

Compaction verification (`tools/process/tool_verify_proc_compaction.py`) completed.

- result: `complete`
- marker id: `compaction.marker.d5d4b2c3baf89e97`
- compaction marker chain: `191181d7bdbef7ead1e0252d4717c81543f31e1a39191297ec247591bfebd403`
- pre/post compaction state hash: unchanged (`070ad844a8ee79e10da6f99ce42bed108ed081cefc3d04b7d618ffd171983b3e`)
- replay hash match mode: `current_state`

## 5) Regression Lock

Regression baseline lock file:

- `data/regression/proc_full_baseline.json`
- update tag required: `PROC-REGRESSION-UPDATE`

Included baseline fingerprints:

- stabilized capsule-heavy scenario
- drift/revalidation scenario
- research candidate promotion scenario
- software pipeline scenario
- degradation scenario

## 6) Gate Snapshot

- RepoX STRICT: `refusal`  
  command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`  
  note: blockers are repository-global refusals outside PROC-9 scope (RWAM/action-template/worktree hygiene and existing SYS/runtime governance checks).

- AuditX STRICT: `pass`  
  command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`  
  summary: `findings=2209`, `promoted_blockers=0`.

- TestX PASS (PROC-9 required subset): `pass`  
  command: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_stress_scenario_deterministic_proc9,test_degradation_order_deterministic_proc9,test_compaction_replay_hash_match_proc9,test_capsule_exec_logged_proc9,test_drift_actions_logged_proc9,test_candidate_promotion_requires_replication_proc9,test_cross_platform_hash_match_proc9`

- stress harness PASS: `pass`  
  command: `python tools/process/tool_run_proc_stress.py --scenario-path build/process/proc9_final/scenario.json --tick-count 96 --max-micro-steps-per-tick 96 --max-total-tasks-per-tick 320 --max-research-inference-per-tick 24 --max-qc-checks-per-tick 96 --out build/process/proc9_final/stress_report.json`

- strict build: `refusal`  
  command: `python tools/xstack/run.py strict --repo-root . --cache on`  
  summary: strict lane blocked by repository-wide pre-existing non-PROC issues (`compatx`, `repox`, full-lane `testx`, `packaging.verify`).

- topology map updated: `pass`  
  command: `python tools/governance/tool_topology_generate.py --repo-root .`  
  fingerprint: `fa27670699899709510d41bfb9989c575109db727e9595dc12243cffb5ea1e0d`

## 7) Readiness Checklist for LOGIC-0

- deterministic stress generation and ordering: complete
- deterministic degradation policy with logged decisions: complete
- capsule execution visibility and forced-expand accounting: complete
- proof/replay verification across PROC chains: complete
- compaction safety verification: complete
- regression lock governance (`PROC-REGRESSION-UPDATE`): complete
- repository-wide strict lane: blocked by non-PROC global governance debt
