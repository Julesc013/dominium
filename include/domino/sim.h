#ifndef DOMINO_SIM_H_INCLUDED
#define DOMINO_SIM_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"
#include "domino/inst.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dom_core_t;
typedef struct dom_core_t dom_core;

typedef struct dom_sim dom_sim;

typedef struct dom_sim_state {
    uint32_t struct_size;
    uint32_t struct_version;
    uint64_t ticks;
    double   sim_time_s;
    double   dt_s;
    double   ups;          /* target updates per second */
    bool     paused;
} dom_sim_state;

bool dom_sim_tick(dom_core* core,
                  dom_instance_id inst,
                  uint32_t ticks);

bool dom_sim_get_state(dom_core* core,
                       dom_instance_id inst,
                       dom_sim_state* out);

/*------------------------------------------------------------
 * Legacy deterministic sim stubs (kept for compatibility)
 *------------------------------------------------------------*/
struct dm_sim_config {
    uint64_t seed;
};

typedef struct dm_sim_context dm_sim_context;

dm_sim_context* dm_sim_create(const struct dm_sim_config* cfg);
void            dm_sim_destroy(dm_sim_context* sim);
void            dm_sim_tick(dm_sim_context* sim, uint32_t dt_usec);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SIM_H_INCLUDED */
