#include "domino/dworld.h"

static TileHeight dworld_clamp_z(TileHeight z)
{
    if (z < (TileHeight)DOM_Z_MIN) return (TileHeight)DOM_Z_MIN;
    if (z > (TileHeight)DOM_Z_MAX) return (TileHeight)DOM_Z_MAX;
    return z;
}

TileCoord dworld_wrap_tile_coord(TileCoord t)
{
    const TileCoord span = (TileCoord)DOM_WORLD_TILES;
    TileCoord wrapped = (TileCoord)(t % span);
    if (wrapped < 0) {
        wrapped += span;
    }
    return wrapped;
}

void dworld_tile_to_chunk_local(const WPosTile *tile, ChunkPos *out_chunk, LocalPos *out_local)
{
    TileCoord wx;
    TileCoord wy;
    TileHeight wz;
    if (!tile) return;
    wx = dworld_wrap_tile_coord(tile->x);
    wy = dworld_wrap_tile_coord(tile->y);
    wz = dworld_clamp_z(tile->z);

    if (out_chunk) {
        out_chunk->cx = (ChunkCoord)(wx >> 4);
        out_chunk->cy = (ChunkCoord)(wy >> 4);
        out_chunk->cz = (ChunkHeight)(((I32)wz - (I32)DOM_Z_MIN) / DOM_CHUNK_SIZE);
    }
    if (out_local) {
        out_local->lx = (LocalCoord)(wx & (DOM_CHUNK_SIZE - 1));
        out_local->ly = (LocalCoord)(wy & (DOM_CHUNK_SIZE - 1));
        out_local->lz = (LocalCoord)((((I32)wz - (I32)DOM_Z_MIN) & (DOM_CHUNK_SIZE - 1)));
    }
}

void dworld_chunk_local_to_tile(const ChunkPos *chunk, const LocalPos *local, WPosTile *out_tile)
{
    TileCoord raw_x;
    TileCoord raw_y;
    I32 raw_z;
    if (!chunk || !local || !out_tile) return;

    raw_x = (TileCoord)((chunk->cx << 4) | (TileCoord)local->lx);
    raw_y = (TileCoord)((chunk->cy << 4) | (TileCoord)local->ly);
    raw_z = (I32)((I32)chunk->cz * DOM_CHUNK_SIZE) + (I32)local->lz + (I32)DOM_Z_MIN;

    out_tile->x = dworld_wrap_tile_coord(raw_x);
    out_tile->y = dworld_wrap_tile_coord(raw_y);
    if (raw_z < DOM_Z_MIN) raw_z = DOM_Z_MIN;
    else if (raw_z > DOM_Z_MAX) raw_z = DOM_Z_MAX;
    out_tile->z = (TileHeight)raw_z;
}

void dworld_init_exact_from_tile(const WPosTile *tile, WPosExact *out_pos)
{
    if (!tile || !out_pos) return;
    out_pos->tile = *tile;
    out_pos->dx = (PosUnit)0;
    out_pos->dy = (PosUnit)0;
    out_pos->dz = (PosUnit)0;
}

EnvironmentKind dworld_env_from_z(TileHeight z)
{
    TileHeight zz = dworld_clamp_z(z);
    if (zz >= (TileHeight)DOM_Z_BUILD_MIN && zz <= (TileHeight)DOM_Z_BUILD_MAX) {
        return ENV_SURFACE_GRID;
    }
    if (zz < (TileHeight)DOM_Z_BUILD_MIN) {
        /* Still inside the voxel grid; finer underground stratification later */
        return ENV_SURFACE_GRID;
    }
    if (zz <= (TileHeight)(DOM_Z_TOP_MAX - 128)) {
        /* TODO: refine atmosphere layering once climate/vehicles are implemented */
        return ENV_AIR_LOCAL;
    }
    return ENV_HIGH_ATMO;
}

bool dworld_z_is_buildable(TileHeight z)
{
    return (z >= (TileHeight)DOM_Z_BUILD_MIN) && (z <= (TileHeight)DOM_Z_BUILD_MAX);
}

bool dworld_should_switch_to_high_atmo(const WPosExact *pos)
{
    if (!pos) return false;
    return pos->tile.z > (TileHeight)DOM_Z_BUILD_MAX;
}

bool dworld_should_switch_to_orbit(const WPosExact *pos)
{
    /* TODO: incorporate speed/altitude thresholds and body gravity */
    if (!pos) return false;
    return pos->tile.z >= (TileHeight)DOM_Z_TOP_MAX;
}
