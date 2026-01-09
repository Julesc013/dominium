/*
FILE: tests/domino_gfx/test_dgfx_caps_contract.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_gfx
RESPONSIBILITY: Validate DGFX capability claims vs command acceptance.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Trace acceptance/rejection must be deterministic for a given mask.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend by adding opcodes and expected mask checks.
*/
#include <stdio.h>
#include <string.h>

#include "domino/config_base.h"
#include "domino/gfx.h"
#include "render/d_gfx_caps.h"
#include "render/dgfx_trace.h"

static d_gfx_color dgfx_color(u8 a, u8 r, u8 g, u8 b)
{
    d_gfx_color c;
    c.a = a;
    c.r = r;
    c.g = g;
    c.b = b;
    return c;
}

static void dgfx_emit_ops(d_gfx_cmd_buffer *buf)
{
    d_gfx_viewport vp;
    d_gfx_camera cam;
    d_gfx_draw_rect_cmd rect;
    d_gfx_draw_text_cmd text;
    d_gfx_cmd unknown;

    d_gfx_cmd_clear(buf, dgfx_color(255u, 0u, 0u, 0u));

    vp.x = 0;
    vp.y = 0;
    vp.w = 64;
    vp.h = 64;
    d_gfx_cmd_set_viewport(buf, &vp);

    memset(&cam, 0, sizeof(cam));
    cam.fov = (q16_16)(60 << 16);
    d_gfx_cmd_set_camera(buf, &cam);

    rect.x = 2;
    rect.y = 2;
    rect.w = 10;
    rect.h = 10;
    rect.color = dgfx_color(255u, 255u, 0u, 0u);
    d_gfx_cmd_draw_rect(buf, &rect);

    text.x = 4;
    text.y = 20;
    text.text = "CAPS";
    text.color = dgfx_color(255u, 0u, 0u, 255u);
    d_gfx_cmd_draw_text(buf, &text);

    if (buf->cmds && buf->count < buf->capacity) {
        memset(&unknown, 0, sizeof(unknown));
        unknown.opcode = (d_gfx_opcode)99;
        buf->cmds[buf->count++] = unknown;
    }
}

static u16 trace_read_u16(const unsigned char* p)
{
    return (u16)((u16)p[0] | ((u16)p[1] << 8u));
}

static u32 trace_read_u32(const unsigned char* p)
{
    return (u32)((u32)p[0] |
                 ((u32)p[1] << 8u) |
                 ((u32)p[2] << 16u) |
                 ((u32)p[3] << 24u));
}

static int trace_extract_counts(const dgfx_trace_blob* blob, u32* out_accept, u32* out_reject)
{
    u32 off;
    int have_accept;
    int have_reject;

    if (!blob || !blob->data || blob->size < 24u) {
        return 0;
    }

    off = 24u;
    have_accept = 0;
    have_reject = 0;
    while (off + 4u <= blob->size) {
        u16 kind = trace_read_u16(blob->data + off);
        u16 len = trace_read_u16(blob->data + off + 2u);
        off += 4u;
        if (off + len > blob->size) {
            return 0;
        }
        if (len >= 4u && kind == DGFX_TRACE_EVENT_ACCEPTED_COUNT) {
            if (out_accept) {
                *out_accept = trace_read_u32(blob->data + off);
            }
            have_accept = 1;
        } else if (len >= 4u && kind == DGFX_TRACE_EVENT_REJECTED_COUNT) {
            if (out_reject) {
                *out_reject = trace_read_u32(blob->data + off);
            }
            have_reject = 1;
        }
        off += (u32)len;
    }

    return have_accept && have_reject;
}

static int dgfx_check_backend(const char* backend_name)
{
    d_gfx_cmd_buffer* buf;
    dgfx_trace_blob blob;
    u32 mask;
    u32 expected_accept;
    u32 expected_reject;
    u32 got_accept;
    u32 got_reject;
    u32 i;

    if (!d_gfx_init(backend_name)) {
        fprintf(stderr, "dgfx_caps: backend '%s' not available\n", backend_name);
        return 0;
    }

    buf = d_gfx_cmd_buffer_begin();
    if (!buf) {
        fprintf(stderr, "dgfx_caps: cmd_buffer_begin failed for '%s'\n", backend_name);
        d_gfx_shutdown();
        return -1;
    }

    dgfx_emit_ops(buf);
    d_gfx_cmd_buffer_end(buf);

    mask = d_gfx_get_opcode_mask();
    expected_accept = 0u;
    expected_reject = 0u;
    for (i = 0u; i < buf->count; ++i) {
        u32 opcode = (u32)buf->cmds[i].opcode;
        if (opcode >= 32u) {
            expected_reject += 1u;
        } else if ((mask & (1u << opcode)) != 0u) {
            expected_accept += 1u;
        } else {
            expected_reject += 1u;
        }
    }

    dgfx_trace_begin(1u);
    d_gfx_submit(buf);
    d_gfx_present();
    if (!dgfx_trace_end(&blob)) {
        fprintf(stderr, "dgfx_caps: trace_end failed for '%s'\n", backend_name);
        d_gfx_shutdown();
        return -1;
    }

    got_accept = 0u;
    got_reject = 0u;
    if (!trace_extract_counts(&blob, &got_accept, &got_reject)) {
        fprintf(stderr, "dgfx_caps: trace parse failed for '%s'\n", backend_name);
        d_gfx_shutdown();
        return -1;
    }

    d_gfx_shutdown();

    if (got_accept != expected_accept || got_reject != expected_reject) {
        fprintf(stderr, "dgfx_caps: mismatch for '%s' (accept %u/%u reject %u/%u)\n",
                backend_name,
                (unsigned)got_accept,
                (unsigned)expected_accept,
                (unsigned)got_reject,
                (unsigned)expected_reject);
        return -1;
    }

    return 1;
}

int main(void)
{
    int failures = 0;
    int ran = 0;
    int r;

#if DOM_BACKEND_SOFT
    r = dgfx_check_backend("soft");
    if (r < 0) failures += 1;
    if (r > 0) ran += 1;
#endif
#if DOM_BACKEND_NULL
    r = dgfx_check_backend("null");
    if (r < 0) failures += 1;
    if (r > 0) ran += 1;
#endif
#if DOM_BACKEND_DX9
    r = dgfx_check_backend("dx9");
    if (r < 0) failures += 1;
    if (r > 0) ran += 1;
#endif
#if DOM_BACKEND_DX11
    r = dgfx_check_backend("dx11");
    if (r < 0) failures += 1;
    if (r > 0) ran += 1;
#endif
#if DOM_BACKEND_GL2
    r = dgfx_check_backend("gl2");
    if (r < 0) failures += 1;
    if (r > 0) ran += 1;
#endif
#if DOM_BACKEND_VK1
    r = dgfx_check_backend("vk1");
    if (r < 0) failures += 1;
    if (r > 0) ran += 1;
#endif
#if DOM_BACKEND_METAL
    r = dgfx_check_backend("metal");
    if (r < 0) failures += 1;
    if (r > 0) ran += 1;
#endif

    if (!ran) {
        return 0;
    }
    return failures ? 1 : 0;
}
