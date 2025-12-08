#ifndef DOMINO_DBLUEPRINT_H
#define DOMINO_DBLUEPRINT_H

#include "dnumeric.h"
#include "dworld.h"
#include "dmatter.h"
#include "daggregate.h"
#include "dmachine.h"
#include "djob.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t BlueprintId;
typedef uint32_t BlueprintElementId;

typedef enum {
    BPOP_PLACE_ELEMENT = 0,
    BPOP_REMOVE_ELEMENT,
    BPOP_MODIFY_TERRAIN,
    BPOP_PLACE_MACHINE,
} BlueprintOpKind;

typedef struct {
    BlueprintElementId id;
    BlueprintOpKind    kind;
    WPosTile           tile;
    MaterialId         material;
    MachineTypeId      machine_type;
    ItemTypeId         required_item;
    U32                required_count;
    BlueprintElementId deps[4];
    U8                 dep_count;
} BlueprintElement;

typedef struct {
    BlueprintId       id;
    const char       *name;
    AggregateId       target_agg;
    U32               elem_count;
    U32               elem_capacity;
    BlueprintElement *elems;
} Blueprint;

BlueprintId        dblueprint_create(const char *name, U32 elem_capacity);
Blueprint          *dblueprint_get(BlueprintId id);
void                dblueprint_destroy(BlueprintId id);

BlueprintElementId  dblueprint_add_element(BlueprintId id, const BlueprintElement *elem);

void dblueprint_generate_jobs(BlueprintId id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DBLUEPRINT_H */
