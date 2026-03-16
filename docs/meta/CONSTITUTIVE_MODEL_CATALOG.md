Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Constitutive Model Catalog (Initial)

Status: CANONICAL-SCOPE
Last Updated: 2026-03-03
Scope: META-MODEL-0 naming and planning catalog only.

## 1) Purpose

This catalog reserves stable IDs and scope for constitutive response models that will be implemented in META-MODEL-1+ and domain series (ELEC/THERM/FLUID/CHEM/DOM/SIG/MECH).

No runtime implementation is introduced in this document.

## 2) Initial Model Categories

- `elec.load.phasor` (P/Q/S, power-factor handling)
- `elec.line.loss` (I^2R proxy and heat coupling)
- `therm.conductance`
- `therm.phase_change_stub`
- `fluid.pump_curve`
- `fluid.valve_curve`
- `mech.plasticity_rate_stub`
- `mech.fatigue_rate`
- `sig.attenuation_model`
- `chem.reaction_rate_stub`
- `poll.dispersion_stub`

## 3) Naming Rules

- Domain-prefixed IDs (`domain.model_name`).
- Stable IDs are immutable once released; breaking behavior requires semver migration/refusal path.
- Stubs are explicit (`*_stub`) and must not masquerade as high-fidelity solvers.

## 4) Implementation Contract (Deferred)

Future implementation must provide for each catalog entry:

- declared inputs and outputs
- deterministic evaluation rule
- tier behavior (`macro|meso|micro`)
- budget class and deterministic degrade policy
- replay/proof hash participation

## 5) Non-Goals

- no domain solver implementation
- no registry runtime activation in META-MODEL-0
