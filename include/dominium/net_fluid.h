#ifndef DOMINIUM_NET_FLUID_H
#define DOMINIUM_NET_FLUID_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "dominium/world.h"
#include "dominium/constructions.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_net_fluid dom_net_fluid;

typedef uint32_t dom_fluid_network_id;
typedef uint32_t dom_fluid_node_id;
typedef uint32_t dom_fluid_link_id;

typedef struct dom_net_fluid_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_net_fluid_desc;

typedef struct dom_fluid_node_desc {
    uint32_t            struct_size;
    uint32_t            struct_version;
    dom_construction_id construction;
    uint32_t            capacity_millilitres;
    uint32_t            flags;
} dom_fluid_node_desc;

typedef struct dom_fluid_link_desc {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_fluid_node_id a;
    dom_fluid_node_id b;
    uint32_t         cross_section_mm2;
    uint32_t         flags;
} dom_fluid_link_desc;

dom_status dom_net_fluid_create(const dom_net_fluid_desc* desc,
                                dom_net_fluid** out_ctx);
void       dom_net_fluid_destroy(dom_net_fluid* ctx);
dom_status dom_net_fluid_register_node(dom_net_fluid* ctx,
                                       const dom_fluid_node_desc* desc,
                                       dom_fluid_node_id* out_id);
dom_status dom_net_fluid_connect(dom_net_fluid* ctx,
                                 const dom_fluid_link_desc* desc,
                                 dom_fluid_link_id* out_id);
dom_status dom_net_fluid_step(dom_net_fluid* ctx, uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_NET_FLUID_H */
