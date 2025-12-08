#include <stddef.h>
#include <string.h>
#include "core_internal.h"
#include "domino/gfx.h"

static int dom_canvas_is_known(const char* canvas_id)
{
    if (!canvas_id) {
        return 0;
    }
    if (strcmp(canvas_id, "world_surface") == 0) {
        return 1;
    }
    if (strcmp(canvas_id, "preview") == 0) {
        return 1;
    }
    return 0;
}

bool dom_canvas_build(dom_core* core, dom_instance_id inst, const char* canvas_id, dom_gfx_buffer* out)
{
    dgfx_cmd cmd;
    uint8_t payload[4];
    size_t needed;

    (void)inst;

    if (!core || !out) {
        return false;
    }

    out->size = 0;

    if (!dom_canvas_is_known(canvas_id)) {
        return true;
    }

    cmd.op = DGFX_CMD_CLEAR;
    cmd.payload_size = (uint16_t)sizeof(payload);
    payload[0] = 0;
    payload[1] = 0;
    payload[2] = 0;
    payload[3] = 0;

    needed = sizeof(cmd) + sizeof(payload);
    if (!out->data || out->capacity < needed) {
        return true;
    }

    memcpy(out->data, &cmd, sizeof(cmd));
    memcpy(out->data + sizeof(cmd), payload, sizeof(payload));
    out->size = needed;
    return true;
}
