Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CHEM-1 Coupling Validation

Status: VALIDATION
Last Updated: 2026-03-05
Scope: CHEM-1 coupling confirmation for THERM and ELEC integration paths.

## Coupling Paths Confirmed

## 1) CHEM -> THERM

Combustion heat coupling now flows through explicit PHYS-3 transform:

- `process.fire_tick`
  - calls `_record_energy_transformation_in_state(...)`
  - `transformation_id = "transform.chemical_to_thermal"`
  - `input_values.quantity.energy_chemical`
  - `output_values.quantity.energy_thermal`
  - `output_values.quantity.heat_loss` (irreversibility split)

Thermal network receives `thermal_heat_input_rows` derived from combustion output; no direct `energy_*` mutation bypass is introduced.

## 2) CHEM -> ELEC (Hook)

Generator hook is explicit and optional:

- enabled only when `generator_target_assembly_id` is present.
- `process.fire_tick` records:
  - `transformation_id = "transform.chemical_to_electrical"`
  - source id bound to generator target assembly.

No generator solver semantics were changed in CHEM-1.

## 3) Process-only Mutation Check

Authoritative mutation remains through process runtime path:

- combustion state update in `process.fire_tick`
- no UI/inspection/tool direct truth mutation
- ledger records emitted through canonical helper path.

## 4) Direct Energy Injection Check

No new direct writes to canonical energy totals were introduced.

All CHEM-1 energy movements are routed through registered transformation IDs and recorded ledger entries.
