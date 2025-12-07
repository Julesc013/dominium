#include "dom_target.h"

#include <string.h>

#define DOM_TARGET_MAX 32

typedef struct dom_target_slot_s {
    dom_bool8 used;
    dom_target tgt;
} dom_target_slot;

static dom_target_slot g_dom_targets[DOM_TARGET_MAX];

static dom_target_id dom_target_alloc(const dom_target *t)
{
    dom_u32 i;
    for (i = 1; i < DOM_TARGET_MAX; ++i) {
        if (!g_dom_targets[i].used) {
            g_dom_targets[i].used = 1;
            g_dom_targets[i].tgt = *t;
            return (dom_target_id)i;
        }
    }
    return DOM_TARGET_ID_INVALID;
}

dom_target_id dom_target_create_backbuffer(void *platform_window,
                                           dom_u32 width,
                                           dom_u32 height)
{
    dom_target t;
    if (width == 0 || height == 0) {
        return DOM_TARGET_ID_INVALID;
    }
    t.type = DOM_TARGET_WINDOW_BACKBUFFER;
    t.width = width;
    t.height = height;
    t.platform_window = platform_window;
    return dom_target_alloc(&t);
}

dom_target_id dom_target_create_offscreen(dom_u32 width, dom_u32 height)
{
    dom_target t;
    if (width == 0 || height == 0) {
        return DOM_TARGET_ID_INVALID;
    }
    t.type = DOM_TARGET_OFFSCREEN_TEXTURE;
    t.width = width;
    t.height = height;
    t.platform_window = 0;
    return dom_target_alloc(&t);
}

dom_err_t dom_target_destroy(dom_target_id id)
{
    if (id == DOM_TARGET_ID_INVALID || id >= DOM_TARGET_MAX) {
        return DOM_ERR_INVALID_ARG;
    }
    if (!g_dom_targets[id].used) {
        return DOM_ERR_NOT_FOUND;
    }
    g_dom_targets[id].used = 0;
    memset(&g_dom_targets[id].tgt, 0, sizeof(dom_target));
    return DOM_OK;
}

dom_target *dom_target_lookup(dom_target_id id)
{
    if (id == DOM_TARGET_ID_INVALID || id >= DOM_TARGET_MAX) {
        return 0;
    }
    if (!g_dom_targets[id].used) {
        return 0;
    }
    return &g_dom_targets[id].tgt;
}
