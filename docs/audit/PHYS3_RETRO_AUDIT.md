# PHYS-3 Retro Consistency Audit

Status: AUDIT
Last Updated: 2026-03-04
Scope: PHYS-3 energy ledger preflight over existing PHYS/ELEC/THERM runtime pathways.

## 1) Existing Loss / Energy-like Channels

Observed canonical and transitional channels:

- Canonical quantities already registered:
  - `quantity.energy_kinetic`
  - `quantity.energy_potential`
  - `quantity.energy_thermal`
  - `quantity.energy_electrical`
  - `quantity.energy_chemical`
  - `quantity.energy_total`
  - `quantity.heat_loss`
- Transitional active runtime channels remain in use:
  - `quantity.thermal.heat_loss_stub`
  - `heat_loss_stub` fields in ELEC edge status rows

Primary runtime sites:

- `src/electric/power_network_engine.py` (line-loss and device-loss outputs)
- `src/thermal/network/thermal_network_engine.py` (thermal loss/heat flow stubs)
- `tools/xstack/sessionx/process_runtime.py` (kinetic observation artifacts, thermal fire heat-input rows)

## 2) Electrical Energy Proxy Audit

Current electrical subsystem behavior:

- ELEC computes deterministic active/reactive/apparent flow components.
- Dissipation is surfaced as `heat_loss_stub` and related model-derived quantities.
- Dissipation is auditable but not yet represented as a canonical PHYS-3 transformation ledger entry.

Migration requirement:

- map electrical dissipation to a registered PHYS-3 transformation (`transform.electrical_to_thermal`)
- retain existing `heat_loss_stub` surfaces for compatibility while adding canonical ledger records

## 3) Kinetic Energy Derivation Audit

Current momentum integration behavior:

- PHYS-1 writes momentum through `process.apply_force` / `process.apply_impulse`.
- Kinetic energy is derived and emitted as `artifact.measurement` (`quantity.energy_kinetic`).
- No canonical PHYS-3 energy ledger entry currently records these kinetic deltas.

Migration requirement:

- preserve existing observation emission
- add deterministic energy-ledger entries for momentum-driven kinetic changes

## 4) Phase-change / Thermal Assumption Audit

Current thermal behavior:

- fire/combustion stubs emit `thermal_heat_input_rows` and hazard/safety records.
- phase/cure state transitions are process-governed and deterministic.
- latent heat and combustion energy are not yet normalized through a PHYS-3 transformation registry.

Migration requirement:

- record combustion/thermal input paths via registered transforms (initially stub-level)
- preserve existing THERM semantics and event ordering

## 5) Energy Total Mutation Audit

Direct writes to canonical `quantity.energy_total` in domain runtime were not found in scan.

Gap:

- explicit aggregate channel updates are not centrally emitted as PHYS-3 ledger entries yet.

Migration:

- introduce dedicated energy ledger entry substrate and hash chains
- route boundary-energy changes through explicit `boundary_flux_event`

## 6) Inline Conversion / Deprecation Notes

Inline conversion patterns identified:

- local conversion from line/load losses to `heat_loss_stub`
- local heat emission stubs in fire-tick path

Deprecation map (PHYS-3 transitional):

- `quantity.thermal.heat_loss_stub`
  - Status: transitional allowed
  - Canonical target: `quantity.heat_loss` + PHYS-3 energy ledger entry
- `heat_loss_stub` row fields
  - Status: transitional allowed for existing UIs/inspection
  - Canonical target: deterministic transform+ledger rows with compatibility mirror

## 7) Direct Cross-domain Mutation Check

No new direct cross-domain mutation pathway is introduced by PHYS-3 planning.

Required coupling discipline remains:

`Domain/Field/Flow input -> ConstitutiveModel -> Process mutation -> Ledger/Artifact`

## 8) Implicit Magic / Debug Bypass Check

No new silent magic injection path identified in current PHYS/ELEC/THERM process handlers.

Existing exception pathways (`exception_event`) are present and must remain mandatory for non-conserving profiles.
