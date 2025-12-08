#include "domino/gfx.h"

#include <stdlib.h>
#include <string.h>

struct dgfx_context {
    dgfx_desc desc;
};

dgfx_context* dgfx_init(const dgfx_desc* desc)
{
    dgfx_context* ctx;
    dgfx_desc local_desc;

    ctx = (dgfx_context*)malloc(sizeof(dgfx_context));
    if (!ctx) {
        return NULL;
    }

    memset(&local_desc, 0, sizeof(local_desc));
    if (desc) {
        local_desc = *desc;
    }

    ctx->desc = local_desc;
    return ctx;
}

void dgfx_shutdown(dgfx_context* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

dgfx_caps dgfx_get_caps(dgfx_context* ctx)
{
    dgfx_caps caps;
    (void)ctx;
    caps.name = "null";
    caps.supports_2d = false;
    caps.supports_3d = false;
    caps.supports_text = false;
    caps.supports_rt = false;
    caps.supports_alpha = false;
    caps.max_texture_size = 0;
    return caps;
}

void dgfx_resize(dgfx_context* ctx, int32_t width, int32_t height)
{
    if (!ctx) {
        return;
    }
    ctx->desc.width = width;
    ctx->desc.height = height;
}

void dgfx_cmd_buffer_reset(dgfx_cmd_buffer* buf)
{
    if (!buf) {
        return;
    }
    buf->size = 0;
}

bool dgfx_cmd_emit(dgfx_cmd_buffer* buf,
                   dgfx_opcode op,
                   const void* payload,
                   uint16_t payload_size)
{
    uint32_t required;
    dgfx_cmd* cmd;
    uint8_t* dst;

    if (!buf || !buf->data) {
        return false;
    }
    if (buf->size > buf->capacity) {
        return false;
    }

    required = (uint32_t)buf->size + sizeof(dgfx_cmd) + (uint32_t)payload_size;
    if (required > buf->capacity) {
        return false;
    }

    cmd = (dgfx_cmd*)(buf->data + buf->size);
    cmd->op = op;
    cmd->payload_size = payload_size;

    dst = (uint8_t*)cmd + sizeof(dgfx_cmd);
    if (payload && payload_size > 0) {
        memcpy(dst, payload, payload_size);
    } else if (payload_size > 0) {
        memset(dst, 0, payload_size);
    }

    buf->size = (uint16_t)required;
    return true;
}

void dgfx_begin_frame(dgfx_context* ctx)
{
    (void)ctx;
}

void dgfx_execute(dgfx_context* ctx, const dgfx_cmd_buffer* buf)
{
    (void)ctx;
    (void)buf;
}

void dgfx_end_frame(dgfx_context* ctx)
{
    (void)ctx;
}
