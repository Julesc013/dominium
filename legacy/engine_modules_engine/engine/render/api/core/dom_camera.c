/*
FILE: source/domino/render/api/core/dom_camera.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_camera
RESPONSIBILITY: Implements `dom_camera`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_camera.h"

#include <string.h>

#define DOM_CAMERA_MAX 32

typedef struct dom_camera_slot_s {
    dom_bool8 used;
    dom_camera cam;
} dom_camera_slot;

static dom_camera_slot g_dom_cameras[DOM_CAMERA_MAX];

dom_camera_id dom_camera_create(dom_camera_type type)
{
    dom_u32 i;
    for (i = 1; i < DOM_CAMERA_MAX; ++i) {
        if (!g_dom_cameras[i].used) {
            dom_camera *cam = &g_dom_cameras[i].cam;
            memset(cam, 0, sizeof(*cam));
            cam->type = type;
            /* Default zoom: 1.0 (1m → 1px) */
            cam->cam2d.zoom_q16_16 = (dom_i32)(1 << 16);
            /* Default 3D fov: ~60deg in q16.16 (approx) */
            cam->cam3d.fov_y_q16_16 = (dom_i32)(60 << 16);
            cam->cam3d.near_mm = 1;
            cam->cam3d.far_mm = 100000;

            g_dom_cameras[i].used = 1;
            return (dom_camera_id)i;
        }
    }
    return DOM_CAMERA_ID_INVALID;
}

dom_err_t dom_camera_destroy(dom_camera_id id)
{
    if (id == DOM_CAMERA_ID_INVALID || id >= DOM_CAMERA_MAX) {
        return DOM_ERR_INVALID_ARG;
    }
    if (!g_dom_cameras[id].used) {
        return DOM_ERR_NOT_FOUND;
    }
    g_dom_cameras[id].used = 0;
    memset(&g_dom_cameras[id].cam, 0, sizeof(dom_camera));
    return DOM_OK;
}

dom_camera *dom_camera_lookup(dom_camera_id id)
{
    if (id == DOM_CAMERA_ID_INVALID || id >= DOM_CAMERA_MAX) {
        return 0;
    }
    if (!g_dom_cameras[id].used) {
        return 0;
    }
    return &g_dom_cameras[id].cam;
}
