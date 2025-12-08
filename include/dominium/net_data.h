#ifndef DOMINIUM_NET_DATA_H
#define DOMINIUM_NET_DATA_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "dominium/world.h"
#include "dominium/constructions.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_net_data dom_net_data;

typedef uint32_t dom_data_network_id;
typedef uint32_t dom_data_node_id;
typedef uint32_t dom_data_link_id;

typedef struct dom_net_data_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_net_data_desc;

typedef struct dom_data_node_desc {
    uint32_t            struct_size;
    uint32_t            struct_version;
    dom_construction_id construction;
    uint32_t            buffer_bytes;
    uint32_t            flags;
} dom_data_node_desc;

typedef struct dom_data_link_desc {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_data_node_id a;
    dom_data_node_id b;
    uint32_t         bandwidth_bps;
    uint32_t         latency_millis;
    uint32_t         flags;
} dom_data_link_desc;

dom_status dom_net_data_create(const dom_net_data_desc* desc,
                               dom_net_data** out_ctx);
void       dom_net_data_destroy(dom_net_data* ctx);
dom_status dom_net_data_register_node(dom_net_data* ctx,
                                      const dom_data_node_desc* desc,
                                      dom_data_node_id* out_id);
dom_status dom_net_data_connect(dom_net_data* ctx,
                                const dom_data_link_desc* desc,
                                dom_data_link_id* out_id);
dom_status dom_net_data_step(dom_net_data* ctx, uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_NET_DATA_H */
