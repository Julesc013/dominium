#ifndef DOMINO_DACTOR_H
#define DOMINO_DACTOR_H

#include "dnumeric.h"
#include "dworld.h"
#include "dmatter.h"
#include "dzone.h"
#include "daggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t SpeciesId;
typedef uint32_t ActorId;

typedef struct {
    SpeciesId   id;
    const char *name;

    MassKg      body_mass_kg;

    /* Life support per second at rest (scaled linearly for now) */
    MassKg      o2_consumption_kg_s;
    MassKg      co2_production_kg_s;
    MassKg      h2o_consumption_kg_s;
    MassKg      waste_production_kg_s;

    EnergyJ     heat_output_W;         /* Joules per second at rest */

    /* Tolerances */
    PressurePa  min_pressure_Pa;
    PressurePa  max_pressure_Pa;
    TempK       min_temp_K;
    TempK       max_temp_K;
    Q16_16      min_o2_fraction;       /* 0..1 */
    Q16_16      max_co2_fraction;      /* 0..1 */

} Species;

typedef struct {
    ActorId     id;
    SpeciesId   species;

    /* Spatial embedding */
    EnvironmentKind env;
    ZoneId      zone;         /* if inside a zone */
    WPosExact   world_pos;    /* if in ENV_SURFACE_GRID or AIR_LOCAL, etc. */

    /* References for attachments (e.g. inside a vehicle) */
    AggregateId parent_agg;   /* 0 if world-anchored */

    /* Life support state */
    TempK       body_temp_K;
    Q16_16      health_0_1;        /* 0..1 */
    Q16_16      stamina_0_1;       /* 0..1 */

    /* Simple inventory placeholder */
    MassKg      carried_mass_kg;
    VolM3       carried_vol_m3;

    /* Knowledge handle */
    uint32_t    knowledge_id;
} Actor;

SpeciesId      dactor_species_register(const Species *def);
const Species *dactor_species_get(SpeciesId id);

ActorId   dactor_create(SpeciesId species, EnvironmentKind env);
Actor    *dactor_get(ActorId id);
void      dactor_destroy(ActorId id);

void      dactor_tick_all(SimTick t);

/* Configure substance ids for life support (oxygen, carbon dioxide, water) */
void      dactor_set_substance_ids(SubstanceId o2, SubstanceId co2, SubstanceId h2o);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DACTOR_H */
