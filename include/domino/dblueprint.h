/*
FILE: include/domino/dblueprint.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dblueprint
RESPONSIBILITY: Defines the public contract for `dblueprint` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
