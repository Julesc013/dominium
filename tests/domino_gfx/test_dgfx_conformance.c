/*
FILE: tests/domino_gfx/test_dgfx_conformance.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_gfx
RESPONSIBILITY: DGFX IR structural trace conformance across backends.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Structural trace must be identical for identical IR streams.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md`.
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

static void dgfx_emit_scene(d_gfx_cmd_buffer *buf)
{
    d_gfx_viewport vp;
    d_gfx_camera cam;
    d_gfx_draw_rect_cmd rect;
    d_gfx_draw_text_cmd text;

    d_gfx_cmd_clear(buf, dgfx_color(255u, 16u, 16u, 16u));

    vp.x = 4;
    vp.y = 4;
    vp.w = 120;
    vp.h = 90;
    d_gfx_cmd_set_viewport(buf, &vp);

    memset(&cam, 0, sizeof(cam));
    cam.fov = (q16_16)(60 << 16);
    d_gfx_cmd_set_camera(buf, &cam);

    rect.x = 10;
    rect.y = 10;
    rect.w = 50;
    rect.h = 30;
    rect.color = dgfx_color(255u, 255u, 0u, 0u);
    d_gfx_cmd_draw_rect(buf, &rect);

    rect.x = 40;
    rect.y = 20;
    rect.w = 20;
    rect.h = 40;
    rect.color = dgfx_color(255u, 0u, 255u, 0u);
    d_gfx_cmd_draw_rect(buf, &rect);

    text.x = 12;
    text.y = 60;
    text.text = "DGFX";
    text.color = dgfx_color(255u, 0u, 0u, 255u);
    d_gfx_cmd_draw_text(buf, &text);
}

static int dgfx_run_backend(const char *backend_name, u64 frame_id, u64 *out_hash, u32 *out_mask)
{
    d_gfx_cmd_buffer *buf;
    dgfx_trace_blob blob;
    if (!d_gfx_init(backend_name)) {
        fprintf(stderr, "dgfx_conformance: backend '%s' not available\n", backend_name);
        return 0;
    }
    if (out_mask) {
        *out_mask = d_gfx_get_opcode_mask();
    }

    buf = d_gfx_cmd_buffer_begin();
    if (!buf) {
        fprintf(stderr, "dgfx_conformance: cmd_buffer_begin failed for '%s'\n", backend_name);
        d_gfx_shutdown();
        return -1;
    }

    dgfx_emit_scene(buf);
    d_gfx_cmd_buffer_end(buf);

    dgfx_trace_begin(frame_id);
    d_gfx_submit(buf);
    d_gfx_present();
    if (!dgfx_trace_end(&blob)) {
        fprintf(stderr, "dgfx_conformance: trace_end failed for '%s'\n", backend_name);
        d_gfx_shutdown();
        return -1;
    }

    if (out_hash) {
        *out_hash = dgfx_trace_hash(blob.data, blob.size);
    }

    d_gfx_shutdown();
    return 1;
}

static int dgfx_compare_backend(const char *backend_name,
                                u64 frame_id,
                                u64 *io_ref_hash,
                                u32 *io_ref_mask,
                                int *io_ref_set)
{
    u64 hash = 0u;
    u32 mask = 0u;
    int r = dgfx_run_backend(backend_name, frame_id, &hash, &mask);
    if (r < 0) {
        return 1;
    }
    if (r == 0) {
        return 0;
    }
    if (!io_ref_set || !io_ref_hash || !io_ref_mask) {
        return 1;
    }
    if (!(*io_ref_set)) {
        *io_ref_hash = hash;
        *io_ref_mask = mask;
        *io_ref_set = 1;
        return 0;
    }
    if (mask != *io_ref_mask) {
        return 0;
    }
    if (hash != *io_ref_hash) {
        fprintf(stderr, "dgfx_conformance: trace hash mismatch for '%s'\n", backend_name);
        return 1;
    }
    return 0;
}

int main(void)
{
    u64 ref_hash = 0u;
    u32 ref_mask = 0u;
    int ref_set = 0;
    int failures = 0;
    const u64 frame_id = 1u;

#if DOM_BACKEND_SOFT
    failures += dgfx_compare_backend("soft", frame_id, &ref_hash, &ref_mask, &ref_set);
#endif
#if DOM_BACKEND_NULL
    failures += dgfx_compare_backend("null", frame_id, &ref_hash, &ref_mask, &ref_set);
#endif
#if DOM_BACKEND_DX9
    failures += dgfx_compare_backend("dx9", frame_id, &ref_hash, &ref_mask, &ref_set);
#endif
#if DOM_BACKEND_DX11
    failures += dgfx_compare_backend("dx11", frame_id, &ref_hash, &ref_mask, &ref_set);
#endif
#if DOM_BACKEND_GL2
    failures += dgfx_compare_backend("gl2", frame_id, &ref_hash, &ref_mask, &ref_set);
#endif
#if DOM_BACKEND_VK1
    failures += dgfx_compare_backend("vk1", frame_id, &ref_hash, &ref_mask, &ref_set);
#endif
#if DOM_BACKEND_METAL
    failures += dgfx_compare_backend("metal", frame_id, &ref_hash, &ref_mask, &ref_set);
#endif

    if (!ref_set) {
        return 0;
    }
    return failures ? 1 : 0;
}
