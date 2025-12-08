#ifndef DOMINO_CANVAS_H_INCLUDED
#define DOMINO_CANVAS_H_INCLUDED

#include <stddef.h>
#include <stdint.h>
#include "domino/core.h"
#include "domino/inst.h"

#ifdef __cplusplus
extern "C" {
#endif

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
