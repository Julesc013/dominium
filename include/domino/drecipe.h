/*
FILE: include/domino/drecipe.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / drecipe
RESPONSIBILITY: Defines the public contract for `drecipe` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DRECIPE_H
#define DOMINO_DRECIPE_H

#include "dnumeric.h"
#include "dmatter.h"

#ifdef __cplusplus
extern "C" {
#endif

/* RecipeId: Identifier type for Recipe objects in `drecipe`. */
typedef uint32_t RecipeId;

/* RecipeKind: Enumeration/classifier for Recipe in `drecipe`. */
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

/* RecipeItemIO: Public type used by `drecipe`. */
typedef struct {
    ItemTypeId item;
    U32        count;
} RecipeItemIO;

/* RecipeFluidIO: Public type used by `drecipe`. */
typedef struct {
    SubstanceId substance;
    VolM3       volume_m3;
} RecipeFluidIO;

/* Recipe: Public type used by `drecipe`. */
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

/* Purpose: Register drecipe.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
RecipeId      drecipe_register(const Recipe *def);
/* Purpose: Get drecipe.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const Recipe *drecipe_get(RecipeId id);

/* RecipeStepResult: Public type used by `drecipe`. */
typedef struct {
    bool    batch_started;
    bool    batch_completed;
} RecipeStepResult;

struct Machine;

/* Purpose: Step machine.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
RecipeStepResult drecipe_step_machine(struct Machine *mach,
                                      const Recipe *recipe,
                                      SimTick t);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DRECIPE_H */
