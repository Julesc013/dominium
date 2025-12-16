/*
FILE: source/domino/render/api/core/dom_view.h
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
#ifndef DOM_VIEW_H
#define DOM_VIEW_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_camera.h"
#include "dom_draw_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef dom_u32 dom_view_id;
#define DOM_VIEW_ID_INVALID ((dom_view_id)0u)

typedef enum dom_view_type_e {
    DOM_VIEW_TYPE_TOPDOWN_2D = 0,
    DOM_VIEW_TYPE_FIRSTPERSON_3D = 1
} dom_view_type;

typedef enum dom_view_mode_e {
    DOM_VIEW_MODE_VECTOR = 0,
    DOM_VIEW_MODE_GRAPHICS = 1
} dom_view_mode;

typedef struct dom_view_desc_s {
    dom_camera_id camera;
    dom_view_type type;
    dom_view_mode mode;
    dom_i32 viewport_x;
    dom_i32 viewport_y;
    dom_i32 viewport_w;
    dom_i32 viewport_h;
    dom_u32 layer;
} dom_view_desc;

typedef struct dom_view_s {
    dom_view_desc desc;
} dom_view;

dom_view_id dom_view_create(const dom_view_desc *desc);
dom_err_t   dom_view_destroy(dom_view_id id);
dom_view   *dom_view_lookup(dom_view_id id);

/* Utility: project a 2D world position into screen space for 2D views. */
dom_err_t dom_view_project_2d(const dom_view *view,
                              dom_i64 world_x_q32_32,
                              dom_i64 world_y_q32_32,
                              dom_i32 *out_sx,
                              dom_i32 *out_sy);

/* Build draw commands for a given view (scene is opaque placeholder for now). */
struct dom_scene_data_s;
void dom_view_build_commands(const dom_view        *view,
                             const struct dom_scene_data_s *scene,
                             DomDrawCommand        *out_cmds,
                             dom_u32               *out_count,
                             dom_u32                max_cmds);

#ifdef __cplusplus
}
#endif

#endif /* DOM_VIEW_H */
