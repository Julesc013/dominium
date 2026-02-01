/*
FILE: tests/domino_gfx/test_dgfx_soft_hash.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_gfx
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>

#include "domino/config_base.h"
#include "domino/gfx.h"
#include "render/soft/d_gfx_soft.h"
#include "xxhash.h"

#if DOM_BACKEND_SOFT

#define DGFX_SOFT_HASH_EXPECTED_XXH64 0xcab983892cad9c2aULL

static d_gfx_color dgfx_color(u8 a, u8 r, u8 g, u8 b)
{
    d_gfx_color c;
    c.a = a;
    c.r = r;
    c.g = g;
    c.b = b;
    return c;
}

static int dgfx_soft_render_fixed_scene(void)
{
    dgfx_desc desc;
    d_gfx_cmd_buffer* buf;
    d_gfx_viewport vp;
    d_gfx_draw_rect_cmd rect;
    d_gfx_draw_text_cmd text;
    const u32* fb;
    i32 w;
    i32 h;
    i32 pitch_bytes;
    u64 got;

    memset(&desc, 0, sizeof(desc));
    desc.backend = DGFX_BACKEND_SOFT;
    desc.width = 64;
    desc.height = 64;
    if (!dgfx_init(&desc)) {
        fprintf(stderr, "dgfx_soft_hash: dgfx_init failed\n");
        return 1;
    }

    buf = d_gfx_cmd_buffer_begin();
    if (!buf) {
        fprintf(stderr, "dgfx_soft_hash: cmd_buffer_begin failed\n");
        dgfx_shutdown();
        return 1;
    }

    d_gfx_cmd_clear(buf, dgfx_color(255u, 16u, 16u, 16u));

    vp.x = 8;
    vp.y = 8;
    vp.w = 48;
    vp.h = 48;
    d_gfx_cmd_set_viewport(buf, &vp);

    rect.x = 0;
    rect.y = 0;
    rect.w = 64;
    rect.h = 64;
    rect.color = dgfx_color(255u, 0u, 0u, 0u);
    d_gfx_cmd_draw_rect(buf, &rect);

    rect.x = 4;
    rect.y = 4;
    rect.w = 16;
    rect.h = 16;
    rect.color = dgfx_color(255u, 255u, 0u, 0u);
    d_gfx_cmd_draw_rect(buf, &rect);

    rect.x = 50;
    rect.y = 50;
    rect.w = 20;
    rect.h = 20;
    rect.color = dgfx_color(255u, 0u, 255u, 0u);
    d_gfx_cmd_draw_rect(buf, &rect);

    text.x = 10;
    text.y = 30;
    text.text = "HASH";
    text.color = dgfx_color(255u, 0u, 0u, 255u);
    d_gfx_cmd_draw_text(buf, &text);

    d_gfx_cmd_buffer_end(buf);
    d_gfx_submit(buf);

    fb = d_gfx_soft_get_framebuffer(&w, &h, &pitch_bytes);
    if (!fb || w != 64 || h != 64 || pitch_bytes != (64 * 4)) {
        fprintf(stderr, "dgfx_soft_hash: framebuffer unavailable (w=%d h=%d pitch=%d)\n", (int)w, (int)h, (int)pitch_bytes);
        dgfx_shutdown();
        return 1;
    }

    got = dom_xxhash64((const void*)fb, (size_t)pitch_bytes * (size_t)h, 0u);
    if (got != (u64)DGFX_SOFT_HASH_EXPECTED_XXH64) {
        fprintf(stderr, "dgfx_soft_hash: got=0x%016llx expected=0x%016llx\n",
                (unsigned long long)got,
                (unsigned long long)DGFX_SOFT_HASH_EXPECTED_XXH64);
        dgfx_shutdown();
        return 1;
    }

    dgfx_shutdown();
    return 0;
}

int main(void)
{
    return dgfx_soft_render_fixed_scene();
}

#else

int main(void)
{
    return 0;
}

#endif
