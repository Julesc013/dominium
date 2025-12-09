#ifndef DOMINO_CANVAS_H_INCLUDED
#define DOMINO_CANVAS_H_INCLUDED

#include <stddef.h>
#include <stdint.h>
#include "domino/gfx.h"
#include "domino/core.h"
#include "domino/inst.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Domino canvas recorder (dcvs)
 *------------------------------------------------------------*/
typedef struct dcvs_t dcvs; /* opaque */

/* Create/destroy a canvas with an internal command buffer */
dcvs *dcvs_create(uint32_t initial_capacity);
void  dcvs_destroy(dcvs *c);

/* Reset to empty; capacity unchanged. */
void  dcvs_reset(dcvs *c);

/* Get underlying command buffer view */
const dgfx_cmd_buffer *dcvs_get_cmd_buffer(const dcvs *c);

/* Command emitters */
bool dcvs_clear(dcvs *c, uint32_t rgba);
bool dcvs_set_viewport(dcvs *c, const dgfx_viewport_t *vp);
bool dcvs_set_camera(dcvs *c, const dgfx_camera_t *cam);
bool dcvs_draw_sprite(dcvs *c, const dgfx_sprite_t *spr);
bool dcvs_draw_line(dcvs *c, const dgfx_line_segment_t *line);
bool dcvs_draw_mesh(dcvs *c, const dgfx_mesh_draw_t *mesh);
bool dcvs_draw_text(dcvs *c, const dgfx_text_draw_t *text);
/* Future: set_pipeline, set_texture, batched sprites/meshes */

/*------------------------------------------------------------
 * Legacy canvas bridge (dom_canvas_*)
 *------------------------------------------------------------*/
typedef struct dom_canvas dom_canvas;

typedef struct dom_gfx_buffer {
    uint8_t *data;
    size_t   size;
    size_t   capacity;
} dom_gfx_buffer;

bool dom_canvas_build(dom_core *core,
                      dom_instance_id inst,
                      const char *canvas_id,
                      dom_gfx_buffer *out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_CANVAS_H_INCLUDED */
