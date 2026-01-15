/*
FILE: source/domino/dweather.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dweather
RESPONSIBILITY: Implements `dweather`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dweather.h"
#include "domino/dclimate.h"
#include "domino/dbody.h"

#include <stdlib.h>
#include <string.h>

#define DWEATHER_MAX_GRIDS 16
#define DWEATHER_Q16_ONE   ((Q16_16)(1 << 16))

static WeatherGrid g_weather_grids[DWEATHER_MAX_GRIDS];
static U64         g_weather_ticks[DWEATHER_MAX_GRIDS];

static FieldId g_field_cloud;

static Q16_16 dweather_abs_q16(Q16_16 v)
{
    return (v < 0) ? -v : v;
}

static Q16_16 dweather_mul_q16(Q16_16 a, Q16_16 b)
{
    return (Q16_16)(((I64)a * (I64)b) >> 16);
}

static Q16_16 dweather_clamp_q16(Q16_16 v, Q16_16 lo, Q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static WeatherGrid *dweather_find_grid(BodyId body, U32 *out_idx)
{
    U32 i;
    if (body == 0) return 0;
    for (i = 0; i < DWEATHER_MAX_GRIDS; ++i) {
        if (g_weather_grids[i].body == body) {
            if (out_idx) *out_idx = i;
            return &g_weather_grids[i];
        }
    }
    return 0;
}

static WeatherGrid *dweather_ensure_grid(BodyId body, U32 *out_idx)
{
    WeatherGrid *grid = dweather_find_grid(body, out_idx);
    if (grid) return grid;
    for (grid = g_weather_grids; grid < g_weather_grids + DWEATHER_MAX_GRIDS; ++grid) {
        if (grid->body == 0) {
            U32 idx = (U32)(grid - g_weather_grids);
            memset(grid, 0, sizeof(*grid));
            grid->body = body;
            g_weather_ticks[idx] = 0;
            if (out_idx) *out_idx = idx;
            return grid;
        }
    }
    return 0;
}

static void dweather_free_grid(WeatherGrid *grid)
{
    if (!grid) return;
    if (grid->pressure) {
        free(grid->pressure);
        grid->pressure = 0;
    }
    if (grid->temp) {
        free(grid->temp);
        grid->temp = 0;
    }
    if (grid->humidity) {
        free(grid->humidity);
        grid->humidity = 0;
    }
    if (grid->wind_u) {
        free(grid->wind_u);
        grid->wind_u = 0;
    }
    if (grid->wind_v) {
        free(grid->wind_v);
        grid->wind_v = 0;
    }
    if (grid->cloud) {
        free(grid->cloud);
        grid->cloud = 0;
    }
    grid->width = 0;
    grid->height = 0;
}

static void dweather_register_fields(void)
{
    FieldDesc def;
    if (g_field_cloud != 0) return;
    memset(&def, 0, sizeof(def));
    def.name = "cloud_cover";
    def.unit = UNIT_FRACTION;
    def.storage = FIELD_STORAGE_Q4_12;
    g_field_cloud = dfield_register(&def);
}

FieldId dweather_field_cloud(void)
{
    dweather_register_fields();
    return g_field_cloud;
}

static U32 dweather_cell_index(const WeatherGrid *grid, U32 gx, U32 gy)
{
    if (!grid || grid->width == 0) return 0;
    return (gy % grid->height) * grid->width + (gx % grid->width);
}

static void dweather_seed_cell_from_climate(const ClimateGrid *c, WeatherGrid *w, U32 wx, U32 wy)
{
    TempK temp = 0;
    Q16_16 precip = 0;
    Q16_16 humidity = 0;
    U32 idx = dweather_cell_index(w, wx, wy);
    if (c && c->width > 0 && c->height > 0) {
        U32 cx = (wx * c->width) / (w->width ? w->width : 1);
        U32 cy = (wy * c->height) / (w->height ? w->height : 1);
        U32 cidx = (cy % c->height) * c->width + (cx % c->width);
        temp = c->mean_temp_K ? c->mean_temp_K[cidx] : 0;
        precip = c->mean_precip ? c->mean_precip[cidx] : 0;
        humidity = c->mean_humidity ? c->mean_humidity[cidx] : 0;
    } else {
        temp = (TempK)(288 << 16);
        precip = (Q16_16)(1 << 16);
        humidity = (Q16_16)(1 << 16);
    }

    w->temp[idx] = temp;
    w->pressure[idx] = (PressurePa)(101 << 16);
    w->humidity[idx] = humidity;
    w->wind_u[idx] = 0;
    w->wind_v[idx] = 0;
    w->cloud[idx] = dweather_clamp_q16(dweather_mul_q16(humidity, (Q16_16)(precip ? (precip >> 4) : 0)), 0, DWEATHER_Q16_ONE);
}

bool dweather_init_grid(BodyId body, U32 width, U32 height)
{
    WeatherGrid *grid;
    U32 cells;
    dweather_register_fields();
    grid = dweather_ensure_grid(body, 0);
    if (!grid) return false;
    if (width == 0 || height == 0) return false;

    if (grid->pressure && (grid->width != width || grid->height != height)) {
        dweather_free_grid(grid);
    }
    grid->width = width;
    grid->height = height;
    cells = width * height;

    if (!grid->pressure) grid->pressure = (PressurePa*)malloc(sizeof(PressurePa) * cells);
    if (!grid->temp) grid->temp = (TempK*)malloc(sizeof(TempK) * cells);
    if (!grid->humidity) grid->humidity = (Q16_16*)malloc(sizeof(Q16_16) * cells);
    if (!grid->wind_u) grid->wind_u = (Q16_16*)malloc(sizeof(Q16_16) * cells);
    if (!grid->wind_v) grid->wind_v = (Q16_16*)malloc(sizeof(Q16_16) * cells);
    if (!grid->cloud) grid->cloud = (Q16_16*)malloc(sizeof(Q16_16) * cells);
    if (!grid->pressure || !grid->temp || !grid->humidity || !grid->wind_u || !grid->wind_v || !grid->cloud) {
        dweather_free_grid(grid);
        return false;
    }
    dweather_seed_from_climate(body);
    return true;
}

WeatherGrid *dweather_get_grid(BodyId body)
{
    return dweather_find_grid(body, 0);
}

bool dweather_seed_from_climate(BodyId body)
{
    WeatherGrid *grid;
    ClimateGrid *climate;
    U32 gx;
    U32 gy;
    grid = dweather_find_grid(body, 0);
    if (!grid || grid->width == 0 || grid->height == 0) return false;
    climate = dclimate_get_grid(body);
    for (gy = 0; gy < grid->height; ++gy) {
        for (gx = 0; gx < grid->width; ++gx) {
            dweather_seed_cell_from_climate(climate, grid, gx, gy);
        }
    }
    return true;
}

static void dweather_update_wind_from_pressure(WeatherGrid *grid, U32 gx, U32 gy)
{
    U32 idx = dweather_cell_index(grid, gx, gy);
    PressurePa p = grid->pressure[idx];
    PressurePa px = grid->pressure[dweather_cell_index(grid, gx + 1, gy)];
    PressurePa py = grid->pressure[dweather_cell_index(grid, gx, gy + 1)];
    PressurePa pmx = grid->pressure[dweather_cell_index(grid, gx + grid->width - 1, gy)];
    PressurePa pmy = grid->pressure[dweather_cell_index(grid, gx, gy + grid->height - 1)];
    grid->wind_u[idx] = (Q16_16)((pmx - px) >> 1);
    grid->wind_v[idx] = (Q16_16)((pmy - py) >> 1);
}

bool dweather_step(BodyId body, U32 ticks)
{
    WeatherGrid *grid;
    U32 idx;
    U32 gx;
    U32 gy;
    U64 tick_accum;
    grid = dweather_find_grid(body, &idx);
    if (!grid || grid->width == 0 || grid->height == 0) return false;
    tick_accum = g_weather_ticks[idx];
    tick_accum += ticks;
    g_weather_ticks[idx] = tick_accum;

    for (gy = 0; gy < grid->height; ++gy) {
        for (gx = 0; gx < grid->width; ++gx) {
            U32 cidx = dweather_cell_index(grid, gx, gy);
            Q16_16 wiggle = (Q16_16)(((tick_accum + gx + gy) & 0xF) << 12);
            Q16_16 wind_mag = dweather_abs_q16(grid->wind_u ? grid->wind_u[cidx] : 0) + dweather_abs_q16(grid->wind_v ? grid->wind_v[cidx] : 0);
            grid->pressure[cidx] = (PressurePa)dweather_clamp_q16((Q16_16)((grid->pressure[cidx]) + (wiggle >> 2) - (Q16_16)(1 << 11)), (Q16_16)(90 << 16), (Q16_16)(110 << 16));
            grid->temp[cidx] = (TempK)dweather_clamp_q16((Q16_16)(grid->temp[cidx] + (wiggle >> 3)), (Q16_16)(180 << 16), (Q16_16)(360 << 16));
            grid->humidity[cidx] = dweather_clamp_q16((Q16_16)(grid->humidity[cidx] + (wiggle >> 4)), 0, DWEATHER_Q16_ONE);
            grid->cloud[cidx] = dweather_clamp_q16((Q16_16)(grid->cloud[cidx] + (grid->humidity[cidx] >> 3) - (wind_mag >> 6) + (wiggle >> 5)), 0, DWEATHER_Q16_ONE);
        }
    }

    for (gy = 0; gy < grid->height; ++gy) {
        for (gx = 0; gx < grid->width; ++gx) {
            dweather_update_wind_from_pressure(grid, gx, gy);
        }
    }

    (void)dweather_abs_q16; /* silence unused if further hooks are added later */
    return true;
}

static bool dweather_sample_tile(BodyId body, const WPosTile *tile, PressurePa *out_pressure, TempK *out_temp, Q16_16 *out_humidity, Q16_16 *out_wind_u, Q16_16 *out_wind_v, Q16_16 *out_cloud)
{
    WeatherGrid *grid;
    TileCoord wx;
    TileCoord wy;
    U32 gx;
    U32 gy;
    U32 idx;
    if (!tile) return false;
    grid = dweather_find_grid(body, 0);
    if (!grid || grid->width == 0 || grid->height == 0) return false;

    wx = dworld_wrap_tile_coord(tile->x);
    wy = dworld_wrap_tile_coord(tile->y);
    gx = ((U32)wx * grid->width) >> DOM_WORLD_TILES_LOG2;
    gy = ((U32)wy * grid->height) >> DOM_WORLD_TILES_LOG2;
    idx = dweather_cell_index(grid, gx, gy);

    if (out_pressure) *out_pressure = grid->pressure ? grid->pressure[idx] : 0;
    if (out_temp) *out_temp = grid->temp ? grid->temp[idx] : 0;
    if (out_humidity) *out_humidity = grid->humidity ? grid->humidity[idx] : 0;
    if (out_wind_u) *out_wind_u = grid->wind_u ? grid->wind_u[idx] : 0;
    if (out_wind_v) *out_wind_v = grid->wind_v ? grid->wind_v[idx] : 0;
    if (out_cloud) *out_cloud = grid->cloud ? grid->cloud[idx] : 0;
    return true;
}

bool dweather_get_surface_weather_at_tile(BodyId body, const WPosTile *tile,
    PressurePa *out_pressure, TempK *out_temp, Q16_16 *out_humidity,
    Q16_16 *out_wind_u, Q16_16 *out_wind_v, Q16_16 *out_cloud, Q16_16 *out_precip)
{
    Q16_16 humidity = 0;
    Q16_16 cloud = 0;
    Q16_16 precip = 0;
    Q16_16 climate_precip = 0;
    TempK temp = 0;
    if (!dweather_sample_tile(body, tile, out_pressure, &temp, &humidity, out_wind_u, out_wind_v, &cloud)) {
        return false;
    }
    if (out_temp) *out_temp = temp;
    precip = dweather_mul_q16(humidity, cloud);
    if (tile) {
        TempK dummy_temp;
        Q16_16 mean_h;
        if (dclimate_sample_at_tile(body, tile, &dummy_temp, &climate_precip, &mean_h)) {
            precip = dweather_clamp_q16(precip + (climate_precip >> 2) + (mean_h >> 3), 0, (Q16_16)(4 << 16));
        }
    }
    if (out_humidity) *out_humidity = humidity;
    if (out_cloud) *out_cloud = cloud;
    if (out_precip) *out_precip = precip;
    return true;
}

bool dweather_project_fields_for_tile(BodyId body, const WPosTile *tile,
    Q16_16 *out_pressure_raw, Q16_16 *out_temp_raw, Q16_16 *out_humidity_raw,
    Q16_16 *out_wind_u_raw, Q16_16 *out_wind_v_raw, Q16_16 *out_cloud_raw)
{
    PressurePa p = 0;
    TempK t = 0;
    Q16_16 h = 0;
    Q16_16 u = 0;
    Q16_16 v = 0;
    Q16_16 c = 0;
    if (!dweather_sample_tile(body, tile, &p, &t, &h, &u, &v, &c)) {
        return false;
    }
    if (out_pressure_raw) *out_pressure_raw = (Q16_16)p;
    if (out_temp_raw) *out_temp_raw = (Q16_16)t;
    if (out_humidity_raw) *out_humidity_raw = h;
    if (out_wind_u_raw) *out_wind_u_raw = u;
    if (out_wind_v_raw) *out_wind_v_raw = v;
    if (out_cloud_raw) *out_cloud_raw = c;
    return true;
}
