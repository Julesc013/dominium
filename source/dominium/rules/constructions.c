#include "dominium/constructions.h"

dom_status dom_construction_spawn(const dom_construction_spawn_desc* desc,
                                  dom_construction_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_construction_destroy(dom_construction_id id)
{
    (void)id;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_construction_get_state(dom_construction_id id,
                                      dom_construction_state* out_state,
                                      size_t out_state_size)
{
    (void)id;
    if (out_state && out_state_size >= sizeof(dom_construction_state)) {
        out_state->struct_size    = (uint32_t)sizeof(dom_construction_state);
        out_state->struct_version = 0;
        out_state->id             = 0;
        out_state->prefab         = 0;
        out_state->surface        = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_construction_tick(dom_construction_id id, uint32_t dt_millis)
{
    (void)id;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_constructions_step(uint32_t dt_millis)
{
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}
