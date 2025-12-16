/*
FILE: include/dominium/net_fluid.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / net_fluid
RESPONSIBILITY: Defines the public contract for `net_fluid` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

/* dom_net_fluid: Public type used by `net_fluid`. */
typedef struct dom_net_fluid dom_net_fluid;

/* dom_fluid_network_id: Public type used by `net_fluid`. */
typedef uint32_t dom_fluid_network_id;
/* dom_fluid_node_id: Public type used by `net_fluid`. */
typedef uint32_t dom_fluid_node_id;
/* dom_fluid_link_id: Public type used by `net_fluid`. */
typedef uint32_t dom_fluid_link_id;

/* dom_net_fluid_desc: Public type used by `net_fluid`. */
typedef struct dom_net_fluid_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_net_fluid_desc;

/* dom_fluid_node_desc: Public type used by `net_fluid`. */
typedef struct dom_fluid_node_desc {
    uint32_t            struct_size;
    uint32_t            struct_version;
    dom_construction_id construction;
    uint32_t            capacity_millilitres;
    uint32_t            flags;
} dom_fluid_node_desc;

/* dom_fluid_link_desc: Public type used by `net_fluid`. */
typedef struct dom_fluid_link_desc {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_fluid_node_id a;
    dom_fluid_node_id b;
    uint32_t         cross_section_mm2;
    uint32_t         flags;
} dom_fluid_link_desc;

/* Purpose: Create net fluid.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_fluid_create(const dom_net_fluid_desc* desc,
                                dom_net_fluid** out_ctx);
/* Purpose: Destroy net fluid.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void       dom_net_fluid_destroy(dom_net_fluid* ctx);
/* Purpose: Register node.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_fluid_register_node(dom_net_fluid* ctx,
                                       const dom_fluid_node_desc* desc,
                                       dom_fluid_node_id* out_id);
/* Purpose: Connect net fluid.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_fluid_connect(dom_net_fluid* ctx,
                                 const dom_fluid_link_desc* desc,
                                 dom_fluid_link_id* out_id);
/* Purpose: Step net fluid.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_net_fluid_step(dom_net_fluid* ctx, uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_NET_FLUID_H */
