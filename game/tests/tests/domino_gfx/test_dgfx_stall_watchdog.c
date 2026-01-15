/*
FILE: tests/domino_gfx/test_dgfx_stall_watchdog.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_gfx
RESPONSIBILITY: Validate DGFX stall watchdog trace emission under synthetic delay.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Trace emission must be deterministic.
*/
#include <stdio.h>

#include "domino/config_base.h"
#include "domino/gfx.h"
#include "render/dgfx_trace.h"
#include "render/null/d_gfx_null.h"

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

static u32 trace_count_stalls(const dgfx_trace_blob* blob)
{
    u32 off;
    u32 count;
    if (!blob || !blob->data || blob->size < 24u) {
        return 0u;
    }
    off = 24u;
    count = 0u;
    while (off + 4u <= blob->size) {
        u16 kind = trace_read_u16(blob->data + off);
        u16 len = trace_read_u16(blob->data + off + 2u);
        off += 4u;
        if (off + len > blob->size) {
            break;
        }
        if (len >= 4u && kind == DGFX_TRACE_EVENT_STALL_MS) {
            (void)trace_read_u32(blob->data + off);
            count += 1u;
        }
        off += (u32)len;
    }
    return count;
}

int main(void)
{
#if !DOM_BACKEND_NULL
    return 0;
#else
    d_gfx_cmd_buffer* buf;
    dgfx_trace_blob blob;
    u32 stall_count;

    if (!d_gfx_init("null")) {
        fprintf(stderr, "dgfx_stall: null backend not available\n");
        return 0;
    }

    d_gfx_null_set_delay_ms(150u, 150u);

    buf = d_gfx_cmd_buffer_begin();
    if (!buf) {
        fprintf(stderr, "dgfx_stall: cmd_buffer_begin failed\n");
        d_gfx_null_set_delay_ms(0u, 0u);
        d_gfx_shutdown();
        return 1;
    }

    {
        d_gfx_color c;
        c.a = 255u;
        c.r = 0u;
        c.g = 0u;
        c.b = 0u;
        d_gfx_cmd_clear(buf, c);
    }

    d_gfx_cmd_buffer_end(buf);

    dgfx_trace_begin(2u);
    d_gfx_submit(buf);
    d_gfx_present();
    if (!dgfx_trace_end(&blob)) {
        fprintf(stderr, "dgfx_stall: trace_end failed\n");
        d_gfx_null_set_delay_ms(0u, 0u);
        d_gfx_shutdown();
        return 1;
    }

    stall_count = trace_count_stalls(&blob);

    d_gfx_null_set_delay_ms(0u, 0u);
    d_gfx_shutdown();

    if (stall_count == 0u) {
        fprintf(stderr, "dgfx_stall: expected stall trace event\n");
        return 1;
    }

    return 0;
#endif
}
