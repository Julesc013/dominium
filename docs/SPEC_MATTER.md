# Matter System

- **Substances** (`Substance { id, name, density_kg_m3, heat_capacity_J_kgK, melting_point_K, boiling_point_K, emissivity, flags }`) register via `dmatter_register_substance`. Fixed-point numerics only (Q16.16 for densities/heat/emissivity, TempK for temperatures). Flags cover properties like flammable/toxic/radioactive.
- **Mixtures** hold up to `DMIX_MAX_COMPONENTS` entries: parallel arrays of `substance[]` + `frac[]` (`FractionQ4_12` ~0..1), plus aggregate `total_mass_kg`/`total_vol_m3`. Mixtures are data-only structs for fluids/gases; solvers will consume them later.
- Helpers: `dmix_clear`, `dmix_add_mass` (supports add/remove by substance), `dmix_normalise` (rebuilds fractions/volume), `dmix_transfer_fraction` (move a fraction of a mixture between zones/containers). All operate on fixed-size arrays; no dynamic allocation.
- **Materials** (`MaterialType { id, name, base_substance, density_kg_m3, compressive_strength, tensile_strength, thermal_conductivity, flags }`) represent manufactured solids; register via `dmatter_register_material`.
- **Item types** (`ItemType { id, name, material_id, mass_per_unit, vol_per_unit, max_stack, flags }`) describe inventory units, including fluid/gas/machine markers. Register via `dmatter_register_item_type`.
- Registries live in `dmatter.c` as bounded arrays for determinism; lookups: `dmatter_get_substance/material/item_type`. IDs auto-assign if zero on registration.
- Type aliases: `SubstanceId` (u16), `MaterialId` (u32, shared with aggregates), `ItemTypeId` (u32).
