#include "world_addr.h"

#include <stdlib.h>

static void wrap_axis(i64 raw_value, SegmentIndex *seg, fix32 *out_coord)
{
    const i64 span = (i64)1 << 32; /* 65536m in Q16.16 */
    i64 value = raw_value;
    i32 seg_accum = (i32)(*seg);
    while (value < 0) {
        value += span;
        seg_accum = (seg_accum - 1) & 0xFF;
    }
    while (value >= span) {
        value -= span;
        seg_accum = (seg_accum + 1) & 0xFF;
    }
    *out_coord = (fix32)(u32)value;
    *seg = (SegmentIndex)seg_accum;
}

void simpos_normalise(SimPos *pos)
{
    if (!pos) return;
    wrap_axis((i64)(i32)pos->x, &pos->sx, &pos->x);
    wrap_axis((i64)(i32)pos->y, &pos->sy, &pos->y);

    if (pos->z < fix32_from_int(WORLD_Z_MIN_METERS)) {
        pos->z = fix32_from_int(WORLD_Z_MIN_METERS);
    } else if (pos->z >= fix32_from_int(WORLD_Z_MAX_METERS)) {
        pos->z = fix32_from_int(WORLD_Z_MAX_METERS - 1);
    }
}

void simpos_move(SimPos *pos, fix32 dx, fix32 dy, fix32 dz)
{
    i64 raw_x;
    i64 raw_y;
    if (!pos) return;
    raw_x = (i64)(u32)pos->x + (i64)(i32)dx;
    raw_y = (i64)(u32)pos->y + (i64)(i32)dy;
    wrap_axis(raw_x, &pos->sx, &pos->x);
    wrap_axis(raw_y, &pos->sy, &pos->y);

    pos->z = pos->z + dz;
    if (pos->z < fix32_from_int(WORLD_Z_MIN_METERS)) {
        pos->z = fix32_from_int(WORLD_Z_MIN_METERS);
    } else if (pos->z >= fix32_from_int(WORLD_Z_MAX_METERS)) {
        pos->z = fix32_from_int(WORLD_Z_MAX_METERS - 1);
    }
}

i32 world_local_meter_x(const SimPos *pos)
{
    if (!pos) return 0;
    return (i32)(((u32)pos->x) >> 16);
}

i32 world_local_meter_y(const SimPos *pos)
{
    if (!pos) return 0;
    return (i32)(((u32)pos->y) >> 16);
}

void world_chunk_from_simpos(const SimPos *pos, ChunkKey3D *out_key, SaveLocalPos *out_local)
{
    u32 raw_x;
    u32 raw_y;
    i32 local_x_m;
    i32 local_y_m;
    i32 z_m;
    i32 z_offset;
    if (!pos || !out_key) return;

    raw_x = (u32)pos->x;
    raw_y = (u32)pos->y;
    local_x_m = (i32)(raw_x >> 16);
    local_y_m = (i32)(raw_y >> 16);

    out_key->gx = ((i32)pos->sx << 12) + (local_x_m >> 4);
    out_key->gy = ((i32)pos->sy << 12) + (local_y_m >> 4);

    z_m = fix32_to_int(pos->z);
    if (z_m < WORLD_Z_MIN_METERS) z_m = WORLD_Z_MIN_METERS;
    if (z_m >= WORLD_Z_MAX_METERS) z_m = WORLD_Z_MAX_METERS - 1;
    z_offset = z_m - WORLD_Z_MIN_METERS;
    out_key->gz = z_offset / CHUNK_SIZE_METERS;

    if (out_local) {
        u32 frac_x = (raw_x & 0xFFFFU) >> 4;
        u32 frac_y = (raw_y & 0xFFFFU) >> 4;
        u32 frac_z = ((u32)pos->z & 0xFFFFU) >> 4;
        u32 lx_m = (u32)(local_x_m & (CHUNK_SIZE_METERS - 1));
        u32 ly_m = (u32)(local_y_m & (CHUNK_SIZE_METERS - 1));
        u32 lz_m = (u32)(z_offset & (CHUNK_SIZE_METERS - 1));
        out_local->chunk_x = (u16)out_key->gx;
        out_local->chunk_y = (u16)out_key->gy;
        out_local->chunk_z = (u16)out_key->gz;
        out_local->lx = (fix16)((lx_m << 12) | frac_x);
        out_local->ly = (fix16)((ly_m << 12) | frac_y);
        out_local->lz = (fix16)((lz_m << 12) | frac_z);
    }
}

void world_simpos_from_chunk(const ChunkKey3D *key, const SaveLocalPos *local, SimPos *out_pos)
{
    u32 chunk_local_x;
    u32 chunk_local_y;
    u32 meter_x;
    u32 meter_y;
    u32 frac_x = 0;
    u32 frac_y = 0;
    u32 frac_z = 0;
    i32 z_base = 0;
    if (!key || !out_pos) return;

    chunk_local_x = (u32)key->gx & 0xFFFU;
    chunk_local_y = (u32)key->gy & 0xFFFU;
    meter_x = chunk_local_x * CHUNK_SIZE_METERS;
    meter_y = chunk_local_y * CHUNK_SIZE_METERS;
    if (local) {
        meter_x += (u32)(local->lx >> 12);
        meter_y += (u32)(local->ly >> 12);
        frac_x = ((u32)local->lx & 0x0FFFU) << 4;
        frac_y = ((u32)local->ly & 0x0FFFU) << 4;
        frac_z = ((u32)local->lz & 0x0FFFU) << 4;
    }
    out_pos->sx = (SegmentIndex)(((u32)key->gx >> 12) & 0xFFU);
    out_pos->sy = (SegmentIndex)(((u32)key->gy >> 12) & 0xFFU);
    out_pos->x = (fix32)((meter_x << 16) | frac_x);
    out_pos->y = (fix32)((meter_y << 16) | frac_y);

    z_base = key->gz * CHUNK_SIZE_METERS;
    if (local) {
        z_base += (i32)(local->lz >> 12);
    }
    z_base += WORLD_Z_MIN_METERS;
    out_pos->z = fix32_from_int(z_base);
    out_pos->z = out_pos->z + (fix32)frac_z;

    simpos_normalise(out_pos);
}
