#ifndef DOMINO_DRECIPE_H
#define DOMINO_DRECIPE_H

#include "dnumeric.h"
#include "dmatter.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t RecipeId;

typedef enum {
    RECIPE_KIND_MACHINE = 0,
    RECIPE_KIND_RESEARCH,
    RECIPE_KIND_ENVIRONMENTAL,
    RECIPE_KIND_CUSTOM,
} RecipeKind;

#define DREC_MAX_ITEMS_IN   8
#define DREC_MAX_ITEMS_OUT  8
#define DREC_MAX_FLUIDS_IN  4
#define DREC_MAX_FLUIDS_OUT 4
#define DREC_MAX_GASES_IN   4
#define DREC_MAX_GASES_OUT  4

typedef struct {
    ItemTypeId item;
    U32        count;
} RecipeItemIO;

typedef struct {
    SubstanceId substance;
    VolM3       volume_m3;
} RecipeFluidIO;

typedef struct {
    RecipeId    id;
    const char *name;

    RecipeKind  kind;

    Q16_16      time_s;

    PowerW      power_in_W;
    PowerW      power_out_W;

    EnergyJ     heat_in_J;
    EnergyJ     heat_out_J;

    U8          item_in_count;
    U8          item_out_count;
    RecipeItemIO item_in[DREC_MAX_ITEMS_IN];
    RecipeItemIO item_out[DREC_MAX_ITEMS_OUT];

    U8          fluid_in_count;
    U8          fluid_out_count;
    RecipeFluidIO fluid_in[DREC_MAX_FLUIDS_IN];
    RecipeFluidIO fluid_out[DREC_MAX_FLUIDS_OUT];

    U8          gas_in_count;
    U8          gas_out_count;
    RecipeFluidIO gas_in[DREC_MAX_GASES_IN];
    RecipeFluidIO gas_out[DREC_MAX_GASES_OUT];

    uint32_t    unlock_tech_id;
} Recipe;

RecipeId      drecipe_register(const Recipe *def);
const Recipe *drecipe_get(RecipeId id);

typedef struct {
    bool    batch_started;
    bool    batch_completed;
} RecipeStepResult;

struct Machine;

RecipeStepResult drecipe_step_machine(struct Machine *mach,
                                      const Recipe *recipe,
                                      SimTick t);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DRECIPE_H */
