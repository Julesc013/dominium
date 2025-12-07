#ifndef DOMINO_SIM_H
#define DOMINO_SIM_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dm_sim_context dm_sim_context;

struct dm_sim_config {
    uint64_t seed;
};

dm_sim_context* dm_sim_create(const struct dm_sim_config* cfg);
void            dm_sim_destroy(dm_sim_context* sim);
void            dm_sim_tick(dm_sim_context* sim, uint32_t dt_usec);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SIM_H */
