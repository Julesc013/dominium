Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CHEM-3 Chemical Degradation Baseline

Date: 2026-03-05  
Scope: CHEM-3 phases 11-12 completion (TestX coverage, gate validation, final baseline report).

## Invariants and Contracts Upheld

- `docs/canon/constitution_v1.md`:
  - A1 determinism
  - A2 process-only mutation
  - A6 provenance/event logging
- `docs/canon/glossary_v1.md` terminology discipline
- CHEM-3 enforcement invariants:
  - `INV-DEGRADATION-MODEL-ONLY`
  - `INV-NO-ADHOC-PIPE-RESTRICTION`
  - `INV-COUPLING-CONTRACT-DECLARED`

## Degradation Model Baseline

Degradation kinds (registry-driven):

- `degr.corrosion`
- `degr.fouling`
- `degr.scaling`

Profiles (registry-driven):

- `profile.pipe_steel_basic`
- `profile.heat_exchanger_basic`
- `profile.tank_basic`

Constitutive model bindings used by `process.degradation_tick`:

- `model.chem_corrosion_rate.default`
- `model.chem_fouling_rate.default`
- `model.chem_scaling_rate.default`

## Coupling Effects

Cross-domain effects remain model-driven and deterministic:

- FLUID:
  - `effect.pipe_capacity_reduction`
  - `effect.pipe_loss_increase`
- THERM:
  - `effect.conductance_reduction`
- MECH:
  - `effect.strength_reduction`
- ELEC hook:
  - `effect.insulation_breakdown_risk`

No direct cross-domain mutation path was introduced in CHEM-3 TestX coverage updates.

## Maintenance Actions

Maintenance process intents validated in runtime and tests:

- `process.clean_heat_exchanger`
- `process.flush_pipe`
- `process.apply_coating`
- `process.replace_section`

Maintenance resets are logged via degradation reset events and `artifact.record.chem_degradation_reset` artifacts.

## TestX Coverage Added (CHEM-3)

- `test_corrosion_increments_deterministic`
- `test_fouling_reduces_conductance`
- `test_scaling_reduces_pipe_capacity`
- `test_maintenance_resets_levels_logged`
- `test_cross_platform_hash_match_degradation`

Run:

- `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_corrosion_increments_deterministic,test_fouling_reduces_conductance,test_scaling_reduces_pipe_capacity,test_maintenance_resets_levels_logged,test_cross_platform_hash_match_degradation`

Result:

- `pass` (5/5)

## Proof / Replay and Stress Evidence

Deterministic replay verifier:

- `python tools/chem/tool_replay_degradation_window.py --state-path build/chem/degradation_state.json --expected-state-path build/chem/degradation_state_expected.json`
- Result: `complete` (no violations)

Deterministic stress-style CHEM-3 run (scripted fixture):

- 50 targets x 6 ticks via `process.degradation_tick`
- Stable chains across equivalent runs:
  - `degradation_hash_chain = 36f1a4285bd5ef8072bd7a5cd1fe8c94536843c06072114a1b2773568d7631d8`
  - `degradation_event_hash_chain = 280965b4e4e77b0b110291d29782cda7de6bab087b8caf7332598b1cc39370ec`

## Gate Results (Current Repository Baseline)

### RepoX STRICT

Command:

- `python tools/xstack/repox/check.py --repo-root . --profile STRICT`

Result:

- `refusal` while report/topology artifacts were still uncommitted:
  - `INV-WORKTREE-HYGIENE`
- No CHEM-3-specific strict blocker was reported in this run.

### AuditX STRICT

Command:

- `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`

Result:

- `fail`
- Promoted blockers are pre-existing global findings:
  - `E179_INLINE_RESPONSE_CURVE_SMELL` (7)

### TestX STRICT (CHEM-3 subset)

Result:

- `pass` (5/5)

### Strict Build Check

Command:

- `python -m py_compile` on CHEM-3 touched runtime/model/replay/test files

Result:

- `pass`

## Topology Map Update

Regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`

Topology fingerprint:

- `8e7117c5db5791ed91392118ba8c039ac56d953e6456d14f30b260a1ecb02875`

## Readiness

CHEM-3 baseline is ready for:

- CHEM-4 stress envelope expansion
- POLL-0 pollutant simulation consumption of CHEM emission/degradation artifacts

Remaining strict-gate blockers are repository-wide and outside the scoped CHEM-3 delta.
