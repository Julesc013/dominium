#include "domino/dclimate.h"
#include "domino/dbody.h"

#include <stdlib.h>
#include <string.h>

#define DCLIMATE_MAX_GRIDS 16
#define DCLIMATE_Q16_ONE   ((Q16_16)(1 << 16))

static ClimateGrid g_climate_grids[DCLIMATE_MAX_GRIDS];

static FieldId g_field_mean_temp;
static FieldId g_field_mean_precip;
static FieldId g_field_mean_humidity;

static Q16_16 dclimate_abs_q16(Q16_16 v)
{
    return (v < 0) ? -v : v;
}

static Q16_16 dclimate_mul_q16(Q16_16 a, Q16_16 b)
{
    return (Q16_16)(((I64)a * (I64)b) >> 16);
}

static Q16_16 dclimate_frac_u32(U32 num, U32 den)
{
    if (den == 0) return 0;
    return (Q16_16)(((I64)num << 16) / (I64)den);
}

static Q16_16 dclimate_clamp_q16(Q16_16 v, Q16_16 lo, Q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static void dclimate_register_fields(void)
{
    FieldDesc def;
    if (g_field_mean_temp != 0 && g_field_mean_precip != 0 && g_field_mean_humidity != 0) {
        return;
    }
    memset(&def, 0, sizeof(def));
    def.unit = UNIT_TEMP_K;
    def.storage = FIELD_STORAGE_Q16_16;
    def.name = "climate_mean_temp";
    g_field_mean_temp = dfield_register(&def);

    def.unit = UNIT_DEPTH_M; /* arbitrary precip depth proxy */
    def.storage = FIELD_STORAGE_Q16_16;
    def.name = "climate_mean_precip";
    g_field_mean_precip = dfield_register(&def);

    def.unit = UNIT_FRACTION;
    def.storage = FIELD_STORAGE_Q16_16;
    def.name = "climate_mean_humidity";
    g_field_mean_humidity = dfield_register(&def);
}

static ClimateGrid *dclimate_find_grid(BodyId body)
{
    U32 i;
    if (body == 0) return 0;
    for (i = 0; i < DCLIMATE_MAX_GRIDS; ++i) {
        if (g_climate_grids[i].body == body) {
            return &g_climate_grids[i];
        }
    }
    return 0;
}

static ClimateGrid *dclimate_ensure_grid(BodyId body)
{
    ClimateGrid *grid = dclimate_find_grid(body);
    if (grid) return grid;
    for (grid = g_climate_grids; grid < g_climate_grids + DCLIMATE_MAX_GRIDS; ++grid) {
        if (grid->body == 0) {
            memset(grid, 0, sizeof(*grid));
            grid->body = body;
            return grid;
        }
    }
    return 0;
}

static void dclimate_free_grid(ClimateGrid *grid)
{
    if (!grid) return;
    if (grid->mean_temp_K) {
        free(grid->mean_temp_K);
        grid->mean_temp_K = 0;
    }
    if (grid->mean_precip) {
        free(grid->mean_precip);
        grid->mean_precip = 0;
    }
    if (grid->mean_humidity) {
        free(grid->mean_humidity);
        grid->mean_humidity = 0;
    }
    grid->width = 0;
    grid->height = 0;
}

static U32 dclimate_cell_index(const ClimateGrid *grid, U32 gx, U32 gy)
{
    if (!grid || grid->width == 0) return 0;
    return (gy % grid->height) * grid->width + (gx % grid->width);
}

static TempK dclimate_base_temp_for_body(BodyId body)
{
    const Body *b = dbody_get(body);
    if (b) {
        return b->base_temp_K;
    }
    return (TempK)(288 << 16); /* Earth-ish default */
}

static Q16_16 dclimate_lat_cooling(U32 gy, U32 h)
{
    Q16_16 lat = dclimate_frac_u32(gy, h); /* 0..1 */
    Q16_16 from_equator = dclimate_abs_q16(lat - (Q16_16)(1 << 15)); /* approx distance from mid-line */
    return dclimate_mul_q16(from_equator, (Q16_16)(18 << 16)); /* up to ~18 K loss toward poles */
}

static Q16_16 dclimate_albedo_cooling(Q16_16 albedo)
{
    return dclimate_mul_q16(albedo, (Q16_16)(8 << 16));
}

static Q16_16 dclimate_greenhouse_warming(Q16_16 greenhouse)
{
    return dclimate_mul_q16(greenhouse, (Q16_16)(6 << 16));
}

static void dclimate_seed_cell(const Body *body, ClimateGrid *grid, U32 gx, U32 gy, Q16_16 albedo, Q16_16 greenhouse)
{
    TempK base_temp = dclimate_base_temp_for_body(body ? body->id : 0);
    TempK temp = base_temp;
    Q16_16 lat_loss = dclimate_lat_cooling(gy, grid->height ? grid->height : 1);
    Q16_16 albedo_loss = dclimate_albedo_cooling(albedo);
    Q16_16 greenhouse_gain = dclimate_greenhouse_warming(greenhouse);
    Q16_16 solar_flux = dbody_solar_flux_at_body(body ? body->id : 0);
    Q16_16 humidity = 0;
    Q16_16 precip = 0;
    U32 idx = dclimate_cell_index(grid, gx, gy);

    temp = (TempK)(temp - lat_loss + greenhouse_gain - albedo_loss);
    if (temp < 0) temp = 0;

    humidity = dclimate_clamp_q16((Q16_16)((DCLIMATE_Q16_ONE - albedo) + (greenhouse >> 2) - (lat_loss >> 3)), 0, DCLIMATE_Q16_ONE);
    precip = dclimate_mul_q16(humidity, solar_flux);

    grid->mean_temp_K[idx] = temp;
    grid->mean_precip[idx] = precip;
    grid->mean_humidity[idx] = humidity;
}

FieldId dclimate_field_mean_temp(void)
{
    dclimate_register_fields();
    return g_field_mean_temp;
}

FieldId dclimate_field_mean_precip(void)
{
    dclimate_register_fields();
    return g_field_mean_precip;
}

FieldId dclimate_field_mean_humidity(void)
{
    dclimate_register_fields();
    return g_field_mean_humidity;
}

bool dclimate_init_grid(BodyId body, U32 width, U32 height, Q16_16 albedo, Q16_16 greenhouse_factor)
{
    ClimateGrid *grid;
    U32 cells;
    U32 i;
    const Body *b;
    dclimate_register_fields();
    grid = dclimate_ensure_grid(body);
    if (!grid) return false;
    if (width == 0 || height == 0) return false;

    if (grid->mean_temp_K && (grid->width != width || grid->height != height)) {
        dclimate_free_grid(grid);
    }

    cells = width * height;
    if (!grid->mean_temp_K) {
        grid->mean_temp_K = (TempK*)malloc(sizeof(TempK) * cells);
    }
    if (!grid->mean_precip) {
        grid->mean_precip = (Q16_16*)malloc(sizeof(Q16_16) * cells);
    }
    if (!grid->mean_humidity) {
        grid->mean_humidity = (Q16_16*)malloc(sizeof(Q16_16) * cells);
    }
    if (!grid->mean_temp_K || !grid->mean_precip || !grid->mean_humidity) {
        dclimate_free_grid(grid);
        return false;
    }

    grid->width = width;
    grid->height = height;

    b = dbody_get(body);
    for (i = 0; i < cells; ++i) {
        U32 gx = i % width;
        U32 gy = i / width;
        dclimate_seed_cell(b, grid, gx, gy, albedo, greenhouse_factor);
    }
    return true;
}

ClimateGrid *dclimate_get_grid(BodyId body)
{
    return dclimate_find_grid(body);
}

bool dclimate_set_cell(BodyId body, U32 gx, U32 gy, TempK temp_K, Q16_16 precip, Q16_16 humidity)
{
    ClimateGrid *grid = dclimate_find_grid(body);
    U32 idx;
    if (!grid || grid->width == 0 || grid->height == 0) return false;
    idx = dclimate_cell_index(grid, gx, gy);
    grid->mean_temp_K[idx] = temp_K;
    grid->mean_precip[idx] = precip;
    grid->mean_humidity[idx] = humidity;
    return true;
}

static void dclimate_sample_cell(const ClimateGrid *grid, U32 gx, U32 gy, TempK *out_temp_K, Q16_16 *out_precip, Q16_16 *out_humidity)
{
    U32 idx;
    if (!grid) return;
    idx = dclimate_cell_index(grid, gx, gy);
    if (out_temp_K) *out_temp_K = grid->mean_temp_K ? grid->mean_temp_K[idx] : 0;
    if (out_precip) *out_precip = grid->mean_precip ? grid->mean_precip[idx] : 0;
    if (out_humidity) *out_humidity = grid->mean_humidity ? grid->mean_humidity[idx] : 0;
}

static void dclimate_apply_height_lapse(Q16_16 height_m, TempK *inout_temp)
{
    /* Dry adiabatic-ish: lose ~6 K per km upward */
    Q16_16 lapse_per_m = (Q16_16)(6 << 10); /* 6 / 1024 K per metre */
    Q16_16 delta = dclimate_mul_q16(height_m, lapse_per_m);
    if (!inout_temp) return;
    *inout_temp = (TempK)((I64)(*inout_temp) - delta);
    if (*inout_temp < 0) {
        *inout_temp = 0;
    }
}

static U32 dclimate_wrap_index(Q16_16 turn, U32 dim)
{
    Turn t = dnum_turn_normalise_0_1(turn);
    return (U32)((((I64)t & 0xFFFF) * (I64)dim) >> 16) % dim;
}

bool dclimate_sample_at_lat_lon(BodyId body, Turn lat, Turn lon, Q16_16 height_m, TempK *out_temp_K, Q16_16 *out_precip, Q16_16 *out_humidity)
{
    ClimateGrid *grid = dclimate_find_grid(body);
    TempK temp = 0;
    if (!grid || grid->width == 0 || grid->height == 0) return false;
    dclimate_sample_cell(grid, dclimate_wrap_index(lon, grid->width), dclimate_wrap_index(lat, grid->height), &temp, out_precip, out_humidity);
    if (out_temp_K) {
        *out_temp_K = temp;
        dclimate_apply_height_lapse(height_m, out_temp_K);
    }
    return true;
}

bool dclimate_sample_at_tile(BodyId body, const WPosTile *tile, TempK *out_temp_K, Q16_16 *out_precip, Q16_16 *out_humidity)
{
    ClimateGrid *grid;
    TileCoord wx;
    TileCoord wy;
    U32 gx;
    U32 gy;
    TempK temp = 0;
    if (!tile) return false;
    grid = dclimate_find_grid(body);
    if (!grid || grid->width == 0 || grid->height == 0) return false;

    wx = dworld_wrap_tile_coord(tile->x);
    wy = dworld_wrap_tile_coord(tile->y);
    gx = ((U32)wx * grid->width) >> DOM_WORLD_TILES_LOG2;
    gy = ((U32)wy * grid->height) >> DOM_WORLD_TILES_LOG2;

    dclimate_sample_cell(grid, gx, gy, &temp, out_precip, out_humidity);
    if (out_temp_K) {
        *out_temp_K = temp;
        dclimate_apply_height_lapse(dnum_from_int32((I32)tile->z), out_temp_K);
    }
    return true;
}
