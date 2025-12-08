#include "domino/dhydro.h"
#include "domino/dclimate.h"
#include "domino/dweather.h"

#include <stdlib.h>
#include <string.h>

#define DHYDRO_MAX_CELLS       8192
#define DHYDRO_MAX_RIVER_LINKS 2048
#define DHYDRO_MAX_BODIES      16
#define DHYDRO_Q16_ONE         ((Q16_16)(1 << 16))

typedef struct {
    BodyId   body;
    WPosTile tile;
    Q16_16   depth;
    Q16_16   rain_accum;
    Q16_16   flow_u;
    Q16_16   flow_v;
} HydroCell;

typedef struct {
    BodyId body;
    Q16_16 evap_per_tick;
} HydroBody;

static HydroCell      g_cells[DHYDRO_MAX_CELLS];
static U32            g_cell_count = 0;
static HydroRiverLink g_river_links[DHYDRO_MAX_RIVER_LINKS];
static U32            g_river_count = 0;
static HydroBody      g_bodies[DHYDRO_MAX_BODIES];
static FieldId        g_field_water_depth;

static Q16_16 dhydro_mul_q16(Q16_16 a, Q16_16 b)
{
    return (Q16_16)(((I64)a * (I64)b) >> 16);
}

static Q16_16 dhydro_clamp_q16(Q16_16 v, Q16_16 lo, Q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

FieldId dhydro_field_water_depth(void)
{
    if (g_field_water_depth != 0) return g_field_water_depth;
    if (!g_field_water_depth) {
        const FieldDesc *desc = dfield_find_by_name("water_depth");
        if (desc) {
            g_field_water_depth = desc->id;
        } else {
            FieldDesc def;
            memset(&def, 0, sizeof(def));
            def.name = "water_depth";
            def.unit = UNIT_DEPTH_M;
            def.storage = FIELD_STORAGE_Q16_16;
            g_field_water_depth = dfield_register(&def);
        }
    }
    return g_field_water_depth;
}

static HydroBody *dhydro_get_body_state(BodyId body, bool create)
{
    U32 i;
    if (body == 0) return 0;
    for (i = 0; i < DHYDRO_MAX_BODIES; ++i) {
        if (g_bodies[i].body == body) {
            return &g_bodies[i];
        }
    }
    if (!create) return 0;
    for (i = 0; i < DHYDRO_MAX_BODIES; ++i) {
        if (g_bodies[i].body == 0) {
            g_bodies[i].body = body;
            g_bodies[i].evap_per_tick = (Q16_16)(1 << 8); /* mild evaporation */
            return &g_bodies[i];
        }
    }
    return 0;
}

static bool dhydro_same_tile(const WPosTile *a, const WPosTile *b)
{
    return a && b && a->x == b->x && a->y == b->y && a->z == b->z;
}

static HydroCell *dhydro_find_cell(BodyId body, const WPosTile *tile)
{
    U32 i;
    if (!tile) return 0;
    for (i = 0; i < g_cell_count; ++i) {
        if (g_cells[i].body == body && dhydro_same_tile(&g_cells[i].tile, tile)) {
            return &g_cells[i];
        }
    }
    return 0;
}

static HydroCell *dhydro_ensure_cell(BodyId body, const WPosTile *tile)
{
    HydroCell *cell = dhydro_find_cell(body, tile);
    if (cell) return cell;
    if (g_cell_count >= DHYDRO_MAX_CELLS) return 0;
    cell = &g_cells[g_cell_count++];
    memset(cell, 0, sizeof(*cell));
    cell->body = body;
    cell->tile = *tile;
    return cell;
}

bool dhydro_init_body(BodyId body)
{
    return dhydro_get_body_state(body, true) != 0;
}

bool dhydro_register_river_link(const HydroRiverLink *link)
{
    if (!link) return false;
    if (g_river_count >= DHYDRO_MAX_RIVER_LINKS) return false;
    g_river_links[g_river_count++] = *link;
    return true;
}

bool dhydro_add_rainfall(BodyId body, const WPosTile *tile, Q16_16 water_depth)
{
    HydroCell *cell;
    if (!tile) return false;
    cell = dhydro_ensure_cell(body, tile);
    if (!cell) return false;
    cell->rain_accum += water_depth;
    return true;
}

bool dhydro_register_evaporation_bias(BodyId body, Q16_16 evap_per_tick)
{
    HydroBody *b = dhydro_get_body_state(body, true);
    if (!b) return false;
    b->evap_per_tick = evap_per_tick;
    return true;
}

static void dhydro_apply_evaporation(HydroBody *body_state, HydroCell *cell, U32 ticks)
{
    Q16_16 evap = 0;
    if (!body_state || !cell) return;
    evap = dhydro_mul_q16(body_state->evap_per_tick, dnum_from_int32((I32)ticks));
    if (evap > cell->depth) {
        cell->depth = 0;
    } else {
        cell->depth -= evap;
    }
}

static void dhydro_apply_rain(HydroCell *cell)
{
    if (!cell) return;
    cell->depth += cell->rain_accum;
    cell->rain_accum = 0;
}

static void dhydro_reset_flow(HydroCell *cell)
{
    if (!cell) return;
    cell->flow_u = 0;
    cell->flow_v = 0;
}

static void dhydro_apply_flow_to_neighbor(HydroCell *cell, HydroCell *nbr, Q16_16 outflow, int dx, int dy)
{
    if (!cell || !nbr) return;
    if (outflow > cell->depth) outflow = cell->depth;
    cell->depth -= outflow;
    nbr->depth += outflow;
    cell->flow_u += (Q16_16)(dx >= 0 ? outflow : -outflow);
    cell->flow_v += (Q16_16)(dy >= 0 ? outflow : -outflow);
}

static void dhydro_step_tile(BodyId body, HydroBody *body_state, HydroCell *cell, const WPosTile *tile, U32 ticks)
{
    WPosTile nbr;
    HydroCell *nbr_cell;
    Q16_16 surface;
    Q16_16 outflow;
    Q16_16 nbr_surface;

    if (!cell || !tile) return;
    dhydro_reset_flow(cell);
    dhydro_apply_rain(cell);
    surface = dnum_from_int32((I32)tile->z) + cell->depth;
    if (surface < 0) surface = 0;

    /* +X neighbor */
    nbr = *tile;
    nbr.x = dworld_wrap_tile_coord(nbr.x + 1);
    nbr_cell = dhydro_ensure_cell(body, &nbr);
    if (nbr_cell) {
        nbr_surface = dnum_from_int32((I32)nbr.z) + nbr_cell->depth;
        if (surface > nbr_surface) {
            outflow = (surface - nbr_surface) >> 3;
            dhydro_apply_flow_to_neighbor(cell, nbr_cell, outflow, 1, 0);
            surface = dnum_from_int32((I32)tile->z) + cell->depth;
        }
    }

    /* -X neighbor */
    nbr = *tile;
    nbr.x = dworld_wrap_tile_coord(nbr.x - 1);
    nbr_cell = dhydro_ensure_cell(body, &nbr);
    if (nbr_cell) {
        nbr_surface = dnum_from_int32((I32)nbr.z) + nbr_cell->depth;
        if (surface > nbr_surface) {
            outflow = (surface - nbr_surface) >> 3;
            dhydro_apply_flow_to_neighbor(cell, nbr_cell, outflow, -1, 0);
            surface = dnum_from_int32((I32)tile->z) + cell->depth;
        }
    }

    /* +Y neighbor */
    nbr = *tile;
    nbr.y = dworld_wrap_tile_coord(nbr.y + 1);
    nbr_cell = dhydro_ensure_cell(body, &nbr);
    if (nbr_cell) {
        nbr_surface = dnum_from_int32((I32)nbr.z) + nbr_cell->depth;
        if (surface > nbr_surface) {
            outflow = (surface - nbr_surface) >> 3;
            dhydro_apply_flow_to_neighbor(cell, nbr_cell, outflow, 0, 1);
            surface = dnum_from_int32((I32)tile->z) + cell->depth;
        }
    }

    /* -Y neighbor */
    nbr = *tile;
    nbr.y = dworld_wrap_tile_coord(nbr.y - 1);
    nbr_cell = dhydro_ensure_cell(body, &nbr);
    if (nbr_cell) {
        nbr_surface = dnum_from_int32((I32)nbr.z) + nbr_cell->depth;
        if (surface > nbr_surface) {
            outflow = (surface - nbr_surface) >> 3;
            dhydro_apply_flow_to_neighbor(cell, nbr_cell, outflow, 0, -1);
        }
    }

    dhydro_apply_evaporation(body_state, cell, ticks);
}

bool dhydro_step(BodyId body, ChunkPos region, U32 ticks)
{
    ChunkPos chunk = region;
    LocalPos local;
    WPosTile tile;
    HydroBody *body_state = dhydro_get_body_state(body, true);
    if (!body_state) return false;
    for (local.ly = 0; local.ly < DOM_CHUNK_SIZE; ++local.ly) {
        for (local.lx = 0; local.lx < DOM_CHUNK_SIZE; ++local.lx) {
            local.lz = 0; /* surface layer stub */
            dworld_chunk_local_to_tile(&chunk, &local, &tile);
            if (tile.z > DOM_Z_MAX) tile.z = DOM_Z_MAX;
            if (tile.z < DOM_Z_MIN) tile.z = DOM_Z_MIN;
            {
                HydroCell *cell = dhydro_ensure_cell(body, &tile);
                if (cell) {
                    dhydro_step_tile(body, body_state, cell, &tile, ticks);
                }
            }
        }
    }
    (void)g_river_links; /* river graph hook reserved */
    return true;
}

bool dhydro_get_water_depth(BodyId body, const WPosTile *tile, Q16_16 *out_depth)
{
    HydroCell *cell = dhydro_find_cell(body, tile);
    if (!cell) return false;
    if (out_depth) *out_depth = cell->depth;
    return true;
}

bool dhydro_get_flow(BodyId body, const WPosTile *tile, Q16_16 *out_flow_u, Q16_16 *out_flow_v)
{
    HydroCell *cell = dhydro_find_cell(body, tile);
    if (!cell) return false;
    if (out_flow_u) *out_flow_u = cell->flow_u;
    if (out_flow_v) *out_flow_v = cell->flow_v;
    return true;
}
