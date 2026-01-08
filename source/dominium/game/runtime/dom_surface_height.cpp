/*
FILE: source/dominium/game/runtime/dom_surface_height.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_height
RESPONSIBILITY: Deterministic procedural surface height sampler (stub v1).
*/
#include "runtime/dom_surface_height.h"

#include <cstring>

namespace {

static u64 mix_u64(u64 v) {
    v ^= v >> 33;
    v *= 0xff51afd7ed558ccdull;
    v ^= v >> 33;
    v *= 0xc4ceb9fe1a85ec53ull;
    v ^= v >> 33;
    return v;
}

} // namespace

int dom_surface_height_sample(dom_body_id body_id,
                              const dom_topo_latlong_q16 *latlong,
                              q48_16 *out_height_m) {
    u64 h;
    u64 ll;
    i64 height;
    const i64 range_m = 1000;

    if (!latlong || !out_height_m) {
        return DOM_SURFACE_HEIGHT_INVALID_ARGUMENT;
    }

    ll = ((u64)(u32)latlong->lat_turns << 32) | (u64)(u32)latlong->lon_turns;
    h = mix_u64(((u64)body_id) ^ ll ^ 0x9e3779b97f4a7c15ull);

    height = (i64)(h % (u64)(range_m * 2 + 1)) - range_m;
    *out_height_m = d_q48_16_from_int(height);
    return DOM_SURFACE_HEIGHT_OK;
}
