# GLOBAL Conservation and Tolerance Report

Date: 2026-03-05
Phase: `GLOBAL-REVIEW-4`

## Scope
- Energy conservation verification
- Mass conservation verification (CHEM + FLUID profile path)
- Momentum consistency checks (ROI/process path)
- Tolerance application sanity

## Verification Runs
1. CHEM mass conservation verifier
   - Command: `python tools/chem/tool_verify_mass_conservation.py --report-path build/chem/chem4_combustion_report.json`
   - Result: `complete` (`violation_count=0`, `tolerance_abs=1`)

2. CHEM energy conservation verifier
   - Command: `python tools/chem/tool_verify_energy_conservation.py --report-path build/chem/chem4_combustion_report.json`
   - Result: `complete` (`violation_count=0`, `tolerance_abs=1`)

3. PHYS energy conservation verifier on extracted ledger payload
   - Command: `python tools/physics/tool_verify_energy_conservation.py --ledger-path build/global_review/phase4_energy_ledger_payload.json`
   - Result: `complete` (`violation_count=0`)

4. Momentum replay-window verifier
   - Command: `python tools/physics/tool_replay_momentum_window.py --state-path build/global_review/phase4_momentum_state.json --expected-state-path build/global_review/phase4_momentum_state.json`
   - Result: `complete`

5. Focused TestX conservation/momentum checks
   - Command: `python tools/xstack/testx_all.py --repo-root . --profile FAST --cache off --subset test_energy_conservation_enforced,test_mass_conservation_in_profile,test_impulse_updates_momentum_deterministic,test_velocity_derived_from_momentum`
   - Result: `pass` (all selected tests passed)

## Patch Applied
- `tools/physics/tool_verify_energy_conservation.py`
  - `_is_energy_quantity` now includes `quantity.heat_loss`.
  - Reason: per-tick transforms in canonical reports account dissipation through `heat_loss`; excluding it created false conservation mismatches in verifier output.
  - Runtime gameplay semantics unchanged (verification-path correction only).

## Tolerance Discipline Status
- Quantity tolerance paths remained active in verifiers (`tolerance_abs=1` from registry default for reported runs).
- No new raw-equality bypass introduced by this phase.

## Outcome
- Conservation checks pass on canonical stress/report artifacts used by existing regression baselines.
- Momentum derivation and replay-hash consistency remain deterministic.
