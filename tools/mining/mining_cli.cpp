/*
FILE: tools/mining/mining_cli.cpp
MODULE: Dominium
PURPOSE: Mining fixture CLI for deterministic cut/extract/support checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/mining_fields.h"

#define MINING_FIXTURE_HEADER "DOMINIUM_MINING_FIXTURE_V1"

#define MINING_VALIDATE_HEADER "DOMINIUM_MINING_VALIDATE_V1"
#define MINING_INSPECT_HEADER "DOMINIUM_MINING_INSPECT_V1"
#define MINING_CUT_HEADER "DOMINIUM_MINING_CUT_V1"
#define MINING_EXTRACT_HEADER "DOMINIUM_MINING_EXTRACT_V1"
#define MINING_SUPPORT_HEADER "DOMINIUM_MINING_SUPPORT_V1"
#define MINING_COLLAPSE_HEADER "DOMINIUM_MINING_COLLAPSE_V1"
#define MINING_CORE_SAMPLE_HEADER "DOMINIUM_MINING_CORE_SAMPLE_V1"

#define MINING_PROVIDER_CHAIN "terrain->geology->mining"

#define MINING_LINE_MAX 512u

typedef struct mining_fixture {
    char fixture_id[96];
    dom_mining_surface_desc desc;
    dom_domain_policy policy;
    u32 cache_capacity;
    u32 policy_set;
    char layer_ids[DOM_GEOLOGY_MAX_LAYERS][64];
    char resource_ids[DOM_GEOLOGY_MAX_RESOURCES][64];
} mining_fixture;

static char* mining_trim(char* text)
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

static int mining_parse_u32(const char* text, u32* out_value)
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

static int mining_parse_u64(const char* text, u64* out_value)
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

static int mining_parse_q16(const char* text, q16_16* out_value)
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

static int mining_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[MINING_LINE_MAX];
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
    if (!mining_parse_q16(mining_trim(first), a)) return 0;
    if (!mining_parse_q16(mining_trim(second), b)) return 0;
    if (!mining_parse_q16(mining_trim(third), c)) return 0;
    return 1;
}

static int mining_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!mining_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 mining_parse_resolution(const char* text)
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

static int mining_parse_indexed_key(const char* key,
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

static void mining_fixture_init(mining_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_mining_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->cache_capacity = 128u;
    fixture->policy_set = 0u;
    strncpy(fixture->fixture_id, "mining.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
    fixture->desc.cache_capacity = fixture->cache_capacity;
}

static int mining_fixture_apply_layer(mining_fixture* fixture,
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
    if (fixture->desc.geology_desc.layer_count <= index) {
        fixture->desc.geology_desc.layer_count = index + 1u;
    }
    layer = &fixture->desc.geology_desc.layers[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->layer_ids[index], value, sizeof(fixture->layer_ids[index]) - 1);
        fixture->layer_ids[index][sizeof(fixture->layer_ids[index]) - 1] = '\0';
        layer->layer_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "thickness") == 0) {
        return mining_parse_q16(value, &layer->thickness);
    }
    if (strcmp(suffix, "hardness") == 0) {
        return mining_parse_q16(value, &layer->hardness);
    }
    if (strcmp(suffix, "fracture") == 0) {
        layer->has_fracture = 1u;
        return mining_parse_q16(value, &layer->fracture_risk);
    }
    return 0;
}

static int mining_fixture_apply_resource(mining_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_geology_resource_desc* res;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_GEOLOGY_MAX_RESOURCES) {
        return 0;
    }
    if (fixture->desc.geology_desc.resource_count <= index) {
        fixture->desc.geology_desc.resource_count = index + 1u;
    }
    res = &fixture->desc.geology_desc.resources[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->resource_ids[index], value, sizeof(fixture->resource_ids[index]) - 1);
        fixture->resource_ids[index][sizeof(fixture->resource_ids[index]) - 1] = '\0';
        res->resource_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "base") == 0) {
        return mining_parse_q16(value, &res->base_density);
    }
    if (strcmp(suffix, "noise_amp") == 0) {
        return mining_parse_q16(value, &res->noise_amplitude);
    }
    if (strcmp(suffix, "noise_cell") == 0) {
        return mining_parse_q16(value, &res->noise_cell_size);
    }
    if (strcmp(suffix, "pocket_threshold") == 0) {
        return mining_parse_q16(value, &res->pocket_threshold);
    }
    if (strcmp(suffix, "pocket_boost") == 0) {
        return mining_parse_q16(value, &res->pocket_boost);
    }
    if (strcmp(suffix, "pocket_cell") == 0) {
        return mining_parse_q16(value, &res->pocket_cell_size);
    }
    if (strcmp(suffix, "seed") == 0) {
        return mining_parse_u64(value, &res->seed);
    }
    return 0;
}

static int mining_fixture_apply(mining_fixture* fixture, const char* key, const char* value)
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
        if (mining_parse_u64(value, &fixture->desc.world_seed)) {
            fixture->desc.terrain_desc.world_seed = fixture->desc.world_seed;
            fixture->desc.geology_desc.world_seed = fixture->desc.world_seed;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "domain_id") == 0) {
        if (mining_parse_u64(value, &fixture->desc.domain_id)) {
            fixture->desc.terrain_desc.domain_id = fixture->desc.domain_id;
            fixture->desc.geology_desc.domain_id = fixture->desc.domain_id;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "shape") == 0) {
        if (strcmp(value, "sphere") == 0) {
            fixture->desc.shape.kind = DOM_TERRAIN_SHAPE_SPHERE;
        } else if (strcmp(value, "oblate") == 0) {
            fixture->desc.shape.kind = DOM_TERRAIN_SHAPE_OBLATE;
        } else if (strcmp(value, "slab") == 0) {
            fixture->desc.shape.kind = DOM_TERRAIN_SHAPE_SLAB;
        } else {
            return 0;
        }
        fixture->desc.terrain_desc.shape = fixture->desc.shape;
        fixture->desc.geology_desc.shape = fixture->desc.shape;
        return 1;
    }
    if (strcmp(key, "radius_equatorial") == 0) {
        if (mining_parse_q16(value, &fixture->desc.shape.radius_equatorial)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "radius_polar") == 0) {
        if (mining_parse_q16(value, &fixture->desc.shape.radius_polar)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        if (mining_parse_q16(value, &fixture->desc.shape.slab_half_extent)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        if (mining_parse_q16(value, &fixture->desc.shape.slab_half_thickness)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        if (mining_parse_q16(value, &fixture->desc.meters_per_unit)) {
            fixture->desc.terrain_desc.meters_per_unit = fixture->desc.meters_per_unit;
            fixture->desc.geology_desc.meters_per_unit = fixture->desc.meters_per_unit;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "cache_capacity") == 0) {
        if (mining_parse_u32(value, &fixture->cache_capacity)) {
            fixture->desc.cache_capacity = fixture->cache_capacity;
            return 1;
        }
        return 0;
    }

    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_q16(value, &fixture->policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->policy.max_resolution = mining_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_q16(value, &fixture->policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return mining_parse_u32(value, &fixture->policy.max_ray_steps);
    }

    if (strcmp(key, "terrain_noise_seed") == 0) {
        return mining_parse_u64(value, &fixture->desc.terrain_desc.noise.seed);
    }
    if (strcmp(key, "terrain_noise_amplitude") == 0) {
        return mining_parse_q16(value, &fixture->desc.terrain_desc.noise.amplitude);
    }
    if (strcmp(key, "terrain_noise_cell_size") == 0) {
        return mining_parse_q16(value, &fixture->desc.terrain_desc.noise.cell_size);
    }
    if (strcmp(key, "terrain_roughness_base") == 0) {
        return mining_parse_q16(value, &fixture->desc.terrain_desc.roughness_base);
    }
    if (strcmp(key, "terrain_travel_cost_base") == 0) {
        return mining_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_base);
    }
    if (strcmp(key, "terrain_travel_cost_slope_scale") == 0) {
        return mining_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_slope_scale);
    }
    if (strcmp(key, "terrain_travel_cost_roughness_scale") == 0) {
        return mining_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_roughness_scale);
    }
    if (strcmp(key, "terrain_material_primary") == 0) {
        return mining_parse_u32(value, &fixture->desc.terrain_desc.material_primary);
    }
    if (strcmp(key, "terrain_walkable_max_slope") == 0) {
        return mining_parse_q16(value, &fixture->desc.terrain_desc.walkable_max_slope);
    }

    if (strcmp(key, "geo_default_hardness") == 0) {
        return mining_parse_q16(value, &fixture->desc.geology_desc.default_hardness);
    }
    if (strcmp(key, "geo_default_fracture_risk") == 0) {
        return mining_parse_q16(value, &fixture->desc.geology_desc.default_fracture_risk);
    }

    if (strcmp(key, "cut_radius_max") == 0) {
        return mining_parse_q16(value, &fixture->desc.cut_radius_max);
    }
    if (strcmp(key, "extract_radius_max") == 0) {
        return mining_parse_q16(value, &fixture->desc.extract_radius_max);
    }
    if (strcmp(key, "support_radius_scale") == 0) {
        return mining_parse_q16(value, &fixture->desc.support_radius_scale);
    }
    if (strcmp(key, "collapse_fill_scale") == 0) {
        return mining_parse_q16(value, &fixture->desc.collapse_fill_scale);
    }
    if (strcmp(key, "cut_cost_base") == 0) {
        return mining_parse_u32(value, &fixture->desc.cut_cost_base);
    }
    if (strcmp(key, "cut_cost_per_unit") == 0) {
        return mining_parse_u32(value, &fixture->desc.cut_cost_per_unit);
    }
    if (strcmp(key, "extract_cost_base") == 0) {
        return mining_parse_u32(value, &fixture->desc.extract_cost_base);
    }
    if (strcmp(key, "extract_cost_per_unit") == 0) {
        return mining_parse_u32(value, &fixture->desc.extract_cost_per_unit);
    }
    if (strcmp(key, "support_cost_base") == 0) {
        return mining_parse_u32(value, &fixture->desc.support_cost_base);
    }
    if (strcmp(key, "overlay_capacity") == 0) {
        return mining_parse_u32(value, &fixture->desc.overlay_capacity);
    }
    if (strcmp(key, "depletion_capacity") == 0) {
        return mining_parse_u32(value, &fixture->desc.depletion_capacity);
    }
    if (strcmp(key, "chunk_capacity") == 0) {
        return mining_parse_u32(value, &fixture->desc.chunk_capacity);
    }
    if (strcmp(key, "law_allow_mining") == 0) {
        return mining_parse_u32(value, &fixture->desc.law_allow_mining);
    }
    if (strcmp(key, "metalaw_allow_mining") == 0) {
        return mining_parse_u32(value, &fixture->desc.metalaw_allow_mining);
    }
    if (strcmp(key, "tailings_material_id") == 0) {
        fixture->desc.tailings_material_id = d_rng_hash_str32(value);
        return 1;
    }

    if (mining_parse_indexed_key(key, "layer", &index, &suffix)) {
        return mining_fixture_apply_layer(fixture, index, suffix, value);
    }
    if (mining_parse_indexed_key(key, "resource", &index, &suffix)) {
        return mining_fixture_apply_resource(fixture, index, suffix, value);
    }
    return 0;
}

static int mining_fixture_load(const char* path, mining_fixture* out_fixture)
{
    FILE* file;
    char line[MINING_LINE_MAX];
    int header_ok = 0;
    mining_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    mining_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = mining_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, MINING_FIXTURE_HEADER) != 0) {
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
        mining_fixture_apply(&fixture, mining_trim(text), mining_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static void mining_domain_init_from_fixture(const mining_fixture* fixture,
                                            dom_mining_domain* out_domain)
{
    dom_mining_domain_init(out_domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_mining_domain_set_policy(out_domain, &fixture->policy);
    }
}

static const char* mining_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 mining_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = mining_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && mining_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 mining_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = mining_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && mining_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static int mining_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* value = mining_find_arg(argc, argv, key);
    if (!value || !out_point) {
        return 0;
    }
    return mining_parse_point(value, out_point);
}

static int mining_parse_arg_q16(int argc, char** argv, const char* key, q16_16* out_value)
{
    const char* value = mining_find_arg(argc, argv, key);
    if (!value || !out_value) {
        return 0;
    }
    return mining_parse_q16(value, out_value);
}

static u64 mining_hash_u64(u64 h, u64 v)
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

static u64 mining_hash_u32(u64 h, u32 v)
{
    return mining_hash_u64(h, (u64)v);
}

static u64 mining_hash_i32(u64 h, i32 v)
{
    return mining_hash_u64(h, (u64)(u32)v);
}

static u32 mining_overlay_id(const mining_fixture* fixture, u32 process_id, u64 tick, u32 offset)
{
    d_rng_state rng;
    const char* stream = "noise.stream.world.mining.overlay";
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    if (!fixture) {
        return 0u;
    }
    d_rng_state_from_context(&rng,
                             fixture->desc.world_seed,
                             fixture->desc.domain_id,
                             (u64)process_id,
                             tick,
                             stream,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
    for (u32 i = 0u; i <= offset; ++i) {
        (void)d_rng_next_u32(&rng);
    }
    return rng.state;
}

static int mining_run_validate(const mining_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    if (fixture->desc.geology_desc.layer_count == 0u) {
        fprintf(stderr, "mining: no geology layers defined\n");
        return 1;
    }
    printf("%s\n", MINING_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", MINING_PROVIDER_CHAIN);
    printf("layer_count=%u\n", (unsigned int)fixture->desc.geology_desc.layer_count);
    printf("resource_count=%u\n", (unsigned int)fixture->desc.geology_desc.resource_count);
    printf("overlay_capacity=%u\n", (unsigned int)fixture->desc.overlay_capacity);
    printf("chunk_capacity=%u\n", (unsigned int)fixture->desc.chunk_capacity);
    return 0;
}

static void mining_apply_cuts(dom_mining_domain* domain,
                              const dom_domain_point* point,
                              u32 cuts,
                              q16_16 cut_radius,
                              u64 tick)
{
    if (!domain || !point || cuts == 0u) {
        return;
    }
    if (cut_radius <= 0) {
        cut_radius = d_q16_16_from_int(1);
    }
    for (u32 i = 0u; i < cuts; ++i) {
        dom_domain_point p = *point;
        dom_domain_budget budget;
        dom_mining_cut_result result;
        p.x = d_q16_16_add(p.x, d_q16_16_from_int((i32)i));
        dom_domain_budget_init(&budget, 1000000u);
        (void)dom_mining_cut(domain, &p, cut_radius, tick + i, &budget, &result);
    }
}

static int mining_run_inspect(const mining_fixture* fixture,
                              const dom_domain_point* point,
                              u32 budget_max,
                              u32 cuts,
                              q16_16 cut_radius,
                              u64 tick)
{
    dom_mining_domain domain;
    dom_domain_budget budget;
    dom_mining_sample sample;

    mining_domain_init_from_fixture(fixture, &domain);
    mining_apply_cuts(&domain, point, cuts, cut_radius, tick);

    dom_domain_budget_init(&budget, budget_max);
    if (dom_mining_sample_query(&domain, point, &budget, &sample) != 0) {
        dom_mining_domain_free(&domain);
        return 1;
    }

    printf("%s\n", MINING_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", MINING_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("phi_q16=%d\n", (int)sample.phi);
    printf("material_primary=%u\n", (unsigned int)sample.material_primary);
    printf("support_capacity_q16=%d\n", (int)sample.support_capacity);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("fields_unknown=%u\n", (unsigned int)((sample.flags & DOM_MINING_SAMPLE_FIELDS_UNKNOWN) ? 1u : 0u));
    printf("overlay_count=%u\n", (unsigned int)domain.overlay_count);
    printf("chunk_count=%u\n", (unsigned int)domain.chunk_count);
    printf("resource_count=%u\n", (unsigned int)sample.resource_count);
    for (u32 i = 0u; i < sample.resource_count; ++i) {
        printf("resource.%u.id=%s\n", (unsigned int)i, fixture->resource_ids[i]);
        printf("resource.%u.density_q16=%d\n", (unsigned int)i, (int)sample.resource_density[i]);
    }
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_mining_domain_free(&domain);
    return 0;
}

static int mining_run_cut(const mining_fixture* fixture,
                           const dom_domain_point* point,
                           q16_16 radius,
                           u64 tick,
                           u32 budget_max,
                           u32 repeat)
{
    dom_mining_domain domain;
    dom_domain_budget budget;
    dom_mining_cut_result result;

    mining_domain_init_from_fixture(fixture, &domain);
    if (repeat == 0u) {
        repeat = 1u;
    }
    for (u32 i = 0u; i < repeat; ++i) {
        dom_domain_budget_init(&budget, budget_max);
        if (dom_mining_cut(&domain, point, radius, tick + i, &budget, &result) != 0) {
            break;
        }
    }

    printf("%s\n", MINING_CUT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", MINING_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("radius_q16=%d\n", (int)radius);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("overlay_id=%u\n", (unsigned int)result.overlay_id);
    printf("overlay_count=%u\n", (unsigned int)domain.overlay_count);
    printf("cut_volume_q16=%d\n", (int)result.cut_volume);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);

    dom_mining_domain_free(&domain);
    return 0;
}

static int mining_run_extract(const mining_fixture* fixture,
                              const dom_domain_point* point,
                              q16_16 radius,
                              u64 tick,
                              u32 budget_max,
                              u32 repeat,
                              u32 pre_cuts,
                              q16_16 cut_radius)
{
    dom_mining_domain domain;
    dom_domain_budget budget;
    dom_mining_extract_result result;

    mining_domain_init_from_fixture(fixture, &domain);
    mining_apply_cuts(&domain, point, pre_cuts, cut_radius, tick);
    if (repeat == 0u) {
        repeat = 1u;
    }
    for (u32 i = 0u; i < repeat; ++i) {
        dom_domain_budget_init(&budget, budget_max);
        if (dom_mining_extract(&domain, point, radius, tick + i, &budget, &result) != 0) {
            break;
        }
    }

    printf("%s\n", MINING_EXTRACT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", MINING_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("radius_q16=%d\n", (int)radius);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("extract_volume_q16=%d\n", (int)result.extract_volume);
    printf("extracted_mass_q16=%d\n", (int)result.extracted_mass);
    printf("tailings_mass_q16=%d\n", (int)result.tailings_mass);
    printf("resource_chunks=%u\n", (unsigned int)result.resource_chunks);
    printf("tailings_chunks=%u\n", (unsigned int)result.tailings_chunks);
    printf("chunk_count=%u\n", (unsigned int)domain.chunk_count);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);

    dom_mining_domain_free(&domain);
    return 0;
}

static int mining_run_support_check(const mining_fixture* fixture,
                                    const dom_domain_point* point,
                                    q16_16 radius,
                                    u64 tick)
{
    dom_mining_domain domain;
    dom_mining_support_result result;

    mining_domain_init_from_fixture(fixture, &domain);
    (void)dom_mining_support_check(&domain, point, radius, tick, &result);

    printf("%s\n", MINING_SUPPORT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", MINING_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("radius_q16=%d\n", (int)radius);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("support_capacity_q16=%d\n", (int)result.support_capacity);
    printf("stress_q16=%d\n", (int)result.stress);
    printf("stress_ratio_q16=%d\n", (int)result.stress_ratio);
    printf("collapse_risk=%u\n", (unsigned int)result.collapse_risk);
    printf("collapse_radius_q16=%d\n", (int)result.collapse_radius);

    dom_mining_domain_free(&domain);
    return 0;
}

static int mining_run_collapse(const mining_fixture* fixture,
                               const dom_domain_point* point,
                               q16_16 radius,
                               u64 tick)
{
    dom_mining_domain domain;
    dom_mining_support_result result;
    u32 overlay_id = 0u;

    mining_domain_init_from_fixture(fixture, &domain);
    (void)dom_mining_support_check(&domain, point, radius, tick, &result);

    if (result.collapse_risk &&
        domain.overlay_count < domain.surface.overlay_capacity &&
        domain.overlay_count < DOM_MINING_MAX_OVERLAYS) {
        dom_mining_overlay* overlay = &domain.overlays[domain.overlay_count];
        u32 process_id = d_rng_hash_str32("process.mine.support_check");
        memset(overlay, 0, sizeof(*overlay));
        overlay->overlay_kind = DOM_MINING_OVERLAY_FILL;
        overlay->center = *point;
        overlay->radius = (result.collapse_radius > 0) ? result.collapse_radius : radius;
        overlay->tick = tick;
        overlay->process_id = process_id;
        overlay->event_id = d_rng_hash_str32("event.mine.collapse");
        overlay->flags = DOM_MINING_OVERLAY_COLLAPSE;
        overlay->overlay_id = mining_overlay_id(fixture, process_id, tick, domain.overlay_count);
        overlay_id = overlay->overlay_id;
        domain.overlay_count += 1u;
    }

    printf("%s\n", MINING_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", MINING_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("radius_q16=%d\n", (int)radius);
    printf("collapse_risk=%u\n", (unsigned int)result.collapse_risk);
    printf("overlay_id=%u\n", (unsigned int)overlay_id);
    printf("overlay_count=%u\n", (unsigned int)domain.overlay_count);

    dom_mining_domain_free(&domain);
    return 0;
}

static u64 mining_core_sample_hash(const mining_fixture* fixture,
                                   const dom_domain_point* origin,
                                   const dom_domain_point* direction,
                                   q16_16 length,
                                   u32 steps,
                                   u32 budget_max,
                                   u32 cuts,
                                   q16_16 cut_radius,
                                   u32 inactive,
                                   u32* out_unknown_steps,
                                   u32* out_cost_max,
                                   u32* out_overlay_count,
                                   u32* out_chunk_count,
                                   int* out_ok)
{
    dom_mining_domain domain;
    dom_mining_domain* inactive_domains = (dom_mining_domain*)0;
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

    mining_domain_init_from_fixture(fixture, &domain);
    mining_apply_cuts(&domain, origin, cuts, cut_radius, 0u);

    if (inactive > 0u) {
        inactive_domains = (dom_mining_domain*)malloc(sizeof(dom_mining_domain) * inactive);
        if (!inactive_domains) {
            dom_mining_domain_free(&domain);
            return 0;
        }
        for (u32 i = 0u; i < inactive; ++i) {
            mining_domain_init_from_fixture(fixture, &inactive_domains[i]);
            dom_mining_domain_set_state(&inactive_domains[i], DOM_DOMAIN_EXISTENCE_NONEXISTENT,
                                        DOM_DOMAIN_ARCHIVAL_LIVE);
        }
    }

    if (steps == 0u) {
        steps = 1u;
    }
    if (steps > 1u) {
        step_len = (q16_16)((i64)length / (i64)(steps - 1u));
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_mining_sample sample;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));
        dom_domain_budget_init(&budget, budget_max);
        if (dom_mining_sample_query(&domain, &p, &budget, &sample) != 0) {
            dom_mining_domain_free(&domain);
            if (inactive_domains) {
                for (u32 j = 0u; j < inactive; ++j) {
                    dom_mining_domain_free(&inactive_domains[j]);
                }
                free(inactive_domains);
            }
            return 0;
        }
        if (sample.flags & DOM_MINING_SAMPLE_FIELDS_UNKNOWN) {
            unknown_steps += 1u;
        }
        if (sample.meta.cost_units > cost_max) {
            cost_max = sample.meta.cost_units;
        }
        hash = mining_hash_i32(hash, sample.phi);
        hash = mining_hash_i32(hash, sample.support_capacity);
        hash = mining_hash_u32(hash, sample.flags);
        for (u32 r = 0u; r < sample.resource_count; ++r) {
            hash = mining_hash_i32(hash, sample.resource_density[r]);
        }
    }

    if (out_overlay_count) {
        *out_overlay_count = domain.overlay_count;
    }
    if (out_chunk_count) {
        *out_chunk_count = domain.chunk_count;
    }
    dom_mining_domain_free(&domain);
    if (inactive_domains) {
        for (u32 i = 0u; i < inactive; ++i) {
            dom_mining_domain_free(&inactive_domains[i]);
        }
        free(inactive_domains);
    }
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

static int mining_run_core_sample(const mining_fixture* fixture,
                                  const dom_domain_point* origin,
                                  const dom_domain_point* direction,
                                  q16_16 length,
                                  u32 steps,
                                  u32 budget_max,
                                  u32 cuts,
                                  q16_16 cut_radius,
                                  u32 inactive)
{
    u32 unknown_steps = 0u;
    u32 cost_max = 0u;
    u32 overlay_count = 0u;
    u32 chunk_count = 0u;
    int ok = 0;
    u64 hash = mining_core_sample_hash(fixture, origin, direction, length, steps,
                                       budget_max, cuts, cut_radius, inactive,
                                       &unknown_steps, &cost_max,
                                       &overlay_count, &chunk_count, &ok);
    if (!ok) {
        return 1;
    }
    printf("%s\n", MINING_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", MINING_PROVIDER_CHAIN);
    printf("steps=%u\n", (unsigned int)steps);
    printf("budget_max=%u\n", (unsigned int)budget_max);
    printf("cuts=%u\n", (unsigned int)cuts);
    printf("unknown_steps=%u\n", (unsigned int)unknown_steps);
    printf("cost_step_max=%u\n", (unsigned int)cost_max);
    printf("sample_hash=%llu\n", (unsigned long long)hash);
    printf("inactive_domains=%u\n", (unsigned int)inactive);
    printf("overlay_count=%u\n", (unsigned int)overlay_count);
    printf("chunk_count=%u\n", (unsigned int)chunk_count);
    return 0;
}

static void mining_usage(void)
{
    printf("dom_tool_mining commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --pos x,y,z [--budget N] [--cuts N] [--cut_radius R] [--tick T]\n");
    printf("  cut --fixture <path> --pos x,y,z --radius R [--tick T] [--budget N] [--repeat N]\n");
    printf("  extract --fixture <path> --pos x,y,z --radius R [--tick T] [--budget N] [--repeat N] [--cuts N] [--cut_radius R]\n");
    printf("  support-check --fixture <path> --pos x,y,z --radius R [--tick T]\n");
    printf("  collapse --fixture <path> --pos x,y,z --radius R [--tick T]\n");
    printf("  core-sample --fixture <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--budget N] [--cuts N] [--cut_radius R] [--inactive N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        mining_usage();
        return 2;
    }
    cmd = argv[1];

    {
        const char* fixture_path = mining_find_arg(argc, argv, "--fixture");
        mining_fixture fixture;
        if (!fixture_path || !mining_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "mining: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return mining_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            dom_domain_point point;
            u32 budget_max = mining_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 cuts = mining_find_arg_u32(argc, argv, "--cuts", 0u);
            q16_16 cut_radius = d_q16_16_from_int(1);
            u64 tick = mining_find_arg_u64(argc, argv, "--tick", 0u);
            if (!mining_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "mining: missing --pos\n");
                return 2;
            }
            if (!mining_parse_arg_q16(argc, argv, "--cut_radius", &cut_radius)) {
                cut_radius = d_q16_16_from_int(1);
            }
            return mining_run_inspect(&fixture, &point, budget_max, cuts, cut_radius, tick);
        }

        if (strcmp(cmd, "cut") == 0) {
            dom_domain_point point;
            q16_16 radius;
            u64 tick = mining_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = mining_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 repeat = mining_find_arg_u32(argc, argv, "--repeat", 1u);
            if (!mining_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "mining: missing --pos\n");
                return 2;
            }
            if (!mining_parse_arg_q16(argc, argv, "--radius", &radius)) {
                fprintf(stderr, "mining: missing --radius\n");
                return 2;
            }
            return mining_run_cut(&fixture, &point, radius, tick, budget_max, repeat);
        }

        if (strcmp(cmd, "extract") == 0) {
            dom_domain_point point;
            q16_16 radius;
            q16_16 cut_radius = d_q16_16_from_int(1);
            u64 tick = mining_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = mining_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 repeat = mining_find_arg_u32(argc, argv, "--repeat", 1u);
            u32 cuts = mining_find_arg_u32(argc, argv, "--cuts", 0u);
            if (!mining_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "mining: missing --pos\n");
                return 2;
            }
            if (!mining_parse_arg_q16(argc, argv, "--radius", &radius)) {
                fprintf(stderr, "mining: missing --radius\n");
                return 2;
            }
            if (!mining_parse_arg_q16(argc, argv, "--cut_radius", &cut_radius)) {
                cut_radius = d_q16_16_from_int(1);
            }
            return mining_run_extract(&fixture, &point, radius, tick, budget_max, repeat, cuts, cut_radius);
        }

        if (strcmp(cmd, "support-check") == 0) {
            dom_domain_point point;
            q16_16 radius;
            u64 tick = mining_find_arg_u64(argc, argv, "--tick", 0u);
            if (!mining_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "mining: missing --pos\n");
                return 2;
            }
            if (!mining_parse_arg_q16(argc, argv, "--radius", &radius)) {
                fprintf(stderr, "mining: missing --radius\n");
                return 2;
            }
            return mining_run_support_check(&fixture, &point, radius, tick);
        }

        if (strcmp(cmd, "collapse") == 0) {
            dom_domain_point point;
            q16_16 radius;
            u64 tick = mining_find_arg_u64(argc, argv, "--tick", 0u);
            if (!mining_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "mining: missing --pos\n");
                return 2;
            }
            if (!mining_parse_arg_q16(argc, argv, "--radius", &radius)) {
                fprintf(stderr, "mining: missing --radius\n");
                return 2;
            }
            return mining_run_collapse(&fixture, &point, radius, tick);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_domain_point origin;
            dom_domain_point direction;
            q16_16 length = d_q16_16_from_int(64);
            q16_16 cut_radius = d_q16_16_from_int(1);
            u32 steps = mining_find_arg_u32(argc, argv, "--steps", 16u);
            u32 budget_max = mining_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 cuts = mining_find_arg_u32(argc, argv, "--cuts", 0u);
            u32 inactive = mining_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!mining_parse_arg_point(argc, argv, "--origin", &origin) ||
                !mining_parse_arg_point(argc, argv, "--dir", &direction)) {
                fprintf(stderr, "mining: missing --origin or --dir\n");
                return 2;
            }
            if (!mining_parse_arg_q16(argc, argv, "--length", &length)) {
                length = d_q16_16_from_int(64);
            }
            if (!mining_parse_arg_q16(argc, argv, "--cut_radius", &cut_radius)) {
                cut_radius = d_q16_16_from_int(1);
            }
            return mining_run_core_sample(&fixture, &origin, &direction, length, steps,
                                          budget_max, cuts, cut_radius, inactive);
        }
    }

    mining_usage();
    return 2;
}
