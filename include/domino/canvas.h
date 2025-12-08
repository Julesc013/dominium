#ifndef DOMINO_CANVAS_H_INCLUDED
#define DOMINO_CANVAS_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_canvas dom_canvas;

typedef enum dom_canvas_format {
    DOM_CANVAS_FORMAT_UNKNOWN = 0,
    DOM_CANVAS_FORMAT_RGBA8,
    DOM_CANVAS_FORMAT_BGRA8
} dom_canvas_format;

typedef struct dom_canvas_desc {
    uint32_t          struct_size;
    uint32_t          struct_version;
    uint32_t          width;
    uint32_t          height;
    dom_canvas_format format;
} dom_canvas_desc;

typedef struct dom_canvas_surface {
    uint32_t        struct_size;
    uint32_t        struct_version;
    void*           pixels;
    uint32_t        pitch_bytes;
    dom_canvas_desc desc;
} dom_canvas_surface;

dom_status dom_canvas_create(const dom_canvas_desc* desc, dom_canvas** out_canvas);
void       dom_canvas_destroy(dom_canvas* canvas);
dom_status dom_canvas_lock(dom_canvas* canvas, dom_canvas_surface* out_surface);
void       dom_canvas_unlock(dom_canvas* canvas);
dom_status dom_canvas_present(dom_canvas* canvas);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_CANVAS_H_INCLUDED */
