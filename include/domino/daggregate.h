#ifndef DOMINO_DAGGREGATE_H
#define DOMINO_DAGGREGATE_H

#include "dnumeric.h"
#include "dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Forward type aliases */

typedef uint64_t ElementId;
typedef uint32_t AggregateId;
#ifndef DOMINO_MATERIAL_ID_TYPEDEF
#define DOMINO_MATERIAL_ID_TYPEDEF
typedef uint32_t MaterialId;
#endif
typedef uint32_t ArchetypeId;    /* item/building/vehicle archetype */
typedef uint32_t RoomLocalId;    /* future room/zone index inside an Aggregate */

/* Flags for elements */
enum {
    ELEM_FLAG_SOLID     = 1u << 0,  /* collision / structure */
    ELEM_FLAG_HULL      = 1u << 1,  /* pressure hull or external boundary */
    ELEM_FLAG_VENT      = 1u << 2,  /* vent for HVAC/gas between zones */
    ELEM_FLAG_DOOR      = 1u << 3,  /* openable door/gate */
    ELEM_FLAG_MACHINE   = 1u << 4,  /* machine block */
    ELEM_FLAG_WINDOW    = 1u << 5,  /* transparent hull */
    /* free bits for more flags */
};

typedef struct {
    ElementId   id;
    MaterialId  material_id;  /* 0 for non-material-only (pure machine) */
    ChunkPos    chunk;
    LocalPos    local;
    uint8_t     rot;          /* discrete rotation, e.g. 0..3 or 0..7 */
    AggregateId agg;          /* 0 == no aggregate assigned */
    uint8_t     flags;        /* ELEM_FLAG_* */
} Element;

/* Aggregate physical composition and mobility */

typedef struct {
    AggregateId           id;
    AggregateMobilityKind mobility;
    EnvironmentKind       env;

    U32                   element_count;
    ElementId            *element_ids;   /* owned pointer or index into ECS table */

    MassKg                mass;
    VolM3                 volume;

    Q16_16                drag_coeff;
    Q16_16                lift_coeff;
    Q16_16                buoyancy_factor;

    /* Future fields:
       - structural graph index
       - HP / damage
       - centre of mass
       - bounding volumes
       - room/zone graph handle
    */
} Aggregate;

/* API */

AggregateId dagg_create(AggregateMobilityKind mobility, EnvironmentKind env);
void        dagg_destroy(AggregateId id);

bool        dagg_attach_element(AggregateId agg, ElementId elem);
bool        dagg_detach_element(AggregateId agg, ElementId elem);

/* Recompute mass/volume from materials + element list.
   For now, these can be stubs that set mass/volume to zero or simple counts,
   but must exist and be called appropriately.
*/
void        dagg_recompute_mass_volume(AggregateId agg);

Aggregate  *dagg_get(AggregateId id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DAGGREGATE_H */
