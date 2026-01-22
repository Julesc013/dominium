/*
FILE: source/domino/render/soft/d_gfx_soft.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/d_gfx_soft
RESPONSIBILITY: Implements `d_gfx_soft`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "render/soft/d_gfx_soft.h"
#include "domino/system/d_system.h"

#define D_GFX_SOFT_FONT_SCALE 2
#define D_GFX_SOFT_GLYPH_W 5
#define D_GFX_SOFT_GLYPH_H 7
#define D_GFX_SOFT_GLYPH_ADV (D_GFX_SOFT_GLYPH_W + 1)
#define D_GFX_SOFT_LINE_ADV (D_GFX_SOFT_GLYPH_H + 1)

static u32 *g_soft_fb = 0;
static i32 g_soft_width = 800;
static i32 g_soft_height = 600;
static d_gfx_viewport g_soft_vp = { 0, 0, 800, 600 };

static u32 d_gfx_soft_pack_color(const d_gfx_color *c)
{
    u32 v = 0u;
    if (!c) {
        return 0xff000000u;
    }
    v |= ((u32)c->a << 24);
    v |= ((u32)c->r << 16);
    v |= ((u32)c->g << 8);
    v |= ((u32)c->b);
    return v;
}

static void d_gfx_soft_fill_rect(const d_gfx_draw_rect_cmd *rect)
{
    i32 x0;
    i32 y0;
    i32 x1;
    i32 y1;
    u32 color;
    i32 y;

    if (!g_soft_fb || !rect) {
        return;
    }

    x0 = rect->x;
    y0 = rect->y;
    x1 = rect->x + rect->w;
    y1 = rect->y + rect->h;

    if (x0 < g_soft_vp.x) x0 = g_soft_vp.x;
    if (y0 < g_soft_vp.y) y0 = g_soft_vp.y;
    if (x1 > g_soft_vp.x + g_soft_vp.w) x1 = g_soft_vp.x + g_soft_vp.w;
    if (y1 > g_soft_vp.y + g_soft_vp.h) y1 = g_soft_vp.y + g_soft_vp.h;

    if (x0 >= x1 || y0 >= y1) {
        return;
    }

    color = d_gfx_soft_pack_color(&rect->color);
    for (y = y0; y < y1; ++y) {
        u32 *row = g_soft_fb + (u32)y * (u32)g_soft_width;
        i32 x;
        for (x = x0; x < x1; ++x) {
            row[x] = color;
        }
    }
}

static void d_gfx_soft_store_pixel(i32 x, i32 y, u32 color)
{
    if (!g_soft_fb) {
        return;
    }
    if (x < 0 || y < 0 || x >= g_soft_width || y >= g_soft_height) {
        return;
    }
    if (x < g_soft_vp.x || y < g_soft_vp.y ||
        x >= (g_soft_vp.x + g_soft_vp.w) ||
        y >= (g_soft_vp.y + g_soft_vp.h)) {
        return;
    }
    g_soft_fb[(u32)y * (u32)g_soft_width + (u32)x] = color;
}

static void d_gfx_soft_stub_text(const d_gfx_draw_text_cmd *text)
{
    int cursor_x;
    int cursor_y;
    int i;
    int scale;
    u32 color;

    static const u8 g_glyph_space[7] = { 0, 0, 0, 0, 0, 0, 0 };
    static const u8 g_glyph_dot[7] = { 0, 0, 0, 0, 0, 0, 0x04 };
    static const u8 g_glyph_colon[7] = { 0, 0x04, 0, 0, 0x04, 0, 0 };
    static const u8 g_glyph_dash[7] = { 0, 0, 0, 0x1F, 0, 0, 0 };
    static const u8 g_glyph_underscore[7] = { 0, 0, 0, 0, 0, 0, 0x1F };
    static const u8 g_glyph_slash[7] = { 0x01, 0x02, 0x04, 0x08, 0x10, 0, 0 };
    static const u8 g_glyph_percent[7] = { 0x19, 0x1A, 0x04, 0x08, 0x16, 0x13, 0 };
    static const u8 g_glyph_lparen[7] = { 0x04, 0x08, 0x10, 0x10, 0x10, 0x08, 0x04 };
    static const u8 g_glyph_rparen[7] = { 0x04, 0x02, 0x01, 0x01, 0x01, 0x02, 0x04 };
    static const u8 g_glyph_question[7] = { 0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04 };
    static const u8 g_glyph_unknown[7] = { 0x1F, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1F };

    static const u8 g_glyph_0[7] = { 0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E };
    static const u8 g_glyph_1[7] = { 0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E };
    static const u8 g_glyph_2[7] = { 0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F };
    static const u8 g_glyph_3[7] = { 0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E };
    static const u8 g_glyph_4[7] = { 0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02 };
    static const u8 g_glyph_5[7] = { 0x1F, 0x10, 0x10, 0x1E, 0x01, 0x01, 0x1E };
    static const u8 g_glyph_6[7] = { 0x0E, 0x10, 0x10, 0x1E, 0x11, 0x11, 0x0E };
    static const u8 g_glyph_7[7] = { 0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08 };
    static const u8 g_glyph_8[7] = { 0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E };
    static const u8 g_glyph_9[7] = { 0x0E, 0x11, 0x11, 0x0F, 0x01, 0x01, 0x0E };

    static const u8 g_glyph_A[7] = { 0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11 };
    static const u8 g_glyph_B[7] = { 0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E };
    static const u8 g_glyph_C[7] = { 0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E };
    static const u8 g_glyph_D[7] = { 0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E };
    static const u8 g_glyph_E[7] = { 0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F };
    static const u8 g_glyph_F[7] = { 0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10 };
    static const u8 g_glyph_G[7] = { 0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F };
    static const u8 g_glyph_H[7] = { 0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11 };
    static const u8 g_glyph_I[7] = { 0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E };
    static const u8 g_glyph_J[7] = { 0x01, 0x01, 0x01, 0x01, 0x11, 0x11, 0x0E };
    static const u8 g_glyph_K[7] = { 0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11 };
    static const u8 g_glyph_L[7] = { 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F };
    static const u8 g_glyph_M[7] = { 0x11, 0x1B, 0x15, 0x11, 0x11, 0x11, 0x11 };
    static const u8 g_glyph_N[7] = { 0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11 };
    static const u8 g_glyph_O[7] = { 0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E };
    static const u8 g_glyph_P[7] = { 0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10 };
    static const u8 g_glyph_Q[7] = { 0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D };
    static const u8 g_glyph_R[7] = { 0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11 };
    static const u8 g_glyph_S[7] = { 0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E };
    static const u8 g_glyph_T[7] = { 0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04 };
    static const u8 g_glyph_U[7] = { 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E };
    static const u8 g_glyph_V[7] = { 0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04 };
    static const u8 g_glyph_W[7] = { 0x11, 0x11, 0x11, 0x11, 0x15, 0x1B, 0x11 };
    static const u8 g_glyph_X[7] = { 0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11 };
    static const u8 g_glyph_Y[7] = { 0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04 };
    static const u8 g_glyph_Z[7] = { 0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F };

    if (!text) {
        return;
    }

    color = d_gfx_soft_pack_color(&text->color);
    cursor_x = text->x;
    cursor_y = text->y;
    scale = D_GFX_SOFT_FONT_SCALE;

    for (i = 0; text->text && text->text[i] != '\0'; ++i) {
        const u8 *glyph = g_glyph_unknown;
        unsigned char ch = (unsigned char)text->text[i];
        int row;
        int col;

        if (text->text[i] == '\n') {
            cursor_x = text->x;
            cursor_y += D_GFX_SOFT_LINE_ADV * scale;
            continue;
        }
        if (ch >= 'a' && ch <= 'z') {
            ch = (unsigned char)(ch - 'a' + 'A');
        }

        switch (ch) {
        case ' ': glyph = g_glyph_space; break;
        case '.': glyph = g_glyph_dot; break;
        case ':': glyph = g_glyph_colon; break;
        case '-': glyph = g_glyph_dash; break;
        case '_': glyph = g_glyph_underscore; break;
        case '/': glyph = g_glyph_slash; break;
        case '%': glyph = g_glyph_percent; break;
        case '(': glyph = g_glyph_lparen; break;
        case ')': glyph = g_glyph_rparen; break;
        case '?': glyph = g_glyph_question; break;
        case '0': glyph = g_glyph_0; break;
        case '1': glyph = g_glyph_1; break;
        case '2': glyph = g_glyph_2; break;
        case '3': glyph = g_glyph_3; break;
        case '4': glyph = g_glyph_4; break;
        case '5': glyph = g_glyph_5; break;
        case '6': glyph = g_glyph_6; break;
        case '7': glyph = g_glyph_7; break;
        case '8': glyph = g_glyph_8; break;
        case '9': glyph = g_glyph_9; break;
        case 'A': glyph = g_glyph_A; break;
        case 'B': glyph = g_glyph_B; break;
        case 'C': glyph = g_glyph_C; break;
        case 'D': glyph = g_glyph_D; break;
        case 'E': glyph = g_glyph_E; break;
        case 'F': glyph = g_glyph_F; break;
        case 'G': glyph = g_glyph_G; break;
        case 'H': glyph = g_glyph_H; break;
        case 'I': glyph = g_glyph_I; break;
        case 'J': glyph = g_glyph_J; break;
        case 'K': glyph = g_glyph_K; break;
        case 'L': glyph = g_glyph_L; break;
        case 'M': glyph = g_glyph_M; break;
        case 'N': glyph = g_glyph_N; break;
        case 'O': glyph = g_glyph_O; break;
        case 'P': glyph = g_glyph_P; break;
        case 'Q': glyph = g_glyph_Q; break;
        case 'R': glyph = g_glyph_R; break;
        case 'S': glyph = g_glyph_S; break;
        case 'T': glyph = g_glyph_T; break;
        case 'U': glyph = g_glyph_U; break;
        case 'V': glyph = g_glyph_V; break;
        case 'W': glyph = g_glyph_W; break;
        case 'X': glyph = g_glyph_X; break;
        case 'Y': glyph = g_glyph_Y; break;
        case 'Z': glyph = g_glyph_Z; break;
        default:
            glyph = g_glyph_unknown;
            break;
        }

        for (row = 0; row < D_GFX_SOFT_GLYPH_H; ++row) {
            u8 bits = glyph[row];
            for (col = 0; col < D_GFX_SOFT_GLYPH_W; ++col) {
                if (bits & (u8)(1u << (4 - col))) {
                    int sx;
                    int sy;
                    int base_x = cursor_x + col * scale;
                    int base_y = cursor_y + row * scale;
                    for (sy = 0; sy < scale; ++sy) {
                        for (sx = 0; sx < scale; ++sx) {
                            d_gfx_soft_store_pixel(base_x + sx, base_y + sy, color);
                        }
                    }
                }
            }
        }

        cursor_x += D_GFX_SOFT_GLYPH_ADV * scale;
    }
}

static int d_gfx_soft_init(void)
{
    size_t bytes;
    bytes = (size_t)g_soft_width * (size_t)g_soft_height * sizeof(u32);
    g_soft_fb = (u32 *)malloc(bytes);
    if (!g_soft_fb) {
        g_soft_width = 0;
        g_soft_height = 0;
        return -1;
    }
    memset(g_soft_fb, 0, bytes);
    g_soft_vp.x = 0;
    g_soft_vp.y = 0;
    g_soft_vp.w = g_soft_width;
    g_soft_vp.h = g_soft_height;
    return 0;
}

static void d_gfx_soft_shutdown(void)
{
    if (g_soft_fb) {
        free(g_soft_fb);
        g_soft_fb = (u32 *)0;
    }
    g_soft_width = 0;
    g_soft_height = 0;
}

static void d_gfx_soft_submit(const d_gfx_cmd_buffer *buf)
{
    u32 i;

    if (!buf || !buf->cmds || buf->count == 0u || !g_soft_fb) {
        return;
    }

    for (i = 0u; i < buf->count; ++i) {
        const d_gfx_cmd *cmd = buf->cmds + i;
        switch (cmd->opcode) {
        case D_GFX_OP_CLEAR: {
            u32 color = d_gfx_soft_pack_color(&cmd->u.clear.color);
            u32 pix_count = (u32)g_soft_width * (u32)g_soft_height;
            u32 p;
            for (p = 0u; p < pix_count; ++p) {
                g_soft_fb[p] = color;
            }
            break;
        }
        case D_GFX_OP_SET_VIEWPORT:
            g_soft_vp = cmd->u.viewport.vp;
            break;
        case D_GFX_OP_SET_CAMERA:
            /* ignored in minimal slice */
            break;
        case D_GFX_OP_DRAW_RECT:
            d_gfx_soft_fill_rect(&cmd->u.rect);
            break;
        case D_GFX_OP_DRAW_TEXT:
            d_gfx_soft_stub_text(&cmd->u.text);
            break;
        default:
            break;
        }
    }
}

static void d_gfx_soft_present(void)
{
    d_system_present_framebuffer(
        g_soft_fb,
        g_soft_width,
        g_soft_height,
        g_soft_width * 4);
}

static d_gfx_backend_soft g_soft_backend = {
    d_gfx_soft_init,
    d_gfx_soft_shutdown,
    d_gfx_soft_submit,
    d_gfx_soft_present
};

const d_gfx_backend_soft *d_gfx_soft_register_backend(void)
{
    return &g_soft_backend;
}

void d_gfx_soft_set_framebuffer_size(i32 w, i32 h)
{
    if (w > 0) {
        g_soft_width = w;
    }
    if (h > 0) {
        g_soft_height = h;
    }
    g_soft_vp.x = 0;
    g_soft_vp.y = 0;
    g_soft_vp.w = g_soft_width;
    g_soft_vp.h = g_soft_height;
}

const u32* d_gfx_soft_get_framebuffer(i32* out_w, i32* out_h, i32* out_pitch_bytes)
{
    if (out_w) {
        *out_w = g_soft_width;
    }
    if (out_h) {
        *out_h = g_soft_height;
    }
    if (out_pitch_bytes) {
        *out_pitch_bytes = g_soft_width * 4;
    }
    return g_soft_fb;
}
