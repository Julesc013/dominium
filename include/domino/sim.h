#ifndef DOMINO_SIM_H_INCLUDED
#define DOMINO_SIM_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dm_sim_context dm_sim_context;

/*------------------------------------------------------------
 * New Domino simulation control (dom_sim_*)
 *------------------------------------------------------------*/
typedef struct dom_sim dom_sim;
typedef struct dom_core dom_core;

typedef struct dom_sim_desc {
    uint32_t struct_size;
    uint32_t struct_version;
    dom_core* core;
    uint64_t seed;
    uint32_t tick_millis;
} dom_sim_desc;

int  dom_sim_create(const dom_sim_desc* desc, dom_sim** out_sim);
void dom_sim_destroy(dom_sim* sim);
int  dom_sim_tick(dom_sim* sim, uint32_t dt_millis);
int  dom_sim_get_time(dom_sim* sim, uint64_t* out_time_millis);

/*------------------------------------------------------------
 * Legacy deterministic sim stubs
 *------------------------------------------------------------*/
struct dm_sim_config {
    uint64_t seed;
};

dm_sim_context* dm_sim_create(const struct dm_sim_config* cfg);
void            dm_sim_destroy(dm_sim_context* sim);
void            dm_sim_tick(dm_sim_context* sim, uint32_t dt_usec);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SIM_H_INCLUDED */
