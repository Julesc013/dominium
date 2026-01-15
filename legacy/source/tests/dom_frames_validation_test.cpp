/*
FILE: source/tests/dom_frames_validation_test.cpp
MODULE: Repository
PURPOSE: Validates frame tree validation and deterministic iteration order.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

#include "runtime/dom_frames.h"

static void zero_posseg(dom_posseg_q16 *pos) {
    u32 i;
    for (i = 0u; i < 3u; ++i) {
        pos->seg[i] = 0;
        pos->loc[i] = 0;
    }
}

static void fill_desc(dom_frame_desc *desc,
                      dom_frame_id id,
                      dom_frame_id parent_id,
                      u32 kind,
                      u64 body_id) {
    std::memset(desc, 0, sizeof(*desc));
    desc->id = id;
    desc->parent_id = parent_id;
    desc->kind = kind;
    desc->body_id = body_id;
    zero_posseg(&desc->origin_offset);
    desc->rotation_period_ticks = 0ull;
    desc->rotation_epoch_tick = 0ull;
    desc->rotation_phase_turns = 0;
}

struct OrderCtx {
    dom_frame_id last_id;
    int first;
};

static void check_order(const dom_frame_info *info, void *user) {
    OrderCtx *ctx = static_cast<OrderCtx *>(user);
    if (ctx->first) {
        ctx->first = 0;
        ctx->last_id = info->id;
        return;
    }
    assert(info->id > ctx->last_id);
    ctx->last_id = info->id;
}

int main(void) {
    dom_frames *frames = dom_frames_create();
    dom_frame_desc desc;
    int rc;

    assert(frames != 0);
    fill_desc(&desc, 10ull, 20ull, DOM_FRAME_KIND_INERTIAL_BARYCENTRIC, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    rc = dom_frames_validate(frames);
    assert(rc == DOM_FRAMES_INVALID_TREE);
    dom_frames_destroy(frames);

    frames = dom_frames_create();
    assert(frames != 0);
    fill_desc(&desc, 1ull, 2ull, DOM_FRAME_KIND_INERTIAL_BARYCENTRIC, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    fill_desc(&desc, 2ull, 1ull, DOM_FRAME_KIND_INERTIAL_BARYCENTRIC, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    rc = dom_frames_validate(frames);
    assert(rc == DOM_FRAMES_INVALID_TREE);
    dom_frames_destroy(frames);

    frames = dom_frames_create();
    assert(frames != 0);
    fill_desc(&desc, 3ull, 0ull, DOM_FRAME_KIND_INERTIAL_BARYCENTRIC, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    fill_desc(&desc, 1ull, 0ull, DOM_FRAME_KIND_INERTIAL_BARYCENTRIC, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    fill_desc(&desc, 2ull, 0ull, DOM_FRAME_KIND_INERTIAL_BARYCENTRIC, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    assert(dom_frames_validate(frames) == DOM_FRAMES_OK);
    {
        OrderCtx ctx;
        ctx.last_id = 0ull;
        ctx.first = 1;
        assert(dom_frames_iterate(frames, check_order, &ctx) == DOM_FRAMES_OK);
    }
    dom_frames_destroy(frames);

    std::printf("dom_frames_validation_test: OK\n");
    return 0;
}
