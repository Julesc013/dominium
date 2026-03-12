Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Constitutive Model Constitution

Status: CANONICAL
Last Updated: 2026-03-03
Scope: META-MODEL-0 constitutive response governance.

## 1) Purpose

A ConstitutiveModel is the canonical way to encode realism details (response curves, threshold laws, policy-weighted modifiers) without bespoke domain logic.

This contract is governance-first in META-MODEL-0: no runtime semantic changes are introduced yet.

## 2) ConstitutiveModel Contract

A ConstitutiveModel is a deterministic, data-defined mapping:

- `inputs -> outputs`

### 2.1 Allowed input classes

A model may read declared inputs from existing substrates only:

- Field samples (`FIELD`)
- Flow quantities (`ABS FlowSystem`)
- Hazard state (`ABS HazardModel`)
- State machine state (`ABS StateMachine`)
- Spec parameters (`SPEC`)
- Material properties (`MAT`)

### 2.2 Allowed output classes

A model may emit declared outputs through existing substrates only:

- Effect applications (`CTRL` effects)
- Hazard increments (`ABS HazardModel`)
- Flow adjustments (`ABS FlowSystem`)
- Derived quantities (inspection/decision logs)
- Compliance signals (`SPEC` checks)

No new ontology primitives are introduced.

## 3) Tier Support

Each model must declare tier behavior:

- `macro`: coarse aggregate evaluation
- `meso`: network/partition-level evaluation
- `micro`: ROI-only high-detail evaluation

Tier execution must respect RS budgeting and negotiation policies.

## 4) Determinism Contract

ConstitutiveModel evaluation must satisfy canon determinism:

- stable evaluation ordering
- stable reduction ordering
- cacheability by deterministic input-merkle key
- no implicit background mutation

Randomness is forbidden unless explicitly declared by model policy:

- named RNG stream
- deterministic seed derivation rule
- deterministic replay behavior

## 5) Budgeting And Degradation

Each model must declare:

- cost class
- budget units
- allowed deterministic degradation strategy

Permitted degradations:

- lower tier evaluation (`micro -> meso -> macro`) when policy allows
- lower update frequency by deterministic tick buckets

Forbidden degradations:

- silent behavior changes
- non-logged approximation drift

## 6) Governance Rules

- New realism details must be introduced as registered ConstitutiveModel entries.
- Domain code must not embed bespoke response functions unless migration policy explicitly allows a temporary compatibility shim.
- Process-only mutation invariant remains unchanged: model outputs apply through lawful process paths.

## 7) Non-Goals (META-MODEL-0)

- No ELEC/THERM/FLUID/CHEM runtime solver implementation.
- No model evaluator runtime engine yet (planned in META-MODEL-1+).
- No semantic rewrite of existing domain behavior in this phase.
