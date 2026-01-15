/*
FILE: source/tests/dom_frames_transform_roundtrip_test.cpp
MODULE: Repository
PURPOSE: Validates baseline frame transforms and round-trip stability.
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
                      u64 body_id,
                      u64 rotation_period_ticks) {
    std::memset(desc, 0, sizeof(*desc));
    desc->id = id;
    desc->parent_id = parent_id;
    desc->kind = kind;
    desc->body_id = body_id;
    zero_posseg(&desc->origin_offset);
    desc->rotation_period_ticks = rotation_period_ticks;
    desc->rotation_epoch_tick = 0ull;
    desc->rotation_phase_turns = 0;
}

static i32 abs_i32(i32 v) {
    return (v < 0) ? -v : v;
}

int main(void) {
    dom_frames *frames = dom_frames_create();
    dom_frame_desc desc;
    dom_posseg_q16 pos;
    dom_posseg_q16 fixed;
    dom_posseg_q16 roundtrip;
    dom_posseg_q16 identity;
    const dom_frame_id root_id = 1ull;
    const dom_frame_id body_centered_id = 2ull;
    const dom_frame_id body_fixed_id = 3ull;
    const u64 body_id = 42ull;
    int rc;

    assert(frames != 0);
    fill_desc(&desc, root_id, 0ull, DOM_FRAME_KIND_INERTIAL_BARYCENTRIC, 0ull, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    fill_desc(&desc, body_centered_id, root_id, DOM_FRAME_KIND_BODY_CENTERED_INERTIAL, body_id, 0ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    fill_desc(&desc, body_fixed_id, body_centered_id, DOM_FRAME_KIND_BODY_FIXED, body_id, 100ull);
    assert(dom_frames_register(frames, &desc) == DOM_FRAMES_OK);
    assert(dom_frames_validate(frames) == DOM_FRAMES_OK);

    zero_posseg(&pos);
    pos.loc[0] = d_q16_16_from_int(1);
    pos.loc[1] = d_q16_16_from_int(2);
    pos.loc[2] = d_q16_16_from_int(3);

    rc = dom_frames_transform_pos(frames, body_centered_id, body_centered_id, &pos, 25ull, &identity);
    assert(rc == DOM_FRAMES_OK);
    assert(std::memcmp(&pos, &identity, sizeof(pos)) == 0);

    rc = dom_frames_transform_pos(frames, body_centered_id, body_fixed_id, &pos, 25ull, &fixed);
    assert(rc == DOM_FRAMES_OK);
    rc = dom_frames_transform_pos(frames, body_fixed_id, body_centered_id, &fixed, 25ull, &roundtrip);
    assert(rc == DOM_FRAMES_OK);

    assert(roundtrip.seg[0] == pos.seg[0]);
    assert(roundtrip.seg[1] == pos.seg[1]);
    assert(roundtrip.seg[2] == pos.seg[2]);
    assert(abs_i32(roundtrip.loc[0] - pos.loc[0]) <= 2);
    assert(abs_i32(roundtrip.loc[1] - pos.loc[1]) <= 2);
    assert(abs_i32(roundtrip.loc[2] - pos.loc[2]) <= 2);

    dom_frames_destroy(frames);

    std::printf("dom_frames_transform_roundtrip_test: OK\n");
    return 0;
}
