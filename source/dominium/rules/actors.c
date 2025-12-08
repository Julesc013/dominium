#include "dominium/actors.h"

dom_status dom_actor_spawn(const dom_actor_spawn_desc* desc,
                           dom_actor_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actor_despawn(dom_actor_id id)
{
    (void)id;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actor_get_state(dom_actor_id id,
                               dom_actor_state* out_state,
                               size_t out_state_size)
{
    (void)id;
    if (out_state && out_state_size >= sizeof(dom_actor_state)) {
        out_state->struct_size      = (uint32_t)sizeof(dom_actor_state);
        out_state->struct_version   = 0;
        out_state->id               = 0;
        out_state->kind             = DOM_ACTOR_KIND_UNKNOWN;
        out_state->surface          = 0;
        out_state->life_support_mbar = 0;
        out_state->health_permille  = 0;
        out_state->flags            = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actor_tick(dom_actor_id id, uint32_t dt_millis)
{
    (void)id;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actors_step(uint32_t dt_millis)
{
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}
