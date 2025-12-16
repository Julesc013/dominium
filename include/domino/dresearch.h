/*
FILE: include/domino/dresearch.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dresearch
RESPONSIBILITY: Defines the public contract for `dresearch` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DRESEARCH_H
#define DOMINO_DRESEARCH_H

#include "dnumeric.h"
#include "dmatter.h"
#include "drecipe.h"
#include "dmachine.h"

#ifdef __cplusplus
extern "C" {
#endif

/* TechId: Identifier type for Tech objects in `dresearch`. */
typedef uint32_t TechId;

/* Tech: Public type used by `dresearch`. */
typedef struct {
    TechId      id;
    const char *name;

    TechId      prereq[8];
    U8          prereq_count;

    Q16_16      research_time_s;
    ItemTypeId  science_item;
    U32         science_count;

    MachineTypeId unlocked_machines[16];
    U8            unlocked_machine_count;

    RecipeId      unlocked_recipes[32];
    U8            unlocked_recipe_count;

} Tech;

/* TechProgress: Public type used by `dresearch`. */
typedef struct {
    TechId   tech_id;
    Q16_16   progress_0_1;
    bool     completed;
} TechProgress;

/* Purpose: Register tech.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
TechId        dresearch_register_tech(const Tech *def);
/* Purpose: Get tech.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const Tech   *dresearch_get_tech(TechId id);

/* Purpose: Init progress.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void          dresearch_init_progress(U32 max_techs);
/* Purpose: Get progress.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
TechProgress *dresearch_get_progress(TechId id);

/* Purpose: Tick dresearch.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void          dresearch_tick(SimTick t);
/* Purpose: Apply work.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void          dresearch_apply_work(TechId tech, U32 science_units);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DRESEARCH_H */
