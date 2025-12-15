#include <stdlib.h>
#include <string.h>

#include "domino/gfx.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "d_gfx_internal.h"
#include "soft/d_gfx_soft.h"
#include "null/d_gfx_null.h"
#include "dx9/d_gfx_dx9.h"
#include "dx11/d_gfx_dx11.h"
#include "gl2/d_gfx_gl2.h"
#include "vk1/d_gfx_vk1.h"
#include "metal/d_gfx_metal.h"

/* Backbuffer defaults */
static i32 g_backbuffer_w = 800;
static i32 g_backbuffer_h = 600;
static void* g_native_window = 0;

static const d_gfx_backend_soft *g_backend = 0;
static d_gfx_cmd_buffer g_frame_cmd_buffer;

static dom_abi_result dgfx_ir_query_interface(dom_iid iid, void** out_iface);

void* d_gfx_get_native_window(void)
{
    return g_native_window;
}

static const dgfx_ir_api_v1 g_dgfx_ir_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dgfx_ir_api_v1),
    dgfx_ir_query_interface,
    d_gfx_init,
    d_gfx_shutdown,
    d_gfx_cmd_buffer_begin,
    d_gfx_cmd_buffer_end,
    d_gfx_cmd_clear,
    d_gfx_cmd_set_viewport,
    d_gfx_cmd_set_camera,
    d_gfx_cmd_draw_rect,
    d_gfx_cmd_draw_text,
    d_gfx_submit,
    d_gfx_present,
    d_gfx_get_surface_size
};

static const void* dgfx_caps_get_ir_api_ptr(u32 requested_abi)
{
    if (requested_abi != g_dgfx_ir_api_v1.abi_version) {
        return (const void*)0;
    }
    return (const void*)&g_dgfx_ir_api_v1;
}

dom_caps_result dom_dgfx_register_caps_backends(void)
{
    dom_backend_desc desc;
    dom_caps_result r;

    memset(&desc, 0, sizeof(desc));
    desc.abi_version = DOM_CAPS_ABI_VERSION;
    desc.struct_size = (u32)sizeof(dom_backend_desc);

    desc.subsystem_id = DOM_SUBSYS_DGFX;
    desc.subsystem_name = "gfx";
    desc.required_hw_flags = 0u;
    desc.subsystem_flags = DOM_CAPS_SUBSYS_LOCKSTEP_RELEVANT;
    desc.backend_flags = DOM_CAPS_BACKEND_PRESENTATION_ONLY;
    desc.perf_class = DOM_CAPS_PERF_BASELINE;
    desc.get_api = dgfx_caps_get_ir_api_ptr;
    desc.probe = (dom_caps_probe_fn)0;

#if DOM_BACKEND_SOFT
    desc.backend_name = "soft";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D0_BIT_EXACT;
    r = dom_caps_register_backend(&desc);
    if (r != DOM_CAPS_OK) {
        return r;
    }
#endif

#if DOM_BACKEND_DX9
    desc.backend_name = "dx9";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = DOM_HW_OS_WIN32;
    r = dom_caps_register_backend(&desc);
    if (r != DOM_CAPS_OK) {
        return r;
    }
#endif

#if DOM_BACKEND_DX11
    desc.backend_name = "dx11";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = DOM_HW_OS_WIN32;
    r = dom_caps_register_backend(&desc);
    if (r != DOM_CAPS_OK) {
        return r;
    }
#endif

#if DOM_BACKEND_GL2
    desc.backend_name = "gl2";
    desc.backend_priority = 90u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_COMPAT;
    desc.required_hw_flags = DOM_HW_OS_WIN32;
    r = dom_caps_register_backend(&desc);
    if (r != DOM_CAPS_OK) {
        return r;
    }
#endif

#if DOM_BACKEND_VK1
    desc.backend_name = "vk1";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = 0u;
    r = dom_caps_register_backend(&desc);
    if (r != DOM_CAPS_OK) {
        return r;
    }
#endif

#if DOM_BACKEND_METAL
    desc.backend_name = "metal";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = DOM_HW_OS_APPLE;
    r = dom_caps_register_backend(&desc);
    if (r != DOM_CAPS_OK) {
        return r;
    }
#endif

#if DOM_BACKEND_NULL
    desc.backend_name = "null";
    desc.backend_priority = 10u;
    desc.determinism = DOM_DET_D0_BIT_EXACT;
    desc.perf_class = DOM_CAPS_PERF_BASELINE;
    desc.required_hw_flags = 0u;
    return dom_caps_register_backend(&desc);
#else
    return DOM_CAPS_OK;
#endif
}

static dom_abi_result dgfx_ir_query_interface(dom_iid iid, void** out_iface)
{
    if (!out_iface) {
        return DGFX_ERR;
    }
    *out_iface = NULL;

    switch (iid) {
    case DGFX_IID_IR_API_V1:
        *out_iface = (void*)&g_dgfx_ir_api_v1;
        return DGFX_OK;
    case DGFX_IID_NATIVE_API_V1:
        return DGFX_ERR_UNSUPPORTED;
    default:
        break;
    }

    return DGFX_ERR_UNSUPPORTED;
}

dgfx_result dgfx_get_ir_api(u32 requested_abi, dgfx_ir_api_v1* out)
{
    if (!out) {
        return DGFX_ERR;
    }
    if (requested_abi != g_dgfx_ir_api_v1.abi_version) {
        return DGFX_ERR_UNSUPPORTED;
    }
    *out = g_dgfx_ir_api_v1;
    return DGFX_OK;
}

static int d_gfx_reserve(d_gfx_cmd_buffer *buf, u32 needed)
{
    d_gfx_cmd *new_cmds;
    u32 new_cap;

    if (!buf) {
        return 0;
    }
    if (buf->capacity >= needed) {
        return 1;
    }

    new_cap = buf->capacity ? buf->capacity : 1024u;
    while (new_cap < needed) {
        new_cap *= 2u;
    }

    new_cmds = (d_gfx_cmd *)realloc(buf->cmds, new_cap * sizeof(d_gfx_cmd));
    if (!new_cmds) {
        return 0;
    }
    buf->cmds = new_cmds;
    buf->capacity = new_cap;
    return 1;
}

static void d_gfx_append(d_gfx_cmd_buffer *buf, const d_gfx_cmd *cmd)
{
    if (!buf || !cmd) {
        return;
    }
    if (!d_gfx_reserve(buf, buf->count + 1u)) {
        return;
    }
    buf->cmds[buf->count++] = *cmd;
}

int d_gfx_init(const char *backend_name)
{
    const d_gfx_backend_soft *chosen;
    const int have_request = (backend_name && backend_name[0]) ? 1 : 0;
    chosen = (const d_gfx_backend_soft*)0;

#if DOM_BACKEND_SOFT
    d_gfx_soft_set_framebuffer_size(g_backbuffer_w, g_backbuffer_h);
#endif

#if DOM_BACKEND_NULL
    if (have_request && strcmp(backend_name, "null") == 0) {
        chosen = d_gfx_null_register_backend();
    }
#endif

#if DOM_BACKEND_SOFT
    if ((have_request && strcmp(backend_name, "soft") == 0) && !chosen) {
        chosen = d_gfx_soft_register_backend();
    }
#endif

#if DOM_BACKEND_DX9
    if (have_request && strcmp(backend_name, "dx9") == 0) {
        chosen = d_gfx_dx9_register_backend();
    }
#endif

#if DOM_BACKEND_DX11
    if (have_request && strcmp(backend_name, "dx11") == 0) {
        chosen = d_gfx_dx11_register_backend();
    }
#endif

#if DOM_BACKEND_GL2
    if (have_request && strcmp(backend_name, "gl2") == 0) {
        chosen = d_gfx_gl2_register_backend();
    }
#endif

#if DOM_BACKEND_VK1
    if (have_request && strcmp(backend_name, "vk1") == 0) {
        chosen = d_gfx_vk1_register_backend();
    }
#endif

#if DOM_BACKEND_METAL
    if (have_request && strcmp(backend_name, "metal") == 0) {
        chosen = d_gfx_metal_register_backend();
    }
#endif

#if DOM_BACKEND_SOFT
    if (!have_request && !chosen) {
        chosen = d_gfx_soft_register_backend();
    }
#endif

#if DOM_BACKEND_DX9
    if (!have_request && !chosen) {
        chosen = d_gfx_dx9_register_backend();
    }
#endif

#if DOM_BACKEND_NULL
    if (!have_request && !chosen) {
        chosen = d_gfx_null_register_backend();
    }
#endif

    if (have_request && !chosen) {
        return 0;
    }

    if (!chosen || !chosen->init) {
        return 0;
    }
    if (chosen->init() != 0) {
        return 0;
    }
    g_backend = chosen;
    return 1;
}

void d_gfx_shutdown(void)
{
    if (g_backend && g_backend->shutdown) {
        g_backend->shutdown();
    }
    g_backend = 0;
    if (g_frame_cmd_buffer.cmds) {
        free(g_frame_cmd_buffer.cmds);
        g_frame_cmd_buffer.cmds = (d_gfx_cmd *)0;
    }
    g_frame_cmd_buffer.count = 0u;
    g_frame_cmd_buffer.capacity = 0u;
}

d_gfx_cmd_buffer *d_gfx_cmd_buffer_begin(void)
{
    if (!g_frame_cmd_buffer.cmds) {
        if (!d_gfx_reserve(&g_frame_cmd_buffer, 1024u)) {
            return (d_gfx_cmd_buffer *)0;
        }
    }
    g_frame_cmd_buffer.count = 0u;
    return &g_frame_cmd_buffer;
}

void d_gfx_cmd_buffer_end(d_gfx_cmd_buffer *buf)
{
    (void)buf;
}

void d_gfx_cmd_clear(d_gfx_cmd_buffer *buf, d_gfx_color color)
{
    d_gfx_cmd cmd;
    cmd.opcode = D_GFX_OP_CLEAR;
    cmd.u.clear.color = color;
    d_gfx_append(buf, &cmd);
}

void d_gfx_cmd_set_viewport(d_gfx_cmd_buffer *buf, const d_gfx_viewport *vp)
{
    d_gfx_cmd cmd;
    if (!vp) {
        return;
    }
    cmd.opcode = D_GFX_OP_SET_VIEWPORT;
    cmd.u.viewport.vp = *vp;
    d_gfx_append(buf, &cmd);
}

void d_gfx_cmd_set_camera(d_gfx_cmd_buffer *buf, const d_gfx_camera *cam)
{
    d_gfx_cmd cmd;
    if (!cam) {
        return;
    }
    cmd.opcode = D_GFX_OP_SET_CAMERA;
    cmd.u.camera.cam = *cam;
    d_gfx_append(buf, &cmd);
}

void d_gfx_cmd_draw_rect(d_gfx_cmd_buffer *buf, const d_gfx_draw_rect_cmd *rect)
{
    d_gfx_cmd cmd;
    if (!rect) {
        return;
    }
    cmd.opcode = D_GFX_OP_DRAW_RECT;
    cmd.u.rect = *rect;
    d_gfx_append(buf, &cmd);
}

void d_gfx_cmd_draw_text(d_gfx_cmd_buffer *buf, const d_gfx_draw_text_cmd *text)
{
    d_gfx_cmd cmd;
    if (!text) {
        return;
    }
    cmd.opcode = D_GFX_OP_DRAW_TEXT;
    cmd.u.text = *text;
    d_gfx_append(buf, &cmd);
}

void d_gfx_submit(d_gfx_cmd_buffer *buf)
{
    if (g_backend && g_backend->submit_cmd_buffer) {
        g_backend->submit_cmd_buffer(buf);
    }
}

void d_gfx_present(void)
{
    if (g_backend && g_backend->present) {
        g_backend->present();
    }
}

void d_gfx_get_surface_size(i32 *out_w, i32 *out_h)
{
    if (out_w) {
        *out_w = g_backbuffer_w;
    }
    if (out_h) {
        *out_h = g_backbuffer_h;
    }
}

/* ------------------------------------------------------------
 * Legacy wrappers
 * ------------------------------------------------------------ */

static d_gfx_color d_gfx_color_from_rgba(u32 rgba)
{
    d_gfx_color c;
    c.a = (u8)((rgba >> 24) & 0xffu);
    c.r = (u8)((rgba >> 16) & 0xffu);
    c.g = (u8)((rgba >> 8) & 0xffu);
    c.b = (u8)(rgba & 0xffu);
    return c;
}

static int d_gfx_abs_i32(int v)
{
    return (v < 0) ? -v : v;
}

int dgfx_init(const dgfx_desc *desc)
{
    dgfx_ir_api_v1 api;
    const char* backend_name;
    g_native_window = 0;
    if (desc) {
        if (desc->width > 0) g_backbuffer_w = desc->width;
        if (desc->height > 0) g_backbuffer_h = desc->height;
        g_native_window = desc->native_window;
        if (desc->backend == DGFX_BACKEND_NULL) {
            return 1;
        }
    }
    if (dgfx_get_ir_api(1u, &api) != DGFX_OK) {
        return 0;
    }
    backend_name = "soft";
    if (desc) {
        if (desc->backend == DGFX_BACKEND_SOFT) backend_name = "soft";
        else if (desc->backend == DGFX_BACKEND_DX9) backend_name = "dx9";
        else if (desc->backend == DGFX_BACKEND_DX11) backend_name = "dx11";
        else if (desc->backend == DGFX_BACKEND_GL2) backend_name = "gl2";
        else if (desc->backend == DGFX_BACKEND_VK1) backend_name = "vk1";
        else if (desc->backend == DGFX_BACKEND_METAL) backend_name = "metal";
        else if (desc->backend == DGFX_BACKEND_NULL) backend_name = "null";
        else if (desc->backend != 0) {
            return 0;
        }
    }
    return api.init(backend_name);
}

void dgfx_shutdown(void)
{
    dgfx_ir_api_v1 api;
    if (dgfx_get_ir_api(1u, &api) == DGFX_OK) {
        api.shutdown();
    }
    g_native_window = 0;
}

void dgfx_begin_frame(void)
{
    dgfx_ir_api_v1 api;
    if (dgfx_get_ir_api(1u, &api) == DGFX_OK) {
        (void)api.cmd_buffer_begin();
    }
}

void dgfx_execute(const dgfx_cmd_buffer *cmd)
{
    dgfx_ir_api_v1 api;
    if (dgfx_get_ir_api(1u, &api) == DGFX_OK) {
        api.submit((d_gfx_cmd_buffer *)cmd);
    }
}

void dgfx_end_frame(void)
{
    dgfx_ir_api_v1 api;
    if (dgfx_get_ir_api(1u, &api) == DGFX_OK) {
        api.present();
    }
}

dgfx_cmd_buffer *dgfx_get_frame_cmd_buffer(void)
{
    dgfx_ir_api_v1 api;
    if (dgfx_get_ir_api(1u, &api) != DGFX_OK) {
        return (dgfx_cmd_buffer *)0;
    }
    return (dgfx_cmd_buffer *)api.cmd_buffer_begin();
}

void dgfx_cmd_buffer_reset(dgfx_cmd_buffer *buf)
{
    if (buf) {
        buf->count = 0u;
    }
}

int dgfx_cmd_emit(dgfx_cmd_buffer *buf,
                  u16 opcode,
                  const void *payload,
                  u16 payload_size)
{
    dgfx_ir_api_v1 api;
    u32 count;
    u32 i;

    if (!buf) {
        return 0;
    }
    if (dgfx_get_ir_api(1u, &api) != DGFX_OK) {
        return 0;
    }

    switch (opcode) {
    case DGFX_CMD_CLEAR:
        if (payload && payload_size >= sizeof(u32)) {
            api.cmd_clear(buf, d_gfx_color_from_rgba(*(const u32 *)payload));
            return 1;
        }
        return 0;
    case DGFX_CMD_SET_VIEWPORT:
        if (payload && payload_size >= sizeof(dgfx_viewport_t)) {
            d_gfx_viewport vp;
            const dgfx_viewport_t *p = (const dgfx_viewport_t *)payload;
            vp.x = p->x;
            vp.y = p->y;
            vp.w = p->w;
            vp.h = p->h;
            api.cmd_set_viewport(buf, &vp);
            return 1;
        }
        return 0;
    case DGFX_CMD_SET_CAMERA:
        if (payload && payload_size >= sizeof(dgfx_camera_t)) {
            const dgfx_camera_t *cam = (const dgfx_camera_t *)payload;
            api.cmd_set_camera(buf, cam);
            return 1;
        }
        return 0;
    case DGFX_CMD_DRAW_SPRITES:
        if (!payload || payload_size < sizeof(dgfx_sprite_t)) {
            return 0;
        }
        count = payload_size / (u16)sizeof(dgfx_sprite_t);
        for (i = 0u; i < count; ++i) {
            const dgfx_sprite_t *spr = ((const dgfx_sprite_t *)payload) + i;
            d_gfx_draw_rect_cmd cmd;
            cmd.x = spr->x;
            cmd.y = spr->y;
            cmd.w = spr->w;
            cmd.h = spr->h;
            cmd.color = d_gfx_color_from_rgba(spr->color_rgba);
            api.cmd_draw_rect(buf, &cmd);
        }
        return 1;
    case DGFX_CMD_DRAW_TEXT:
        if (payload && payload_size >= sizeof(dgfx_text_draw_t)) {
            const dgfx_text_draw_t *td = (const dgfx_text_draw_t *)payload;
            d_gfx_draw_text_cmd cmd;
            cmd.x = td->x;
            cmd.y = td->y;
            cmd.text = td->utf8_text;
            cmd.color = d_gfx_color_from_rgba(td->color_rgba);
            api.cmd_draw_text(buf, &cmd);
            return 1;
        }
        return 0;
    case DGFX_CMD_DRAW_LINES:
        if (!payload || payload_size < sizeof(dgfx_line_segment_t)) {
            return 0;
        }
        count = payload_size / (u16)sizeof(dgfx_line_segment_t);
        for (i = 0u; i < count; ++i) {
            const dgfx_line_segment_t *ln = ((const dgfx_line_segment_t *)payload) + i;
            int x0 = ln->x0;
            int y0 = ln->y0;
            int x1 = ln->x1;
            int y1 = ln->y1;
            int thickness = ln->thickness;
            int dx;
            int sx;
            int dy;
            int sy;
            int err;
            d_gfx_color col = d_gfx_color_from_rgba(ln->color_rgba);

            if (thickness < 1) {
                thickness = 1;
            }

            dx = d_gfx_abs_i32(x1 - x0);
            sx = (x0 < x1) ? 1 : -1;
            dy = -d_gfx_abs_i32(y1 - y0);
            sy = (y0 < y1) ? 1 : -1;
            err = dx + dy;

            while (1) {
                d_gfx_draw_rect_cmd r;
                int half = thickness / 2;
                r.x = x0 - half;
                r.y = y0 - half;
                r.w = thickness;
                r.h = thickness;
                r.color = col;
                api.cmd_draw_rect(buf, &r);

                if (x0 == x1 && y0 == y1) {
                    break;
                }
                {
                    int e2 = 2 * err;
                    if (e2 >= dy) {
                        err += dy;
                        x0 += sx;
                    }
                    if (e2 <= dx) {
                        err += dx;
                        y0 += sy;
                    }
                }
            }
        }
        return 1;
    default:
        return 0;
    }
}
