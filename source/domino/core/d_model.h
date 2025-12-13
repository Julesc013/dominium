/* Unified model registry (C89). */
#ifndef D_MODEL_H
#define D_MODEL_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u16 d_model_family_id;
typedef u16 d_model_id;

/* Model family IDs. More will be added later. */
enum {
    D_MODEL_FAMILY_RES    = 1,
    D_MODEL_FAMILY_ENV    = 2,
    D_MODEL_FAMILY_BUILD  = 3,
    D_MODEL_FAMILY_TRANS  = 4,
    D_MODEL_FAMILY_VEH    = 5,
    D_MODEL_FAMILY_JOB    = 6,
    D_MODEL_FAMILY_NET    = 7,
    D_MODEL_FAMILY_REPLAY = 8,
    D_MODEL_FAMILY_HYDRO  = 9,
    /* Reserve 1000+ for mods/third-party model families. */
};

/* Generic model descriptor */
typedef struct d_model_desc {
    d_model_family_id family_id;
    d_model_id        model_id;

    const char       *name;     /* e.g. "strata_ore", "thermal_gas_diffusion" */
    u32               version;  /* model-specific version */

    /* family-specific function table; cast to appropriate vtable struct in each subsystem */
    void             *fn_table;
} d_model_desc;

/* Registration and lookup APIs */
int  d_model_register(const d_model_desc *desc);
/* Return number of models in given family */
u32  d_model_count(d_model_family_id family_id);
/* Get model by family+index */
const d_model_desc *d_model_get_by_index(d_model_family_id family_id, u32 index);
/* Get model by family+id */
const d_model_desc *d_model_get(d_model_family_id family_id, d_model_id model_id);

#ifdef __cplusplus
}
#endif

#endif /* D_MODEL_H */
