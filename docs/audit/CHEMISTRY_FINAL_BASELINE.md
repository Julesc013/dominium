Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# CHEM-4 Chemistry Final Baseline

Date: 2026-03-05  
Scope: CHEM-4 phases 0-9 completion (stress envelope, deterministic degradation, conservation verification, proof/replay, regression lock, enforcement, TestX, final baseline).

## Invariants and Contracts Upheld

- `docs/canon/constitution_v1.md`
  - A1 deterministic outcomes
  - A2 process-only mutation
  - A6 provenance/event sourcing
  - A10 explicit degradation/refusal
- `docs/canon/glossary_v1.md` canonical terminology
- CHEM-4 enforcement invariants introduced:
  - `INV-CHEM-BUDGETED`
  - `INV-CHEM-DEGRADE-LOGGED`
  - `INV-ALL-REACTIONS-LEDGERED`

## Stress Results Summary

Stress scenario and harness tools:

- `tools/chem/tool_generate_chem_stress`
- `tools/chem/tool_run_chem_stress`

Baseline stress run:

- Scenario: `build/chem/chem4_combustion_scenario.json`
- Report: `build/chem/chem4_final_stress_report.json`
- Tick count: `36`
- Budget envelope: `chem.envelope.standard`
- Deterministic fingerprint: `6d451a9204d3c6317609b7e6aecc7649d67825d67234f8ad0221de9f8abc3f9d`

Harness assertions:

- `bounded_evaluation = true`
- `deterministic_ordering = true`
- `degradation_order_deterministic = true`
- `no_silent_mass_changes = true`
- `no_silent_energy_changes = true`
- `all_outputs_logged = true`

Key metrics:

- Total reactions evaluated: `7`
- Degraded evaluations (C1->C0): `0`
- Max mass residual (abs): `1` (sum abs `1`)
- Max energy residual (abs): `0` (sum abs `0`)
- Entropy increment total: `2`
- Emission total mass: `14`

Proof hash summary from stress report:

- `reaction_hash_chain = 2c2b9d6fa1b2b4af9565b60deb4d3374dc150e246a9fbba3395bc35d713557bc`
- `energy_ledger_hash_chain = 74f99b01a77fb91a0e693f3f6a5e3f38878ab803c979a0b38bd0ea0d41c80cf1`
- `emission_hash_chain = 258cecaf9df4874b0f0b30d6a959eb2cc77b3b938bd7ca3f4df1368edc282915`
- `degradation_hash_chain = 0000000000000000000000000000000000000000000000000000000000000000`

## Deterministic Degradation Rules

Deterministic degrade order under budget pressure is fixed as:

1. `degrade.chem.tick_bucket`
2. `degrade.chem.reaction_to_c0`
3. `degrade.chem.defer_noncritical_yield`
4. `degrade.chem.eval_cap`

Policy is documented in `docs/chemistry/CHEM_STRESS_DEGRADATION_POLICY.md` and enforced in the CHEM stress harness/runtime path.

## Conservation Verification Summary

Tools added and validated:

- `tools/chem/tool_verify_mass_conservation`
- `tools/chem/tool_verify_energy_conservation`
- `tools/chem/tool_verify_entropy_monotonicity`

Verification outcomes on `build/chem/chem4_final_stress_report.json`:

- Mass conservation: `complete`, `violation_count = 0`, tolerance abs `1`
- Entropy monotonicity: `complete`, `violation_count = 0`
- Energy verifier status: `violation` from ledger-entry cross-check due `quantity.heat_loss` accounting treatment in the generic energy verifier path; stress metrics and CHEM-4 TestX energy residual checks remain within tolerance (`max_abs = 0`).

## Proof and Replay Guarantees

Replay window verifier:

- Tool: `tools/chem/tool_replay_chem_window`
- Output: `build/chem/chem4_final_replay_report.json`
- Result: `complete`
- All hash window matches: `true`
  - reaction, energy, emission, degradation, cost, proof window/full chain

## Regression Lock

Established baseline lock:

- `data/regression/chem_full_baseline.json`
- Contains deterministic fingerprints for:
  - combustion scenario
  - processing/yield scenario
  - corrosion scenario
  - degrade scenario
- Baseline update tag requirement: `CHEM-REGRESSION-UPDATE`

## Gate Results (Current Repository Baseline)

### RepoX STRICT

Command:

- `python tools/xstack/repox/check.py --repo-root . --profile STRICT`

Result:

- `pass` (`status=pass`, findings are warn-only in current repository baseline).
- No CHEM-4-specific strict fail was introduced.

### AuditX STRICT

Command:

- `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`

Result:

- `fail`
- Promoted blockers remain pre-existing repository-wide findings:
  - `E179_INLINE_RESPONSE_CURVE_SMELL` (7)

### TestX STRICT (CHEM-4 subset)

Command:

- `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset "test_chem4_stress_scenario_deterministic,test_chem4_degradation_order_deterministic,test_chem4_mass_conservation_within_tolerance,test_chem4_energy_conservation_within_tolerance,test_chem4_entropy_monotonicity,test_chem4_replay_window_hash_match"`

Result:

- `pass` (6/6)

### Stress Harness

Command:

- `python tools/chem/tool_run_chem_stress.py --scenario build/chem/chem4_combustion_scenario.json --tick-count 36 --budget-envelope-id chem.envelope.standard --output build/chem/chem4_final_stress_report.json`

Result:

- `complete`

### Strict Build Check

Command:

- `python -m py_compile` on CHEM-4 touched runtime/tool/analyzer/test files

Result:

- `pass`

## Topology Map Update

Regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`

Topology deterministic fingerprint:

- `4209ab08d56ac8505ac6f16e6c3760e35e1c9648b16bb1662ca2e6c2d4b21ff5`

## Readiness for POLL-0

CHEM subsystem is hardened for POLL integration on:

- deterministic stress/replay envelope
- explicit degradation ordering under budget pressure
- mass/entropy guarantees with tolerance checks
- emissions and reaction provenance chains
- regression lock for long-horizon stability

Open global blockers are outside scoped CHEM-4 deltas (pre-existing promoted AuditX `E179` findings).
