Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FLUID Final Baseline

Status: BASELINE
Last Updated: 2026-03-04
Scope: FLUID-3 stress/proof/regression hardening envelope.

## 1) Stress Results Summary

Reference lock: `data/regression/fluid_full_baseline.json`

- Baseline ID: `fluid.full.baseline.v1`
- Composite anchor: `ae01864cc74146820ed86666b45965337f5ea732fabc07cef4ab4ef80d29c32a`
- Baseline fingerprint: `6c51a5a536316db122e48a7465bbc32c51275ceefdb3d5546beefb181af0e823`

Scenario snapshots:

- Normal flow snapshot:
  - `max_head_observed=903`
  - `total_relief_events=38`
  - `total_burst_events=77`
- Overpressure relief snapshot:
  - `max_head_observed=456`
  - `total_relief_events=45`
  - `total_burst_events=0`
- Burst/leak cascade snapshot:
  - `max_head_observed=755`
  - `total_relief_events=43`
  - `total_burst_events=144`
  - `total_active_leak_count=57`
- Downgrade snapshot:
  - `total_downgraded_networks=60`
  - `degradation_row_count=150`

## 2) Deterministic Degradation Rules

Applied deterministic order:

1. `degrade.fluid.tick_bucket`
2. `degrade.fluid.subgraph_f0_budget`
3. `degrade.fluid.defer_noncritical_models`
4. `degrade.fluid.leak_eval_cap`

Enforcement status:

- Stress harness records degradation rows with deterministic `step_order`.
- RepoX rule coverage added for budget/degrade discipline.
- AuditX analyzer coverage added for unbudgeted solve and leak-loop/silent-leak smells.

## 3) Proof and Replay Guarantees

Proof hash-chain surfaces:

- `fluid_flow_hash_chain`
- `relief_event_hash_chain`
- `leak_hash_chain`
- `burst_hash_chain`
- `proof_tick_hash_chain`

Replay verification:

- Window proof chain expected/observed match:
  - `dcd52646019b42f0e7d09892a58425ffb17ddc3b18cfe473c9121be6c3d338bb`
  - `dcd52646019b42f0e7d09892a58425ffb17ddc3b18cfe473c9121be6c3d338bb`
- Replay assertions in lock:
  - `proof_window_match=true`
  - `head_window_match=true`
  - `event_window_match=true`
  - `degradation_window_match=true`
  - `full_proof_summary_match=true`

## 4) Regression Lock

Committed lock:

- `data/regression/fluid_full_baseline.json`

Update policy:

- Required tag: `FLUID-REGRESSION-UPDATE`
- Baseline update requires deterministic stress + replay rerun.

## 5) Readiness for CHEM-0

FLUID now has:

- deterministic stress scenario generation,
- bounded/degrading large-network solve envelope,
- explicit failure logging assertions,
- replay-window equivalence checks,
- regression lock for future drift detection.

This baseline is ready for CHEM-0 coupling work without changing FLUID core semantics.

## 6) Gate Execution Snapshot (2026-03-04)

- RepoX STRICT:
  - Command: `python tools/xstack/repox/check.py --profile STRICT`
  - Result: `pass` (warnings only, no blocking findings)
- AuditX STRICT-equivalent scan:
  - Command: `python tools/auditx/auditx.py scan --repo-root . --output-root build/fluid/auditx --format both`
  - Result: `scan_complete`
  - Findings: `2106` (workspace-global, includes pre-existing non-FLUID findings; cache mode `full_reuse`)
- TestX STRICT (FLUID-3 target subset):
  - Command: `python tools/xstack/testx/runner.py --profile STRICT --cache off --subset test_fluid_stress_scenario_deterministic,test_fluid_degradation_order_deterministic,test_fluid_proof_hash_chain_stable,test_fluid_replay_window_hash_match,test_mass_conservation_in_profile`
  - Result: `pass` (`selected_tests=5`)
- Strict build lane:
  - Command: `python scripts/dev/gate.py strict`
  - Result: `failed` with primary class `STRUCTURAL` (pre-existing lane-level baseline issue outside FLUID-3 scope)
- Topology map:
  - Command: `python tools/governance/tool_topology_generate.py`
  - Result: `complete`
  - Fingerprint: `2f8d5798f3bb84886d1b74f9fd35634da6c03f4db68c7ee65eb3715f31914f1a`
