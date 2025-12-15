#ifndef DOMINO_DMATTER_H
#define DOMINO_DMATTER_H

#include "dnumeric.h"
#include "daggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint16_t SubstanceId;
#ifndef DOMINO_MATERIAL_ID_TYPEDEF
#define DOMINO_MATERIAL_ID_TYPEDEF
typedef uint32_t MaterialId;
#endif
typedef uint32_t ItemTypeId;

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

#define DMIX_MAX_COMPONENTS 8

typedef struct {
    U8          count;
    SubstanceId substance[DMIX_MAX_COMPONENTS];
    FractionQ4_12 frac[DMIX_MAX_COMPONENTS]; /* approx 0..1, sum ~1 */
    MassKg      total_mass_kg;
    VolM3       total_vol_m3;
} Mixture;

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
SubstanceId  dmatter_register_substance(const Substance *def);
MaterialId   dmatter_register_material(const MaterialType *def);
ItemTypeId   dmatter_register_item_type(const ItemType *def);

const Substance    *dmatter_get_substance(SubstanceId id);
const MaterialType *dmatter_get_material(MaterialId id);
const ItemType     *dmatter_get_item_type(ItemTypeId id);

/* Mixture helpers */
void    dmix_clear(Mixture *mix);
bool    dmix_add_mass(Mixture *mix, SubstanceId s, MassKg mass_delta_kg);
bool    dmix_normalise(Mixture *mix);
bool    dmix_transfer_fraction(Mixture *from, Mixture *to, Q16_16 fraction_0_1);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DMATTER_H */
