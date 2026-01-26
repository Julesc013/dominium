/*
FILE: source/domino/render/d_gfx.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/d_gfx
RESPONSIBILITY: Implements `d_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `include/render/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "domino/gfx.h"
#include "render/d_gfx_caps.h"
#include "render/dgfx_trace.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/sys.h"
#include "soft/d_gfx_soft.h"
#include "render/null/d_gfx_null.h"

/* Backbuffer defaults */
static i32 g_backbuffer_w = 800;
static i32 g_backbuffer_h = 600;
static void* g_native_window = 0;
static const char* g_backend_name = 0;
static u32 g_backend_op_mask = 0u;

static const d_gfx_backend_soft *g_backend = 0;
static d_gfx_cmd_buffer g_frame_cmd_buffer;

static dom_abi_result dgfx_ir_query_interface(dom_iid iid, void** out_iface);

enum {
    DGFX_TRACE_GLYPH_W = 5,
    DGFX_TRACE_GLYPH_H = 7,
    DGFX_TRACE_GLYPH_ADV = 6,
    DGFX_TRACE_LINE_ADV = 8,
    DGFX_STALL_THRESHOLD_MS = 100
};

static void dgfx_trace_write_u32(unsigned char out[4], u32 v)
{
    out[0] = (unsigned char)(v & 0xffu);
    out[1] = (unsigned char)((v >> 8u) & 0xffu);
    out[2] = (unsigned char)((v >> 16u) & 0xffu);
    out[3] = (unsigned char)((v >> 24u) & 0xffu);
}

static void dgfx_trace_write_i32(unsigned char out[4], i32 v)
{
    dgfx_trace_write_u32(out, (u32)v);
}

static void dgfx_trace_record_u32(u16 kind, u32 v)
{
    unsigned char buf[4];
    dgfx_trace_write_u32(buf, v);
    dgfx_trace_record_backend_event(kind, buf, 4u);
}

static void dgfx_trace_record_bbox(i32 min_x, i32 min_y, i32 max_x, i32 max_y)
{
    unsigned char buf[16];
    dgfx_trace_write_i32(buf + 0, min_x);
    dgfx_trace_write_i32(buf + 4, min_y);
    dgfx_trace_write_i32(buf + 8, max_x);
    dgfx_trace_write_i32(buf + 12, max_y);
    dgfx_trace_record_backend_event(DGFX_TRACE_EVENT_BBOX, buf, 16u);
}

static u32 dgfx_elapsed_ms(u64 start_us, u64 end_us)
{
    if (end_us <= start_us) {
        return 0u;
    }
    return (u32)((end_us - start_us) / 1000ull);
}

static u32 dgfx_caps_mask_for_backend(const char* name)
{
    if (!name || !name[0]) {
        return 0u;
    }
    if (strcmp(name, "null") == 0) {
        return 0u;
    }
    return DGFX_CAP_OP_ALL;
}

static int dgfx_opcode_supported(u32 opcode)
{
    if (opcode >= 32u) {
        return 0;
    }
    return (g_backend_op_mask & (1u << opcode)) != 0u;
}

u32 d_gfx_get_opcode_mask(void)
{
    return g_backend_op_mask;
}

u32 d_gfx_get_opcode_mask_for_backend(const char* name)
{
    return dgfx_caps_mask_for_backend(name);
}

const char* d_gfx_get_backend_name(void)
{
    return g_backend_name ? g_backend_name : "";
}

static void dgfx_trace_text_metrics(const char *text, u32 *out_glyphs, i32 *out_w, i32 *out_h)
{
    u32 glyphs = 0u;
    u32 line_len = 0u;
    u32 max_line = 0u;
    u32 lines = 0u;

    if (!text || !text[0]) {
        if (out_glyphs) *out_glyphs = 0u;
        if (out_w) *out_w = 0;
        if (out_h) *out_h = 0;
        return;
    }
    lines = 1u;
    while (*text) {
        if (*text == '\n') {
            if (line_len > max_line) {
                max_line = line_len;
            }
            line_len = 0u;
            lines += 1u;
        } else {
            line_len += 1u;
            glyphs += 1u;
        }
        ++text;
    }
    if (line_len > max_line) {
        max_line = line_len;
    }
    if (out_glyphs) {
        *out_glyphs = glyphs;
    }
    if (out_w) {
        *out_w = (i32)(max_line * DGFX_TRACE_GLYPH_ADV);
    }
    if (out_h) {
        *out_h = (lines == 0u) ? 0 : (i32)((lines - 1u) * DGFX_TRACE_LINE_ADV + DGFX_TRACE_GLYPH_H);
    }
}

typedef struct dgfx_ir_buf {
    unsigned char *data;
    u32 size;
    u32 cap;
} dgfx_ir_buf;

static int dgfx_ir_reserve(dgfx_ir_buf *b, u32 need)
{
    unsigned char *p;
    u32 new_cap;
    if (!b) {
        return 0;
    }
    if (b->cap >= need) {
        return 1;
    }
    new_cap = b->cap ? b->cap : 256u;
    while (new_cap < need) {
        new_cap *= 2u;
    }
    p = (unsigned char *)realloc(b->data, (size_t)new_cap);
    if (!p) {
        return 0;
    }
    b->data = p;
    b->cap = new_cap;
    return 1;
}

static int dgfx_ir_append(dgfx_ir_buf *b, const void *data, u32 len)
{
    if (!b || (!data && len > 0u)) {
        return 0;
    }
    if (!dgfx_ir_reserve(b, b->size + len)) {
        return 0;
    }
    if (len > 0u) {
        memcpy(b->data + b->size, data, len);
        b->size += len;
    }
    return 1;
}

static int dgfx_ir_append_u16(dgfx_ir_buf *b, u16 v)
{
    unsigned char buf[2];
    buf[0] = (unsigned char)(v & 0xffu);
    buf[1] = (unsigned char)((v >> 8u) & 0xffu);
    return dgfx_ir_append(b, buf, 2u);
}

static int dgfx_ir_append_u32(dgfx_ir_buf *b, u32 v)
{
    unsigned char buf[4];
    dgfx_trace_write_u32(buf, v);
    return dgfx_ir_append(b, buf, 4u);
}

static int dgfx_ir_append_i32(dgfx_ir_buf *b, i32 v)
{
    return dgfx_ir_append_u32(b, (u32)v);
}

static void dgfx_trace_build_ir(const d_gfx_cmd_buffer *buf)
{
    dgfx_ir_buf b;
    u32 i;
    if (!buf || !buf->cmds) {
        return;
    }
    b.data = 0;
    b.size = 0u;
    b.cap = 0u;

    if (!dgfx_ir_append_u32(&b, 0x52494744u)) { /* 'DGIR' */
        if (b.data) free(b.data);
        return;
    }
    if (!dgfx_ir_append_u32(&b, 1u)) {
        if (b.data) free(b.data);
        return;
    }
    if (!dgfx_ir_append_u32(&b, 0x0000FFFEu)) {
        if (b.data) free(b.data);
        return;
    }
    if (!dgfx_ir_append_u32(&b, buf->count)) {
        if (b.data) free(b.data);
        return;
    }

    for (i = 0u; i < buf->count; ++i) {
        const d_gfx_cmd *cmd = buf->cmds + i;
        u16 opcode = (u16)cmd->opcode;
        dgfx_ir_buf payload;
        payload.data = 0;
        payload.size = 0u;
        payload.cap = 0u;

        switch (cmd->opcode) {
        case D_GFX_OP_CLEAR:
            dgfx_ir_append(&payload, &cmd->u.clear.color, 4u);
            break;
        case D_GFX_OP_SET_VIEWPORT:
            dgfx_ir_append_i32(&payload, cmd->u.viewport.vp.x);
            dgfx_ir_append_i32(&payload, cmd->u.viewport.vp.y);
            dgfx_ir_append_i32(&payload, cmd->u.viewport.vp.w);
            dgfx_ir_append_i32(&payload, cmd->u.viewport.vp.h);
            break;
        case D_GFX_OP_SET_CAMERA: {
            const d_gfx_camera *cam = &cmd->u.camera.cam;
            dgfx_ir_append_i32(&payload, cam->pos_x);
            dgfx_ir_append_i32(&payload, cam->pos_y);
            dgfx_ir_append_i32(&payload, cam->pos_z);
            dgfx_ir_append_i32(&payload, cam->dir_x);
            dgfx_ir_append_i32(&payload, cam->dir_y);
            dgfx_ir_append_i32(&payload, cam->dir_z);
            dgfx_ir_append_i32(&payload, cam->up_x);
            dgfx_ir_append_i32(&payload, cam->up_y);
            dgfx_ir_append_i32(&payload, cam->up_z);
            dgfx_ir_append_i32(&payload, cam->fov);
            break;
        }
        case D_GFX_OP_DRAW_RECT:
            dgfx_ir_append_i32(&payload, cmd->u.rect.x);
            dgfx_ir_append_i32(&payload, cmd->u.rect.y);
            dgfx_ir_append_i32(&payload, cmd->u.rect.w);
            dgfx_ir_append_i32(&payload, cmd->u.rect.h);
            dgfx_ir_append(&payload, &cmd->u.rect.color, 4u);
            break;
        case D_GFX_OP_DRAW_TEXT: {
            const char *text = cmd->u.text.text ? cmd->u.text.text : "";
            u32 text_len = (u32)strlen(text);
            u32 max_payload = 0xffffu - (4u + 4u + 4u + 4u);
            if (text_len > max_payload) {
                text_len = max_payload;
            }
            dgfx_ir_append_i32(&payload, cmd->u.text.x);
            dgfx_ir_append_i32(&payload, cmd->u.text.y);
            dgfx_ir_append(&payload, &cmd->u.text.color, 4u);
            dgfx_ir_append_u32(&payload, text_len);
            dgfx_ir_append(&payload, text, text_len);
            break;
        }
        default:
            break;
        }

        if (payload.size > 0xffffu) {
            payload.size = 0xffffu;
        }
        dgfx_ir_append_u16(&b, opcode);
        dgfx_ir_append_u16(&b, (u16)payload.size);
        dgfx_ir_append(&b, payload.data, payload.size);
        if (payload.data) {
            free(payload.data);
        }
    }

    dgfx_trace_record_ir(b.data, b.size);
    if (b.data) {
        free(b.data);
    }
}

static void dgfx_trace_metrics(const d_gfx_cmd_buffer *buf)
{
    u32 accepted = 0u;
    u32 rejected = 0u;
    u32 prims = 0u;
    u32 glyphs = 0u;
    i32 min_x = 0;
    i32 min_y = 0;
    i32 max_x = 0;
    i32 max_y = 0;
    int have_bbox = 0;
    u32 i;

    if (!buf || !buf->cmds) {
        dgfx_trace_record_u32(DGFX_TRACE_EVENT_ACCEPTED_COUNT, 0u);
        dgfx_trace_record_u32(DGFX_TRACE_EVENT_REJECTED_COUNT, 0u);
        dgfx_trace_record_u32(DGFX_TRACE_EVENT_PRIMITIVE_COUNT, 0u);
        dgfx_trace_record_u32(DGFX_TRACE_EVENT_TEXT_GLYPH_COUNT, 0u);
        return;
    }

    for (i = 0u; i < buf->count; ++i) {
        const d_gfx_cmd *cmd = buf->cmds + i;
        if (!dgfx_opcode_supported((u32)cmd->opcode)) {
            rejected += 1u;
            continue;
        }
        switch (cmd->opcode) {
        case D_GFX_OP_CLEAR:
        case D_GFX_OP_SET_VIEWPORT:
        case D_GFX_OP_SET_CAMERA:
            accepted += 1u;
            break;
        case D_GFX_OP_DRAW_RECT: {
            i32 x0 = cmd->u.rect.x;
            i32 y0 = cmd->u.rect.y;
            i32 x1 = cmd->u.rect.x + cmd->u.rect.w;
            i32 y1 = cmd->u.rect.y + cmd->u.rect.h;
            i32 minx = (x0 < x1) ? x0 : x1;
            i32 maxx = (x0 < x1) ? x1 : x0;
            i32 miny = (y0 < y1) ? y0 : y1;
            i32 maxy = (y0 < y1) ? y1 : y0;

            accepted += 1u;
            prims += 1u;
            if (!have_bbox) {
                min_x = minx;
                min_y = miny;
                max_x = maxx;
                max_y = maxy;
                have_bbox = 1;
            } else {
                if (minx < min_x) min_x = minx;
                if (miny < min_y) min_y = miny;
                if (maxx > max_x) max_x = maxx;
                if (maxy > max_y) max_y = maxy;
            }
            break;
        }
        case D_GFX_OP_DRAW_TEXT: {
            i32 w = 0;
            i32 h = 0;
            u32 g = 0u;
            dgfx_trace_text_metrics(cmd->u.text.text, &g, &w, &h);
            accepted += 1u;
            prims += 1u;
            glyphs += g;
            if (w > 0 && h > 0) {
                i32 minx = cmd->u.text.x;
                i32 miny = cmd->u.text.y;
                i32 maxx = cmd->u.text.x + w;
                i32 maxy = cmd->u.text.y + h;
                if (!have_bbox) {
                    min_x = minx;
                    min_y = miny;
                    max_x = maxx;
                    max_y = maxy;
                    have_bbox = 1;
                } else {
                    if (minx < min_x) min_x = minx;
                    if (miny < min_y) min_y = miny;
                    if (maxx > max_x) max_x = maxx;
                    if (maxy > max_y) max_y = maxy;
                }
            }
            break;
        }
        default:
            rejected += 1u;
            break;
        }
    }

    dgfx_trace_record_u32(DGFX_TRACE_EVENT_ACCEPTED_COUNT, accepted);
    dgfx_trace_record_u32(DGFX_TRACE_EVENT_REJECTED_COUNT, rejected);
    dgfx_trace_record_u32(DGFX_TRACE_EVENT_PRIMITIVE_COUNT, prims);
    dgfx_trace_record_u32(DGFX_TRACE_EVENT_TEXT_GLYPH_COUNT, glyphs);
    if (have_bbox) {
        dgfx_trace_record_bbox(min_x, min_y, max_x, max_y);
    }
}

void* d_gfx_get_native_window(void)
{
    return g_native_window;
}

int d_gfx_bind_surface(void* native_window, i32 width, i32 height)
{
    g_native_window = native_window;
    if (width > 0) {
        g_backbuffer_w = width;
    }
    if (height > 0) {
        g_backbuffer_h = height;
    }
#if DOM_BACKEND_SOFT
    d_gfx_soft_set_native_window(native_window);
    d_gfx_soft_set_framebuffer_size(g_backbuffer_w, g_backbuffer_h);
    if (g_backend == d_gfx_soft_register_backend()) {
        if (g_backend->shutdown) {
            g_backend->shutdown();
        }
        if (g_backend->init) {
            g_backend->init();
        }
    }
#endif
    return 1;
}

int d_gfx_resize(i32 width, i32 height)
{
    return d_gfx_bind_surface(g_native_window, width, height);
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

static const dgfx_native_api_v1 g_dgfx_native_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dgfx_native_api_v1),
    d_gfx_bind_surface,
    d_gfx_resize,
    d_gfx_get_native_window
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
    desc.perf_class = DOM_CAPS_PERF_BASELINE;
    desc.required_hw_flags = 0u;
    if (dom_caps_register_backend(&desc) != DOM_CAPS_OK) {
        return DOM_CAPS_ERR;
    }
#endif

#if DOM_BACKEND_DX9
    desc.backend_name = "dx9";
#if DOM_PLATFORM_ID == DOM_PLATFORM_ID_WIN32
    desc.backend_priority = 120u;
#else
    desc.backend_priority = 100u;
#endif
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = DOM_HW_OS_WIN32;
    if (dom_caps_register_backend(&desc) != DOM_CAPS_OK) {
        return DOM_CAPS_ERR;
    }
#endif

#if DOM_BACKEND_DX11
    desc.backend_name = "dx11";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = DOM_HW_OS_WIN32;
    if (dom_caps_register_backend(&desc) != DOM_CAPS_OK) {
        return DOM_CAPS_ERR;
    }
#endif

#if DOM_BACKEND_GL2
    desc.backend_name = "gl2";
#if DOM_PLATFORM_ID == DOM_PLATFORM_ID_WIN32
    desc.backend_priority = 100u;
#else
    desc.backend_priority = 120u;
#endif
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = DOM_HW_OS_WIN32;
    if (dom_caps_register_backend(&desc) != DOM_CAPS_OK) {
        return DOM_CAPS_ERR;
    }
#endif

#if DOM_BACKEND_VK1
    desc.backend_name = "vk1";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = 0u;
    if (dom_caps_register_backend(&desc) != DOM_CAPS_OK) {
        return DOM_CAPS_ERR;
    }
#endif

#if DOM_BACKEND_METAL
    desc.backend_name = "metal";
    desc.backend_priority = 100u;
    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    desc.perf_class = DOM_CAPS_PERF_PERF;
    desc.required_hw_flags = DOM_HW_OS_APPLE;
    if (dom_caps_register_backend(&desc) != DOM_CAPS_OK) {
        return DOM_CAPS_ERR;
    }
#endif

#if DOM_BACKEND_NULL
    desc.backend_name = "null";
    desc.backend_priority = 10u;
    desc.determinism = DOM_DET_D0_BIT_EXACT;
    desc.perf_class = DOM_CAPS_PERF_BASELINE;
    desc.required_hw_flags = 0u;
    if (dom_caps_register_backend(&desc) != DOM_CAPS_OK) {
        return DOM_CAPS_ERR;
    }
#endif

    return DOM_CAPS_OK;
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
        *out_iface = (void*)&g_dgfx_native_api_v1;
        return DGFX_OK;
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

static const d_gfx_backend_soft* dgfx_choose_backend(const char* backend_name, const char** out_name, const char** out_reason)
{
    if (out_name) {
        *out_name = 0;
    }
    if (out_reason) {
        *out_reason = 0;
    }

    if (!backend_name || !backend_name[0]) {
        return 0;
    }

    if (strcmp(backend_name, "soft") == 0) {
#if DOM_BACKEND_SOFT
        if (out_name) *out_name = "soft";
        if (out_reason) *out_reason = "built-in soft backend";
        return d_gfx_soft_register_backend();
#else
        return 0;
#endif
    }
    if (strcmp(backend_name, "null") == 0) {
#if DOM_BACKEND_NULL
        if (out_name) *out_name = "null";
        if (out_reason) *out_reason = "headless null backend";
        return d_gfx_null_register_backend();
#else
        return 0;
#endif
    }

#if DOM_BACKEND_DX9
    if (strcmp(backend_name, "dx9") == 0) {
        if (out_name) *out_name = "dx9";
        if (out_reason) *out_reason = "unavailable (stubbed)";
        return 0;
    }
#endif
#if DOM_BACKEND_DX11
    if (strcmp(backend_name, "dx11") == 0) {
        if (out_name) *out_name = "dx11";
        if (out_reason) *out_reason = "unavailable (stubbed)";
        return 0;
    }
#endif
#if DOM_BACKEND_GL2
    if (strcmp(backend_name, "gl2") == 0) {
        if (out_name) *out_name = "gl2";
        if (out_reason) *out_reason = "unavailable (stubbed)";
        return 0;
    }
#endif
#if DOM_BACKEND_VK1
    if (strcmp(backend_name, "vk1") == 0) {
        if (out_name) *out_name = "vk1";
        if (out_reason) *out_reason = "unavailable (stubbed)";
        return 0;
    }
#endif
#if DOM_BACKEND_METAL
    if (strcmp(backend_name, "metal") == 0) {
        if (out_name) *out_name = "metal";
        if (out_reason) *out_reason = "unavailable (stubbed)";
        return 0;
    }
#endif

    return 0;
}

int d_gfx_init(const char *backend_name)
{
    const d_gfx_backend_soft *chosen;
    const int have_request = (backend_name && backend_name[0] &&
                              strcmp(backend_name, "auto") != 0 &&
                              strcmp(backend_name, "default") != 0) ? 1 : 0;
    const char* chosen_name = 0;
    const char* chosen_reason = 0;
    chosen = (const d_gfx_backend_soft*)0;

#if DOM_BACKEND_SOFT
    d_gfx_soft_set_framebuffer_size(g_backbuffer_w, g_backbuffer_h);
#endif

    if (have_request) {
        chosen = dgfx_choose_backend(backend_name, &chosen_name, &chosen_reason);
        if (!chosen) {
            fprintf(stderr, "dgfx: requested backend '%s' unavailable\n", backend_name);
            return 0;
        }
    } else {
#if DOM_BACKEND_SOFT
        chosen = dgfx_choose_backend("soft", &chosen_name, &chosen_reason);
#endif
        if (!chosen) {
#if DOM_BACKEND_DX11
            chosen = dgfx_choose_backend("dx11", &chosen_name, &chosen_reason);
#endif
        }
        if (!chosen) {
#if DOM_BACKEND_DX9
            chosen = dgfx_choose_backend("dx9", &chosen_name, &chosen_reason);
#endif
        }
        if (!chosen) {
#if DOM_BACKEND_GL2
            chosen = dgfx_choose_backend("gl2", &chosen_name, &chosen_reason);
#endif
        }
        if (!chosen) {
#if DOM_BACKEND_VK1
            chosen = dgfx_choose_backend("vk1", &chosen_name, &chosen_reason);
#endif
        }
        if (!chosen) {
#if DOM_BACKEND_METAL
            chosen = dgfx_choose_backend("metal", &chosen_name, &chosen_reason);
#endif
        }
        if (!chosen) {
#if DOM_BACKEND_NULL
            chosen = dgfx_choose_backend("null", &chosen_name, &chosen_reason);
#endif
        }
        if (!chosen) {
            fprintf(stderr, "dgfx: no backend available (auto)\n");
            return 0;
        }
        fprintf(stderr, "dgfx: auto selected backend '%s' (%s)\n",
                chosen_name ? chosen_name : "unknown",
                chosen_reason ? chosen_reason : "no detail");
    }

    if (!chosen || !chosen->init) {
        return 0;
    }
    if (chosen->init() != 0) {
        return 0;
    }
    g_backend = chosen;
    g_backend_name = chosen_name ? chosen_name : (have_request ? backend_name : "soft");
    g_backend_op_mask = dgfx_caps_mask_for_backend(g_backend_name);
    return 1;
}

void d_gfx_shutdown(void)
{
    if (g_backend && g_backend->shutdown) {
        g_backend->shutdown();
    }
    g_backend = 0;
    g_backend_name = 0;
    g_backend_op_mask = 0u;
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
    u64 t0 = dsys_time_now_us();
    dgfx_trace_record_backend_event(DGFX_TRACE_EVENT_BACKEND_SUBMIT_BEGIN, 0, 0u);
    dgfx_trace_build_ir(buf);
    dgfx_trace_metrics(buf);
    if (g_backend && g_backend->submit_cmd_buffer) {
        if (buf && buf->cmds && buf->count > 0u && g_backend_op_mask != DGFX_CAP_OP_ALL) {
            d_gfx_cmd_buffer filtered;
            filtered.count = 0u;
            filtered.capacity = buf->count;
            filtered.cmds = (d_gfx_cmd*)malloc(sizeof(d_gfx_cmd) * (size_t)buf->count);
            if (filtered.cmds) {
                u32 i;
                for (i = 0u; i < buf->count; ++i) {
                    const d_gfx_cmd *cmd = buf->cmds + i;
                    if (dgfx_opcode_supported((u32)cmd->opcode)) {
                        filtered.cmds[filtered.count++] = *cmd;
                    }
                }
                if (filtered.count > 0u) {
                    g_backend->submit_cmd_buffer(&filtered);
                }
                free(filtered.cmds);
            }
        } else {
            g_backend->submit_cmd_buffer(buf);
        }
    }
    dgfx_trace_record_backend_event(DGFX_TRACE_EVENT_BACKEND_SUBMIT_END, 0, 0u);
    {
        u64 t1 = dsys_time_now_us();
        u32 dt_ms = dgfx_elapsed_ms(t0, t1);
        if (dt_ms > DGFX_STALL_THRESHOLD_MS) {
            dgfx_trace_record_u32(DGFX_TRACE_EVENT_STALL_MS, dt_ms);
        }
    }
}

void d_gfx_present(void)
{
    u64 t0 = dsys_time_now_us();
    dgfx_trace_record_backend_event(DGFX_TRACE_EVENT_BACKEND_PRESENT_BEGIN, 0, 0u);
    if (g_backend && g_backend->present) {
        g_backend->present();
    }
    dgfx_trace_record_backend_event(DGFX_TRACE_EVENT_BACKEND_PRESENT_END, 0, 0u);
    {
        u64 t1 = dsys_time_now_us();
        u32 dt_ms = dgfx_elapsed_ms(t0, t1);
        if (dt_ms > DGFX_STALL_THRESHOLD_MS) {
            dgfx_trace_record_u32(DGFX_TRACE_EVENT_STALL_MS, dt_ms);
        }
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
    }
    if (dgfx_get_ir_api(1u, &api) != DGFX_OK) {
        return 0;
    }
    backend_name = 0;
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
