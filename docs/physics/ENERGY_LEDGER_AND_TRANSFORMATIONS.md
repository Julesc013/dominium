# Energy Ledger and Transformations

Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-3 unified energy accounting contract.

## 1) Purpose

Define a deterministic, auditable substrate where all authoritative energy form changes are represented as explicit registered transformations and ledger records.

This doctrine standardizes energy accounting across ELEC, THERM, PHYS micro momentum, and future CHEM/FLUID domains.

## 2) Canonical Energy Forms

Canonical PHYS energy channels:

- `quantity.energy_kinetic`
- `quantity.energy_potential`
- `quantity.energy_thermal`
- `quantity.energy_electrical` (accounting label)
- `quantity.energy_chemical` (accounting label)
- `quantity.energy_total` (aggregate invariant)

Transitional compatibility channel:

- `quantity.thermal.heat_loss_stub` may remain as compatibility mirror but does not replace PHYS-3 ledger accounting.

## 3) Transformation Contract

Every authoritative energy transform must declare:

- `transformation_id`
- input quantity map
- output quantity map

and must reference a row in `energy_transformation_registry`.

Required transformation behavior:

- produce deterministic `energy_ledger_entry`
- include deterministic fingerprint
- preserve ordering stability (`transformation_id`, then `source_id`)

## 4) Conservation Rule

Default realistic profiles enforce energy conservation on each transformation:

`sum(input_values) == sum(output_values)`

Allowed deviations only when one of the following is emitted explicitly:

- `boundary_flux_event`
- `exception_event` (profile-permitted)

Silent creation or destruction of energy is forbidden.

## 5) Boundary Flux Rule

External energy interactions (for example irradiance, scripted injection, boundary export) must:

- emit `boundary_flux_event` (`RECORD`)
- include direction (`in|out`), reason code, deterministic fingerprint
- update aggregate energy accounting through the ledger path

## 6) Ledger Record Contract

Each transform emits an `energy_ledger_entry` with:

- deterministic `entry_id`
- tick
- source identifier
- input/output value maps
- `energy_total_delta`
- deterministic fingerprint

Ledger entries are never optional for authoritative transforms.

## 7) Tier Contracts

### Macro

- ledger/accounting only
- no force-integration requirement

### Meso

- network/domain transforms emitted by constitutive model pathways
- ledger required for each authoritative conversion

### Micro (ROI)

- force/impulse integration updates momentum and derived kinetic energy
- kinetic deltas must be represented in energy ledger records

## 8) Coupling Discipline

Energy coupling across domains must remain model/process mediated:

`Field/Flow/State -> ConstitutiveModel -> Process mutation -> Energy ledger entry`

Direct cross-domain energy mutation in ad hoc domain code is forbidden.

## 9) Proof and Replay Requirements

Energy ledger integration must expose deterministic witness chains:

- `energy_ledger_hash_chain`
- `boundary_flux_hash_chain`

Replay windows must reproduce identical ordered entries and hash chains for equivalent inputs.

## 10) Non-goals (PHYS-3)

- no advanced thermodynamic solver introduction
- no wall-clock semantics
- no nondeterministic accounting shortcuts
- no bypass of process-only mutation invariant
