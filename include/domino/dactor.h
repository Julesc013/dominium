/*
FILE: include/domino/dactor.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dactor
RESPONSIBILITY: Defines the public contract for `dactor` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

/* Species registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t SpeciesId;
/* Actor registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t ActorId;

/* Species definition used by the actor simulation (POD). */
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

/* Actor instance state updated by `dactor_tick_all()` (POD). */
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

/* Registers a species definition.
 *
 * Parameters:
 *   - def: Input definition (must be non-NULL and `def->name` must be non-NULL).
 *         `*def` is copied into internal storage; caller retains ownership.
 *
 * Returns:
 *   - Non-zero SpeciesId on success; 0 on failure (invalid input or capacity limit).
 */
SpeciesId      dactor_species_register(const Species *def);

/* Looks up a previously registered species definition.
 *
 * Returns:
 *   - Pointer to internal, read-only storage on success; NULL if `id` is invalid.
 *
 * Lifetime:
 *   - The returned pointer remains valid for the lifetime of the process.
 */
const Species *dactor_species_get(SpeciesId id);

/* Creates a new actor instance.
 *
 * Returns:
 *   - Non-zero ActorId on success; 0 on failure (no free slots).
 */
ActorId   dactor_create(SpeciesId species, EnvironmentKind env);

/* Returns a mutable pointer to the actor state for `id`.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid or destroyed.
 */
Actor    *dactor_get(ActorId id);

/* Destroys an actor instance. Accepts invalid ids as a no-op. */
void      dactor_destroy(ActorId id);

/* Advances the actor simulation by one tick for all active actors.
 *
 * Side effects:
 *   - Updates `Actor` health/stamina/body temperature and may interact with `dzone` atmosphere/heat.
 */
void      dactor_tick_all(SimTick t);

/* Configures substance ids for life support gases (oxygen, carbon dioxide, water).
 *
 * Parameters:
 *   - o2/co2/h2o: Non-zero ids override the current mapping; passing 0 leaves the mapping unchanged.
 */
void      dactor_set_substance_ids(SubstanceId o2, SubstanceId co2, SubstanceId h2o);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DACTOR_H */
