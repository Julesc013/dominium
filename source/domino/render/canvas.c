#include <stdlib.h>
#include <string.h>
#include "domino/canvas.h"

struct dcvs_t {
    dgfx_cmd_buffer buf;
};

static int dcvs_reserve(dcvs *c, uint32_t add_bytes)
{
    uint32_t required;
    uint32_t new_cap;
    uint8_t *new_data;

    if (!c) {
        return 0;
    }

    required = c->buf.size + add_bytes;
    if (required <= c->buf.capacity) {
        return 1;
    }

    new_cap = c->buf.capacity ? c->buf.capacity : 256u;
    while (new_cap < required) {
        new_cap *= 2u;
    }

    new_data = (uint8_t *)realloc(c->buf.data, new_cap);
    if (!new_data) {
        return 0;
    }

    c->buf.data = new_data;
    c->buf.capacity = new_cap;
    return 1;
}

dcvs *dcvs_create(uint32_t initial_capacity)
{
    dcvs *c;

    c = (dcvs *)malloc(sizeof(dcvs));
    if (!c) {
        return NULL;
    }
    c->buf.data = NULL;
    c->buf.size = 0u;
    c->buf.capacity = 0u;

    if (initial_capacity > 0u) {
        c->buf.data = (uint8_t *)malloc(initial_capacity);
        if (!c->buf.data) {
            free(c);
            return NULL;
        }
        c->buf.capacity = initial_capacity;
    }

    return c;
}

void dcvs_destroy(dcvs *c)
{
    if (!c) {
        return;
    }
    if (c->buf.data) {
        free(c->buf.data);
    }
    free(c);
}

void dcvs_reset(dcvs *c)
{
    if (!c) {
        return;
    }
    c->buf.size = 0u;
}

const dgfx_cmd_buffer *dcvs_get_cmd_buffer(const dcvs *c)
{
    if (!c) {
        return NULL;
    }
    return &c->buf;
}

static int dcvs_emit(dcvs *c, uint16_t opcode, const void *payload, uint32_t payload_size)
{
    dgfx_cmd_header hdr;
    uint32_t total;
    uint8_t *dst;

    if (!c) {
        return 0;
    }
    if (payload_size > 0xFFFFu) {
        return 0;
    }

    total = (uint32_t)sizeof(dgfx_cmd_header) + payload_size;
    if (!dcvs_reserve(c, total)) {
        return 0;
    }

    hdr.opcode = opcode;
    hdr.payload_size = (uint16_t)(payload_size & 0xffffu);
    hdr.size = total;

    dst = c->buf.data + c->buf.size;
    memcpy(dst, &hdr, sizeof(hdr));
    dst += sizeof(hdr);

    if (payload && payload_size > 0u) {
        memcpy(dst, payload, payload_size);
    } else if (payload_size > 0u) {
        memset(dst, 0, payload_size);
    }

    c->buf.size += total;
    return 1;
}

bool dcvs_clear(dcvs *c, uint32_t rgba)
{
    return dcvs_emit(c, DGFX_CMD_CLEAR, &rgba, (uint32_t)sizeof(uint32_t)) ? true : false;
}

bool dcvs_set_viewport(dcvs *c, const dgfx_viewport_t *vp)
{
    if (!vp) {
        return false;
    }
    return dcvs_emit(c, DGFX_CMD_SET_VIEWPORT, vp, (uint32_t)sizeof(dgfx_viewport_t)) ? true : false;
}

bool dcvs_set_camera(dcvs *c, const dgfx_camera_t *cam)
{
    if (!cam) {
        return false;
    }
    return dcvs_emit(c, DGFX_CMD_SET_CAMERA, cam, (uint32_t)sizeof(dgfx_camera_t)) ? true : false;
}

bool dcvs_draw_sprite(dcvs *c, const dgfx_sprite_t *spr)
{
    if (!spr) {
        return false;
    }
    return dcvs_emit(c, DGFX_CMD_DRAW_SPRITES, spr, (uint32_t)sizeof(dgfx_sprite_t)) ? true : false;
}

bool dcvs_draw_line(dcvs *c, const dgfx_line_segment_t *line)
{
    if (!line) {
        return false;
    }
    return dcvs_emit(c, DGFX_CMD_DRAW_LINES, line, (uint32_t)sizeof(dgfx_line_segment_t)) ? true : false;
}

bool dcvs_draw_mesh(dcvs *c, const dgfx_mesh_draw_t *mesh)
{
    if (!mesh) {
        return false;
    }
    return dcvs_emit(c, DGFX_CMD_DRAW_MESHES, mesh, (uint32_t)sizeof(dgfx_mesh_draw_t)) ? true : false;
}

bool dcvs_draw_text(dcvs *c, const dgfx_text_draw_t *text)
{
    if (!text) {
        return false;
    }
    return dcvs_emit(c, DGFX_CMD_DRAW_TEXT, text, (uint32_t)sizeof(dgfx_text_draw_t)) ? true : false;
}

/* Legacy helpers retained for manual buffer authors */
void dgfx_cmd_buffer_reset(dgfx_cmd_buffer* buf)
{
    if (!buf) {
        return;
    }
    buf->size = 0u;
}

bool dgfx_cmd_emit(dgfx_cmd_buffer* buf,
                   uint16_t opcode,
                   const void* payload,
                   uint16_t payload_size)
{
    uint32_t total;
    dgfx_cmd_header hdr;
    uint8_t *dst;

    if (!buf || !buf->data) {
        return false;
    }
    if (payload_size > 0xFFFFu) {
        return false;
    }

    total = (uint32_t)sizeof(dgfx_cmd_header) + (uint32_t)payload_size;
    if (buf->size + total > buf->capacity) {
        return false;
    }

    hdr.opcode = opcode;
    hdr.payload_size = payload_size;
    hdr.size = total;

    dst = buf->data + buf->size;
    memcpy(dst, &hdr, sizeof(hdr));
    dst += sizeof(hdr);

    if (payload && payload_size > 0u) {
        memcpy(dst, payload, payload_size);
    } else if (payload_size > 0u) {
        memset(dst, 0, payload_size);
    }

    buf->size += total;
    return true;
}
