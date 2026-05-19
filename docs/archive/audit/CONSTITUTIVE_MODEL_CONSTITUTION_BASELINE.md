Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Constitutive Model Constitution Baseline

Status: BASELINE
Last Updated: 2026-03-03
Scope: META-MODEL-0 finalization report.

## 1) Constitution Summary

Implemented constitutional artifacts:

- `docs/meta/CONSTITUTIVE_MODEL_CONSTITUTION.md`
- `docs/meta/CONSTITUTIVE_MODEL_CATALOG.md`
- `docs/audit/META_MODEL0_RETRO_AUDIT.md`

Core decisions frozen:

- realism response details are represented as `ConstitutiveModel` definitions (governance contract in META-MODEL-0)
- deterministic inputs/outputs and tier behavior are mandatory
- named RNG streams only when explicitly policy-declared
- budget class and deterministic degradation policy are required model metadata

## 2) Catalog Summary

Initial reserved model categories were documented for future implementation:

- ELEC: `elec.load.phasor`, `elec.line.loss`
- THERM: `therm.conductance`, `therm.phase_change_stub`
- FLUID: `fluid.pump_curve`, `fluid.valve_curve`
- MECH: `mech.plasticity_rate_stub`, `mech.fatigue_rate`
- SIG: `sig.attenuation_model`
- CHEM/POLL: `chem.reaction_rate_stub`, `poll.dispersion_stub`

## 3) Enforcement Hooks

RepoX (warn-phase scaffolding):

- `INV-REALISM-DETAIL-MUST-BE-MODEL`
  - detects inline response-curve style logic in mobility/field/signals/mechanics code paths
  - warns now to support migration planning without hard breaks

AuditX:

- `InlineResponseCurveSmell` (`E179_INLINE_RESPONSE_CURVE_SMELL`)
  - highlights likely bespoke response-curve code requiring migration to model registries

## 4) RWAM And Grammar Integration

Completed integration updates:

- RWAM now declares `META_MODEL` series coverage in machine-readable matrix.
- Action template contract now allows optional `uses_constitutive_model_ids` declarations.
- Information grammar contract now explicitly maps constitutive outputs to `OBSERVATION` / `REPORT` / `RECORD` families.

## 5) Readiness For META-MODEL-1

Ready next-step work:

- schema definitions for constitutive model records/bindings
- deterministic evaluation engine with cache key contract
- migration of inline response formulas to registered model IDs
- hardening RepoX invariant from warn to fail/refusal after migration thresholds are met
