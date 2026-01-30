/*
FILE: tools/climate/climate_cli.cpp
MODULE: Dominium
PURPOSE: Climate fixture CLI for deterministic envelope and biome checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/climate_fields.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/geology_fields.h"

#define CLIMATE_FIXTURE_HEADER "DOMINIUM_CLIMATE_FIXTURE_V1"

#define CLIMATE_INSPECT_HEADER "DOMINIUM_CLIMATE_INSPECT_V1"
#define CLIMATE_CORE_SAMPLE_HEADER "DOMINIUM_CLIMATE_CORE_SAMPLE_V1"
#define CLIMATE_MAP_HEADER "DOMINIUM_CLIMATE_MAP_V1"
#define CLIMATE_SLICE_HEADER "DOMINIUM_CLIMATE_SLICE_V1"
#define CLIMATE_VALIDATE_HEADER "DOMINIUM_CLIMATE_VALIDATE_V1"
#define CLIMATE_DIFF_HEADER "DOMINIUM_CLIMATE_DIFF_V1"
#define CLIMATE_COLLAPSE_HEADER "DOMINIUM_CLIMATE_COLLAPSE_V1"

#define CLIMATE_PROVIDER_CHAIN "procedural_base"

#define CLIMATE_LINE_MAX 512u

typedef struct climate_fixture {
    char fixture_id[96];
    dom_climate_surface_desc climate_desc;
    dom_domain_policy climate_policy;
    u32 cache_capacity;
    u32 policy_set;
    dom_terrain_surface_desc terrain_desc;
    dom_geology_surface_desc geology_desc;
    char geology_layer_ids[DOM_GEOLOGY_MAX_LAYERS][64];
    char biome_ids[DOM_CLIMATE_MAX_BIOMES][64];
    dom_climate_biome_catalog biome_catalog;
    q16_16 moisture_roughness_scale;
} climate_fixture;

static u64 climate_hash_u64(u64 h, u64 v)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((v >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((v >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((v >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((v >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((v >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((v >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((v >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(v & 0xFFu);
    for (u32 i = 0u; i < 8u; ++i) {
        h ^= (u64)bytes[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 climate_hash_u32(u64 h, u32 v)
{
    return climate_hash_u64(h, (u64)v);
}

static u64 climate_hash_i32(u64 h, i32 v)
{
    return climate_hash_u64(h, (u64)(u32)v);
}

static char* climate_trim(char* text)
{
    char* end;
    while (text && *text && isspace((unsigned char)*text)) {
        ++text;
    }
    if (!text || !*text) {
        return text;
    }
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) {
        --end;
    }
    *end = '\0';
    return text;
}

static int climate_parse_u32(const char* text, u32* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoul(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u32)value;
    return 1;
}

static int climate_parse_u64(const char* text, u64* out_value)
{
    char* end = 0;
    unsigned long long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoull(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u64)value;
    return 1;
}

static int climate_parse_q16(const char* text, q16_16* out_value)
{
    char* end = 0;
    double value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtod(text, &end);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = d_q16_16_from_double(value);
    return 1;
}

static int climate_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[CLIMATE_LINE_MAX];
    char* first;
    char* second;
    char* third;
    if (!text || !a || !b || !c) {
        return 0;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    first = buffer;
    second = strchr(first, ',');
    if (!second) {
        return 0;
    }
    *second++ = '\0';
    third = strchr(second, ',');
    if (!third) {
        return 0;
    }
    *third++ = '\0';
    if (!climate_parse_q16(climate_trim(first), a)) return 0;
    if (!climate_parse_q16(climate_trim(second), b)) return 0;
    if (!climate_parse_q16(climate_trim(third), c)) return 0;
    return 1;
}

static int climate_parse_pair_q16(const char* text, q16_16* a, q16_16* b)
{
    char buffer[CLIMATE_LINE_MAX];
    char* first;
    char* second;
    if (!text || !a || !b) {
        return 0;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    first = buffer;
    second = strchr(first, ',');
    if (!second) {
        return 0;
    }
    *second++ = '\0';
    if (!climate_parse_q16(climate_trim(first), a)) return 0;
    if (!climate_parse_q16(climate_trim(second), b)) return 0;
    return 1;
}

static int climate_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!climate_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 climate_parse_resolution(const char* text)
{
    if (!text) {
        return DOM_DOMAIN_RES_FULL;
    }
    if (strcmp(text, "full") == 0) return DOM_DOMAIN_RES_FULL;
    if (strcmp(text, "medium") == 0) return DOM_DOMAIN_RES_MEDIUM;
    if (strcmp(text, "coarse") == 0) return DOM_DOMAIN_RES_COARSE;
    if (strcmp(text, "analytic") == 0) return DOM_DOMAIN_RES_ANALYTIC;
    return DOM_DOMAIN_RES_FULL;
}

static int climate_parse_indexed_key(const char* key,
                                     const char* prefix,
                                     u32* out_index,
                                     const char** out_suffix)
{
    size_t len;
    char* end = 0;
    unsigned long idx;
    if (!key || !prefix || !out_index || !out_suffix) {
        return 0;
    }
    len = strlen(prefix);
    if (strncmp(key, prefix, len) != 0) {
        return 0;
    }
    idx = strtoul(key + len, &end, 10);
    if (!end || end == key + len || *end != '_') {
        return 0;
    }
    *out_index = (u32)idx;
    *out_suffix = end + 1;
    return 1;
}

static void climate_biome_rule_init(dom_climate_biome_rule* rule)
{
    if (!rule) {
        return;
    }
    memset(rule, 0, sizeof(*rule));
    rule->temp_min = 0;
    rule->temp_max = d_q16_16_from_int(1);
    rule->precip_min = 0;
    rule->precip_max = d_q16_16_from_int(1);
    rule->season_min = 0;
    rule->season_max = d_q16_16_from_int(1);
    rule->elevation_min = 0;
    rule->elevation_max = d_q16_16_from_int(1);
    rule->moisture_min = 0;
    rule->moisture_max = d_q16_16_from_int(1);
    rule->hardness_min = 0;
    rule->hardness_max = d_q16_16_from_int(1);
}

static void climate_fixture_init(climate_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_climate_surface_desc_init(&fixture->climate_desc);
    dom_domain_policy_init(&fixture->climate_policy);
    dom_terrain_surface_desc_init(&fixture->terrain_desc);
    dom_geology_surface_desc_init(&fixture->geology_desc);
    fixture->cache_capacity = 128u;
    fixture->policy_set = 0u;
    fixture->moisture_roughness_scale = d_q16_16_from_double(0.5);
    strncpy(fixture->fixture_id, "climate.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';

    fixture->terrain_desc.noise.amplitude = d_q16_16_from_double(0.1);
    fixture->terrain_desc.noise.cell_size = d_q16_16_from_int(16);
    fixture->terrain_desc.roughness_base = d_q16_16_from_double(0.1);

    fixture->geology_desc.layer_count = 1u;
    fixture->geology_desc.layers[0].layer_id = d_rng_hash_str32("geo.bedrock");
    fixture->geology_desc.layers[0].thickness = 0;
    fixture->geology_desc.layers[0].hardness = d_q16_16_from_double(0.8);
    fixture->geology_desc.layers[0].fracture_risk = d_q16_16_from_double(0.2);
    fixture->geology_desc.layers[0].has_fracture = 1u;
    strncpy(fixture->geology_layer_ids[0], "geo.bedrock", sizeof(fixture->geology_layer_ids[0]) - 1);
    fixture->geology_layer_ids[0][sizeof(fixture->geology_layer_ids[0]) - 1] = '\0';

    fixture->biome_catalog.biome_count = 0u;
    for (u32 i = 0u; i < DOM_CLIMATE_MAX_BIOMES; ++i) {
        climate_biome_rule_init(&fixture->biome_catalog.rules[i]);
    }
}

static int climate_fixture_apply_geo_layer(climate_fixture* fixture,
                                           u32 index,
                                           const char* suffix,
                                           const char* value)
{
    dom_geology_layer_desc* layer;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_GEOLOGY_MAX_LAYERS) {
        return 0;
    }
    if (fixture->geology_desc.layer_count <= index) {
        fixture->geology_desc.layer_count = index + 1u;
    }
    layer = &fixture->geology_desc.layers[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->geology_layer_ids[index], value, sizeof(fixture->geology_layer_ids[index]) - 1);
        fixture->geology_layer_ids[index][sizeof(fixture->geology_layer_ids[index]) - 1] = '\0';
        layer->layer_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "thickness") == 0) {
        return climate_parse_q16(value, &layer->thickness);
    }
    if (strcmp(suffix, "hardness") == 0) {
        return climate_parse_q16(value, &layer->hardness);
    }
    if (strcmp(suffix, "fracture") == 0) {
        layer->has_fracture = 1u;
        return climate_parse_q16(value, &layer->fracture_risk);
    }
    return 0;
}

static int climate_fixture_apply_biome(climate_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_climate_biome_rule* rule;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CLIMATE_MAX_BIOMES) {
        return 0;
    }
    if (fixture->biome_catalog.biome_count <= index) {
        fixture->biome_catalog.biome_count = index + 1u;
    }
    rule = &fixture->biome_catalog.rules[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->biome_ids[index], value, sizeof(fixture->biome_ids[index]) - 1);
        fixture->biome_ids[index][sizeof(fixture->biome_ids[index]) - 1] = '\0';
        rule->biome_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "temp_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_TEMP;
        return climate_parse_q16(value, &rule->temp_min);
    }
    if (strcmp(suffix, "temp_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_TEMP;
        return climate_parse_q16(value, &rule->temp_max);
    }
    if (strcmp(suffix, "precip_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_PRECIP;
        return climate_parse_q16(value, &rule->precip_min);
    }
    if (strcmp(suffix, "precip_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_PRECIP;
        return climate_parse_q16(value, &rule->precip_max);
    }
    if (strcmp(suffix, "season_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_SEASON;
        return climate_parse_q16(value, &rule->season_min);
    }
    if (strcmp(suffix, "season_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_SEASON;
        return climate_parse_q16(value, &rule->season_max);
    }
    if (strcmp(suffix, "elevation_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_ELEVATION;
        return climate_parse_q16(value, &rule->elevation_min);
    }
    if (strcmp(suffix, "elevation_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_ELEVATION;
        return climate_parse_q16(value, &rule->elevation_max);
    }
    if (strcmp(suffix, "moisture_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_MOISTURE;
        return climate_parse_q16(value, &rule->moisture_min);
    }
    if (strcmp(suffix, "moisture_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_MOISTURE;
        return climate_parse_q16(value, &rule->moisture_max);
    }
    if (strcmp(suffix, "hardness_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_HARDNESS;
        return climate_parse_q16(value, &rule->hardness_min);
    }
    if (strcmp(suffix, "hardness_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_HARDNESS;
        return climate_parse_q16(value, &rule->hardness_max);
    }
    if (strcmp(suffix, "strata_id") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_STRATA;
        rule->required_strata_id = d_rng_hash_str32(value);
        return 1;
    }
    return 0;
}

static int climate_fixture_apply(climate_fixture* fixture, const char* key, const char* value)
{
    u32 index = 0u;
    const char* suffix = 0;
    if (!fixture || !key || !value) {
        return 0;
    }
    if (strcmp(key, "fixture_id") == 0) {
        strncpy(fixture->fixture_id, value, sizeof(fixture->fixture_id) - 1);
        fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
        return 1;
    }
    if (strcmp(key, "world_seed") == 0) {
        return climate_parse_u64(value, &fixture->climate_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return climate_parse_u64(value, &fixture->climate_desc.domain_id);
    }
    if (strcmp(key, "shape") == 0) {
        if (strcmp(value, "sphere") == 0) {
            fixture->climate_desc.shape.kind = DOM_TERRAIN_SHAPE_SPHERE;
            return 1;
        }
        if (strcmp(value, "oblate") == 0) {
            fixture->climate_desc.shape.kind = DOM_TERRAIN_SHAPE_OBLATE;
            return 1;
        }
        if (strcmp(value, "slab") == 0) {
            fixture->climate_desc.shape.kind = DOM_TERRAIN_SHAPE_SLAB;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "radius_equatorial") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.shape.radius_equatorial);
    }
    if (strcmp(key, "radius_polar") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.shape.radius_polar);
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.shape.slab_half_extent);
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.shape.slab_half_thickness);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.meters_per_unit);
    }
    if (strcmp(key, "noise_seed") == 0) {
        return climate_parse_u64(value, &fixture->climate_desc.noise.seed);
    }
    if (strcmp(key, "noise_amplitude") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.noise.amplitude);
    }
    if (strcmp(key, "noise_cell_size") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.noise.cell_size);
    }
    if (strcmp(key, "temp_equator") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.temp_equator);
    }
    if (strcmp(key, "temp_pole") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.temp_pole);
    }
    if (strcmp(key, "temp_altitude_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.temp_altitude_scale);
    }
    if (strcmp(key, "temp_range_base") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.temp_range_base);
    }
    if (strcmp(key, "temp_range_lat_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.temp_range_lat_scale);
    }
    if (strcmp(key, "precip_equator") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.precip_equator);
    }
    if (strcmp(key, "precip_pole") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.precip_pole);
    }
    if (strcmp(key, "precip_altitude_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.precip_altitude_scale);
    }
    if (strcmp(key, "precip_range_base") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.precip_range_base);
    }
    if (strcmp(key, "precip_range_lat_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.precip_range_lat_scale);
    }
    if (strcmp(key, "seasonality_base") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.seasonality_base);
    }
    if (strcmp(key, "seasonality_lat_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.seasonality_lat_scale);
    }
    if (strcmp(key, "noise_temp_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.noise_temp_scale);
    }
    if (strcmp(key, "noise_precip_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.noise_precip_scale);
    }
    if (strcmp(key, "noise_season_scale") == 0) {
        return climate_parse_q16(value, &fixture->climate_desc.noise_season_scale);
    }
    if (strcmp(key, "wind_band_count") == 0) {
        return climate_parse_u32(value, &fixture->climate_desc.wind_band_count);
    }
    if (strcmp(key, "anchor_mask") == 0) {
        return climate_parse_u32(value, &fixture->climate_desc.anchor.mask);
    }
    if (strcmp(key, "anchor_temperature_mean") == 0) {
        fixture->climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_TEMPERATURE_MEAN;
        return climate_parse_q16(value, &fixture->climate_desc.anchor.temperature_mean);
    }
    if (strcmp(key, "anchor_temperature_range") == 0) {
        fixture->climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_TEMPERATURE_RANGE;
        return climate_parse_q16(value, &fixture->climate_desc.anchor.temperature_range);
    }
    if (strcmp(key, "anchor_precipitation_mean") == 0) {
        fixture->climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_PRECIP_MEAN;
        return climate_parse_q16(value, &fixture->climate_desc.anchor.precipitation_mean);
    }
    if (strcmp(key, "anchor_precipitation_range") == 0) {
        fixture->climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_PRECIP_RANGE;
        return climate_parse_q16(value, &fixture->climate_desc.anchor.precipitation_range);
    }
    if (strcmp(key, "anchor_seasonality") == 0) {
        fixture->climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_SEASONALITY;
        return climate_parse_q16(value, &fixture->climate_desc.anchor.seasonality);
    }
    if (strcmp(key, "anchor_wind_prevailing") == 0) {
        fixture->climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_WIND_PREVAILING;
        return climate_parse_u32(value, &fixture->climate_desc.anchor.wind_prevailing);
    }
    if (strcmp(key, "cache_capacity") == 0) {
        return climate_parse_u32(value, &fixture->cache_capacity);
    }
    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_q16(value, &fixture->climate_policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->climate_policy.max_resolution = climate_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_q16(value, &fixture->climate_policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return climate_parse_u32(value, &fixture->climate_policy.max_ray_steps);
    }
    if (strcmp(key, "terrain_noise_seed") == 0) {
        return climate_parse_u64(value, &fixture->terrain_desc.noise.seed);
    }
    if (strcmp(key, "terrain_noise_amplitude") == 0) {
        return climate_parse_q16(value, &fixture->terrain_desc.noise.amplitude);
    }
    if (strcmp(key, "terrain_noise_cell_size") == 0) {
        return climate_parse_q16(value, &fixture->terrain_desc.noise.cell_size);
    }
    if (strcmp(key, "terrain_roughness_base") == 0) {
        return climate_parse_q16(value, &fixture->terrain_desc.roughness_base);
    }
    if (strcmp(key, "terrain_material_primary") == 0) {
        return climate_parse_u32(value, &fixture->terrain_desc.material_primary);
    }
    if (strcmp(key, "terrain_walkable_max_slope") == 0) {
        return climate_parse_q16(value, &fixture->terrain_desc.walkable_max_slope);
    }
    if (strcmp(key, "geo_default_hardness") == 0) {
        return climate_parse_q16(value, &fixture->geology_desc.default_hardness);
    }
    if (strcmp(key, "geo_default_fracture_risk") == 0) {
        return climate_parse_q16(value, &fixture->geology_desc.default_fracture_risk);
    }
    if (strcmp(key, "geo_layer_count") == 0) {
        return climate_parse_u32(value, &fixture->geology_desc.layer_count);
    }
    if (strcmp(key, "moisture_roughness_scale") == 0) {
        return climate_parse_q16(value, &fixture->moisture_roughness_scale);
    }
    if (strcmp(key, "biome_count") == 0) {
        return climate_parse_u32(value, &fixture->biome_catalog.biome_count);
    }
    if (climate_parse_indexed_key(key, "geo_layer", &index, &suffix)) {
        return climate_fixture_apply_geo_layer(fixture, index, suffix, value);
    }
    if (climate_parse_indexed_key(key, "biome", &index, &suffix)) {
        return climate_fixture_apply_biome(fixture, index, suffix, value);
    }
    return 0;
}

static int climate_fixture_load(const char* path, climate_fixture* out_fixture)
{
    FILE* file;
    char line[CLIMATE_LINE_MAX];
    int header_ok = 0;
    climate_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    climate_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = climate_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, CLIMATE_FIXTURE_HEADER) != 0) {
                fclose(file);
                return 0;
            }
            header_ok = 1;
            continue;
        }
        eq = strchr(text, '=');
        if (!eq) {
            continue;
        }
        *eq++ = '\0';
        climate_fixture_apply(&fixture, climate_trim(text), climate_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static void climate_domains_init_from_fixture(const climate_fixture* fixture,
                                              dom_climate_domain* out_climate,
                                              dom_terrain_domain* out_terrain,
                                              dom_geology_domain* out_geology)
{
    dom_climate_domain_init(out_climate, &fixture->climate_desc, fixture->cache_capacity);
    if (fixture->policy_set) {
        dom_climate_domain_set_policy(out_climate, &fixture->climate_policy);
    }

    if (out_terrain) {
        dom_terrain_surface_desc terrain_desc = fixture->terrain_desc;
        terrain_desc.domain_id = fixture->climate_desc.domain_id;
        terrain_desc.world_seed = fixture->climate_desc.world_seed;
        terrain_desc.meters_per_unit = fixture->climate_desc.meters_per_unit;
        terrain_desc.shape = fixture->climate_desc.shape;
        dom_terrain_domain_init(out_terrain, &terrain_desc, 0u);
    }

    if (out_geology) {
        dom_geology_surface_desc geology_desc = fixture->geology_desc;
        geology_desc.domain_id = fixture->climate_desc.domain_id;
        geology_desc.world_seed = fixture->climate_desc.world_seed;
        geology_desc.meters_per_unit = fixture->climate_desc.meters_per_unit;
        geology_desc.shape = fixture->climate_desc.shape;
        dom_geology_domain_init(out_geology, &geology_desc, 0u);
    }
}

static const char* climate_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 climate_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = climate_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && climate_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static int climate_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* value = climate_find_arg(argc, argv, key);
    if (!value || !out_point) {
        return 0;
    }
    return climate_parse_point(value, out_point);
}

static const char* climate_provider_chain_label(const climate_fixture* fixture)
{
    if (!fixture) {
        return CLIMATE_PROVIDER_CHAIN;
    }
    if (fixture->climate_desc.anchor.mask != 0u) {
        return "procedural_base+anchor";
    }
    return CLIMATE_PROVIDER_CHAIN;
}

static q16_16 climate_elevation_ratio(const dom_terrain_shape_desc* shape,
                                      const dom_domain_point* point)
{
    q16_16 denom;
    q16_16 alt;
    if (!shape || !point) {
        return 0;
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        denom = shape->slab_half_thickness;
        alt = (point->z < 0) ? (q16_16)-point->z : point->z;
    } else {
        dom_terrain_latlon latlon = dom_terrain_local_to_latlon(shape, point);
        denom = shape->radius_equatorial;
        if (shape->radius_polar > denom) {
            denom = shape->radius_polar;
        }
        alt = latlon.altitude;
        if (alt < 0) {
            alt = 0;
        }
    }
    if (denom <= 0) {
        denom = d_q16_16_from_int(1);
    }
    return d_fixed_div_q16_16(alt, denom);
}

static q16_16 climate_moisture_proxy(const climate_fixture* fixture,
                                     const dom_climate_sample* climate,
                                     const dom_terrain_sample* terrain,
                                     u32* out_flags)
{
    q16_16 moisture = 0;
    if (out_flags) {
        *out_flags = 0u;
    }
    if (!fixture || !climate) {
        if (out_flags) {
            *out_flags |= DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN;
        }
        return 0;
    }
    if (climate->flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN) {
        if (out_flags) {
            *out_flags |= DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN;
        }
        return 0;
    }
    moisture = climate->precipitation_mean;
    if (terrain && (terrain->flags & DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN) == 0u) {
        q16_16 adjust = d_q16_16_mul(terrain->roughness, fixture->moisture_roughness_scale);
        moisture = d_q16_16_sub(moisture, adjust);
        if (moisture < 0) {
            moisture = 0;
        }
        if (moisture > d_q16_16_from_int(1)) {
            moisture = d_q16_16_from_int(1);
        }
    }
    return moisture;
}

static const char* climate_biome_label(const climate_fixture* fixture, u32 biome_id)
{
    if (!fixture || biome_id == 0u) {
        return "biome.unknown";
    }
    for (u32 i = 0u; i < fixture->biome_catalog.biome_count && i < DOM_CLIMATE_MAX_BIOMES; ++i) {
        if (fixture->biome_catalog.rules[i].biome_id == biome_id) {
            const char* label = fixture->biome_ids[i];
            if (label && *label) {
                return label;
            }
        }
    }
    return "biome.unknown";
}

static dom_domain_point climate_latlon_to_local(const dom_terrain_shape_desc* shape,
                                                q16_16 lat_turns,
                                                q16_16 lon_turns)
{
    if (!shape) {
        dom_domain_point zero = {0, 0, 0};
        return zero;
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        q16_16 extent = shape->slab_half_extent;
        if (extent <= 0) {
            extent = d_q16_16_from_int(512);
        }
        {
            dom_domain_point point;
            point.x = d_q16_16_mul(lon_turns, d_q16_16_mul(extent, d_q16_16_from_int(2)));
            point.y = d_q16_16_mul(lat_turns, d_q16_16_mul(extent, d_q16_16_from_int(2)));
            point.z = 0;
            return point;
        }
    }
    return dom_terrain_latlon_to_local(shape, lat_turns, lon_turns, 0);
}

static int climate_build_tile_desc(const dom_climate_domain* domain,
                                   const dom_domain_point* point,
                                   u32 resolution,
                                   dom_domain_tile_desc* out_desc)
{
    const dom_domain_sdf_source* source = dom_terrain_surface_sdf(&domain->surface.terrain_surface);
    q16_16 tile_size = domain->policy.tile_size;
    i32 tx;
    i32 ty;
    i32 tz;
    if (!source || !point || !out_desc) {
        return 0;
    }
    if (tile_size <= 0) {
        tile_size = d_q16_16_from_int(64);
    }
    tx = (i32)(((i64)point->x - (i64)source->bounds.min.x) / (i64)tile_size);
    ty = (i32)(((i64)point->y - (i64)source->bounds.min.y) / (i64)tile_size);
    tz = (i32)(((i64)point->z - (i64)source->bounds.min.z) / (i64)tile_size);
    dom_domain_tile_desc_init(out_desc);
    out_desc->resolution = resolution;
    out_desc->sample_dim = (resolution == DOM_DOMAIN_RES_FULL) ? domain->policy.sample_dim_full
                          : (resolution == DOM_DOMAIN_RES_MEDIUM) ? domain->policy.sample_dim_medium
                          : domain->policy.sample_dim_coarse;
    out_desc->tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, resolution);
    out_desc->authoring_version = domain->authoring_version;
    out_desc->bounds.min.x = (q16_16)(source->bounds.min.x + (q16_16)((i64)tx * (i64)tile_size));
    out_desc->bounds.min.y = (q16_16)(source->bounds.min.y + (q16_16)((i64)ty * (i64)tile_size));
    out_desc->bounds.min.z = (q16_16)(source->bounds.min.z + (q16_16)((i64)tz * (i64)tile_size));
    out_desc->bounds.max.x = (q16_16)(out_desc->bounds.min.x + tile_size);
    out_desc->bounds.max.y = (q16_16)(out_desc->bounds.min.y + tile_size);
    out_desc->bounds.max.z = (q16_16)(out_desc->bounds.min.z + tile_size);
    return 1;
}

static int climate_run_validate(const climate_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    if (fixture->biome_catalog.biome_count == 0u) {
        fprintf(stderr, "climate: no biomes defined\n");
        return 1;
    }
    printf("%s\n", CLIMATE_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", climate_provider_chain_label(fixture));
    printf("biome_count=%u\n", (unsigned int)fixture->biome_catalog.biome_count);
    printf("wind_band_count=%u\n", (unsigned int)fixture->climate_desc.wind_band_count);
    return 0;
}

static int climate_run_inspect(const climate_fixture* fixture,
                               const dom_domain_point* point,
                               u32 budget_max)
{
    dom_climate_domain climate_domain;
    dom_terrain_domain terrain_domain;
    dom_geology_domain geology_domain;
    dom_domain_budget climate_budget;
    dom_domain_budget terrain_budget;
    dom_domain_budget geology_budget;
    dom_climate_sample climate_sample;
    dom_terrain_sample terrain_sample;
    dom_geology_sample geology_sample;
    dom_climate_biome_inputs biome_inputs;
    dom_climate_biome_result biome_result;
    q16_16 elevation_ratio;
    u32 moisture_flags = 0u;
    q16_16 moisture_proxy;

    climate_domains_init_from_fixture(fixture, &climate_domain, &terrain_domain, &geology_domain);
    dom_domain_budget_init(&climate_budget, budget_max);
    dom_domain_budget_init(&terrain_budget, budget_max);
    dom_domain_budget_init(&geology_budget, budget_max);

    if (dom_climate_sample_query(&climate_domain, point, &climate_budget, &climate_sample) != 0) {
        dom_climate_domain_free(&climate_domain);
        dom_terrain_domain_free(&terrain_domain);
        dom_geology_domain_free(&geology_domain);
        return 1;
    }
    (void)dom_terrain_sample_query(&terrain_domain, point, &terrain_budget, &terrain_sample);
    (void)dom_geology_sample_query(&geology_domain, point, &geology_budget, &geology_sample);

    elevation_ratio = climate_elevation_ratio(&fixture->climate_desc.shape, point);
    moisture_proxy = climate_moisture_proxy(fixture, &climate_sample, &terrain_sample, &moisture_flags);

    memset(&biome_inputs, 0, sizeof(biome_inputs));
    biome_inputs.climate = &climate_sample;
    biome_inputs.terrain = &terrain_sample;
    biome_inputs.geology = &geology_sample;
    biome_inputs.elevation = elevation_ratio;
    biome_inputs.moisture_proxy = moisture_proxy;
    biome_inputs.flags = moisture_flags;
    (void)dom_climate_biome_resolve(&fixture->biome_catalog, &biome_inputs, &biome_result);

    printf("%s\n", CLIMATE_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", climate_provider_chain_label(fixture));
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("temperature_mean_q16=%d\n", (int)climate_sample.temperature_mean);
    printf("temperature_range_q16=%d\n", (int)climate_sample.temperature_range);
    printf("precipitation_mean_q16=%d\n", (int)climate_sample.precipitation_mean);
    printf("precipitation_range_q16=%d\n", (int)climate_sample.precipitation_range);
    printf("seasonality_q16=%d\n", (int)climate_sample.seasonality);
    printf("wind_prevailing=%u\n", (unsigned int)climate_sample.wind_prevailing);
    printf("flags=%u\n", (unsigned int)climate_sample.flags);
    printf("fields_unknown=%u\n", (unsigned int)((climate_sample.flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN) ? 1u : 0u));
    printf("wind_unknown=%u\n", (unsigned int)((climate_sample.flags & DOM_CLIMATE_SAMPLE_WIND_UNKNOWN) ? 1u : 0u));
    printf("collapsed=%u\n", (unsigned int)((climate_sample.flags & DOM_CLIMATE_SAMPLE_COLLAPSED) ? 1u : 0u));
    printf("elevation_ratio_q16=%d\n", (int)elevation_ratio);
    printf("moisture_proxy_q16=%d\n", (int)moisture_proxy);
    printf("geology_hardness_q16=%d\n", (int)geology_sample.hardness);
    printf("strata_layer_id=%u\n", (unsigned int)geology_sample.strata_layer_id);
    printf("biome_id=%s\n", climate_biome_label(fixture, biome_result.biome_id));
    printf("biome_confidence_q16=%d\n", (int)biome_result.confidence);
    printf("biome_unknown=%u\n", (unsigned int)((biome_result.flags & DOM_CLIMATE_BIOME_RESULT_UNKNOWN) ? 1u : 0u));

    dom_climate_domain_free(&climate_domain);
    dom_terrain_domain_free(&terrain_domain);
    dom_geology_domain_free(&geology_domain);
    return 0;
}

static u64 climate_core_sample_hash(const climate_fixture* fixture,
                                    const dom_domain_point* origin,
                                    const dom_domain_point* direction,
                                    q16_16 length,
                                    u32 steps,
                                    u32 budget_max,
                                    u32 inactive,
                                    int collapse,
                                    u32* out_unknown_steps,
                                    u32* out_cost_max,
                                    u32* out_capsule_count,
                                    int* out_ok)
{
    dom_climate_domain climate_domain;
    dom_terrain_domain terrain_domain;
    dom_geology_domain geology_domain;
    u64 hash = 14695981039346656037ULL;
    q16_16 step_len = 0;
    u32 unknown_steps = 0u;
    u32 cost_max = 0u;
    if (out_ok) {
        *out_ok = 0;
    }
    if (!fixture || !origin || !direction) {
        return 0;
    }
    climate_domains_init_from_fixture(fixture, &climate_domain, &terrain_domain, &geology_domain);

    if (collapse) {
        dom_domain_tile_desc desc;
        if (climate_build_tile_desc(&climate_domain, origin, DOM_DOMAIN_RES_COARSE, &desc)) {
            (void)dom_climate_domain_collapse_tile(&climate_domain, &desc);
        }
    }
    if (out_capsule_count) {
        *out_capsule_count = dom_climate_domain_capsule_count(&climate_domain);
    }

    if (steps == 0u) {
        steps = 1u;
    }
    if (steps > 1u) {
        step_len = (q16_16)((i64)length / (i64)(steps - 1u));
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget climate_budget;
        dom_domain_budget terrain_budget;
        dom_domain_budget geology_budget;
        dom_climate_sample climate_sample;
        dom_terrain_sample terrain_sample;
        dom_geology_sample geology_sample;
        dom_climate_biome_inputs biome_inputs;
        dom_climate_biome_result biome_result;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        u32 step_cost = 0u;
        u32 moisture_flags = 0u;
        q16_16 moisture_proxy;
        q16_16 elevation_ratio;

        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));

        dom_domain_budget_init(&climate_budget, budget_max);
        dom_domain_budget_init(&terrain_budget, budget_max);
        dom_domain_budget_init(&geology_budget, budget_max);
        if (dom_climate_sample_query(&climate_domain, &p, &climate_budget, &climate_sample) != 0) {
            dom_climate_domain_free(&climate_domain);
            dom_terrain_domain_free(&terrain_domain);
            dom_geology_domain_free(&geology_domain);
            return 0;
        }
        (void)dom_terrain_sample_query(&terrain_domain, &p, &terrain_budget, &terrain_sample);
        (void)dom_geology_sample_query(&geology_domain, &p, &geology_budget, &geology_sample);

        elevation_ratio = climate_elevation_ratio(&fixture->climate_desc.shape, &p);
        moisture_proxy = climate_moisture_proxy(fixture, &climate_sample, &terrain_sample, &moisture_flags);

        memset(&biome_inputs, 0, sizeof(biome_inputs));
        biome_inputs.climate = &climate_sample;
        biome_inputs.terrain = &terrain_sample;
        biome_inputs.geology = &geology_sample;
        biome_inputs.elevation = elevation_ratio;
        biome_inputs.moisture_proxy = moisture_proxy;
        biome_inputs.flags = moisture_flags;
        (void)dom_climate_biome_resolve(&fixture->biome_catalog, &biome_inputs, &biome_result);

        step_cost = climate_sample.meta.cost_units +
                    terrain_sample.meta.cost_units +
                    geology_sample.meta.cost_units;
        if (step_cost > cost_max) {
            cost_max = step_cost;
        }
        if ((climate_sample.flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN) ||
            (biome_result.flags & DOM_CLIMATE_BIOME_RESULT_UNKNOWN)) {
            unknown_steps += 1u;
        }
        hash = climate_hash_i32(hash, climate_sample.temperature_mean);
        hash = climate_hash_i32(hash, climate_sample.temperature_range);
        hash = climate_hash_i32(hash, climate_sample.precipitation_mean);
        hash = climate_hash_i32(hash, climate_sample.precipitation_range);
        hash = climate_hash_i32(hash, climate_sample.seasonality);
        hash = climate_hash_u32(hash, climate_sample.wind_prevailing);
        hash = climate_hash_u32(hash, biome_result.biome_id);
        hash = climate_hash_u32(hash, climate_sample.flags);
    }

    if (inactive > 0u) {
        /* inactive bodies are intentionally ignored for cost accounting */
    }
    dom_climate_domain_free(&climate_domain);
    dom_terrain_domain_free(&terrain_domain);
    dom_geology_domain_free(&geology_domain);
    if (out_unknown_steps) {
        *out_unknown_steps = unknown_steps;
    }
    if (out_cost_max) {
        *out_cost_max = cost_max;
    }
    if (out_ok) {
        *out_ok = 1;
    }
    return hash;
}

static int climate_run_core_sample(const climate_fixture* fixture,
                                   const dom_domain_point* origin,
                                   const dom_domain_point* direction,
                                   q16_16 length,
                                   u32 steps,
                                   u32 budget_max,
                                   u32 inactive,
                                   int collapse)
{
    u32 unknown_steps = 0u;
    u32 cost_max = 0u;
    u32 capsule_count = 0u;
    int ok = 0;
    u64 hash = climate_core_sample_hash(fixture, origin, direction, length, steps,
                                        budget_max, inactive, collapse,
                                        &unknown_steps, &cost_max, &capsule_count, &ok);
    if (!ok) {
        return 1;
    }
    printf("%s\n", CLIMATE_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", climate_provider_chain_label(fixture));
    printf("steps=%u\n", (unsigned int)steps);
    printf("budget_max=%u\n", (unsigned int)budget_max);
    printf("unknown_steps=%u\n", (unsigned int)unknown_steps);
    printf("cost_step_max=%u\n", (unsigned int)cost_max);
    printf("sample_hash=%llu\n", (unsigned long long)hash);
    printf("inactive_domains=%u\n", (unsigned int)inactive);
    printf("capsule_count=%u\n", (unsigned int)capsule_count);
    return 0;
}

static int climate_run_map(const climate_fixture* fixture,
                           q16_16 center_lat,
                           q16_16 center_lon,
                           q16_16 span,
                           u32 dim,
                           u32 budget_max)
{
    dom_climate_domain climate_domain;
    dom_terrain_domain terrain_domain;
    dom_geology_domain geology_domain;
    u32 cells = 0u;
    u32 unknown = 0u;
    u64 hash = 14695981039346656037ULL;
    q16_16 step = 0;
    q16_16 half_span = d_fixed_div_q16_16(span, d_q16_16_from_int(2));

    climate_domains_init_from_fixture(fixture, &climate_domain, &terrain_domain, &geology_domain);
    if (dim == 0u) {
        dim = 1u;
    }
    if (dim > 1u) {
        step = (q16_16)((i64)span / (i64)(dim - 1u));
    }

    for (u32 y = 0u; y < dim; ++y) {
        q16_16 lat = d_q16_16_add(d_q16_16_sub(center_lat, half_span), (q16_16)((i64)step * (i64)y));
        for (u32 x = 0u; x < dim; ++x) {
            q16_16 lon = d_q16_16_add(d_q16_16_sub(center_lon, half_span), (q16_16)((i64)step * (i64)x));
            dom_domain_point p = climate_latlon_to_local(&fixture->climate_desc.shape, lat, lon);
            dom_domain_budget climate_budget;
            dom_domain_budget terrain_budget;
            dom_domain_budget geology_budget;
            dom_climate_sample climate_sample;
            dom_terrain_sample terrain_sample;
            dom_geology_sample geology_sample;
            dom_climate_biome_inputs biome_inputs;
            dom_climate_biome_result biome_result;
            q16_16 elevation_ratio;
            u32 moisture_flags = 0u;
            q16_16 moisture_proxy;

            dom_domain_budget_init(&climate_budget, budget_max);
            dom_domain_budget_init(&terrain_budget, budget_max);
            dom_domain_budget_init(&geology_budget, budget_max);
            if (dom_climate_sample_query(&climate_domain, &p, &climate_budget, &climate_sample) != 0) {
                dom_climate_domain_free(&climate_domain);
                dom_terrain_domain_free(&terrain_domain);
                dom_geology_domain_free(&geology_domain);
                return 1;
            }
            (void)dom_terrain_sample_query(&terrain_domain, &p, &terrain_budget, &terrain_sample);
            (void)dom_geology_sample_query(&geology_domain, &p, &geology_budget, &geology_sample);

            elevation_ratio = climate_elevation_ratio(&fixture->climate_desc.shape, &p);
            moisture_proxy = climate_moisture_proxy(fixture, &climate_sample, &terrain_sample, &moisture_flags);

            memset(&biome_inputs, 0, sizeof(biome_inputs));
            biome_inputs.climate = &climate_sample;
            biome_inputs.terrain = &terrain_sample;
            biome_inputs.geology = &geology_sample;
            biome_inputs.elevation = elevation_ratio;
            biome_inputs.moisture_proxy = moisture_proxy;
            biome_inputs.flags = moisture_flags;
            (void)dom_climate_biome_resolve(&fixture->biome_catalog, &biome_inputs, &biome_result);

            cells += 1u;
            if (biome_result.flags & DOM_CLIMATE_BIOME_RESULT_UNKNOWN) {
                unknown += 1u;
            }
            hash = climate_hash_u32(hash, biome_result.biome_id);
        }
    }

    printf("%s\n", CLIMATE_MAP_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", climate_provider_chain_label(fixture));
    printf("cells=%u\n", (unsigned int)cells);
    printf("unknown_cells=%u\n", (unsigned int)unknown);
    printf("map_hash=%llu\n", (unsigned long long)hash);

    dom_climate_domain_free(&climate_domain);
    dom_terrain_domain_free(&terrain_domain);
    dom_geology_domain_free(&geology_domain);
    return 0;
}

static int climate_sample_field_value(const dom_climate_sample* sample,
                                      const char* field,
                                      q16_16* out_value)
{
    if (!sample || !field || !out_value) {
        return 0;
    }
    if (strcmp(field, "temp_mean") == 0) {
        *out_value = sample->temperature_mean;
        return 1;
    }
    if (strcmp(field, "temp_range") == 0) {
        *out_value = sample->temperature_range;
        return 1;
    }
    if (strcmp(field, "precip_mean") == 0) {
        *out_value = sample->precipitation_mean;
        return 1;
    }
    if (strcmp(field, "precip_range") == 0) {
        *out_value = sample->precipitation_range;
        return 1;
    }
    if (strcmp(field, "seasonality") == 0) {
        *out_value = sample->seasonality;
        return 1;
    }
    return 0;
}

static int climate_run_slice(const climate_fixture* fixture,
                             const dom_domain_point* center,
                             q16_16 radius,
                             u32 dim,
                             u32 budget_max,
                             const char* field,
                             const char* axis)
{
    dom_climate_domain climate_domain;
    u64 hash = 14695981039346656037ULL;
    u32 cells = 0u;
    u32 unknown = 0u;
    q16_16 step = 0;
    q16_16 minv = DOM_CLIMATE_UNKNOWN_Q16;
    q16_16 maxv = DOM_CLIMATE_UNKNOWN_Q16;
    i64 sum = 0;
    q16_16 value;

    climate_domains_init_from_fixture(fixture, &climate_domain, (dom_terrain_domain*)0, (dom_geology_domain*)0);
    if (dim == 0u) {
        dim = 1u;
    }
    if (dim > 1u) {
        step = (q16_16)((i64)(d_q16_16_mul(radius, d_q16_16_from_int(2))) / (i64)(dim - 1u));
    }

    for (u32 y = 0u; y < dim; ++y) {
        q16_16 dy = (q16_16)((i64)step * (i64)y);
        q16_16 yoff = d_q16_16_sub(dy, radius);
        for (u32 x = 0u; x < dim; ++x) {
            q16_16 dx = (q16_16)((i64)step * (i64)x);
            q16_16 xoff = d_q16_16_sub(dx, radius);
            dom_domain_point p = *center;
            if (axis && strcmp(axis, "xz") == 0) {
                p.x = d_q16_16_add(center->x, xoff);
                p.z = d_q16_16_add(center->z, yoff);
            } else if (axis && strcmp(axis, "yz") == 0) {
                p.y = d_q16_16_add(center->y, xoff);
                p.z = d_q16_16_add(center->z, yoff);
            } else {
                p.x = d_q16_16_add(center->x, xoff);
                p.y = d_q16_16_add(center->y, yoff);
            }
            dom_domain_budget budget;
            dom_climate_sample sample;
            dom_domain_budget_init(&budget, budget_max);
            if (dom_climate_sample_query(&climate_domain, &p, &budget, &sample) != 0) {
                dom_climate_domain_free(&climate_domain);
                return 1;
            }
            cells += 1u;
            if (sample.flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN) {
                unknown += 1u;
                hash = climate_hash_i32(hash, DOM_CLIMATE_UNKNOWN_Q16);
                continue;
            }
            if (!climate_sample_field_value(&sample, field, &value)) {
                dom_climate_domain_free(&climate_domain);
                return 1;
            }
            hash = climate_hash_i32(hash, value);
            if (minv == DOM_CLIMATE_UNKNOWN_Q16 || value < minv) {
                minv = value;
            }
            if (maxv == DOM_CLIMATE_UNKNOWN_Q16 || value > maxv) {
                maxv = value;
            }
            sum += (i64)value;
        }
    }

    printf("%s\n", CLIMATE_SLICE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", climate_provider_chain_label(fixture));
    printf("field=%s\n", field);
    printf("cells=%u\n", (unsigned int)cells);
    printf("unknown_cells=%u\n", (unsigned int)unknown);
    printf("min_q16=%d\n", (int)minv);
    printf("max_q16=%d\n", (int)maxv);
    printf("mean_q16=%d\n", (int)((cells > 0u) ? (q16_16)(sum / (i64)cells) : 0));
    printf("slice_hash=%llu\n", (unsigned long long)hash);

    dom_climate_domain_free(&climate_domain);
    return 0;
}

static int climate_run_diff(const climate_fixture* fixture_a,
                            const climate_fixture* fixture_b,
                            const dom_domain_point* origin,
                            const dom_domain_point* direction,
                            q16_16 length,
                            u32 steps,
                            u32 budget_max)
{
    int ok_a = 0;
    int ok_b = 0;
    u64 hash_a = climate_core_sample_hash(fixture_a, origin, direction, length, steps, budget_max,
                                          0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_a);
    u64 hash_b = climate_core_sample_hash(fixture_b, origin, direction, length, steps, budget_max,
                                          0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_b);
    if (!ok_a || !ok_b) {
        return 1;
    }
    printf("%s\n", CLIMATE_DIFF_HEADER);
    printf("fixture_a=%s\n", fixture_a->fixture_id);
    printf("fixture_b=%s\n", fixture_b->fixture_id);
    printf("hash_a=%llu\n", (unsigned long long)hash_a);
    printf("hash_b=%llu\n", (unsigned long long)hash_b);
    printf("equal=%u\n", (unsigned int)(hash_a == hash_b ? 1u : 0u));
    return 0;
}

static int climate_run_collapse(const climate_fixture* fixture,
                                const dom_domain_point* point,
                                u32 budget_max)
{
    dom_climate_domain climate_domain;
    dom_domain_tile_desc desc;
    dom_domain_budget budget;
    dom_climate_sample inside;
    dom_climate_sample outside;
    dom_domain_point outside_point;
    u32 count_before;
    u32 count_after;
    u32 count_final;

    dom_climate_domain_init(&climate_domain, &fixture->climate_desc, fixture->cache_capacity);
    if (!climate_build_tile_desc(&climate_domain, point, DOM_DOMAIN_RES_COARSE, &desc)) {
        dom_climate_domain_free(&climate_domain);
        return 1;
    }
    count_before = dom_climate_domain_capsule_count(&climate_domain);
    (void)dom_climate_domain_collapse_tile(&climate_domain, &desc);
    count_after = dom_climate_domain_capsule_count(&climate_domain);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_climate_sample_query(&climate_domain, point, &budget, &inside);

    outside_point = *point;
    outside_point.x = d_q16_16_add(outside_point.x,
                                   d_q16_16_mul(climate_domain.policy.tile_size, d_q16_16_from_int(2)));
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_climate_sample_query(&climate_domain, &outside_point, &budget, &outside);

    (void)dom_climate_domain_expand_tile(&climate_domain, desc.tile_id);
    count_final = dom_climate_domain_capsule_count(&climate_domain);

    printf("%s\n", CLIMATE_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", climate_provider_chain_label(fixture));
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);
    printf("capsule_count_final=%u\n", (unsigned int)count_final);
    printf("tile_id=%llu\n", (unsigned long long)desc.tile_id);
    printf("inside_resolution=%u\n", (unsigned int)inside.meta.resolution);
    printf("outside_resolution=%u\n", (unsigned int)outside.meta.resolution);
    printf("inside_flags=%u\n", (unsigned int)inside.flags);
    printf("outside_flags=%u\n", (unsigned int)outside.flags);

    dom_climate_domain_free(&climate_domain);
    return 0;
}

static void climate_usage(void)
{
    printf("dom_tool_climate commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --pos x,y,z [--budget N]\n");
    printf("  core-sample --fixture <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--budget N] [--inactive N] [--collapsed 0|1]\n");
    printf("  map --fixture <path> [--center-latlon lat,lon] [--span S] [--dim N] [--budget N]\n");
    printf("  slice --fixture <path> --field <temp_mean|temp_range|precip_mean|precip_range|seasonality> --center x,y,z --radius R [--dim N] [--axis xy|xz|yz] [--budget N]\n");
    printf("  diff --fixture-a <path> --fixture-b <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--budget N]\n");
    printf("  collapse --fixture <path> --pos x,y,z [--budget N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        climate_usage();
        return 2;
    }
    cmd = argv[1];

    if (strcmp(cmd, "diff") == 0) {
        const char* fixture_a_path = climate_find_arg(argc, argv, "--fixture-a");
        const char* fixture_b_path = climate_find_arg(argc, argv, "--fixture-b");
        climate_fixture fixture_a;
        climate_fixture fixture_b;
        dom_domain_point origin;
        dom_domain_point direction;
        q16_16 length = d_q16_16_from_int(64);
        u32 steps = climate_find_arg_u32(argc, argv, "--steps", 16u);
        u32 budget_max;
        if (!fixture_a_path || !fixture_b_path ||
            !climate_fixture_load(fixture_a_path, &fixture_a) ||
            !climate_fixture_load(fixture_b_path, &fixture_b)) {
            fprintf(stderr, "climate: missing or invalid --fixture-a/--fixture-b\n");
            return 2;
        }
        if (!climate_parse_arg_point(argc, argv, "--origin", &origin) ||
            !climate_parse_arg_point(argc, argv, "--dir", &direction)) {
            fprintf(stderr, "climate: missing --origin or --dir\n");
            return 2;
        }
        if (!climate_parse_q16(climate_find_arg(argc, argv, "--length"), &length)) {
            length = d_q16_16_from_int(64);
        }
        budget_max = climate_find_arg_u32(argc, argv, "--budget", fixture_a.climate_policy.cost_medium);
        return climate_run_diff(&fixture_a, &fixture_b, &origin, &direction, length, steps, budget_max);
    }

    {
        const char* fixture_path = climate_find_arg(argc, argv, "--fixture");
        climate_fixture fixture;
        if (!fixture_path || !climate_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "climate: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return climate_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            dom_domain_point point;
            u32 budget_max = climate_find_arg_u32(argc, argv, "--budget", fixture.climate_policy.cost_full);
            if (!climate_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "climate: missing --pos\n");
                return 2;
            }
            return climate_run_inspect(&fixture, &point, budget_max);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_domain_point origin;
            dom_domain_point direction;
            q16_16 length = d_q16_16_from_int(64);
            u32 steps = climate_find_arg_u32(argc, argv, "--steps", 16u);
            u32 budget_max = climate_find_arg_u32(argc, argv, "--budget",
                                                  fixture.climate_policy.cost_medium +
                                                  fixture.climate_policy.tile_build_cost_medium);
            u32 inactive = climate_find_arg_u32(argc, argv, "--inactive", 0u);
            u32 collapsed = climate_find_arg_u32(argc, argv, "--collapsed", 0u);
            if (!climate_parse_arg_point(argc, argv, "--origin", &origin) ||
                !climate_parse_arg_point(argc, argv, "--dir", &direction)) {
                fprintf(stderr, "climate: missing --origin or --dir\n");
                return 2;
            }
            if (!climate_parse_q16(climate_find_arg(argc, argv, "--length"), &length)) {
                length = d_q16_16_from_int(64);
            }
            return climate_run_core_sample(&fixture, &origin, &direction, length, steps, budget_max,
                                           inactive, collapsed ? 1 : 0);
        }

        if (strcmp(cmd, "map") == 0) {
            q16_16 center_lat = 0;
            q16_16 center_lon = 0;
            q16_16 span = d_q16_16_from_double(0.1);
            u32 dim = climate_find_arg_u32(argc, argv, "--dim", 8u);
            u32 budget_max = climate_find_arg_u32(argc, argv, "--budget", fixture.climate_policy.cost_medium);
            const char* center_text = climate_find_arg(argc, argv, "--center-latlon");
            if (center_text) {
                climate_parse_pair_q16(center_text, &center_lat, &center_lon);
            }
            if (!climate_parse_q16(climate_find_arg(argc, argv, "--span"), &span)) {
                span = d_q16_16_from_double(0.1);
            }
            return climate_run_map(&fixture, center_lat, center_lon, span, dim, budget_max);
        }

        if (strcmp(cmd, "slice") == 0) {
            dom_domain_point center;
            q16_16 radius;
            u32 dim = climate_find_arg_u32(argc, argv, "--dim", 8u);
            u32 budget_max = climate_find_arg_u32(argc, argv, "--budget", fixture.climate_policy.cost_medium);
            const char* field = climate_find_arg(argc, argv, "--field");
            const char* axis = climate_find_arg(argc, argv, "--axis");
            if (!field) {
                fprintf(stderr, "climate: missing --field\n");
                return 2;
            }
            if (!climate_parse_arg_point(argc, argv, "--center", &center)) {
                fprintf(stderr, "climate: missing --center\n");
                return 2;
            }
            if (!climate_parse_q16(climate_find_arg(argc, argv, "--radius"), &radius)) {
                fprintf(stderr, "climate: missing --radius\n");
                return 2;
            }
            return climate_run_slice(&fixture, &center, radius, dim, budget_max, field, axis);
        }

        if (strcmp(cmd, "collapse") == 0) {
            dom_domain_point point;
            u32 budget_max = climate_find_arg_u32(argc, argv, "--budget", fixture.climate_policy.cost_analytic);
            if (!climate_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "climate: missing --pos\n");
                return 2;
            }
            return climate_run_collapse(&fixture, &point, budget_max);
        }
    }

    climate_usage();
    return 2;
}
