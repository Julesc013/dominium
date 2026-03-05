# Pollution Final Baseline

Status: BASELINE (POLL-3)  
Date: 2026-03-05  
Scope: stress scenario generation, deterministic degradation under RS-5-style budgets, mass-accounting verification under declared proxy bounds, proof/replay integration, and regression locking.

## 1) Stress Results Summary

Deterministic stress harness execution (`tools/pollution/tool_run_poll_stress.py`) completed with bounded execution and logged behavior.

- scenario_id: `scenario.poll.stress.10f98775f90c`
- deterministic_fingerprint: `08b59a80908918368823c686c431033c8ad4c6e34c25694eeac231ae6ffe4091`
- assertions:
  - bounded_execution: `true`
  - deterministic_ordering: `true`
  - no_silent_field_writes: `true`
  - all_events_logged: `true`
- metrics:
  - max_concentration_observed: `147`
  - total_threshold_events: `8`
  - total_compliance_reports: `24`
  - total_compliance_delays: `0`
  - total_measurement_refusals: `0`

Primary stress surfaces:

- `tools/pollution/tool_generate_poll_stress.py`
- `tools/pollution/tool_run_poll_stress.py`
- `src/pollution/dispersion_engine.py`
- `src/pollution/exposure_engine.py`
- `src/pollution/compliance_engine.py`

## 2) Deterministic Degradation Rules

POLL-3 degradation order is deterministic and policy-driven.

1. reduce dispersion update frequency using tick buckets
2. reduce cell coverage deterministically (subset by stable order)
3. reduce exposure evaluation frequency using subject buckets
4. delay low-priority compliance reports
5. refuse non-essential measurements

All degrade actions emit decision/event rows and preserve canonical emission totals.

Primary surfaces:

- `tools/pollution/tool_run_poll_stress.py`
- `src/pollution/dispersion_engine.py`
- `src/pollution/exposure_engine.py`
- `src/pollution/compliance_engine.py`

## 3) Mass Balance Verification

Mass accounting verifier (`tools/pollution/tool_verify_poll_mass_balance.py`) ran against stress output.

- proxy mode: concentration fields treated as proxy (not strict mass state)
- declared bound used: `500` permille
- result: `complete`
- deterministic_fingerprint: `d10831b8fb64c69a78557db105dd8f0d29b2593fa7e2519439d6a1bdfdbcfd31`
- summary:
  - pollutant_count: `4`
  - violation_count: `0`
  - max_residual_abs: `334`
  - max_allowed_residual_abs: `739`

Note: tighter bound (`25` permille) correctly reports violation for proxy concentration mode and is outside declared POLL-3 proxy tolerance envelope.

## 4) Proof and Replay Guarantees

Replay verifier (`tools/pollution/tool_replay_poll_window.py`) confirms stable hash-chain reconstruction.

- result: `complete`
- deterministic_fingerprint: `7f60c06e513f8d7cc1072cdcb6d9c936614671b64438ed9b0a1dc1059a91eadd`

Verified chains:

- `pollution_emission_hash_chain`: `dcb7ff2ed3be0c386fb26b3f0342cac958d3bf4e3a1ec76ed88f0a2bd298ea75`
- `pollution_field_hash_chain`: `82a61c47fd9b044f19ca2d649c66276f18f8e6b0fca57738d018b810330c673e`
- `pollution_exposure_hash_chain`: `5b88d91a40089603c97008b93cd3056c4a6f6c59a42b8cef13761e1d4a9aeedf`
- `pollution_compliance_hash_chain`: `db0e9953ed86526f4baf54a9e5b680292820c3888d5988d73ac83fb0421f8c3a`
- `pollution_degradation_event_hash_chain`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

## 5) Gate Execution

Validation level executed: STRICT governance checks + POLL-3 target suite.

- topology map updated:  
  `py -3 tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`  
  - result: `complete`  
  - deterministic_fingerprint: `e3e9cc0877e4677ce5e5c7e892276e8d886e9a760dff83b5989489115e472d56`

- RepoX STRICT:  
  `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`  
  - status in in-flight run: `refusal` (`INV-WORKTREE-HYGIENE` due uncommitted topology artifacts while phase-final artifacts were pending commit)

- AuditX STRICT:  
  `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`  
  - result: `pass` (`findings=1310`, `promoted_blockers=0`)

- TestX PASS (POLL-3 required suite):  
  `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_poll3_stress_scenario_deterministic,test_poll3_degradation_order_deterministic,test_poll3_mass_balance_within_bounds,test_poll3_proof_hash_chain_stable,test_poll3_replay_window_hash_match`  
  - result: `pass` (`selected_tests=5`)

- stress harness PASS:  
  `py -3 tools/pollution/tool_run_poll_stress.py --seed 7301 --region-count 4 --cells-per-region 36 --subject-count 240 --tick-count 24 --emissions-per-tick 14 --measurements-per-tick 10 --compliance-interval-ticks 4 --include-wind-field --output build/pollution/poll3_final_stress_report.json`  
  - result: `complete`

- strict build gate:  
  `py -3 tools/xstack/run.py strict --repo-root . --cache on`  
  - result: `refusal` due existing repository-global strict-lane blockers outside POLL-3 scope (`compatx`, `registry_compile`, `session_boot`, full-lane `testx`, `packaging.verify`)

## 6) Regression Lock and Readiness

Regression lock established:

- `data/regression/poll_full_baseline.json`
- update tag required: `POLL-REGRESSION-UPDATE`

Readiness for LOGIC-0:

- deterministic stress generation and execution: complete
- bounded degradation policy with logging: complete
- mass accounting verifier with declared proxy bounds: complete
- proof/replay hash-chain verification: complete
- regression baseline lock: complete
- global strict lane: blocked by pre-existing non-POLL global strict findings
