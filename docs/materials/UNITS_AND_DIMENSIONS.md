Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Units And Dimensions

## Purpose
Define the canonical deterministic dimensional system for invariant material quantities and ledger accounting.

## Scope Constraints
- No chemistry, thermodynamic, or domain solver implementation in this document.
- No floating nondeterminism for invariant quantities.
- No hardcoded SI-only assumptions in engine runtime behavior.

## A) Dimensional Philosophy
- Every invariant quantity declares a `dimension_id`.
- A dimension is represented by a deterministic integer exponent vector over base dimensions.
- Default base dimensions:
  - `M` mass
  - `L` length
  - `T` time
  - `Q` charge
  - `THETA` temperature
  - `I` ledger balance / currency
- Additional base dimensions are pack-defined and registry-governed.

## B) Invariant Quantities
- Authoritative ledger quantities use fixed-point numeric representation only.
- Dimensional compatibility is validated in two layers:
  - registry compile and schema validation
  - strict runtime checks for process accounting and conversion paths

## C) Derived Units And Dimensions
- Derived dimensions are deterministic compositions of base exponents.
- Baseline examples:
  - `dim.energy = M L^2 T^-2`
  - `dim.force = M L T^-2`
  - `dim.power = M L^2 T^-3`
- Multiplication/division of quantities composes dimension vectors algebraically.
- Addition/subtraction requires exact dimension identity.

## D) No Implicit Units
- Runtime math does not assume a unit unless one is declared in registries.
- Quantities carry explicit `quantity_id`, `dimension_id`, and unit metadata.
- Direct ad-hoc numeric channels without registry-declared quantity type are refused.

## E) Extensibility
- Packs may add:
  - new base dimensions (rare; governance-reviewed)
  - new derived dimensions
  - fictional quantity channels (example: mana)
- RS-2 conservation contracts bind by `quantity_id`, not display symbol.
- Unit labels are presentation metadata; invariants are anchored to quantity and dimension contracts.

## Constitutional Alignment
- A1 Determinism is primary.
- A2 Process-only mutation.
- A6 Provenance is mandatory.
- A9 Pack-driven integration.
