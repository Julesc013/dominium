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
