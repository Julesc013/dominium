#include <string.h>
#include <math.h>
#include "dominium/world.h"
#include "domino/gfx.h"

typedef struct dom_world_sim_state {
    dom_instance_id inst;
    uint64_t        step_count;
} dom_world_sim_state;

#define DOM_WORLD_MAX_SIM_STATES 16

static dom_world_sim_state g_world_states[DOM_WORLD_MAX_SIM_STATES];
static uint32_t            g_world_state_count = 0;

static dom_world_sim_state* dom_world_find_state(dom_instance_id inst)
{
    uint32_t i;

    for (i = 0u; i < g_world_state_count; ++i) {
        if (g_world_states[i].inst == inst) {
            return &g_world_states[i];
        }
    }
    return NULL;
}

static dom_world_sim_state* dom_world_get_state(dom_instance_id inst)
{
    dom_world_sim_state* state;

    state = dom_world_find_state(inst);
    if (state) {
        return state;
    }
    if (g_world_state_count >= DOM_WORLD_MAX_SIM_STATES) {
        return NULL;
    }
    state = &g_world_states[g_world_state_count];
    state->inst = inst;
    state->step_count = 0u;
    g_world_state_count += 1u;
    return state;
}

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

static int dom_gfx_emit_cmd(dom_gfx_buffer* out, dgfx_opcode op, const void* payload, size_t payload_size)
{
    size_t     required;
    dgfx_cmd*  cmd;
    uint8_t*   dst;

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
    cmd->opcode = op;
    cmd->payload_size = (uint16_t)payload_size;
    cmd->size = (uint32_t)(sizeof(dgfx_cmd) + payload_size);

    dst = ((uint8_t*)cmd) + sizeof(dgfx_cmd);
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

    header.vertex_count = count;
    header.reserved = 0u;

    if (!out || !out->data) {
        return 0;
    }

    required = out->size + sizeof(dgfx_cmd) + payload_size;
    if (required > out->capacity) {
        return 0;
    }

    cmd = (dgfx_cmd*)(out->data + out->size);
    cmd->opcode = DGFX_CMD_DRAW_LINES;
    cmd->payload_size = (uint16_t)payload_size;
    cmd->size = (uint32_t)(sizeof(dgfx_cmd) + payload_size);

    dst = out->data + out->size + sizeof(dgfx_cmd);
    memcpy(dst, &header, sizeof(header));
    memcpy(dst + sizeof(header),
           verts,
           (size_t)count * sizeof(dom_gfx_line_vertex));

    out->size = required;
    return 1;
}

static void dom_world_make_grid(dom_gfx_line_vertex* verts, uint16_t max_verts, uint16_t* out_count)
{
    uint16_t i;
    uint16_t count;
    const float span = 10.0f;
    const float step = 1.0f;
    const uint32_t color = 0xff4c7088u;

    count = 0u;
    for (i = 0u; i <= 10u && (uint16_t)(count + 2u) <= max_verts; ++i) {
        float x = (float)i * step;
        verts[count].x = x;
        verts[count].y = 0.0f;
        verts[count].z = 0.0f;
        verts[count].color = color;
        verts[count + 1u].x = x;
        verts[count + 1u].y = span;
        verts[count + 1u].z = 0.0f;
        verts[count + 1u].color = color;
        count = (uint16_t)(count + 2u);
    }

    for (i = 0u; i <= 10u && (uint16_t)(count + 2u) <= max_verts; ++i) {
        float y = (float)i * step;
        verts[count].x = 0.0f;
        verts[count].y = y;
        verts[count].z = 0.0f;
        verts[count].color = color;
        verts[count + 1u].x = span;
        verts[count + 1u].y = y;
        verts[count + 1u].z = 0.0f;
        verts[count + 1u].color = color;
        count = (uint16_t)(count + 2u);
    }

    if (out_count) {
        *out_count = count;
    }
}

static int dom_world_emit_circle(dom_gfx_buffer* out,
                                 float cx,
                                 float cy,
                                 float radius,
                                 uint32_t color,
                                 uint16_t segments)
{
    dom_gfx_line_vertex verts[64];
    uint16_t i;
    uint16_t count;

    if (segments < 3u) {
        segments = 3u;
    }
    if (segments * 2u > (uint16_t)(sizeof(verts) / sizeof(verts[0]))) {
        segments = (uint16_t)((sizeof(verts) / sizeof(verts[0])) / 2u);
    }

    count = 0u;
    for (i = 0u; i < segments; ++i) {
        float a0 = ((float)i / (float)segments) * 6.2831853f;
        float a1 = ((float)(i + 1u) / (float)segments) * 6.2831853f;
        float x0 = cx + (float)cos(a0) * radius;
        float y0 = cy + (float)sin(a0) * radius;
        float x1 = cx + (float)cos(a1) * radius;
        float y1 = cy + (float)sin(a1) * radius;

        verts[count].x = x0;
        verts[count].y = y0;
        verts[count].z = 0.0f;
        verts[count].color = color;
        verts[count + 1u].x = x1;
        verts[count + 1u].y = y1;
        verts[count + 1u].z = 0.0f;
        verts[count + 1u].color = color;
        count = (uint16_t)(count + 2u);
    }

    return dom_gfx_emit_lines(out, verts, count);
}

struct dom_world {
    const dom_world_desc* desc;
};

dom_status dom_world_create(const dom_world_desc* desc, dom_world** out_world)
{
    (void)desc;
    (void)out_world;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_world_destroy(dom_world* world)
{
    (void)world;
}

dom_status dom_world_tick(dom_world* world, uint32_t dt_millis)
{
    (void)world;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_create_surface(dom_world* world,
                                    const dom_surface_desc* desc,
                                    dom_surface_id* out_surface)
{
    (void)world;
    (void)desc;
    if (out_surface) {
        *out_surface = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_remove_surface(dom_world* world, dom_surface_id surface)
{
    (void)world;
    (void)surface;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_get_surface_info(dom_world* world,
                                      dom_surface_id surface,
                                      dom_surface_info* out_info,
                                      size_t out_info_size)
{
    (void)world;
    (void)surface;
    if (out_info && out_info_size >= sizeof(dom_surface_info)) {
        out_info->struct_size    = (uint32_t)sizeof(dom_surface_info);
        out_info->struct_version = 0;
        out_info->id             = 0;
        out_info->seed           = 0;
        out_info->tier           = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_acquire_frame(dom_world* world,
                                   dom_surface_id surface,
                                   dom_surface_frame_view* out_frame)
{
    (void)world;
    (void)surface;
    if (out_frame) {
        out_frame->struct_size    = (uint32_t)sizeof(dom_surface_frame_view);
        out_frame->struct_version = 0;
        out_frame->surface        = 0;
        out_frame->frame          = 0;
        out_frame->tick_index     = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_world_release_frame(dom_world* world,
                                   dom_surface_frame_id frame)
{
    (void)world;
    (void)frame;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_world_sim_step(dom_core* core, dom_instance_id inst, double dt_s)
{
    dom_world_sim_state* state;

    (void)core;
    (void)dt_s;

    state = dom_world_get_state(inst);
    if (!state) {
        return;
    }
    state->step_count += 1u;
}

uint64_t dom_world_debug_step_count(dom_instance_id inst)
{
    dom_world_sim_state* state;

    state = dom_world_find_state(inst);
    if (!state) {
        return 0u;
    }
    return state->step_count;
}

bool dom_world_build_surface_canvas(dom_core* core,
                                    dom_instance_id inst,
                                    dom_gfx_buffer* out)
{
    dom_gfx_clear_payload clear;
    dom_gfx_line_vertex   verts[64];
    uint16_t              vcount;

    (void)core;
    (void)inst;

    if (!out || !out->data) {
        return false;
    }

    dom_gfx_buffer_reset(out);

    clear.r = 10u;
    clear.g = 18u;
    clear.b = 28u;
    clear.a = 255u;
    if (!dom_gfx_emit_cmd(out, DGFX_CMD_CLEAR, &clear, sizeof(clear))) {
        out->size = 0;
        return false;
    }

    dom_world_make_grid(verts, (uint16_t)(sizeof(verts) / sizeof(verts[0])), &vcount);
    if (vcount > 0u) {
        if (!dom_gfx_emit_lines(out, verts, vcount)) {
            out->size = 0;
            return false;
        }
    }

    return true;
}

bool dom_world_build_orbit_canvas(dom_core* core,
                                  dom_instance_id inst,
                                  dom_gfx_buffer* out)
{
    dom_gfx_clear_payload clear;

    (void)core;
    (void)inst;

    if (!out || !out->data) {
        return false;
    }

    dom_gfx_buffer_reset(out);

    clear.r = 4u;
    clear.g = 4u;
    clear.b = 8u;
    clear.a = 255u;
    if (!dom_gfx_emit_cmd(out, DGFX_CMD_CLEAR, &clear, sizeof(clear))) {
        out->size = 0;
        return false;
    }

    if (!dom_world_emit_circle(out, 0.0f, 0.0f, 1.0f, 0xff2d7fd8u, 16u)) {
        out->size = 0;
        return false;
    }
    if (!dom_world_emit_circle(out, 0.0f, 0.0f, 2.5f, 0xff3a536bu, 18u)) {
        out->size = 0;
        return false;
    }
    if (!dom_world_emit_circle(out, 0.0f, 0.0f, 3.5f, 0xff203548u, 20u)) {
        out->size = 0;
        return false;
    }
    if (!dom_world_emit_circle(out, 0.0f, 0.0f, 2.8f, 0xffcbe04fu, 12u)) {
        out->size = 0;
        return false;
    }

    return true;
}
