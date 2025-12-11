#ifndef DOMINO_SIM_SIM_H
#define DOMINO_SIM_SIM_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/rng.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_world_config {
    u32 seed;
    u32 width;
    u32 height;
} d_world_config;

d_world* d_world_create_from_config(const d_world_config* cfg);
void     d_world_tick(d_world* world);
u32      d_world_checksum(const d_world* world);
d_bool   d_world_save_tlv(const d_world* world, const char* path);
d_world* d_world_load_tlv(const char* path);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SIM_SIM_H */
