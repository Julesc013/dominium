#include "dom_view.h"
#include "dom_draw_common.h"

/*
 * Placeholder view-to-draw-command builder.
 * Scene data is intentionally opaque here; callers should adapt it later.
 */

typedef struct dom_scene_data_s dom_scene_data;

void dom_view_build_commands(const dom_view        *view,
                             const dom_scene_data  *scene,
                             DomDrawCommand        *out_cmds,
                             dom_u32               *out_count,
                             dom_u32                max_cmds)
{
    (void)scene;
    if (!out_count) {
        return;
    }
    if (!view || !out_cmds) {
        *out_count = 0;
        return;
    }
    *out_count = 0;

    /* Branching skeleton: real emitters to be filled later. */
    if (view->desc.type == DOM_VIEW_TYPE_TOPDOWN_2D) {
        if (view->desc.mode == DOM_VIEW_MODE_VECTOR) {
            /* TODO: emit grid/outlines/labels */
        } else {
            /* TODO: emit textured sprites/tiles + overlays */
        }
    } else if (view->desc.type == DOM_VIEW_TYPE_FIRSTPERSON_3D) {
        if (view->desc.mode == DOM_VIEW_MODE_VECTOR) {
            /* TODO: emit wireframe/flat TRIANGLE commands */
        } else {
            /* TODO: emit textured TRIANGLE commands */
        }
    }
    (void)max_cmds;
}
