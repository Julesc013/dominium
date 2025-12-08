#include "domino/gfx.h"
#include "domino/canvas.h"

#include <stdlib.h>
#include <string.h>

struct dgfx_device {
    dgfx_device_desc desc;
    dom_canvas*      canvas;
};

int dgfx_create_device(const dgfx_device_desc* desc, dgfx_device** out_device)
{
    dgfx_device* dev;
    dgfx_device_desc local_desc;
    dom_canvas_desc canvas_desc;

    if (!out_device) {
        return -1;
    }
    *out_device = NULL;

    dev = (dgfx_device*)malloc(sizeof(dgfx_device));
    if (!dev) {
        return -1;
    }
    memset(dev, 0, sizeof(*dev));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
        local_desc.backend = DGFX_BACKEND_DEFAULT;
    }

    dev->desc = local_desc;
    dev->desc.struct_size = sizeof(dgfx_device_desc);
    dev->desc.struct_version = local_desc.struct_version;

    canvas_desc.struct_size = sizeof(dom_canvas_desc);
    canvas_desc.struct_version = 1u;
    canvas_desc.width = local_desc.width;
    canvas_desc.height = local_desc.height;
    canvas_desc.format = DOM_CANVAS_FORMAT_RGBA8;

    if (dom_canvas_create(&canvas_desc, &dev->canvas) != DOM_STATUS_OK) {
        dev->canvas = NULL;
    }

    *out_device = dev;
    return 0;
}

void dgfx_destroy_device(dgfx_device* device)
{
    if (!device) {
        return;
    }
    if (device->canvas) {
        dom_canvas_destroy(device->canvas);
    }
    free(device);
}

dgfx_backend dgfx_get_backend(dgfx_device* device)
{
    if (!device) {
        return DGFX_BACKEND_DEFAULT;
    }
    return device->desc.backend;
}

int dgfx_resize(dgfx_device* device, uint32_t width, uint32_t height)
{
    if (!device) {
        return -1;
    }
    device->desc.width = width;
    device->desc.height = height;
    return 0;
}

int dgfx_begin_frame(dgfx_device* device)
{
    (void)device;
    return 0;
}

int dgfx_end_frame(dgfx_device* device)
{
    (void)device;
    return 0;
}

int dgfx_get_canvas(dgfx_device* device, dom_canvas** out_canvas)
{
    if (!device || !out_canvas) {
        return -1;
    }
    *out_canvas = device->canvas;
    return 0;
}
