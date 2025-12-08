#ifndef DOMINO_DZONE_H
#define DOMINO_DZONE_H

#include "dnumeric.h"
#include "dworld.h"
#include "dmatter.h"
#include "daggregate.h"
#include "dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t ZoneId;
typedef uint32_t ZoneLinkId;

typedef struct {
    ZoneLinkId  id;
    ZoneId      a;
    ZoneId      b;

    Q16_16      area_m2;           /* effective cross-section */
    Q16_16      flow_coeff;        /* relative flow factor */
    U32         flags;
} ZoneLink;

typedef struct {
    ZoneId       id;
    AggregateId  agg;           /* owning aggregate (building/vehicle/station), 0 if world zone */
    BodyId       body;          /* body this zone belongs to (for gravity/env) */

    /* Atmosphere mixture inside this zone */
    Mixture      atm;           /* Mixture: gases, vapours, etc. */

    PressurePa   pressure_Pa;
    TempK        temp_K;

    Q16_16       volume_m3;     /* approximate volume of zone */
    Q16_16       leak_factor_0_1;   /* leakage to external env per tick */
    Q16_16       thermal_leak_0_1;  /* thermal leakage to outside */
} Zone;

enum {
    ZLINK_FLAG_OPENABLE  = 1u << 0,
    ZLINK_FLAG_VENT      = 1u << 1,
    ZLINK_FLAG_ONE_WAY   = 1u << 2,
};

/* Registry */

ZoneId      dzone_register(const Zone *def);
Zone       *dzone_get(ZoneId id);

ZoneLinkId  dzone_link_register(const ZoneLink *def);
ZoneLink   *dzone_link_get(ZoneLinkId id);

U32         dzone_get_by_aggregate(AggregateId agg,
                                   ZoneId *out_ids,
                                   U32 max_out);

/* Called once per simulation tick to update all zone atmospheres. */
void dzone_tick(SimTick t);

/* HVAC hooks */
bool dzone_add_gas(ZoneId id, SubstanceId s, MassKg mass_delta_kg, EnergyJ energy_delta_J);
bool dzone_add_heat(ZoneId id, EnergyJ energy_delta_J);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DZONE_H */
