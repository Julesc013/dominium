/*
FILE: source/domino/replay/d_replay.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / replay/d_replay
RESPONSIBILITY: Implements `d_replay`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "d_replay.h"
#include "core/d_subsystem.h"
#include "world/d_world.h"

#define D_REPLAY_TAG_FRAME 1u

static int g_replay_registered = 0;

typedef struct dreplay_builder {
    unsigned char *data;
    u32            length;
    u32            capacity;
} dreplay_builder;

static void d_replay_builder_init(dreplay_builder *b) {
    if (!b) {
        return;
    }
    b->data = (unsigned char *)0;
    b->length = 0u;
    b->capacity = 0u;
}

static void d_replay_builder_reset(dreplay_builder *b) {
    if (!b) {
        return;
    }
    if (b->data) {
        free(b->data);
    }
    b->data = (unsigned char *)0;
    b->length = 0u;
    b->capacity = 0u;
}

static int d_replay_builder_reserve(dreplay_builder *b, u32 extra) {
    u32 needed;
    u32 new_cap;
    unsigned char *new_data;
    if (!b) {
        return -1;
    }
    if (extra > 0xFFFFFFFFu - b->length) {
        return -1;
    }
    needed = b->length + extra;
    if (needed <= b->capacity) {
        return 0;
    }
    new_cap = b->capacity ? b->capacity : 256u;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    new_data = (unsigned char *)realloc(b->data, new_cap);
    if (!new_data) {
        return -1;
    }
    b->data = new_data;
    b->capacity = new_cap;
    return 0;
}

static int d_replay_builder_append(dreplay_builder *b, u32 tag, const unsigned char *payload, u32 payload_len) {
    int rc;
    rc = d_replay_builder_reserve(b, 8u + payload_len);
    if (rc != 0) {
        return rc;
    }
    memcpy(b->data + b->length, &tag, sizeof(u32));
    b->length += 4u;
    memcpy(b->data + b->length, &payload_len, sizeof(u32));
    b->length += 4u;
    if (payload_len > 0u && payload) {
        memcpy(b->data + b->length, payload, payload_len);
        b->length += payload_len;
    } else if (payload_len > 0u && !payload) {
        return -1;
    }
    return 0;
}

static void d_replay_free_inputs(d_net_input_frame *inputs, u32 count) {
    u32 i;
    if (!inputs) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        if (inputs[i].payload) {
            free(inputs[i].payload);
        }
        inputs[i].payload = (u8 *)0;
        inputs[i].payload_size = 0u;
    }
    free(inputs);
}

static void d_replay_free_frames(dreplay_frame *frames, u32 count) {
    u32 i;
    if (!frames) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        d_replay_free_inputs(frames[i].inputs, frames[i].input_count);
        frames[i].inputs = (d_net_input_frame *)0;
        frames[i].input_count = 0u;
        frames[i].tick_index = 0u;
    }
    free(frames);
}

static int d_replay_clone_inputs(d_net_input_frame **out_inputs, const d_net_input_frame *src, u32 count) {
    d_net_input_frame *dst;
    u32 i;
    if (!out_inputs) {
        return -1;
    }
    if (count == 0u) {
        *out_inputs = (d_net_input_frame *)0;
        return 0;
    }
    if (!src) {
        return -1;
    }

    dst = (d_net_input_frame *)malloc(sizeof(d_net_input_frame) * count);
    if (!dst) {
        return -1;
    }
    for (i = 0u; i < count; ++i) {
        dst[i].tick_index = src[i].tick_index;
        dst[i].player_id = src[i].player_id;
        dst[i].payload_size = src[i].payload_size;
        if (src[i].payload_size > 0u) {
            if (!src[i].payload) {
                d_replay_free_inputs(dst, i);
                return -1;
            }
            dst[i].payload = (u8 *)malloc(src[i].payload_size);
            if (!dst[i].payload) {
                d_replay_free_inputs(dst, i);
                return -1;
            }
            memcpy(dst[i].payload, src[i].payload, src[i].payload_size);
        } else {
            dst[i].payload = (u8 *)0;
        }
    }

    *out_inputs = dst;
    return 0;
}

static int d_replay_ensure_capacity(d_replay_context *ctx, u32 needed) {
    u32 new_cap;
    dreplay_frame *new_frames;
    if (!ctx) {
        return -1;
    }
    if (needed <= ctx->frame_capacity) {
        return 0;
    }
    new_cap = ctx->frame_capacity ? ctx->frame_capacity * 2u : 4u;
    if (new_cap < needed) {
        new_cap = needed;
    }
    new_frames = (dreplay_frame *)realloc(ctx->frames, sizeof(dreplay_frame) * new_cap);
    if (!new_frames) {
        return -1;
    }
    if (new_cap > ctx->frame_capacity) {
        u32 i;
        for (i = ctx->frame_capacity; i < new_cap; ++i) {
            new_frames[i].tick_index = 0u;
            new_frames[i].input_count = 0u;
            new_frames[i].inputs = (d_net_input_frame *)0;
        }
    }
    ctx->frames = new_frames;
    ctx->frame_capacity = new_cap;
    return 0;
}

int d_replay_init_record(d_replay_context *ctx, u32 initial_capacity) {
    if (!ctx) {
        return -1;
    }

    d_replay_shutdown(ctx);

    ctx->mode = DREPLAY_MODE_RECORD;
    ctx->determinism_mode = 1u;
    ctx->last_hash = 0u;
    ctx->frames = (dreplay_frame *)0;
    ctx->frame_count = 0u;
    ctx->frame_capacity = 0u;
    ctx->cursor = 0u;

    if (initial_capacity > 0u) {
        if (d_replay_ensure_capacity(ctx, initial_capacity) != 0) {
            d_replay_shutdown(ctx);
            return -1;
        }
    }
    return 0;
}

int d_replay_init_playback(d_replay_context *ctx, dreplay_frame *frames, u32 frame_count) {
    if (!ctx) {
        return -1;
    }
    d_replay_shutdown(ctx);

    ctx->mode = DREPLAY_MODE_PLAYBACK;
    ctx->determinism_mode = 2u;
    ctx->last_hash = 0u;
    ctx->frames = frames;
    ctx->frame_count = frame_count;
    ctx->frame_capacity = 0u; /* mark as external / non-owned */
    ctx->cursor = 0u;
    if (frame_count > 0u && !frames) {
        return -1;
    }
    return 0;
}

void d_replay_shutdown(d_replay_context *ctx) {
    if (!ctx) {
        return;
    }
    if (ctx->frames && ctx->frame_capacity > 0u) {
        d_replay_free_frames(ctx->frames, ctx->frame_count);
    }
    ctx->frames = (dreplay_frame *)0;
    ctx->frame_count = 0u;
    ctx->frame_capacity = 0u;
    ctx->cursor = 0u;
    ctx->mode = DREPLAY_MODE_OFF;
    ctx->determinism_mode = 0u;
    ctx->last_hash = 0u;
}

int d_replay_record_frame(
    d_replay_context        *ctx,
    u32                      tick_index,
    const d_net_input_frame *inputs,
    u32                      input_count
) {
    u32 i;
    dreplay_frame *frame = (dreplay_frame *)0;
    if (!ctx || ctx->mode != DREPLAY_MODE_RECORD) {
        return -1;
    }
    if (input_count > 0u && !inputs) {
        return -1;
    }

    for (i = 0u; i < ctx->frame_count; ++i) {
        if (ctx->frames[i].tick_index == tick_index) {
            frame = &ctx->frames[i];
            break;
        }
    }

    if (!frame) {
        if (d_replay_ensure_capacity(ctx, ctx->frame_count + 1u) != 0) {
            return -1;
        }
        frame = &ctx->frames[ctx->frame_count];
        ctx->frame_count += 1u;
    } else {
        d_replay_free_inputs(frame->inputs, frame->input_count);
    }

    frame->tick_index = tick_index;
    frame->input_count = input_count;
    frame->inputs = (d_net_input_frame *)0;
    if (input_count > 0u) {
        if (d_replay_clone_inputs(&frame->inputs, inputs, input_count) != 0) {
            frame->input_count = 0u;
            return -1;
        }
    }
    return 0;
}

int d_replay_get_frame(
    d_replay_context  *ctx,
    u32                tick_index,
    d_net_input_frame *out_inputs,
    u32               *in_out_input_count
) {
    dreplay_frame *frame = (dreplay_frame *)0;
    u32 i;
    if (!ctx || ctx->mode != DREPLAY_MODE_PLAYBACK || !in_out_input_count) {
        return -1;
    }
    if (*in_out_input_count == 0u && out_inputs == (d_net_input_frame *)0) {
        return -1;
    }

    if (ctx->cursor < ctx->frame_count) {
        if (ctx->frames[ctx->cursor].tick_index == tick_index) {
            frame = &ctx->frames[ctx->cursor];
        }
    }
    if (!frame) {
        for (i = 0u; i < ctx->frame_count; ++i) {
            if (ctx->frames[i].tick_index == tick_index) {
                frame = &ctx->frames[i];
                ctx->cursor = i;
                break;
            }
        }
    }
    if (!frame) {
        *in_out_input_count = 0u;
        return -2;
    }
    if (!out_inputs || *in_out_input_count < frame->input_count) {
        *in_out_input_count = frame->input_count;
        return -3;
    }

    for (i = 0u; i < frame->input_count; ++i) {
        out_inputs[i] = frame->inputs[i];
    }
    *in_out_input_count = frame->input_count;

    if (ctx->cursor < ctx->frame_count && ctx->frames[ctx->cursor].tick_index == tick_index) {
        ctx->cursor += 1u;
    }
    return 0;
}

int d_replay_serialize(
    const d_replay_context *ctx,
    d_tlv_blob             *out
) {
    dreplay_builder builder;
    u32 i;
    if (!ctx || !out) {
        return -1;
    }
    if (!ctx->frames && ctx->frame_count > 0u) {
        return -1;
    }

    d_replay_builder_init(&builder);
    for (i = 0u; i < ctx->frame_count; ++i) {
        const dreplay_frame *frame = &ctx->frames[i];
        unsigned char *payload;
        u32 payload_len;
        u32 offset;
        u32 j;

        payload_len = 8u; /* tick_index + input_count */
        for (j = 0u; j < frame->input_count; ++j) {
            if (frame->inputs[j].payload_size > 0xFFFFFFFFu - (payload_len + 12u)) {
                d_replay_builder_reset(&builder);
                return -1;
            }
            payload_len += 12u + frame->inputs[j].payload_size;
        }

        payload = (unsigned char *)malloc(payload_len);
        if (!payload && payload_len != 0u) {
            d_replay_builder_reset(&builder);
            return -1;
        }
        offset = 0u;
        memcpy(payload + offset, &frame->tick_index, sizeof(u32));
        offset += 4u;
        memcpy(payload + offset, &frame->input_count, sizeof(u32));
        offset += 4u;

        for (j = 0u; j < frame->input_count; ++j) {
            memcpy(payload + offset, &frame->inputs[j].tick_index, sizeof(u32));
            offset += 4u;
            memcpy(payload + offset, &frame->inputs[j].player_id, sizeof(u32));
            offset += 4u;
            memcpy(payload + offset, &frame->inputs[j].payload_size, sizeof(u32));
            offset += 4u;
            if (frame->inputs[j].payload_size > 0u) {
                memcpy(payload + offset, frame->inputs[j].payload, frame->inputs[j].payload_size);
                offset += frame->inputs[j].payload_size;
            }
        }

        if (d_replay_builder_append(&builder, D_REPLAY_TAG_FRAME, payload, payload_len) != 0) {
            free(payload);
            d_replay_builder_reset(&builder);
            return -1;
        }
        free(payload);
    }

    out->ptr = builder.data;
    out->len = builder.length;
    return 0;
}

int d_replay_deserialize(
    const d_tlv_blob *in,
    d_replay_context *out_ctx
) {
    u32 offset;
    dreplay_frame *frames = (dreplay_frame *)0;
    u32 frame_cap = 0u;
    u32 frame_count = 0u;

    if (!in || !out_ctx) {
        return -1;
    }

    d_replay_shutdown(out_ctx);

    offset = 0u;
    while (offset + 8u <= in->len) {
        u32 tag;
        u32 len;

        memcpy(&tag, in->ptr + offset, sizeof(u32));
        memcpy(&len, in->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > in->len - offset) {
            d_replay_free_frames(frames, frame_count);
            return -1;
        }

        if (tag == D_REPLAY_TAG_FRAME) {
            const unsigned char *p = in->ptr + offset;
            u32 remaining = len;
            dreplay_frame frame;
            u32 j;

            if (remaining < 8u) {
                d_replay_free_frames(frames, frame_count);
                return -1;
            }
            memcpy(&frame.tick_index, p, sizeof(u32));
            p += 4u;
            memcpy(&frame.input_count, p, sizeof(u32));
            p += 4u;
            remaining -= 8u;

            frame.inputs = (d_net_input_frame *)0;
            if (frame.input_count > 0u) {
                frame.inputs = (d_net_input_frame *)malloc(sizeof(d_net_input_frame) * frame.input_count);
                if (!frame.inputs) {
                    d_replay_free_frames(frames, frame_count);
                    return -1;
                }
                memset(frame.inputs, 0, sizeof(d_net_input_frame) * frame.input_count);
            }

            for (j = 0u; j < frame.input_count; ++j) {
                if (remaining < 12u) {
                    d_replay_free_inputs(frame.inputs, j);
                    d_replay_free_frames(frames, frame_count);
                    return -1;
                }
                memcpy(&frame.inputs[j].tick_index, p, sizeof(u32));
                p += 4u;
                memcpy(&frame.inputs[j].player_id, p, sizeof(u32));
                p += 4u;
                memcpy(&frame.inputs[j].payload_size, p, sizeof(u32));
                p += 4u;
                remaining -= 12u;

                if (frame.inputs[j].payload_size > remaining) {
                    d_replay_free_inputs(frame.inputs, frame.input_count);
                    d_replay_free_frames(frames, frame_count);
                    return -1;
                }
                if (frame.inputs[j].payload_size > 0u) {
                    frame.inputs[j].payload = (u8 *)malloc(frame.inputs[j].payload_size);
                    if (!frame.inputs[j].payload) {
                        d_replay_free_inputs(frame.inputs, frame.input_count);
                        d_replay_free_frames(frames, frame_count);
                        return -1;
                    }
                    memcpy(frame.inputs[j].payload, p, frame.inputs[j].payload_size);
                    p += frame.inputs[j].payload_size;
                    remaining -= frame.inputs[j].payload_size;
                } else {
                    frame.inputs[j].payload = (u8 *)0;
                }
            }

            if (frame_count >= frame_cap) {
                u32 new_cap = frame_cap ? frame_cap * 2u : 4u;
                dreplay_frame *new_frames;
                if (new_cap <= frame_count) {
                    new_cap = frame_count + 1u;
                }
                new_frames = (dreplay_frame *)realloc(frames, sizeof(dreplay_frame) * new_cap);
                if (!new_frames) {
                    d_replay_free_inputs(frame.inputs, frame.input_count);
                    d_replay_free_frames(frames, frame_count);
                    return -1;
                }
                frames = new_frames;
                frame_cap = new_cap;
            }
            frames[frame_count] = frame;
            frame_count += 1u;
        }

        offset += len;
    }

    out_ctx->mode = DREPLAY_MODE_PLAYBACK;
    out_ctx->determinism_mode = 2u;
    out_ctx->last_hash = 0u;
    out_ctx->frames = frames;
    out_ctx->frame_count = frame_count;
    out_ctx->frame_capacity = frame_cap;
    out_ctx->cursor = 0u;
    return 0;
}

static void d_replay_tick_stub(d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static int d_replay_save_instance_stub(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_replay_load_instance_stub(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void d_replay_register_models_stub(void) {
}

static void d_replay_load_protos_stub(const d_tlv_blob *blob) {
    (void)blob;
}

void d_replay_register_subsystem(void) {
    d_subsystem_desc desc;
    const d_subsystem_desc *existing;
    int rc;

    if (g_replay_registered) {
        return;
    }
    existing = d_subsystem_get_by_id(D_SUBSYS_REPLAY);
    if (existing) {
        g_replay_registered = 1;
        return;
    }

    desc.subsystem_id = D_SUBSYS_REPLAY;
    desc.name = "replay";
    desc.version = 1u;
    desc.register_models = d_replay_register_models_stub;
    desc.load_protos = d_replay_load_protos_stub;
    desc.init_instance = (void (*)(d_world *))0;
    desc.tick = d_replay_tick_stub;
    desc.save_chunk = (int (*)(d_world *, d_chunk *, d_tlv_blob *))0;
    desc.load_chunk = (int (*)(d_world *, d_chunk *, const d_tlv_blob *))0;
    desc.save_instance = d_replay_save_instance_stub;
    desc.load_instance = d_replay_load_instance_stub;

    rc = d_subsystem_register(&desc);
    if (rc == 0) {
        g_replay_registered = 1;
    }
}
