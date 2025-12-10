#include "dominium/net_data.h"

struct dom_net_data {
    const dom_net_data_desc* desc;
};

dom_status dom_net_data_create(const dom_net_data_desc* desc,
                               dom_net_data** out_ctx)
{
    (void)desc;
    (void)out_ctx;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_net_data_destroy(dom_net_data* ctx)
{
    (void)ctx;
}

dom_status dom_net_data_register_node(dom_net_data* ctx,
                                      const dom_data_node_desc* desc,
                                      dom_data_node_id* out_id)
{
    (void)ctx;
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_net_data_connect(dom_net_data* ctx,
                                const dom_data_link_desc* desc,
                                dom_data_link_id* out_id)
{
    (void)ctx;
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_net_data_step(dom_net_data* ctx, uint32_t dt_millis)
{
    (void)ctx;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}
