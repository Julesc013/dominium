#include "domino/audio.h"

#include <stdlib.h>
#include <string.h>

struct daudio_device {
    daudio_device_desc desc;
};

dom_status daudio_create_device(const daudio_device_desc* desc, daudio_device** out_device)
{
    daudio_device* dev;
    daudio_device_desc local_desc;

    if (!out_device) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_device = NULL;

    dev = (daudio_device*)malloc(sizeof(daudio_device));
    if (!dev) {
        return DOM_STATUS_ERROR;
    }
    memset(dev, 0, sizeof(*dev));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
        local_desc.sample_rate = 48000u;
        local_desc.channel_count = 2u;
        local_desc.buffer_frames = 0u;
    }

    dev->desc = local_desc;
    dev->desc.struct_size = sizeof(daudio_device_desc);
    dev->desc.struct_version = local_desc.struct_version;

    *out_device = dev;
    return DOM_STATUS_OK;
}

void daudio_destroy_device(daudio_device* device)
{
    if (!device) {
        return;
    }
    free(device);
}

dom_status daudio_submit_buffer(daudio_device* device, const daudio_buffer* buffer)
{
    (void)device;
    (void)buffer;
    return DOM_STATUS_OK;
}

dom_status daudio_get_latency_ms(daudio_device* device, uint32_t* out_latency_ms)
{
    (void)device;
    if (!out_latency_ms) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_latency_ms = 0u;
    return DOM_STATUS_OK;
}
