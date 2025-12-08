#include "dominium/world.h"

struct dom_world {
    const dom_world_desc* desc;
};

dom_status dom_world_create(const dom_world_desc* desc, dom_world** out_world)
{
    (void)desc;
    (void)out_world;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_world_destroy(dom_world* world)
{
    (void)world;
}

dom_status dom_world_tick(dom_world* world, uint32_t dt_millis)
{
    (void)world;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_create_surface(dom_world* world,
                                    const dom_surface_desc* desc,
                                    dom_surface_id* out_surface)
{
    (void)world;
    (void)desc;
    if (out_surface) {
        *out_surface = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_remove_surface(dom_world* world, dom_surface_id surface)
{
    (void)world;
    (void)surface;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_get_surface_info(dom_world* world,
                                      dom_surface_id surface,
                                      dom_surface_info* out_info,
                                      size_t out_info_size)
{
    (void)world;
    (void)surface;
    if (out_info && out_info_size >= sizeof(dom_surface_info)) {
        out_info->struct_size    = (uint32_t)sizeof(dom_surface_info);
        out_info->struct_version = 0;
        out_info->id             = 0;
        out_info->seed           = 0;
        out_info->tier           = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_acquire_frame(dom_world* world,
                                   dom_surface_id surface,
                                   dom_surface_frame_view* out_frame)
{
    (void)world;
    (void)surface;
    if (out_frame) {
        out_frame->struct_size    = (uint32_t)sizeof(dom_surface_frame_view);
        out_frame->struct_version = 0;
        out_frame->surface        = 0;
        out_frame->frame          = 0;
        out_frame->tick_index     = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_release_frame(dom_world* world,
                                   dom_surface_frame_id frame)
{
    (void)world;
    (void)frame;
    return DOM_STATUS_UNSUPPORTED;
}
