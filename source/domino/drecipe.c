#include "domino/drecipe.h"
#include "domino/dmachine.h"

#include <string.h>

#define DRECIPE_MAX 1024

static Recipe   g_recipes[DRECIPE_MAX];
static RecipeId g_recipe_count = 0;

RecipeId drecipe_register(const Recipe *def)
{
    Recipe copy;
    if (!def || !def->name) return 0;
    if (g_recipe_count >= (RecipeId)DRECIPE_MAX) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (RecipeId)(g_recipe_count + 1);
    }
    g_recipes[g_recipe_count] = copy;
    g_recipe_count++;
    return copy.id;
}

const Recipe *drecipe_get(RecipeId id)
{
    if (id == 0 || id > g_recipe_count) return 0;
    return &g_recipes[id - 1];
}

RecipeStepResult drecipe_step_machine(struct Machine *mach,
                                      const Recipe *recipe,
                                      SimTick t)
{
    RecipeStepResult res;
    Q16_16 dt = g_domino_dt_s;
    Q16_16 incr = 0;
    (void)t;
    res.batch_started = false;
    res.batch_completed = false;
    if (!mach || !recipe) {
        return res;
    }
    if (recipe->time_s == 0) {
        mach->progress_0_1 = (Q16_16)(1 << 16);
        res.batch_started = true;
        res.batch_completed = true;
        return res;
    }
    incr = (Q16_16)(((I64)dt << 16) / (I64)recipe->time_s);
    if (mach->progress_0_1 == 0 && incr > 0) {
        res.batch_started = true;
    }
    mach->progress_0_1 = (Q16_16)(mach->progress_0_1 + incr);
    if (mach->progress_0_1 >= (Q16_16)(1 << 16)) {
        mach->progress_0_1 = 0;
        res.batch_completed = true;
    }
    return res;
}
