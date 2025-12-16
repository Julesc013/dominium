/*
FILE: include/domino/dmatter.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dmatter
RESPONSIBILITY: Defines the public contract for `dmatter` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DMATTER_H
#define DOMINO_DMATTER_H

#include "dnumeric.h"
#include "daggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Substance registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint16_t SubstanceId;
#ifndef DOMINO_MATERIAL_ID_TYPEDEF
#define DOMINO_MATERIAL_ID_TYPEDEF
/* Purpose: Material type registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t MaterialId;
#endif
/* Purpose: Item type registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t ItemTypeId;

/* Purpose: Substance/material properties used by atmosphere and thermal systems (POD).
 *
 * Ownership:
 * - `name` is a borrowed, NUL-terminated string; registries copy the record as implemented.
 */
typedef struct {
    SubstanceId id;
    const char *name;
    Q16_16      density_kg_m3;
    Q16_16      heat_capacity_J_kgK;
    TempK       melting_point_K;
    TempK       boiling_point_K;
    Q16_16      emissivity;
    U32         flags;   /* flammable, toxic, radioactive, etc. */
} Substance;

/* Purpose: Maximum number of distinct component substances tracked in a `Mixture`. */
#define DMIX_MAX_COMPONENTS 8

/* Purpose: Multi-component mixture for gases/fluids (POD).
 *
 * Invariants:
 * - `count` is the number of valid entries in `substance[]`/`frac[]` (0..DMIX_MAX_COMPONENTS).
 * - `frac[]` entries are approximate fractions in Q4.12 (0..1) and are intended to sum to ~1.
 */
typedef struct {
    U8          count;
    SubstanceId substance[DMIX_MAX_COMPONENTS];
    FractionQ4_12 frac[DMIX_MAX_COMPONENTS]; /* approx 0..1, sum ~1 */
    MassKg      total_mass_kg;
    VolM3       total_vol_m3;
} Mixture;

/* Purpose: Material type definition for structural/items systems (POD). */
typedef struct {
    MaterialId  id;
    const char *name;
    SubstanceId base_substance;
    Q16_16      density_kg_m3;
    Q16_16      compressive_strength;
    Q16_16      tensile_strength;
    Q16_16      thermal_conductivity;
    U32         flags; /* structural, hull-grade, etc. */
} MaterialType;

/* Purpose: Item type definition for inventory/stacking and material binding (POD). */
typedef struct {
    ItemTypeId  id;
    const char *name;
    MaterialId  material_id;   /* 0 if not a simple material item */
    MassKg      mass_per_unit;
    VolM3       vol_per_unit;
    U32         max_stack;
    U32         flags; /* fluid, gas, machine, etc. */
} ItemType;

/* Registry API */
/* Registers a substance definition.
 *
 * Purpose: Add a substance record to the registry.
 *
 * Returns:
 *   - Non-zero SubstanceId on success; 0 on failure (invalid input or capacity limit).
 */
SubstanceId  dmatter_register_substance(const Substance *def);

/* Registers a material type definition.
 *
 * Purpose: Add a material type record to the registry.
 *
 * Returns:
 *   - Non-zero MaterialId on success; 0 on failure (invalid input or capacity limit).
 */
MaterialId   dmatter_register_material(const MaterialType *def);

/* Registers an item type definition.
 *
 * Purpose: Add an item type record to the registry.
 *
 * Returns:
 *   - Non-zero ItemTypeId on success; 0 on failure (invalid input or capacity limit).
 */
ItemTypeId   dmatter_register_item_type(const ItemType *def);

/* Looks up a substance definition by id (read-only).
 *
 * Purpose: Retrieve a previously registered substance record.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid.
 */
const Substance    *dmatter_get_substance(SubstanceId id);

/* Looks up a material type definition by id (read-only).
 *
 * Purpose: Retrieve a previously registered material type record.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid.
 */
const MaterialType *dmatter_get_material(MaterialId id);

/* Looks up an item type definition by id (read-only).
 *
 * Purpose: Retrieve a previously registered item type record.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid.
 */
const ItemType     *dmatter_get_item_type(ItemTypeId id);

/* Mixture helpers */
/* Clears a mixture to the empty state. Accepts NULL. */
void    dmix_clear(Mixture *mix);

/* Adds/removes mass of a component substance and re-normalises the mixture.
 *
 * Purpose: Adjust component mass totals and update derived fraction/volume fields.
 *
 * Parameters:
 *   - mass_delta_kg: Signed delta; negative values remove mass.
 *
 * Returns:
 *   - true on success; false on invalid input, component underflow, or capacity limit.
 */
bool    dmix_add_mass(Mixture *mix, SubstanceId s, MassKg mass_delta_kg);

/* Recomputes mixture fractions/volume from the current mass totals.
 *
 * Purpose: Re-normalize a mixture after direct edits to mass fields.
 *
 * Returns:
 *   - true on success; false if `mix` is NULL.
 */
bool    dmix_normalise(Mixture *mix);

/* Transfers a fraction of `from` into `to`.
 *
 * Purpose: Move a fraction of mixture mass/volume into another mixture.
 *
 * Parameters:
 *   - fraction_0_1: Q16.16 in [0,1]; values outside range are clamped.
 *
 * Returns:
 *   - true on success; false on invalid input or destination capacity overflow.
 */
bool    dmix_transfer_fraction(Mixture *from, Mixture *to, Q16_16 fraction_0_1);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DMATTER_H */
