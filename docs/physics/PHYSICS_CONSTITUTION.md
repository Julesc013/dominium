Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Physics Constitution

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-0 constitutional substrate for quantities, invariants, tier contracts, and exception governance.

## 1) Purpose

Freeze a deterministic, auditable physics contract so present and future domains compose through shared quantities, conservation rules, constitutive models, and explicit exception pathways.

This constitution is governance and substrate policy. It does not introduce new solvers or gameplay features.

## 2) Canonical Quantities (Normative)

All authoritative quantities are fixed-point and registry-declared.

### 2.1 Mass

- `quantity.mass` (`dim.mass`)

### 2.2 Motion

- `quantity.momentum_linear` (`dim.momentum`)
- `quantity.momentum_angular` (`dim.angular_momentum`)
- `quantity.force` (`dim.force`)
- `quantity.torque` (`dim.torque`)

### 2.3 Energy

- `quantity.energy_kinetic` (`dim.energy`)
- `quantity.energy_potential` (`dim.energy`)
- `quantity.energy_thermal` (`dim.energy`)
- `quantity.energy_electrical` (`dim.energy`) accounting label
- `quantity.energy_chemical` (`dim.energy`) accounting label
- `quantity.energy_total` (`dim.energy`) ledger aggregate
- `quantity.heat_loss` (`dim.power`) as energy-per-tick loss channel under MAT-1 convention

### 2.4 Entropy / Irreversibility

- `quantity.entropy_index` is a diagnostic scalar tracked with `dim.energy_per_temperature` policy
- entropy is auditable but not globally conserved

### 2.5 Radiation

- `quantity.radiation_dose` uses `dim.specific_energy` policy (energy per mass)

### 2.6 Information (Optional Label)

- `quantity.information_rate` is optional and non-conserved for SIG congestion diagnostics
- if used, it must be registry-declared with explicit dimension policy for the selected profile

## 3) Conservation Rules (Default Realistic Profile)

Default enforcement (`phys.realistic.*` profiles):

- mass is conserved unless an explicit transformation contract declares otherwise
- `quantity.energy_total` is conserved except for declared boundary flux or explicit exception events
- momentum is conserved absent declared external field force under the active tier contract
- entropy is tracked for diagnostics and proof, not as a global hard invariant

## 4) Transformation Rules

- all energy transformations must be declared through `EnergyTransformationRegistry` contract surfaces (PHYS-3 implementation target)
- loss pathways must map to either:
  - `quantity.heat_loss` (preferred/default), or
  - explicit boundary-flux exception events
- silent dissipation/drop is forbidden

## 5) Tier Contracts

### 5.1 Macro

- track conserved quantities and budget-safe aggregates
- no micro force integration requirement

### 5.2 Meso

- execute network solves, constitutive model evaluation, and field sampling
- couple domains only through model outputs/effects/hazards/flow adjustments

### 5.3 Micro (ROI only)

- force/impulse integration may run with EB/MOB/MECH substrates
- must remain budget-governed, deterministic, and replay-safe

## 6) Coupling Discipline

Cross-domain effects are legal only via:

`Field/Flow/State input -> ConstitutiveModel -> {Effects, Hazards, Flow adjustments, Derived quantities}`

Rules:

- no direct cross-domain mutation in domain-local ad hoc code
- no domain-specific bypass of process commit boundaries
- all authoritative mutation remains process-mediated

## 7) Exceptions, Magic, Alternate Physics

`PhysicsProfile` declares:

- `invariants_enforced`
- `invariants_track_only`
- `allowed_exceptions`
- `loss_to_heat_policy_id`
- determinism policy requirements

Any invariant violation or alternate-physics action must emit all of:

- exception artifact (`exception_event`, INFO family `RECORD`)
- ledger exception entry with quantity deltas
- proof/decision log entry with deterministic fingerprint

Silent violations are forbidden.

## 8) Integration Obligations

PHYS constitution integrates with:

- RS-2 ledgers for conservation and exception accounting
- META-MODEL constitutive model pathways for cross-domain coupling
- FIELD sampling as external-force/boundary input pathway
- SAFETY patterns for protection semantics
- CTRL proof bundles / DecisionLog for deterministic replay and audit
- SPEC contracts for standards-compliance constraints

## 9) Non-Goals (PHYS-0)

- no rigid-body solver introduction
- no orbital/relativity implementation
- no wall-clock semantics
- no default-pack dependency for null boot
