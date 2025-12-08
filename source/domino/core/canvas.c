#include "domino/canvas.h"

#include <stdlib.h>
#include <string.h>

struct dom_canvas {
    dom_canvas_desc desc;
    void*           pixels;
};

dom_status dom_canvas_create(const dom_canvas_desc* desc, dom_canvas** out_canvas)
{
    dom_canvas* canvas;
    dom_canvas_desc local_desc;

    if (!out_canvas) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_canvas = NULL;

    canvas = (dom_canvas*)malloc(sizeof(dom_canvas));
    if (!canvas) {
        return DOM_STATUS_ERROR;
    }
    memset(canvas, 0, sizeof(*canvas));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
        local_desc.format = DOM_CANVAS_FORMAT_RGBA8;
    }
    local_desc.struct_size = sizeof(dom_canvas_desc);
    canvas->desc = local_desc;
    canvas->pixels = NULL;

    *out_canvas = canvas;
    return DOM_STATUS_OK;
}

void dom_canvas_destroy(dom_canvas* canvas)
{
    if (!canvas) {
        return;
    }
    if (canvas->pixels) {
        free(canvas->pixels);
    }
    free(canvas);
}

dom_status dom_canvas_lock(dom_canvas* canvas, dom_canvas_surface* out_surface)
{
    if (!canvas || !out_surface) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    memset(out_surface, 0, sizeof(*out_surface));
    out_surface->struct_size = sizeof(dom_canvas_surface);
    out_surface->struct_version = 1u;
    out_surface->pixels = canvas->pixels;
    out_surface->pitch_bytes = 0u;
    out_surface->desc = canvas->desc;
    return DOM_STATUS_OK;
}

void dom_canvas_unlock(dom_canvas* canvas)
{
    (void)canvas;
}

dom_status dom_canvas_present(dom_canvas* canvas)
{
    (void)canvas;
    return DOM_STATUS_OK;
}
