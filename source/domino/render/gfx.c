#include "domino/gfx.h"

#include <stdlib.h>
#include <string.h>

struct dgfx_context {
    dgfx_desc                    desc;
    const dgfx_backend_vtable*   vtable;
};

static const dgfx_backend_vtable* g_dgfx = NULL;

static bool dgfx_null_init(const dgfx_desc* desc);
static void dgfx_null_shutdown(void);
static dgfx_caps dgfx_null_get_caps(void);
static void dgfx_null_resize(int width, int height);
static void dgfx_null_begin_frame(void);
static void dgfx_null_execute(const dgfx_cmd_buffer* buf);
static void dgfx_null_end_frame(void);

static const dgfx_backend_vtable g_dgfx_null_vtable = {
    dgfx_null_init,
    dgfx_null_shutdown,
    dgfx_null_get_caps,
    dgfx_null_resize,
    dgfx_null_begin_frame,
    dgfx_null_execute,
    dgfx_null_end_frame
};

static bool dgfx_null_init(const dgfx_desc* desc)
{
    (void)desc;
    return true;
}

static void dgfx_null_shutdown(void)
{
}

static dgfx_caps dgfx_null_get_caps(void)
{
    dgfx_caps caps;
    caps.name = "null";
    caps.supports_2d = false;
    caps.supports_3d = false;
    caps.supports_text = false;
    caps.supports_rt = false;
    caps.supports_alpha = false;
    caps.max_texture_size = 0;
    return caps;
}

static void dgfx_null_resize(int width, int height)
{
    (void)width;
    (void)height;
}

static void dgfx_null_begin_frame(void)
{
}

static void dgfx_null_execute(const dgfx_cmd_buffer* buf)
{
    (void)buf;
}

static void dgfx_null_end_frame(void)
{
}

dgfx_context* dgfx_init(const dgfx_desc* desc)
{
    dgfx_context* ctx;
    dgfx_desc local_desc;
    const dgfx_desc* init_desc;

    ctx = (dgfx_context*)malloc(sizeof(dgfx_context));
    if (!ctx) {
        return NULL;
    }

    memset(&local_desc, 0, sizeof(local_desc));
    if (desc) {
        local_desc = *desc;
    }
    ctx->desc = local_desc;
    ctx->vtable = &g_dgfx_null_vtable;
    g_dgfx = &g_dgfx_null_vtable;
    init_desc = &ctx->desc;

    switch (ctx->desc.backend) {
    case DGFX_BACKEND_DX9:
#if defined(_WIN32)
        {
            extern const dgfx_backend_vtable* dgfx_dx9_get_vtable(void);
            g_dgfx = dgfx_dx9_get_vtable();
        }
#else
        g_dgfx = &g_dgfx_null_vtable;
#endif
        break;
    case DGFX_BACKEND_DX11:
#if defined(_WIN32)
        {
            extern const dgfx_backend_vtable* dgfx_dx11_get_vtable(void);
            g_dgfx = dgfx_dx11_get_vtable();
        }
#else
        g_dgfx = &g_dgfx_null_vtable;
#endif
        break;
    default:
        g_dgfx = &g_dgfx_null_vtable;
        break;
    }

    ctx->vtable = g_dgfx;

    if (!ctx->vtable || !ctx->vtable->init(init_desc)) {
        ctx->vtable = &g_dgfx_null_vtable;
        g_dgfx = &g_dgfx_null_vtable;
        if (!g_dgfx->init(init_desc)) {
            free(ctx);
            return NULL;
        }
    }

    return ctx;
}

void dgfx_shutdown(dgfx_context* ctx)
{
    if (!ctx) {
        return;
    }
    if (g_dgfx && g_dgfx->shutdown) {
        g_dgfx->shutdown();
    }
    g_dgfx = NULL;
    ctx->vtable = NULL;
    free(ctx);
}

dgfx_caps dgfx_get_caps(dgfx_context* ctx)
{
    (void)ctx;
    if (g_dgfx && g_dgfx->get_caps) {
        return g_dgfx->get_caps();
    }
    return dgfx_null_get_caps();
}

void dgfx_resize(dgfx_context* ctx, int32_t width, int32_t height)
{
    if (!ctx) {
        return;
    }
    ctx->desc.width = width;
    ctx->desc.height = height;
    if (g_dgfx && g_dgfx->resize) {
        g_dgfx->resize(width, height);
    }
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
    if (g_dgfx && g_dgfx->begin_frame) {
        g_dgfx->begin_frame();
    }
}

void dgfx_execute(dgfx_context* ctx, const dgfx_cmd_buffer* buf)
{
    (void)ctx;
    if (g_dgfx && g_dgfx->execute) {
        g_dgfx->execute(buf);
    }
}

void dgfx_end_frame(dgfx_context* ctx)
{
    (void)ctx;
    if (g_dgfx && g_dgfx->end_frame) {
        g_dgfx->end_frame();
    }
}
