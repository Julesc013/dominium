/*
FILE: tools/geology/geology_cli.cpp
MODULE: Dominium
PURPOSE: Geology fixture CLI for deterministic subsurface checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/geology_fields.h"
#include "domino/world/terrain_surface.h"

#define GEOLOGY_FIXTURE_HEADER "DOMINIUM_GEOLOGY_FIXTURE_V1"

#define GEOLOGY_INSPECT_HEADER "DOMINIUM_GEOLOGY_INSPECT_V1"
#define GEOLOGY_CORE_SAMPLE_HEADER "DOMINIUM_GEOLOGY_CORE_SAMPLE_V1"
#define GEOLOGY_MAP_HEADER "DOMINIUM_GEOLOGY_MAP_V1"
#define GEOLOGY_SLICE_HEADER "DOMINIUM_GEOLOGY_SLICE_V1"
#define GEOLOGY_VALIDATE_HEADER "DOMINIUM_GEOLOGY_VALIDATE_V1"
#define GEOLOGY_DIFF_HEADER "DOMINIUM_GEOLOGY_DIFF_V1"
#define GEOLOGY_COLLAPSE_HEADER "DOMINIUM_GEOLOGY_COLLAPSE_V1"

#define GEOLOGY_PROVIDER_CHAIN "procedural_base"

#define GEOLOGY_LINE_MAX 512u
#define GEOLOGY_MAX_SEGMENTS 64u

typedef struct geology_fixture {
    char fixture_id[96];
    dom_geology_surface_desc desc;
    dom_domain_policy policy;
    u32 cache_capacity;
    u32 policy_set;
    char layer_ids[DOM_GEOLOGY_MAX_LAYERS][64];
    char resource_ids[DOM_GEOLOGY_MAX_RESOURCES][64];
} geology_fixture;

typedef struct geology_segment {
    u32 layer_id;
    q16_16 depth_start;
    q16_16 depth_end;
    u32 count;
} geology_segment;

static u64 geology_hash_u64(u64 h, u64 v)
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

static u64 geology_hash_u32(u64 h, u32 v)
{
    return geology_hash_u64(h, (u64)v);
}

static u64 geology_hash_i32(u64 h, i32 v)
{
    return geology_hash_u64(h, (u64)(u32)v);
}

static char* geology_trim(char* text)
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

static int geology_parse_u32(const char* text, u32* out_value)
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

static int geology_parse_u64(const char* text, u64* out_value)
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

static int geology_parse_q16(const char* text, q16_16* out_value)
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

static int geology_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[GEOLOGY_LINE_MAX];
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
    if (!geology_parse_q16(geology_trim(first), a)) return 0;
    if (!geology_parse_q16(geology_trim(second), b)) return 0;
    if (!geology_parse_q16(geology_trim(third), c)) return 0;
    return 1;
}

static int geology_parse_pair_q16(const char* text, q16_16* a, q16_16* b)
{
    char buffer[GEOLOGY_LINE_MAX];
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
    if (!geology_parse_q16(geology_trim(first), a)) return 0;
    if (!geology_parse_q16(geology_trim(second), b)) return 0;
    return 1;
}

static int geology_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!geology_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 geology_parse_resolution(const char* text)
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

static int geology_parse_indexed_key(const char* key,
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

static void geology_fixture_init(geology_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_geology_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->cache_capacity = 128u;
    fixture->policy_set = 0u;
    strncpy(fixture->fixture_id, "geology.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
    fixture->desc.domain_id = 1u;
    fixture->desc.world_seed = 1u;
}

static int geology_fixture_apply_layer(geology_fixture* fixture,
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
    if (fixture->desc.layer_count <= index) {
        fixture->desc.layer_count = index + 1u;
    }
    layer = &fixture->desc.layers[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->layer_ids[index], value, sizeof(fixture->layer_ids[index]) - 1);
        fixture->layer_ids[index][sizeof(fixture->layer_ids[index]) - 1] = '\0';
        layer->layer_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "thickness") == 0) {
        return geology_parse_q16(value, &layer->thickness);
    }
    if (strcmp(suffix, "hardness") == 0) {
        return geology_parse_q16(value, &layer->hardness);
    }
    if (strcmp(suffix, "fracture") == 0) {
        layer->has_fracture = 1u;
        return geology_parse_q16(value, &layer->fracture_risk);
    }
    return 0;
}

static int geology_fixture_apply_resource(geology_fixture* fixture,
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
    if (fixture->desc.resource_count <= index) {
        fixture->desc.resource_count = index + 1u;
    }
    res = &fixture->desc.resources[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->resource_ids[index], value, sizeof(fixture->resource_ids[index]) - 1);
        fixture->resource_ids[index][sizeof(fixture->resource_ids[index]) - 1] = '\0';
        res->resource_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "base") == 0) {
        return geology_parse_q16(value, &res->base_density);
    }
    if (strcmp(suffix, "noise_amp") == 0) {
        return geology_parse_q16(value, &res->noise_amplitude);
    }
    if (strcmp(suffix, "noise_cell") == 0) {
        return geology_parse_q16(value, &res->noise_cell_size);
    }
    if (strcmp(suffix, "pocket_threshold") == 0) {
        return geology_parse_q16(value, &res->pocket_threshold);
    }
    if (strcmp(suffix, "pocket_boost") == 0) {
        return geology_parse_q16(value, &res->pocket_boost);
    }
    if (strcmp(suffix, "pocket_cell") == 0) {
        return geology_parse_q16(value, &res->pocket_cell_size);
    }
    if (strcmp(suffix, "seed") == 0) {
        return geology_parse_u64(value, &res->seed);
    }
    return 0;
}

static int geology_fixture_apply(geology_fixture* fixture, const char* key, const char* value)
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
        return geology_parse_u64(value, &fixture->desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return geology_parse_u64(value, &fixture->desc.domain_id);
    }
    if (strcmp(key, "shape") == 0) {
        if (strcmp(value, "sphere") == 0) {
            fixture->desc.shape.kind = DOM_TERRAIN_SHAPE_SPHERE;
            return 1;
        }
        if (strcmp(value, "oblate") == 0) {
            fixture->desc.shape.kind = DOM_TERRAIN_SHAPE_OBLATE;
            return 1;
        }
        if (strcmp(value, "slab") == 0) {
            fixture->desc.shape.kind = DOM_TERRAIN_SHAPE_SLAB;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "radius_equatorial") == 0) {
        return geology_parse_q16(value, &fixture->desc.shape.radius_equatorial);
    }
    if (strcmp(key, "radius_polar") == 0) {
        return geology_parse_q16(value, &fixture->desc.shape.radius_polar);
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        return geology_parse_q16(value, &fixture->desc.shape.slab_half_extent);
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        return geology_parse_q16(value, &fixture->desc.shape.slab_half_thickness);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return geology_parse_q16(value, &fixture->desc.meters_per_unit);
    }
    if (strcmp(key, "noise_seed") == 0) {
        return geology_parse_u64(value, &fixture->desc.noise.seed);
    }
    if (strcmp(key, "noise_amplitude") == 0) {
        return geology_parse_q16(value, &fixture->desc.noise.amplitude);
    }
    if (strcmp(key, "noise_cell_size") == 0) {
        return geology_parse_q16(value, &fixture->desc.noise.cell_size);
    }
    if (strcmp(key, "default_hardness") == 0) {
        return geology_parse_q16(value, &fixture->desc.default_hardness);
    }
    if (strcmp(key, "default_fracture_risk") == 0) {
        return geology_parse_q16(value, &fixture->desc.default_fracture_risk);
    }
    if (strcmp(key, "layer_count") == 0) {
        return geology_parse_u32(value, &fixture->desc.layer_count);
    }
    if (strcmp(key, "resource_count") == 0) {
        return geology_parse_u32(value, &fixture->desc.resource_count);
    }
    if (strcmp(key, "cache_capacity") == 0) {
        return geology_parse_u32(value, &fixture->cache_capacity);
    }
    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_q16(value, &fixture->policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->policy.max_resolution = geology_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_q16(value, &fixture->policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return geology_parse_u32(value, &fixture->policy.max_ray_steps);
    }
    if (geology_parse_indexed_key(key, "layer", &index, &suffix)) {
        return geology_fixture_apply_layer(fixture, index, suffix, value);
    }
    if (geology_parse_indexed_key(key, "resource", &index, &suffix)) {
        return geology_fixture_apply_resource(fixture, index, suffix, value);
    }
    return 0;
}

static int geology_fixture_load(const char* path, geology_fixture* out_fixture)
{
    FILE* file;
    char line[GEOLOGY_LINE_MAX];
    int header_ok = 0;
    geology_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    geology_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = geology_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, GEOLOGY_FIXTURE_HEADER) != 0) {
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
        geology_fixture_apply(&fixture, geology_trim(text), geology_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static void geology_domain_init_from_fixture(const geology_fixture* fixture,
                                             dom_geology_domain* out_domain)
{
    dom_geology_domain_init(out_domain, &fixture->desc, fixture->cache_capacity);
    if (fixture->policy_set) {
        dom_geology_domain_set_policy(out_domain, &fixture->policy);
    }
}

static const char* geology_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 geology_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = geology_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && geology_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static int geology_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* value = geology_find_arg(argc, argv, key);
    if (!value || !out_point) {
        return 0;
    }
    return geology_parse_point(value, out_point);
}

static int geology_find_resource_index(const geology_fixture* fixture,
                                       const char* resource_id,
                                       u32* out_index)
{
    if (!fixture || !resource_id || !out_index) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->desc.resource_count && i < DOM_GEOLOGY_MAX_RESOURCES; ++i) {
        if (strcmp(fixture->resource_ids[i], resource_id) == 0) {
            *out_index = i;
            return 1;
        }
    }
    return 0;
}

static int geology_run_inspect(const geology_fixture* fixture,
                               const dom_domain_point* point,
                               u32 budget_max)
{
    dom_geology_domain domain;
    dom_domain_budget budget;
    dom_geology_sample sample;

    geology_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    if (dom_geology_sample_query(&domain, point, &budget, &sample) != 0) {
        dom_geology_domain_free(&domain);
        return 1;
    }

    printf("%s\n", GEOLOGY_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", GEOLOGY_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("strata_layer_id=%u\n", (unsigned int)sample.strata_layer_id);
    printf("strata_index=%u\n", (unsigned int)sample.strata_index);
    printf("hardness_q16=%d\n", (int)sample.hardness);
    printf("fracture_risk_q16=%d\n", (int)sample.fracture_risk);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("strata_unknown=%u\n", (unsigned int)((sample.flags & DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN) ? 1u : 0u));
    printf("fields_unknown=%u\n", (unsigned int)((sample.flags & DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN) ? 1u : 0u));
    printf("resources_unknown=%u\n", (unsigned int)((sample.flags & DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN) ? 1u : 0u));
    printf("collapsed=%u\n", (unsigned int)((sample.flags & DOM_GEOLOGY_SAMPLE_COLLAPSED) ? 1u : 0u));
    printf("resource_count=%u\n", (unsigned int)fixture->desc.resource_count);
    for (u32 i = 0u; i < fixture->desc.resource_count; ++i) {
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

    dom_geology_domain_free(&domain);
    return 0;
}

static void geology_segment_push(geology_segment* segments,
                                 u32* count,
                                 u32 layer_id,
                                 q16_16 depth_start)
{
    if (!segments || !count || *count >= GEOLOGY_MAX_SEGMENTS) {
        return;
    }
    segments[*count].layer_id = layer_id;
    segments[*count].depth_start = depth_start;
    segments[*count].depth_end = depth_start;
    segments[*count].count = 0u;
    *count += 1u;
}

static int geology_run_core_sample(const geology_fixture* fixture,
                                   const dom_domain_point* origin,
                                   const dom_domain_point* direction,
                                   q16_16 length,
                                   u32 steps,
                                   u32 budget_max,
                                   u32 inactive_count,
                                   int collapse_tile)
{
    dom_geology_domain domain;
    dom_geology_domain* inactive = 0;
    u64 hash = 14695981039346656037ULL;
    u32 step_cost_min = 0xFFFFFFFFu;
    u32 step_cost_max = 0u;
    u64 cost_total = 0u;
    u32 unknown_steps = 0u;
    geology_segment segments[GEOLOGY_MAX_SEGMENTS];
    u32 segment_count = 0u;
    q16_16 step_len = 0;
    u32 resource_count = fixture->desc.resource_count;
    i64 resource_sum[DOM_GEOLOGY_MAX_RESOURCES];
    q16_16 resource_min[DOM_GEOLOGY_MAX_RESOURCES];
    q16_16 resource_max[DOM_GEOLOGY_MAX_RESOURCES];

    geology_domain_init_from_fixture(fixture, &domain);

    if (inactive_count > 0u) {
        inactive = (dom_geology_domain*)malloc(sizeof(dom_geology_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                geology_fixture temp = *fixture;
                temp.desc.domain_id = fixture->desc.domain_id + (u64)(i + 1u);
                geology_domain_init_from_fixture(&temp, &inactive[i]);
                dom_geology_domain_set_state(&inactive[i],
                                             DOM_DOMAIN_EXISTENCE_DECLARED,
                                             DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    if (steps == 0u) {
        steps = 1u;
    }
    if (steps > 1u) {
        step_len = (q16_16)((i64)length / (i64)(steps - 1u));
    }

    for (u32 r = 0u; r < resource_count; ++r) {
        resource_sum[r] = 0;
        resource_min[r] = DOM_GEOLOGY_UNKNOWN_Q16;
        resource_max[r] = DOM_GEOLOGY_UNKNOWN_Q16;
    }

    if (collapse_tile) {
        dom_domain_tile_desc desc;
        const dom_domain_sdf_source* source = dom_terrain_surface_sdf(&domain.surface.terrain_surface);
        if (source) {
            q16_16 tile_size = domain.policy.tile_size;
            if (tile_size <= 0) {
                tile_size = d_q16_16_from_int(64);
            }
            i32 tx = (i32)(((i64)origin->x - (i64)source->bounds.min.x) / (i64)tile_size);
            i32 ty = (i32)(((i64)origin->y - (i64)source->bounds.min.y) / (i64)tile_size);
            i32 tz = (i32)(((i64)origin->z - (i64)source->bounds.min.z) / (i64)tile_size);
            dom_domain_tile_desc_init(&desc);
            desc.resolution = DOM_DOMAIN_RES_COARSE;
            desc.sample_dim = domain.policy.sample_dim_coarse;
            desc.tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, desc.resolution);
            desc.authoring_version = domain.authoring_version;
            desc.bounds.min.x = (q16_16)(source->bounds.min.x + (q16_16)((i64)tx * (i64)tile_size));
            desc.bounds.min.y = (q16_16)(source->bounds.min.y + (q16_16)((i64)ty * (i64)tile_size));
            desc.bounds.min.z = (q16_16)(source->bounds.min.z + (q16_16)((i64)tz * (i64)tile_size));
            desc.bounds.max.x = (q16_16)(desc.bounds.min.x + tile_size);
            desc.bounds.max.y = (q16_16)(desc.bounds.min.y + tile_size);
            desc.bounds.max.z = (q16_16)(desc.bounds.min.z + tile_size);
            (void)dom_geology_domain_collapse_tile(&domain, &desc);
        }
    }

    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_geology_sample sample;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));
        dom_domain_budget_init(&budget, budget_max);
        if (dom_geology_sample_query(&domain, &p, &budget, &sample) != 0) {
            dom_geology_domain_free(&domain);
            free(inactive);
            return 1;
        }
        cost_total += (u64)sample.meta.cost_units;
        if (sample.meta.cost_units < step_cost_min) step_cost_min = sample.meta.cost_units;
        if (sample.meta.cost_units > step_cost_max) step_cost_max = sample.meta.cost_units;

        if (sample.flags & (DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                            DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                            DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN)) {
            unknown_steps += 1u;
        }

        if (segment_count == 0u) {
            geology_segment_push(segments, &segment_count, sample.strata_layer_id, t);
        } else if (segments[segment_count - 1u].layer_id != sample.strata_layer_id) {
            segments[segment_count - 1u].depth_end = t;
            geology_segment_push(segments, &segment_count, sample.strata_layer_id, t);
        }
        if (segment_count > 0u) {
            segments[segment_count - 1u].count += 1u;
        }

        hash = geology_hash_u32(hash, sample.strata_layer_id);
        hash = geology_hash_u32(hash, sample.strata_index);
        hash = geology_hash_i32(hash, sample.hardness);
        hash = geology_hash_i32(hash, sample.fracture_risk);
        hash = geology_hash_u32(hash, sample.flags);
        hash = geology_hash_u32(hash, sample.meta.status);
        hash = geology_hash_u32(hash, sample.meta.resolution);
        hash = geology_hash_u32(hash, sample.meta.confidence);
        hash = geology_hash_u32(hash, sample.meta.refusal_reason);
        for (u32 r = 0u; r < resource_count; ++r) {
            q16_16 value = sample.resource_density[r];
            hash = geology_hash_i32(hash, value);
            if (resource_min[r] == DOM_GEOLOGY_UNKNOWN_Q16 || value < resource_min[r]) {
                resource_min[r] = value;
            }
            if (resource_max[r] == DOM_GEOLOGY_UNKNOWN_Q16 || value > resource_max[r]) {
                resource_max[r] = value;
            }
            resource_sum[r] += (i64)value;
        }
    }

    if (step_cost_min == 0xFFFFFFFFu) {
        step_cost_min = 0u;
    }
    if (segment_count > 0u) {
        segments[segment_count - 1u].depth_end = length;
    }

    printf("%s\n", GEOLOGY_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", GEOLOGY_PROVIDER_CHAIN);
    printf("steps=%u\n", (unsigned int)steps);
    printf("budget_max=%u\n", (unsigned int)budget_max);
    printf("cost_step_min=%u\n", (unsigned int)step_cost_min);
    printf("cost_step_max=%u\n", (unsigned int)step_cost_max);
    printf("cost_total=%llu\n", (unsigned long long)cost_total);
    printf("unknown_steps=%u\n", (unsigned int)unknown_steps);
    printf("uncertainty_ratio_q16=%d\n", (int)((steps > 0u) ? (q16_16)((((i64)unknown_steps) << 16) / (i64)steps) : 0));
    printf("segments=%u\n", (unsigned int)segment_count);
    for (u32 s = 0u; s < segment_count; ++s) {
        printf("segment.%u.layer_id=%u\n", (unsigned int)s, (unsigned int)segments[s].layer_id);
        printf("segment.%u.depth_start_q16=%d\n", (unsigned int)s, (int)segments[s].depth_start);
        printf("segment.%u.depth_end_q16=%d\n", (unsigned int)s, (int)segments[s].depth_end);
        printf("segment.%u.samples=%u\n", (unsigned int)s, (unsigned int)segments[s].count);
    }
    printf("resource_count=%u\n", (unsigned int)resource_count);
    for (u32 r = 0u; r < resource_count; ++r) {
        q16_16 mean = (steps > 0u) ? (q16_16)(resource_sum[r] / (i64)steps) : 0;
        printf("resource.%u.id=%s\n", (unsigned int)r, fixture->resource_ids[r]);
        printf("resource.%u.min_q16=%d\n", (unsigned int)r, (int)resource_min[r]);
        printf("resource.%u.max_q16=%d\n", (unsigned int)r, (int)resource_max[r]);
        printf("resource.%u.mean_q16=%d\n", (unsigned int)r, (int)mean);
    }
    printf("sample_hash=%llu\n", (unsigned long long)hash);
    printf("cache_entries=%u\n", (unsigned int)domain.cache.count);
    printf("capsule_count=%u\n", (unsigned int)dom_geology_domain_capsule_count(&domain));

    dom_geology_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_geology_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static dom_domain_point geology_latlon_to_local(const dom_terrain_shape_desc* shape,
                                                q16_16 lat_turns,
                                                q16_16 lon_turns)
{
    dom_domain_point point;
    if (!shape) {
        memset(&point, 0, sizeof(point));
        return point;
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        q16_16 span = d_q16_16_mul(shape->slab_half_extent, d_q16_16_from_int(2));
        point.x = d_q16_16_mul(lon_turns, span);
        point.y = d_q16_16_mul(lat_turns, span);
        point.z = 0;
        return point;
    }
    return dom_terrain_latlon_to_local(shape, lat_turns, lon_turns, 0);
}

static int geology_run_map(const geology_fixture* fixture,
                           q16_16 center_lat,
                           q16_16 center_lon,
                           q16_16 span,
                           u32 dim,
                           u32 budget_max)
{
    dom_geology_domain domain;
    u32 cells = 0u;
    u32 unknown = 0u;
    u64 hash = 14695981039346656037ULL;
    q16_16 step = 0;
    q16_16 half_span = d_fixed_div_q16_16(span, d_q16_16_from_int(2));

    geology_domain_init_from_fixture(fixture, &domain);
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
            dom_domain_point p = geology_latlon_to_local(&fixture->desc.shape, lat, lon);
            dom_domain_budget budget;
            dom_geology_sample sample;
            dom_domain_budget_init(&budget, budget_max);
            if (dom_geology_sample_query(&domain, &p, &budget, &sample) != 0) {
                dom_geology_domain_free(&domain);
                return 1;
            }
            cells += 1u;
            if (sample.flags & DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN) {
                unknown += 1u;
            }
            hash = geology_hash_u32(hash, sample.strata_layer_id);
        }
    }

    printf("%s\n", GEOLOGY_MAP_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", GEOLOGY_PROVIDER_CHAIN);
    printf("cells=%u\n", (unsigned int)cells);
    printf("unknown_cells=%u\n", (unsigned int)unknown);
    printf("map_hash=%llu\n", (unsigned long long)hash);

    dom_geology_domain_free(&domain);
    return 0;
}

static int geology_run_slice(const geology_fixture* fixture,
                             const dom_domain_point* center,
                             q16_16 radius,
                             u32 dim,
                             u32 budget_max,
                             u32 resource_index,
                             const char* axis)
{
    dom_geology_domain domain;
    u64 hash = 14695981039346656037ULL;
    u32 cells = 0u;
    u32 unknown = 0u;
    q16_16 step = 0;
    q16_16 minv = DOM_GEOLOGY_UNKNOWN_Q16;
    q16_16 maxv = DOM_GEOLOGY_UNKNOWN_Q16;
    i64 sum = 0;

    geology_domain_init_from_fixture(fixture, &domain);
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
            dom_geology_sample sample;
            dom_domain_budget_init(&budget, budget_max);
            if (dom_geology_sample_query(&domain, &p, &budget, &sample) != 0) {
                dom_geology_domain_free(&domain);
                return 1;
            }
            cells += 1u;
            if (resource_index >= sample.resource_count ||
                (sample.flags & DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN)) {
                unknown += 1u;
                hash = geology_hash_i32(hash, DOM_GEOLOGY_UNKNOWN_Q16);
                continue;
            }
            {
                q16_16 value = sample.resource_density[resource_index];
                hash = geology_hash_i32(hash, value);
                if (minv == DOM_GEOLOGY_UNKNOWN_Q16 || value < minv) {
                    minv = value;
                }
                if (maxv == DOM_GEOLOGY_UNKNOWN_Q16 || value > maxv) {
                    maxv = value;
                }
                sum += (i64)value;
            }
        }
    }

    printf("%s\n", GEOLOGY_SLICE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", GEOLOGY_PROVIDER_CHAIN);
    printf("resource_id=%s\n", fixture->resource_ids[resource_index]);
    printf("cells=%u\n", (unsigned int)cells);
    printf("unknown_cells=%u\n", (unsigned int)unknown);
    printf("min_q16=%d\n", (int)minv);
    printf("max_q16=%d\n", (int)maxv);
    printf("mean_q16=%d\n", (int)((cells > 0u) ? (q16_16)(sum / (i64)cells) : 0));
    printf("slice_hash=%llu\n", (unsigned long long)hash);

    dom_geology_domain_free(&domain);
    return 0;
}

static int geology_run_validate(const geology_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    if (fixture->desc.layer_count == 0u) {
        fprintf(stderr, "geology: no layers defined\n");
        return 1;
    }
    printf("%s\n", GEOLOGY_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", GEOLOGY_PROVIDER_CHAIN);
    printf("layer_count=%u\n", (unsigned int)fixture->desc.layer_count);
    printf("resource_count=%u\n", (unsigned int)fixture->desc.resource_count);
    return 0;
}

static u64 geology_core_sample_hash(const geology_fixture* fixture,
                                    const dom_domain_point* origin,
                                    const dom_domain_point* direction,
                                    q16_16 length,
                                    u32 steps,
                                    u32 budget_max,
                                    int* out_ok)
{
    dom_geology_domain domain;
    u64 hash = 14695981039346656037ULL;
    q16_16 step_len = 0;
    if (out_ok) {
        *out_ok = 0;
    }
    if (!fixture || !origin || !direction) {
        return 0;
    }
    geology_domain_init_from_fixture(fixture, &domain);
    if (steps == 0u) {
        steps = 1u;
    }
    if (steps > 1u) {
        step_len = (q16_16)((i64)length / (i64)(steps - 1u));
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_geology_sample sample;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));
        dom_domain_budget_init(&budget, budget_max);
        if (dom_geology_sample_query(&domain, &p, &budget, &sample) != 0) {
            dom_geology_domain_free(&domain);
            return 0;
        }
        hash = geology_hash_u32(hash, sample.strata_layer_id);
        hash = geology_hash_i32(hash, sample.hardness);
        hash = geology_hash_i32(hash, sample.fracture_risk);
        hash = geology_hash_u32(hash, sample.flags);
        for (u32 r = 0u; r < sample.resource_count; ++r) {
            hash = geology_hash_i32(hash, sample.resource_density[r]);
        }
    }
    dom_geology_domain_free(&domain);
    if (out_ok) {
        *out_ok = 1;
    }
    return hash;
}

static int geology_run_diff(const geology_fixture* fixture_a,
                            const geology_fixture* fixture_b,
                            const dom_domain_point* origin,
                            const dom_domain_point* direction,
                            q16_16 length,
                            u32 steps,
                            u32 budget_max)
{
    int ok_a = 0;
    int ok_b = 0;
    u64 hash_a = geology_core_sample_hash(fixture_a, origin, direction, length, steps, budget_max, &ok_a);
    u64 hash_b = geology_core_sample_hash(fixture_b, origin, direction, length, steps, budget_max, &ok_b);
    if (!ok_a || !ok_b) {
        return 1;
    }
    printf("%s\n", GEOLOGY_DIFF_HEADER);
    printf("fixture_a=%s\n", fixture_a->fixture_id);
    printf("fixture_b=%s\n", fixture_b->fixture_id);
    printf("hash_a=%llu\n", (unsigned long long)hash_a);
    printf("hash_b=%llu\n", (unsigned long long)hash_b);
    printf("equal=%u\n", (unsigned int)(hash_a == hash_b ? 1u : 0u));
    return 0;
}

static int geology_build_tile_desc(const dom_geology_domain* domain,
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

static int geology_run_collapse(const geology_fixture* fixture,
                                const dom_domain_point* point,
                                u32 budget_max)
{
    dom_geology_domain domain;
    dom_domain_tile_desc desc;
    dom_domain_budget budget;
    dom_geology_sample inside;
    dom_geology_sample outside;
    dom_domain_point outside_point;
    u32 count_before;
    u32 count_after;
    u32 count_final;

    geology_domain_init_from_fixture(fixture, &domain);
    if (!geology_build_tile_desc(&domain, point, DOM_DOMAIN_RES_COARSE, &desc)) {
        dom_geology_domain_free(&domain);
        return 1;
    }
    count_before = dom_geology_domain_capsule_count(&domain);
    (void)dom_geology_domain_collapse_tile(&domain, &desc);
    count_after = dom_geology_domain_capsule_count(&domain);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_geology_sample_query(&domain, point, &budget, &inside);

    outside_point = *point;
    outside_point.x = d_q16_16_add(outside_point.x, d_q16_16_mul(domain.policy.tile_size, d_q16_16_from_int(2)));
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_geology_sample_query(&domain, &outside_point, &budget, &outside);

    (void)dom_geology_domain_expand_tile(&domain, desc.tile_id);
    count_final = dom_geology_domain_capsule_count(&domain);

    printf("%s\n", GEOLOGY_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", GEOLOGY_PROVIDER_CHAIN);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);
    printf("capsule_count_final=%u\n", (unsigned int)count_final);
    printf("tile_id=%llu\n", (unsigned long long)desc.tile_id);
    printf("inside_resolution=%u\n", (unsigned int)inside.meta.resolution);
    printf("outside_resolution=%u\n", (unsigned int)outside.meta.resolution);
    printf("inside_flags=%u\n", (unsigned int)inside.flags);
    printf("outside_flags=%u\n", (unsigned int)outside.flags);

    dom_geology_domain_free(&domain);
    return 0;
}

static void geology_usage(void)
{
    printf("dom_tool_geology commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --pos x,y,z [--budget N]\n");
    printf("  core-sample --fixture <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--budget N] [--inactive N] [--collapsed 0|1]\n");
    printf("  map --fixture <path> [--center-latlon lat,lon] [--span S] [--dim N] [--budget N]\n");
    printf("  slice --fixture <path> --resource <id> --center x,y,z --radius R [--dim N] [--axis xy|xz|yz] [--budget N]\n");
    printf("  diff --fixture-a <path> --fixture-b <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--budget N]\n");
    printf("  collapse --fixture <path> --pos x,y,z [--budget N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        geology_usage();
        return 2;
    }
    cmd = argv[1];

    if (strcmp(cmd, "diff") == 0) {
        const char* fixture_a_path = geology_find_arg(argc, argv, "--fixture-a");
        const char* fixture_b_path = geology_find_arg(argc, argv, "--fixture-b");
        geology_fixture fixture_a;
        geology_fixture fixture_b;
        dom_domain_point origin;
        dom_domain_point direction;
        q16_16 length = d_q16_16_from_int(64);
        u32 steps = geology_find_arg_u32(argc, argv, "--steps", 16u);
        u32 budget_max;
        if (!fixture_a_path || !fixture_b_path ||
            !geology_fixture_load(fixture_a_path, &fixture_a) ||
            !geology_fixture_load(fixture_b_path, &fixture_b)) {
            fprintf(stderr, "geology: missing or invalid --fixture-a/--fixture-b\n");
            return 2;
        }
        if (!geology_parse_arg_point(argc, argv, "--origin", &origin) ||
            !geology_parse_arg_point(argc, argv, "--dir", &direction)) {
            fprintf(stderr, "geology: missing --origin or --dir\n");
            return 2;
        }
        if (!geology_parse_q16(geology_find_arg(argc, argv, "--length"), &length)) {
            length = d_q16_16_from_int(64);
        }
        budget_max = geology_find_arg_u32(argc, argv, "--budget", fixture_a.policy.cost_medium);
        return geology_run_diff(&fixture_a, &fixture_b, &origin, &direction, length, steps, budget_max);
    }

    {
        const char* fixture_path = geology_find_arg(argc, argv, "--fixture");
        geology_fixture fixture;
        if (!fixture_path || !geology_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "geology: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return geology_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            dom_domain_point point;
            u32 budget_max = geology_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (!geology_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "geology: missing --pos\n");
                return 2;
            }
            return geology_run_inspect(&fixture, &point, budget_max);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_domain_point origin;
            dom_domain_point direction;
            q16_16 length = d_q16_16_from_int(64);
            u32 steps = geology_find_arg_u32(argc, argv, "--steps", 16u);
            u32 budget_max = geology_find_arg_u32(argc, argv, "--budget",
                                                  fixture.policy.cost_medium + fixture.policy.tile_build_cost_medium);
            u32 inactive = geology_find_arg_u32(argc, argv, "--inactive", 0u);
            u32 collapsed = geology_find_arg_u32(argc, argv, "--collapsed", 0u);
            if (!geology_parse_arg_point(argc, argv, "--origin", &origin) ||
                !geology_parse_arg_point(argc, argv, "--dir", &direction)) {
                fprintf(stderr, "geology: missing --origin or --dir\n");
                return 2;
            }
            if (!geology_parse_q16(geology_find_arg(argc, argv, "--length"), &length)) {
                length = d_q16_16_from_int(64);
            }
            return geology_run_core_sample(&fixture, &origin, &direction, length, steps, budget_max, inactive,
                                           collapsed ? 1 : 0);
        }

        if (strcmp(cmd, "map") == 0) {
            q16_16 center_lat = 0;
            q16_16 center_lon = 0;
            q16_16 span = d_q16_16_from_double(0.1);
            u32 dim = geology_find_arg_u32(argc, argv, "--dim", 8u);
            u32 budget_max = geology_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            const char* center_text = geology_find_arg(argc, argv, "--center-latlon");
            if (center_text) {
                geology_parse_pair_q16(center_text, &center_lat, &center_lon);
            }
            if (!geology_parse_q16(geology_find_arg(argc, argv, "--span"), &span)) {
                span = d_q16_16_from_double(0.1);
            }
            return geology_run_map(&fixture, center_lat, center_lon, span, dim, budget_max);
        }

        if (strcmp(cmd, "slice") == 0) {
            dom_domain_point center;
            q16_16 radius;
            u32 dim = geology_find_arg_u32(argc, argv, "--dim", 8u);
            u32 budget_max = geology_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            const char* resource_id = geology_find_arg(argc, argv, "--resource");
            const char* axis = geology_find_arg(argc, argv, "--axis");
            u32 resource_index = 0u;
            if (!resource_id || !geology_find_resource_index(&fixture, resource_id, &resource_index)) {
                fprintf(stderr, "geology: invalid --resource\n");
                return 2;
            }
            if (!geology_parse_arg_point(argc, argv, "--center", &center)) {
                fprintf(stderr, "geology: missing --center\n");
                return 2;
            }
            if (!geology_parse_q16(geology_find_arg(argc, argv, "--radius"), &radius)) {
                fprintf(stderr, "geology: missing --radius\n");
                return 2;
            }
            return geology_run_slice(&fixture, &center, radius, dim, budget_max, resource_index, axis);
        }

        if (strcmp(cmd, "collapse") == 0) {
            dom_domain_point point;
            u32 budget_max = geology_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!geology_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "geology: missing --pos\n");
                return 2;
            }
            return geology_run_collapse(&fixture, &point, budget_max);
        }
    }

    geology_usage();
    return 2;
}
