/*
FILE: source/domino/render/api/core/dom_view.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_view
RESPONSIBILITY: Implements `dom_view`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_view.h"

#include <string.h>

#define DOM_VIEW_MAX 64

typedef struct dom_view_slot_s {
    dom_bool8 used;
    dom_view view;
} dom_view_slot;

static dom_view_slot g_dom_views[DOM_VIEW_MAX];

dom_view_id dom_view_create(const dom_view_desc *desc)
{
    dom_u32 i;
    dom_camera *cam;
    if (!desc) {
        return DOM_VIEW_ID_INVALID;
    }
    if (desc->camera == DOM_CAMERA_ID_INVALID) {
        return DOM_VIEW_ID_INVALID;
    }
    cam = dom_camera_lookup(desc->camera);
    if (!cam) {
        return DOM_VIEW_ID_INVALID;
    }
    if (desc->viewport_w <= 0 || desc->viewport_h <= 0) {
        return DOM_VIEW_ID_INVALID;
    }

    for (i = 1; i < DOM_VIEW_MAX; ++i) {
        if (!g_dom_views[i].used) {
            g_dom_views[i].used = 1;
            g_dom_views[i].view.desc = *desc;
            return (dom_view_id)i;
        }
    }
    return DOM_VIEW_ID_INVALID;
}

dom_err_t dom_view_destroy(dom_view_id id)
{
    if (id == DOM_VIEW_ID_INVALID || id >= DOM_VIEW_MAX) {
        return DOM_ERR_INVALID_ARG;
    }
    if (!g_dom_views[id].used) {
        return DOM_ERR_NOT_FOUND;
    }
    g_dom_views[id].used = 0;
    memset(&g_dom_views[id].view, 0, sizeof(dom_view));
    return DOM_OK;
}

dom_view *dom_view_lookup(dom_view_id id)
{
    if (id == DOM_VIEW_ID_INVALID || id >= DOM_VIEW_MAX) {
        return 0;
    }
    if (!g_dom_views[id].used) {
        return 0;
    }
    return &g_dom_views[id].view;
}

dom_err_t dom_view_project_2d(const dom_view *view,
                              dom_i64 world_x_q32_32,
                              dom_i64 world_y_q32_32,
                              dom_i32 *out_sx,
                              dom_i32 *out_sy)
{
    dom_i64 dx;
    dom_i64 dy;
    dom_i64 sx_fp;
    dom_i64 sy_fp;
    dom_camera *cam;
    if (!view || !out_sx || !out_sy) {
        return DOM_ERR_INVALID_ARG;
    }
    if (view->desc.type != DOM_VIEW_TYPE_TOPDOWN_2D) {
        return DOM_ERR_NOT_IMPLEMENTED;
    }
    cam = dom_camera_lookup(view->desc.camera);
    if (!cam) {
        return DOM_ERR_NOT_FOUND;
    }

    dx = world_x_q32_32 - cam->cam2d.world_x_q32_32;
    dy = world_y_q32_32 - cam->cam2d.world_y_q32_32;

    /* zoom q16.16, dx/dy q32.32 -> sx_fp q32.16 */
    sx_fp = (dx >> 16) * cam->cam2d.zoom_q16_16;
    sy_fp = (dy >> 16) * cam->cam2d.zoom_q16_16;

    *out_sx = view->desc.viewport_x + (dom_i32)(sx_fp >> 16);
    *out_sy = view->desc.viewport_y + (dom_i32)(sy_fp >> 16);
    return DOM_OK;
}
