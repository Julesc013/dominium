/* View descriptions and dgfx IR generation (C89). */
#ifndef D_VIEW_H
#define D_VIEW_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "domino/gfx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_view_id;

typedef struct d_view_camera_s {
    q16_16 pos_x, pos_y, pos_z;
    q16_16 dir_x, dir_y, dir_z;
    q16_16 up_x,  up_y,  up_z;
    q16_16 fov;
} d_view_camera;

typedef struct d_view_desc_s {
    d_view_id     id;
    u32           flags;
    d_view_camera camera;
    q16_16        vp_x, vp_y, vp_w, vp_h; /* normalized 0..1; will map to pixels */
    u32           layer_mask;
} d_view_desc;

typedef struct d_view_frame_s {
    d_view_desc      *view;
    d_gfx_cmd_buffer *cmd_buffer;
} d_view_frame;

/* Create/destroy views */
d_view_id d_view_create(const d_view_desc *desc);
int       d_view_destroy(d_view_id id);

/* Get mutable descriptor for a view (for camera updates etc.) */
d_view_desc *d_view_get(d_view_id id);

/*
 * Render a view:
 * - Fills cmd_buffer with dgfx IR commands for the given world and view.
 * - Does NOT submit or present; that is done by a higher layer.
 */
int d_view_render(
    d_world      *w,
    d_view_desc  *view,
    d_view_frame *frame
);

#ifdef __cplusplus
}
#endif

#endif /* D_VIEW_H */
