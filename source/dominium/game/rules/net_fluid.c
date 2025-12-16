/*
FILE: source/dominium/game/rules/net_fluid.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/rules/net_fluid
RESPONSIBILITY: Implements `net_fluid`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/net_fluid.h"

struct dom_net_fluid {
    const dom_net_fluid_desc* desc;
};

dom_status dom_net_fluid_create(const dom_net_fluid_desc* desc,
                                dom_net_fluid** out_ctx)
{
    (void)desc;
    (void)out_ctx;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_net_fluid_destroy(dom_net_fluid* ctx)
{
    (void)ctx;
}

dom_status dom_net_fluid_register_node(dom_net_fluid* ctx,
                                       const dom_fluid_node_desc* desc,
                                       dom_fluid_node_id* out_id)
{
    (void)ctx;
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_net_fluid_connect(dom_net_fluid* ctx,
                                 const dom_fluid_link_desc* desc,
                                 dom_fluid_link_id* out_id)
{
    (void)ctx;
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_net_fluid_step(dom_net_fluid* ctx, uint32_t dt_millis)
{
    (void)ctx;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}
