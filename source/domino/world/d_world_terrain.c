#include <string.h>

#include "world/d_world_terrain.h"

#define DWTERRAIN_CELL_SHIFT 5u /* 32m grid for height interpolation */
#define DWTERRAIN_CELL_SIZE  (1u << DWTERRAIN_CELL_SHIFT)

static u32 dwterrain_hash_u32(u64 seed, i32 gx, i32 gy) {
    u32 x = (u32)(seed ^ (seed >> 32));
    x ^= (u32)gx * 0x85ebca6bu;
    x ^= (u32)gy * 0xc2b2ae35u;
    x ^= x >> 16;
    x *= 0x7feb352du;
    x ^= x >> 15;
    x *= 0x846ca68bu;
    x ^= x >> 16;
    return x;
}

static i32 dwterrain_floor_div_i32_pow2(i32 v, u32 shift) {
    u32 mask = (1u << shift) - 1u;
    if (v >= 0) {
        return (i32)((u32)v >> shift);
    }
    /* floor division for negatives: -ceil(|v|/2^shift) */
    {
        u32 av = (u32)(-v);
        u32 add = (av & mask) ? 1u : 0u;
        return -(i32)((av >> shift) + add);
    }
}

static i32 dwterrain_floor_q32_32_to_i32(q32_32 v) {
    if (v >= 0) {
        return (i32)(v >> Q32_32_FRAC_BITS);
    }
    {
        q32_32 nv = (q32_32)(-v);
        i32 ip = (i32)(nv >> Q32_32_FRAC_BITS);
        u32 frac = (u32)(nv & (q32_32)0xFFFFFFFFu);
        if (frac != 0u) {
            ip += 1;
        }
        return -ip;
    }
}

static q16_16 dwterrain_height_corner_q16(u64 seed, i32 gx, i32 gy) {
    u32 h = dwterrain_hash_u32(seed, gx, gy);
    i32 r = (i32)(h & 0xFFu);
    /* [-128..127] scaled to ~[-32..+31.75] meters in Q16.16 */
    r -= 128;
    return (q16_16)(r << 14);
}

static q16_16 dwterrain_q16_mul(q16_16 a, q16_16 b) {
    return (q16_16)(((i64)a * (i64)b) >> 16);
}

int d_world_height_at(d_world *w, q32_32 x, q32_32 y, q32_32 *out_z) {
    i32 x_floor;
    i32 y_floor;
    i32 cell_x;
    i32 cell_y;
    i32 rem_x;
    i32 rem_y;
    u32 frac_x;
    u32 frac_y;
    u64 local_x_q32;
    u64 local_y_q32;
    q16_16 tx;
    q16_16 ty;
    q16_16 h00, h10, h01, h11;
    q16_16 hx0, hx1, hxy;
    q32_32 z;

    if (out_z) {
        *out_z = 0;
    }
    if (!w || !out_z) {
        return -1;
    }

    x_floor = dwterrain_floor_q32_32_to_i32(x);
    y_floor = dwterrain_floor_q32_32_to_i32(y);
    frac_x = (u32)(x - (((q32_32)x_floor) << Q32_32_FRAC_BITS));
    frac_y = (u32)(y - (((q32_32)y_floor) << Q32_32_FRAC_BITS));

    cell_x = dwterrain_floor_div_i32_pow2(x_floor, DWTERRAIN_CELL_SHIFT);
    cell_y = dwterrain_floor_div_i32_pow2(y_floor, DWTERRAIN_CELL_SHIFT);
    rem_x = x_floor - (cell_x * (i32)DWTERRAIN_CELL_SIZE);
    rem_y = y_floor - (cell_y * (i32)DWTERRAIN_CELL_SIZE);
    if (rem_x < 0) rem_x = 0;
    if (rem_y < 0) rem_y = 0;

    local_x_q32 = ((u64)(u32)rem_x << 32) | (u64)frac_x;
    local_y_q32 = ((u64)(u32)rem_y << 32) | (u64)frac_y;
    tx = (q16_16)((local_x_q32 << 16) / ((u64)DWTERRAIN_CELL_SIZE << 32));
    ty = (q16_16)((local_y_q32 << 16) / ((u64)DWTERRAIN_CELL_SIZE << 32));

    h00 = dwterrain_height_corner_q16(w->meta.seed, cell_x, cell_y);
    h10 = dwterrain_height_corner_q16(w->meta.seed, cell_x + 1, cell_y);
    h01 = dwterrain_height_corner_q16(w->meta.seed, cell_x, cell_y + 1);
    h11 = dwterrain_height_corner_q16(w->meta.seed, cell_x + 1, cell_y + 1);

    hx0 = (q16_16)((i64)h00 + (i64)dwterrain_q16_mul((q16_16)(h10 - h00), tx));
    hx1 = (q16_16)((i64)h01 + (i64)dwterrain_q16_mul((q16_16)(h11 - h01), tx));
    hxy = (q16_16)((i64)hx0 + (i64)dwterrain_q16_mul((q16_16)(hx1 - hx0), ty));

    z = ((q32_32)hxy) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
    *out_z = z;
    return 0;
}

