Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Energy & Momentum Integrity Report (PATCH-A2)

Status: COMPLETE  
Date: 2026-03-04  
Scope: Ledger discipline, momentum integration checks, coupling compliance, and replay/proof coverage.

## 1) Summary

PATCH-A2 completed a repo-wide consistency sweep for energy/momentum governance and determinism hardening.

- direct energy mutation remained constrained to PHYS ledger runtime/engine pathways
- strict AuditX promotion now blocks `DirectEnergyWriteSmell` in STRICT/FULL
- FLUID dissipation now exposes deterministic `heat_loss_stub` and transform-ready energy rows
- replay verification tools now exist for both energy and momentum hash windows
- new TestX coverage added for static write scans + replay consistency

## 2) Direct-Write Cleanup Counts

- direct energy writes removed: `0` (no non-compliant write sites found; governance preserved)
- direct velocity writes removed: `0` (no out-of-allowlist sites found; constrained rail path remains tracked migration target)
- loss-to-heat bridge additions: `1` domain path (FLUID head-loss -> heat-loss surfacing)

## 3) Transformations Used / Confirmed

- `transform.impulse_to_kinetic`
- `transform.potential_to_kinetic`
- `transform.kinetic_to_thermal`
- `transform.electrical_to_thermal`
- `transform.chemical_to_thermal`
- `transform.phase_change_stub`
- `transform.plastic_deformation_stub`
- `transform.external_irradiance` (boundary-enabled)

## 4) Coupling Fixes / Confirmations

- ELEC -> THERM remains transform-only (`transform.electrical_to_thermal`)
- THERM -> MECH remains model-only (`model.mech.fatigue.default`)
- FLUID -> INT remains leak-process/model coupling (`process.start_leak`, `process.leak_tick`)
- FIELD -> MOB/THERM remains model/policy mediated (`model.phys_gravity_force`, irradiance model, field policy)
- FLUID friction dissipation now exported as deterministic heat-loss/energy-transform candidates (model-derived, no ad hoc solver branch)

## 5) Proof Bundle Coverage

Coverage confirmed for:

- `energy_ledger_hash_chain`
- `boundary_flux_hash_chain`
- `momentum_hash_chain`
- `impulse_event_hash_chain`

Replay/verification tools:

- `tools/physics/tool_verify_energy_conservation`
- `tools/physics/tool_replay_energy_window`
- `tools/physics/tool_replay_momentum_window`

Verification run in PATCH-A2:

- `python tools/physics/tool_replay_energy_window.py --state-path <temporary fixture>` -> complete
- `python tools/physics/tool_replay_momentum_window.py --state-path <temporary fixture>` -> complete
- `python tools/physics/tool_verify_energy_conservation.py --ledger-path <temporary fixture>` -> complete

## 6) Enforcement Upgrades

- RepoX STRICT checks confirmed:
  - `INV-NO-DIRECT-ENERGY-MUTATION`
  - `INV-NO-DIRECT-VELOCITY-MUTATION`
  - `INV-LOSS-MAPPED-TO-HEAT`
- AuditX STRICT promotion added:
  - `E212_DIRECT_ENERGY_WRITE_SMELL` -> `fail`
  - `E208_DIRECT_VELOCITY_WRITE_SMELL` retained as `fail`

## 7) Remaining Migration Track (Non-blocking for PATCH-A2)

- constrained rail micro motion (`step_micro_motion`) remains velocity-first in deterministic process path; flagged in retro audit as migration target for full momentum-native parity.

## 8) Gate Results

- RepoX STRICT: `PASS`  
  `python tools/xstack/repox/check.py --profile STRICT` -> `status=pass`, findings=`17` (warn-only).
- AuditX STRICT: `FAIL (pre-existing global blockers)`  
  `python tools/xstack/auditx/check.py --profile STRICT` -> `status=fail`, promoted blockers=`7` (`E179_INLINE_RESPONSE_CURVE_SMELL` instances outside PATCH-A2 scope).
- TestX PATCH-A2 subset: `PASS`  
  `python tools/xstack/testx/runner.py --profile STRICT --cache off --subset test_no_direct_energy_writes,test_no_direct_velocity_writes,test_energy_ledger_entries_emitted,test_loss_to_heat_transform_present,test_momentum_velocity_derivation,test_replay_energy_hash_match,test_replay_momentum_hash_match` -> `7/7 pass`.
- strict build: `not run in PATCH-A2 sweep` (no canonical strict-build command in this pass).
- topology map: `updated`  
  `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md` -> fingerprint `536937b500bbc86fd10f1c699a67b474d3ab7101388e2ec409e8d40939c27a8f`.

## 9) Readiness

PATCH-A2 baseline is ready for Phase A3 (field discipline sweep), with explicit migration note retained for constrained rail velocity parity.
