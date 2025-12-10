#ifndef DOMINO_SIM_SIM_H
#define DOMINO_SIM_SIM_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/rng.h"

typedef struct d_world d_world;

typedef struct d_world_config {
    u32 seed;
    u32 width;
    u32 height;
} d_world_config;

d_world* d_world_create(const d_world_config* cfg);
void     d_world_destroy(d_world* world);
void     d_world_tick(d_world* world);
u32      d_world_checksum(const d_world* world);
d_bool   d_world_save_tlv(const d_world* world, const char* path);
d_world* d_world_load_tlv(const char* path);

#endif /* DOMINO_SIM_SIM_H */
