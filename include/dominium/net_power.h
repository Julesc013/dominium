/*
FILE: include/dominium/net_power.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / net_power
RESPONSIBILITY: Defines the public contract for `net_power` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_NET_POWER_H
#define DOMINIUM_NET_POWER_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "dominium/world.h"
#include "dominium/constructions.h"
#include "dominium/content_parts.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_net_power dom_net_power;

typedef uint32_t dom_power_network_id;
typedef uint32_t dom_power_node_id;
typedef uint32_t dom_power_link_id;

typedef struct dom_net_power_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    dom_world*  world;
} dom_net_power_desc;

typedef struct dom_power_node_desc {
    uint32_t            struct_size;
    uint32_t            struct_version;
    dom_construction_id construction;
    dom_part_id         part;
    uint32_t            capacity_watts;
    uint32_t            flags;
} dom_power_node_desc;

typedef struct dom_power_link_desc {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_power_node_id a;
    dom_power_node_id b;
    uint32_t         max_current_mA;
    uint32_t         flags;
} dom_power_link_desc;

dom_status dom_net_power_create(const dom_net_power_desc* desc,
                                dom_net_power** out_ctx);
void       dom_net_power_destroy(dom_net_power* ctx);
dom_status dom_net_power_register_node(dom_net_power* ctx,
                                       const dom_power_node_desc* desc,
                                       dom_power_node_id* out_id);
dom_status dom_net_power_connect(dom_net_power* ctx,
                                 const dom_power_link_desc* desc,
                                 dom_power_link_id* out_id);
dom_status dom_net_power_step(dom_net_power* ctx, uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_NET_POWER_H */
