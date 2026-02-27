Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Material Taxonomy

## Purpose
Define canonical, deterministic, pack-driven material taxonomy and composition contracts for MAT-2.

## Scope Constraints
- No reaction kinetics.
- No thermodynamic solver behavior.
- No particle-physics simulation.
- No hardcoded periodic table behavior in runtime logic.

## A) Material Ontology Layers
1. `Element`
   - atomic number (optional for fictional elements)
   - molar mass (fixed-point)
   - optional isotope metadata
2. `Compound`
   - explicit stoichiometric combination of elements
3. `Mixture`
   - weighted combination of compounds/materials by mass fraction
4. `Material Class`
   - structural/functional material definition referencing element/compound/mixture bases
5. `Fuel Class`
   - material class with declared energy-conversion potential (`specific_energy`)

## B) Composition Philosophy
- Composition is explicit, not inferred.
- Composition must remain dimensionally consistent with declared properties.
- Fractions are expressed in deterministic fixed-point mass fractions by default.
- Composition declarations do not imply reaction behavior.

## C) Conservation Integration
- Composition must interoperate with RS-2 channels:
  - `quantity.mass_energy_total`
  - `quantity.mass`
  - `quantity.energy`
- Ledger stock accounting uses material mass channels.
- Energy content is a material property and only affects ledgers when a declared process emits a conversion.

## D) Extensibility
- Packs/mods may:
  - add real or fictional elements
  - add compounds, mixtures, and material classes
  - provide material property overrides
- Engine code does not embed a hardcoded periodic table.
- Canonical conservation contracts bind by `quantity_id`, not display naming.

## Constitutional Alignment
- A1 Determinism is primary.
- A2 Process-only mutation.
- A6 Provenance is mandatory.
- A9 Pack-driven integration.
