/*
FILE: data/mods/examples/launcher_example/launcher_example.c
MODULE: Repository
LAYER / SUBSYSTEM: data/mods/examples/launcher_example
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include <stdlib.h>
#include "domino/mod.h"
#include "domino/view.h"

static bool build_debug_canvas(dom_core* core, dom_instance_id inst, const char* canvas_id, dom_gfx_buffer* out)
{
    dcvs* c;
    const dgfx_cmd_buffer* buf;
    uint32_t color;

    (void)core;
    (void)inst;
    if (!canvas_id || !out) return false;
    if (strcmp(canvas_id, "launcher_debug_canvas") != 0) {
        return false;
    }

    c = dcvs_create(256u);
    if (!c) return false;
    color = 0x202040FFu;
    dcvs_clear(c, color);
    buf = dcvs_get_cmd_buffer(c);
    out->data = (uint8_t*)malloc(buf->size);
    if (!out->data) {
        dcvs_destroy(c);
        return false;
    }
    memcpy(out->data, buf->data, buf->size);
    out->size = buf->size;
    out->capacity = buf->size;
    dcvs_destroy(c);
    return true;
}

static void register_views(dom_core* core)
{
    dom_view_desc desc;
    memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = 1;
    desc.id = "view_launcher_debug";
    desc.title = "Debug";
    desc.kind = DOM_VIEW_KIND_CANVAS;
    desc.model_id = "launcher_debug_canvas";
    dom_view_register(core, &desc);
}

static const dom_launcher_ext_v1 g_ext = {
    sizeof(dom_launcher_ext_v1),
    1,
    NULL,
    register_views,
    NULL,
    build_debug_canvas
};

const dom_launcher_ext_v1* dom_get_launcher_ext_v1(void)
{
    return &g_ext;
}
