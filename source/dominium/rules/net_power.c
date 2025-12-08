#include "dominium/net_power.h"

struct dom_net_power {
    const dom_net_power_desc* desc;
};

dom_status dom_net_power_create(const dom_net_power_desc* desc,
                                dom_net_power** out_ctx)
{
    (void)desc;
    (void)out_ctx;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_net_power_destroy(dom_net_power* ctx)
{
    (void)ctx;
}

dom_status dom_net_power_register_node(dom_net_power* ctx,
                                       const dom_power_node_desc* desc,
                                       dom_power_node_id* out_id)
{
    (void)ctx;
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_net_power_connect(dom_net_power* ctx,
                                 const dom_power_link_desc* desc,
                                 dom_power_link_id* out_id)
{
    (void)ctx;
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_net_power_step(dom_net_power* ctx, uint32_t dt_millis)
{
    (void)ctx;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}
