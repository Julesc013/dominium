/*
FILE: source/domino/render/dgfx_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/dgfx_stub
RESPONSIBILITY: Implements `dgfx_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include <stdlib.h>

#include "domino/gfx.h"

static dgfx_cmd_buffer g_frame_cmd_buffer;

bool dgfx_init(const dgfx_desc *desc) {
    (void)desc;
    /* Allocate a small default buffer for IR. */
    g_frame_cmd_buffer.data = (uint8_t *)malloc(64 * 1024);
    if (!g_frame_cmd_buffer.data) {
        g_frame_cmd_buffer.capacity = 0u;
        g_frame_cmd_buffer.size = 0u;
        return false;
    }
    g_frame_cmd_buffer.capacity = 64 * 1024;
    g_frame_cmd_buffer.size = 0u;
    return true;
}

void dgfx_shutdown(void) {
    if (g_frame_cmd_buffer.data) {
        free(g_frame_cmd_buffer.data);
        g_frame_cmd_buffer.data = NULL;
    }
    g_frame_cmd_buffer.capacity = 0u;
    g_frame_cmd_buffer.size = 0u;
}

dgfx_caps dgfx_get_caps(void) {
    dgfx_caps caps;
    memset(&caps, 0, sizeof(caps));
    caps.supports_2d = 1;
    caps.supports_vector = 1;
    caps.name = "dgfx_stub";
    return caps;
}

void dgfx_resize(int width, int height) {
    (void)width;
    (void)height;
}

void dgfx_begin_frame(void) {
    dgfx_cmd_buffer_reset(&g_frame_cmd_buffer);
}

void dgfx_execute(const dgfx_cmd_buffer *cmd) {
    (void)cmd;
}

void dgfx_end_frame(void) {
}

dgfx_cmd_buffer *dgfx_get_frame_cmd_buffer(void) {
    return &g_frame_cmd_buffer;
}

struct dcvs_t *dgfx_get_frame_canvas(void) {
    return NULL;
}
