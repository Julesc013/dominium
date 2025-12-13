/* Interior/exterior volume graph (C89). */
#ifndef D_ENV_VOLUME_H
#define D_ENV_VOLUME_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_env_volume_id;

typedef struct d_env_volume_s {
    d_env_volume_id id;

    q32_32 min_x, min_y, min_z;
    q32_32 max_x, max_y, max_z;

    u32 owner_struct_eid;
    u32 owner_vehicle_eid;

    q16_16 pressure;
    q16_16 temperature;
    q16_16 gas0_fraction;
    q16_16 gas1_fraction;
    q16_16 humidity;
    q16_16 pollutant;
} d_env_volume;

typedef struct d_env_volume_edge_s {
    d_env_volume_id a;
    d_env_volume_id b;

    q16_16 gas_conductance;
    q16_16 heat_conductance;
} d_env_volume_edge;

void d_env_volume_tick(d_world *w, u32 ticks);

d_env_volume_id d_env_volume_find_at(
    const d_world *w,
    q32_32         x,
    q32_32         y,
    q32_32         z
);

/* Minimal management API (kept generic). */
d_env_volume_id d_env_volume_create(d_world *w, const d_env_volume *vol);
int d_env_volume_destroy(d_world *w, d_env_volume_id id);
int d_env_volume_remove_owned_by(d_world *w, u32 owner_struct_eid, u32 owner_vehicle_eid);
int d_env_volume_add_edge(d_world *w, const d_env_volume_edge *edge);
const d_env_volume *d_env_volume_get(const d_world *w, d_env_volume_id id);
u32 d_env_volume_count(const d_world *w);
const d_env_volume *d_env_volume_get_by_index(const d_world *w, u32 index);

/* Serialization helpers (used by the ENV subsystem container). */
int d_env_volume_save_instance(d_world *w, d_tlv_blob *out);
int d_env_volume_load_instance(d_world *w, const d_tlv_blob *in);
void d_env_volume_init_instance(d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_ENV_VOLUME_H */
