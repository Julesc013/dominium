/*
FILE: include/dominium/net_data.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / net_data
RESPONSIBILITY: Defines the public contract for `net_data` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_NET_DATA_H
#define DOMINIUM_NET_DATA_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "dominium/world.h"
#include "dominium/constructions.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_net_data: Public type used by `net_data`. */
typedef struct dom_net_data dom_net_data;

/* dom_data_network_id: Public type used by `net_data`. */
typedef uint32_t dom_data_network_id;
/* dom_data_node_id: Public type used by `net_data`. */
typedef uint32_t dom_data_node_id;
/* dom_data_link_id: Public type used by `net_data`. */
typedef uint32_t dom_data_link_id;

/* dom_net_data_desc: Public type used by `net_data`. */
typedef struct dom_net_data_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_net_data_desc;

/* dom_data_node_desc: Public type used by `net_data`. */
typedef struct dom_data_node_desc {
    uint32_t            struct_size;
    uint32_t            struct_version;
    dom_construction_id construction;
    uint32_t            buffer_bytes;
    uint32_t            flags;
} dom_data_node_desc;

/* dom_data_link_desc: Public type used by `net_data`. */
typedef struct dom_data_link_desc {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_data_node_id a;
    dom_data_node_id b;
    uint32_t         bandwidth_bps;
    uint32_t         latency_millis;
    uint32_t         flags;
} dom_data_link_desc;

/* Purpose: Create net data.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_data_create(const dom_net_data_desc* desc,
                               dom_net_data** out_ctx);
/* Purpose: Destroy net data.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void       dom_net_data_destroy(dom_net_data* ctx);
/* Purpose: Register node.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_data_register_node(dom_net_data* ctx,
                                      const dom_data_node_desc* desc,
                                      dom_data_node_id* out_id);
/* Purpose: Connect net data.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_data_connect(dom_net_data* ctx,
                                const dom_data_link_desc* desc,
                                dom_data_link_id* out_id);
/* Purpose: Step net data.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_data_step(dom_net_data* ctx, uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_NET_DATA_H */
