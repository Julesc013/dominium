#include <string.h>
#include "dominium/constructions.h"
#include "domino/gfx.h"

typedef struct dom_gfx_clear_payload {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} dom_gfx_clear_payload;

typedef struct dom_gfx_lines_header {
    uint16_t vertex_count;
    uint16_t reserved;
} dom_gfx_lines_header;

typedef struct dom_gfx_line_vertex {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} dom_gfx_line_vertex;

static void dom_gfx_buffer_reset(dom_gfx_buffer* out)
{
    dgfx_cmd_buffer tmp;

    if (!out) {
        return;
    }
    tmp.data = out->data;
    tmp.size = 0u;
    tmp.capacity = (uint16_t)((out->capacity > 0xFFFFu) ? 0xFFFFu : out->capacity);
    dgfx_cmd_buffer_reset(&tmp);
    out->size = 0u;
}

typedef struct dom_constructions_sim_state {
    dom_instance_id inst;
    uint64_t        step_count;
} dom_constructions_sim_state;

#define DOM_CONSTRUCTIONS_MAX_SIM_STATES 16

static dom_constructions_sim_state g_construction_states[DOM_CONSTRUCTIONS_MAX_SIM_STATES];
static uint32_t                    g_construction_state_count = 0;

static dom_constructions_sim_state* dom_constructions_find_state(dom_instance_id inst)
{
    uint32_t i;

    for (i = 0u; i < g_construction_state_count; ++i) {
        if (g_construction_states[i].inst == inst) {
            return &g_construction_states[i];
        }
    }
    return NULL;
}

static dom_constructions_sim_state* dom_constructions_get_state(dom_instance_id inst)
{
    dom_constructions_sim_state* state;

    state = dom_constructions_find_state(inst);
    if (state) {
        return state;
    }
    if (g_construction_state_count >= DOM_CONSTRUCTIONS_MAX_SIM_STATES) {
        return NULL;
    }
    state = &g_construction_states[g_construction_state_count];
    state->inst = inst;
    state->step_count = 0u;
    g_construction_state_count += 1u;
    return state;
}

static int dom_gfx_emit_cmd(dom_gfx_buffer* out, dgfx_opcode op, const void* payload, size_t payload_size)
{
    size_t    required;
    dgfx_cmd* cmd;
    uint8_t*  dst;

    if (!out || !out->data) {
        return 0;
    }
    if (payload_size > 0xFFFFu) {
        return 0;
    }

    required = out->size + sizeof(dgfx_cmd) + payload_size;
    if (required > out->capacity) {
        return 0;
    }

    cmd = (dgfx_cmd*)(out->data + out->size);
    cmd->op = op;
    cmd->payload_size = (uint16_t)payload_size;

    dst = out->data + out->size + sizeof(dgfx_cmd);
    if (payload && payload_size > 0u) {
        memcpy(dst, payload, payload_size);
    } else if (payload_size > 0u) {
        memset(dst, 0, payload_size);
    }

    out->size = required;
    return 1;
}

static int dom_gfx_emit_lines(dom_gfx_buffer* out, const dom_gfx_line_vertex* verts, uint16_t count)
{
    dom_gfx_lines_header header;
    size_t               payload_size;
    size_t               required;
    dgfx_cmd*            cmd;
    uint8_t*             dst;

    if (!verts || count == 0u) {
        return 1;
    }

    payload_size = sizeof(header) + ((size_t)count * sizeof(dom_gfx_line_vertex));
    if (payload_size > 0xFFFFu) {
        return 0;
    }

    if (!out || !out->data) {
        return 0;
    }

    required = out->size + sizeof(dgfx_cmd) + payload_size;
    if (required > out->capacity) {
        return 0;
    }

    header.vertex_count = count;
    header.reserved = 0u;

    cmd = (dgfx_cmd*)(out->data + out->size);
    cmd->op = DGFX_CMD_DRAW_LINES;
    cmd->payload_size = (uint16_t)payload_size;

    dst = out->data + out->size + sizeof(dgfx_cmd);
    memcpy(dst, &header, sizeof(header));
    memcpy(dst + sizeof(header), verts, (size_t)count * sizeof(dom_gfx_line_vertex));

    out->size = required;
    return 1;
}

static uint16_t dom_construction_add_rect(dom_gfx_line_vertex* verts,
                                          uint16_t max_verts,
                                          float x0,
                                          float y0,
                                          float x1,
                                          float y1,
                                          uint32_t color,
                                          uint16_t start)
{
    uint16_t count = start;

    if ((uint16_t)(count + 8u) > max_verts) {
        return count;
    }

    verts[count].x = x0; verts[count].y = y0; verts[count].z = 0.0f; verts[count].color = color;
    verts[count + 1u].x = x1; verts[count + 1u].y = y0; verts[count + 1u].z = 0.0f; verts[count + 1u].color = color;

    verts[count + 2u].x = x1; verts[count + 2u].y = y0; verts[count + 2u].z = 0.0f; verts[count + 2u].color = color;
    verts[count + 3u].x = x1; verts[count + 3u].y = y1; verts[count + 3u].z = 0.0f; verts[count + 3u].color = color;

    verts[count + 4u].x = x1; verts[count + 4u].y = y1; verts[count + 4u].z = 0.0f; verts[count + 4u].color = color;
    verts[count + 5u].x = x0; verts[count + 5u].y = y1; verts[count + 5u].z = 0.0f; verts[count + 5u].color = color;

    verts[count + 6u].x = x0; verts[count + 6u].y = y1; verts[count + 6u].z = 0.0f; verts[count + 6u].color = color;
    verts[count + 7u].x = x0; verts[count + 7u].y = y0; verts[count + 7u].z = 0.0f; verts[count + 7u].color = color;

    return (uint16_t)(count + 8u);
}

dom_status dom_construction_spawn(const dom_construction_spawn_desc* desc,
                                  dom_construction_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_construction_destroy(dom_construction_id id)
{
    (void)id;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_construction_get_state(dom_construction_id id,
                                      dom_construction_state* out_state,
                                      size_t out_state_size)
{
    (void)id;
    if (out_state && out_state_size >= sizeof(dom_construction_state)) {
        out_state->struct_size    = (uint32_t)sizeof(dom_construction_state);
        out_state->struct_version = 0;
        out_state->id             = 0;
        out_state->prefab         = 0;
        out_state->surface        = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_construction_tick(dom_construction_id id, uint32_t dt_millis)
{
    (void)id;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_constructions_step(uint32_t dt_millis)
{
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_constructions_sim_step(dom_core* core, dom_instance_id inst, double dt_s)
{
    dom_constructions_sim_state* state;

    (void)core;
    (void)dt_s;

    state = dom_constructions_get_state(inst);
    if (!state) {
        return;
    }
    state->step_count += 1u;
}

uint64_t dom_constructions_debug_step_count(dom_instance_id inst)
{
    dom_constructions_sim_state* state;

    state = dom_constructions_find_state(inst);
    if (!state) {
        return 0u;
    }
    return state->step_count;
}

bool dom_construction_build_canvas(dom_core* core,
                                   dom_instance_id inst,
                                   const char* canvas_id,
                                   dom_gfx_buffer* out)
{
    dom_gfx_clear_payload clear;
    dom_gfx_line_vertex   verts[48];
    uint16_t              vcount;
    uint32_t              outline_color;

    (void)core;
    (void)inst;

    if (!canvas_id || !out || !out->data) {
        return false;
    }

    dom_gfx_buffer_reset(out);
    clear.r = 16u;
    clear.g = 12u;
    clear.b = 16u;
    clear.a = 255u;

    if (strcmp(canvas_id, "construction_interior") == 0) {
        clear.r = 10u;
        clear.g = 10u;
        clear.b = 18u;
    }

    if (!dom_gfx_emit_cmd(out, DGFX_CMD_CLEAR, &clear, sizeof(clear))) {
        return false;
    }

    vcount = 0u;
    outline_color = 0xffa9c6ffu;

    if (strcmp(canvas_id, "construction_exterior") == 0) {
        vcount = dom_construction_add_rect(verts,
                                           (uint16_t)(sizeof(verts) / sizeof(verts[0])),
                                           -4.0f,
                                           -2.0f,
                                           4.0f,
                                           2.0f,
                                           outline_color,
                                           0u);
    } else if (strcmp(canvas_id, "construction_interior") == 0) {
        vcount = dom_construction_add_rect(verts,
                                           (uint16_t)(sizeof(verts) / sizeof(verts[0])),
                                           0.0f,
                                           0.0f,
                                           8.0f,
                                           6.0f,
                                           outline_color,
                                           0u);
        /* simple two-by-two room split */
        if ((uint16_t)(vcount + 8u) <= (uint16_t)(sizeof(verts) / sizeof(verts[0]))) {
            uint32_t grid_color = 0xff7ea1d0u;
            verts[vcount].x = 4.0f; verts[vcount].y = 0.0f; verts[vcount].z = 0.0f; verts[vcount].color = grid_color;
            verts[vcount + 1u].x = 4.0f; verts[vcount + 1u].y = 6.0f; verts[vcount + 1u].z = 0.0f; verts[vcount + 1u].color = grid_color;
            verts[vcount + 2u].x = 0.0f; verts[vcount + 2u].y = 3.0f; verts[vcount + 2u].z = 0.0f; verts[vcount + 2u].color = grid_color;
            verts[vcount + 3u].x = 8.0f; verts[vcount + 3u].y = 3.0f; verts[vcount + 3u].z = 0.0f; verts[vcount + 3u].color = grid_color;
            verts[vcount + 4u].x = 2.0f; verts[vcount + 4u].y = 0.0f; verts[vcount + 4u].z = 0.0f; verts[vcount + 4u].color = grid_color;
            verts[vcount + 5u].x = 2.0f; verts[vcount + 5u].y = 6.0f; verts[vcount + 5u].z = 0.0f; verts[vcount + 5u].color = grid_color;
            verts[vcount + 6u].x = 6.0f; verts[vcount + 6u].y = 0.0f; verts[vcount + 6u].z = 0.0f; verts[vcount + 6u].color = grid_color;
            verts[vcount + 7u].x = 6.0f; verts[vcount + 7u].y = 6.0f; verts[vcount + 7u].z = 0.0f; verts[vcount + 7u].color = grid_color;
            vcount = (uint16_t)(vcount + 8u);
        }
    } else {
        return true;
    }

    if (vcount > 0u) {
        if (!dom_gfx_emit_lines(out, verts, vcount)) {
            dom_gfx_buffer_reset(out);
            return false;
        }
    }

    return true;
}
