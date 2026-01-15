/*
FILE: include/domino/dzone.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dzone
RESPONSIBILITY: Defines the public contract for `dzone` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

/* Purpose: Zone registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t ZoneId;
/* Purpose: ZoneLink registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t ZoneLinkId;

/* Purpose: Link between two zones for atmosphere/thermal exchange (POD). */
typedef struct {
    ZoneLinkId  id;
    ZoneId      a;
    ZoneId      b;

    Q16_16      area_m2;           /* effective cross-section */
    Q16_16      flow_coeff;        /* relative flow factor */
    U32         flags;
} ZoneLink;

/* Purpose: Enclosed environment/compartment state record (POD). */
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

/* Purpose: Flags for `ZoneLink.flags`. */
enum {
    ZLINK_FLAG_OPENABLE  = 1u << 0,
    ZLINK_FLAG_VENT      = 1u << 1,
    ZLINK_FLAG_ONE_WAY   = 1u << 2,
};

/* Registry */

/* Registers a zone definition (copied into internal storage).
 *
 * Purpose: Add a zone record to the registry.
 *
 * Returns:
 *   - Non-zero ZoneId on success; 0 on failure (invalid input or capacity limit).
 */
ZoneId      dzone_register(const Zone *def);

/* Looks up a zone by id.
 *
 * Purpose: Retrieve a previously registered zone record.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid.
 */
Zone       *dzone_get(ZoneId id);

/* Registers a zone link definition (copied into internal storage).
 *
 * Purpose: Add a zone-link record to the registry.
 *
 * Returns:
 *   - Non-zero ZoneLinkId on success; 0 on failure (invalid input or capacity limit).
 */
ZoneLinkId  dzone_link_register(const ZoneLink *def);

/* Looks up a zone link by id.
 *
 * Purpose: Retrieve a previously registered zone-link record.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid.
 */
ZoneLink   *dzone_link_get(ZoneLinkId id);

/* Enumerates zones owned by an aggregate.
 *
 * Purpose: Query zone ids associated with a specific aggregate.
 *
 * Parameters:
 *   - out_ids/max_out: Output array and capacity.
 *
 * Returns:
 *   - Number of ids written to `out_ids` (0 on invalid output buffer).
 */
U32         dzone_get_by_aggregate(AggregateId agg,
                                   ZoneId *out_ids,
                                   U32 max_out);

/* Updates all zone atmospheres for one simulation tick.
 *
 * Purpose: Advance zone atmosphere/thermal exchange simulation by one tick.
 *
 * Side effects:
 *   - Exchanges mass between linked zones, applies leak/thermal terms, and recomputes pressures.
 */
void dzone_tick(SimTick t);

/* HVAC hooks */
/* Adds/removes gas mass in a zone and optionally applies an energy delta.
 *
 * Purpose: Apply a mass/energy delta to a zone atmosphere mixture.
 *
 * Returns:
 *   - true on success; false if the zone is invalid or the mixture update fails.
 */
bool dzone_add_gas(ZoneId id, SubstanceId s, MassKg mass_delta_kg, EnergyJ energy_delta_J);

/* Applies an energy delta to a zone atmosphere.
 *
 * Purpose: Adjust zone atmosphere energy/temperature bookkeeping.
 *
 * Returns:
 *   - true on success; false if the zone is invalid.
 */
bool dzone_add_heat(ZoneId id, EnergyJ energy_delta_J);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DZONE_H */
