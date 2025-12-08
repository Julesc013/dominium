#ifndef DOMINO_DRESEARCH_H
#define DOMINO_DRESEARCH_H

#include "dnumeric.h"
#include "dmatter.h"
#include "drecipe.h"
#include "dmachine.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t TechId;

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

typedef struct {
    TechId   tech_id;
    Q16_16   progress_0_1;
    bool     completed;
} TechProgress;

TechId        dresearch_register_tech(const Tech *def);
const Tech   *dresearch_get_tech(TechId id);

void          dresearch_init_progress(U32 max_techs);
TechProgress *dresearch_get_progress(TechId id);

void          dresearch_tick(SimTick t);
void          dresearch_apply_work(TechId tech, U32 science_units);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DRESEARCH_H */
