#include "domino/audio.h"

#include <stdlib.h>
#include <string.h>

struct daudio_context {
    daudio_desc desc;
};

struct daudio_buffer {
    float*   samples;
    uint32_t frame_count;
    uint32_t channel_count;
};

daudio_context* daudio_init(const daudio_desc* desc)
{
    daudio_context* ctx;
    daudio_desc local_desc;

    ctx = (daudio_context*)malloc(sizeof(daudio_context));
    if (!ctx) {
        return NULL;
    }

    memset(&local_desc, 0, sizeof(local_desc));
    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.sample_rate = 48000u;
        local_desc.channels = 2u;
        local_desc.buffer_frames = 0u;
    }

    ctx->desc = local_desc;
    return ctx;
}

void daudio_shutdown(daudio_context* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

daudio_caps daudio_get_caps(daudio_context* ctx)
{
    daudio_caps caps;
    (void)ctx;
    caps.name = "null";
    caps.max_channels = 0u;
    caps.supports_streams = false;
    caps.supports_3d = false;
    return caps;
}

daudio_buffer* daudio_buffer_create(daudio_context* ctx,
                                    const float* interleaved_samples,
                                    uint32_t frame_count,
                                    uint32_t channel_count)
{
    daudio_buffer* buf;
    size_t bytes;

    (void)ctx;
    buf = (daudio_buffer*)malloc(sizeof(daudio_buffer));
    if (!buf) {
        return NULL;
    }
    buf->samples = NULL;
    buf->frame_count = frame_count;
    buf->channel_count = channel_count;

    bytes = (size_t)frame_count * (size_t)channel_count * sizeof(float);
    if (interleaved_samples && bytes > 0u) {
        buf->samples = (float*)malloc(bytes);
        if (buf->samples) {
            memcpy(buf->samples, interleaved_samples, bytes);
        }
    }

    return buf;
}

void daudio_buffer_destroy(daudio_context* ctx, daudio_buffer* buffer)
{
    (void)ctx;
    if (!buffer) {
        return;
    }
    if (buffer->samples) {
        free(buffer->samples);
    }
    free(buffer);
}

daudio_voice_id daudio_play(daudio_context* ctx, const daudio_buffer* buffer, int loop)
{
    (void)ctx;
    (void)buffer;
    (void)loop;
    return 0u;
}

void daudio_stop(daudio_context* ctx, daudio_voice_id voice)
{
    (void)ctx;
    (void)voice;
}

void daudio_set_gain(daudio_context* ctx, daudio_voice_id voice, float gain)
{
    (void)ctx;
    (void)voice;
    (void)gain;
}

void daudio_set_pan(daudio_context* ctx, daudio_voice_id voice, float pan)
{
    (void)ctx;
    (void)voice;
    (void)pan;
}

daudio_voice_id daudio_play_stream(daudio_context* ctx)
{
    (void)ctx;
    return 0u;
}
