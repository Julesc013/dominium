/*
FILE: tools/terrain/terrain_cli.cpp
MODULE: Dominium
PURPOSE: Terrain fixture CLI for deterministic terrain geometry checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/world/terrain_mesh.h"
#include "domino/world/terrain_surface.h"

#define TERRAIN_FIXTURE_HEADER "DOMINIUM_TERRAIN_FIXTURE_V1"
#define TERRAIN_NAV_HEADER "DOMINIUM_TERRAIN_NAV_V1"

#define TERRAIN_INSPECT_HEADER "DOMINIUM_TERRAIN_INSPECT_V1"
#define TERRAIN_WALK_HEADER "DOMINIUM_TERRAIN_WALK_V1"
#define TERRAIN_RENDER_HEADER "DOMINIUM_TERRAIN_RENDER_V1"
#define TERRAIN_COLLAPSE_HEADER "DOMINIUM_TERRAIN_COLLAPSE_V1"

#define TERRAIN_PROVIDER_CHAIN "procedural_base"

#define TERRAIN_MAX_POINTS 512u
#define TERRAIN_LINE_MAX 512u

typedef struct terrain_nav {
    dom_domain_point points[TERRAIN_MAX_POINTS];
    u32 count;
} terrain_nav;

typedef struct terrain_fixture {
    char fixture_id[96];
    dom_terrain_surface_desc desc;
    dom_domain_policy policy;
    u32 cache_capacity;
    u32 policy_set;
} terrain_fixture;

static u64 terrain_hash_u64(u64 h, u64 v)
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

static u64 terrain_hash_u32(u64 h, u32 v)
{
    return terrain_hash_u64(h, (u64)v);
}

static u64 terrain_hash_i32(u64 h, i32 v)
{
    return terrain_hash_u64(h, (u64)(u32)v);
}

static char* terrain_trim(char* text)
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

static int terrain_parse_u32(const char* text, u32* out_value)
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

static int terrain_parse_u64(const char* text, u64* out_value)
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

static int terrain_parse_q16(const char* text, q16_16* out_value)
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

static int terrain_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[TERRAIN_LINE_MAX];
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
    if (!terrain_parse_q16(terrain_trim(first), a)) return 0;
    if (!terrain_parse_q16(terrain_trim(second), b)) return 0;
    if (!terrain_parse_q16(terrain_trim(third), c)) return 0;
    return 1;
}

static int terrain_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!terrain_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 terrain_parse_resolution(const char* text)
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

static void terrain_fixture_init(terrain_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_terrain_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->cache_capacity = 128u;
    fixture->policy_set = 0u;
    strncpy(fixture->fixture_id, "terrain.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
    fixture->desc.domain_id = 1u;
    fixture->desc.world_seed = 1u;
}

static int terrain_fixture_apply(terrain_fixture* fixture, const char* key, const char* value)
{
    if (!fixture || !key || !value) {
        return 0;
    }
    if (strcmp(key, "fixture_id") == 0) {
        strncpy(fixture->fixture_id, value, sizeof(fixture->fixture_id) - 1);
        fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
        return 1;
    }
    if (strcmp(key, "world_seed") == 0) {
        return terrain_parse_u64(value, &fixture->desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return terrain_parse_u64(value, &fixture->desc.domain_id);
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
        return terrain_parse_q16(value, &fixture->desc.shape.radius_equatorial);
    }
    if (strcmp(key, "radius_polar") == 0) {
        return terrain_parse_q16(value, &fixture->desc.shape.radius_polar);
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        return terrain_parse_q16(value, &fixture->desc.shape.slab_half_extent);
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        return terrain_parse_q16(value, &fixture->desc.shape.slab_half_thickness);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return terrain_parse_q16(value, &fixture->desc.meters_per_unit);
    }
    if (strcmp(key, "noise_seed") == 0) {
        return terrain_parse_u64(value, &fixture->desc.noise.seed);
    }
    if (strcmp(key, "noise_amplitude") == 0) {
        return terrain_parse_q16(value, &fixture->desc.noise.amplitude);
    }
    if (strcmp(key, "noise_cell_size") == 0) {
        return terrain_parse_q16(value, &fixture->desc.noise.cell_size);
    }
    if (strcmp(key, "material_primary") == 0) {
        return terrain_parse_u32(value, &fixture->desc.material_primary);
    }
    if (strcmp(key, "roughness_base") == 0) {
        return terrain_parse_q16(value, &fixture->desc.roughness_base);
    }
    if (strcmp(key, "travel_cost_base") == 0) {
        return terrain_parse_q16(value, &fixture->desc.travel_cost_base);
    }
    if (strcmp(key, "travel_cost_slope_scale") == 0) {
        return terrain_parse_q16(value, &fixture->desc.travel_cost_slope_scale);
    }
    if (strcmp(key, "travel_cost_roughness_scale") == 0) {
        return terrain_parse_q16(value, &fixture->desc.travel_cost_roughness_scale);
    }
    if (strcmp(key, "walkable_max_slope") == 0) {
        return terrain_parse_q16(value, &fixture->desc.walkable_max_slope);
    }
    if (strcmp(key, "walkable_max_slope_deg") == 0) {
        char* end = 0;
        double deg = strtod(value, &end);
        if (!end || *end != '\0') {
            return 0;
        }
        fixture->desc.walkable_max_slope = d_q16_16_from_double(tan(deg * 3.14159265358979323846 / 180.0));
        return 1;
    }
    if (strcmp(key, "cache_capacity") == 0) {
        return terrain_parse_u32(value, &fixture->cache_capacity);
    }
    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_q16(value, &fixture->policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->policy.max_resolution = terrain_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_q16(value, &fixture->policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return terrain_parse_u32(value, &fixture->policy.max_ray_steps);
    }
    return 0;
}

static int terrain_fixture_load(const char* path, terrain_fixture* out_fixture)
{
    FILE* file;
    char line[TERRAIN_LINE_MAX];
    int header_ok = 0;
    terrain_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    terrain_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = terrain_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, TERRAIN_FIXTURE_HEADER) != 0) {
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
        terrain_fixture_apply(&fixture, terrain_trim(text), terrain_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static void terrain_nav_init(terrain_nav* nav)
{
    if (!nav) {
        return;
    }
    nav->count = 0u;
}

static int terrain_nav_add(terrain_nav* nav, const dom_domain_point* point)
{
    if (!nav || !point || nav->count >= TERRAIN_MAX_POINTS) {
        return 0;
    }
    nav->points[nav->count++] = *point;
    return 1;
}

static int terrain_nav_add_latlon(terrain_nav* nav,
                                  const dom_terrain_shape_desc* shape,
                                  q16_16 lat_turns,
                                  q16_16 lon_turns,
                                  q16_16 altitude)
{
    dom_domain_point point;
    if (!nav || !shape) {
        return 0;
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        q16_16 span = d_q16_16_mul(shape->slab_half_extent, d_q16_16_from_int(2));
        point.x = d_q16_16_mul(lon_turns, span);
        point.y = d_q16_16_mul(lat_turns, span);
        point.z = altitude;
    } else {
        point = dom_terrain_latlon_to_local(shape, lat_turns, lon_turns, altitude);
    }
    return terrain_nav_add(nav, &point);
}

static int terrain_nav_load(const char* path,
                            const dom_terrain_shape_desc* shape,
                            terrain_nav* out_nav)
{
    FILE* file;
    char line[TERRAIN_LINE_MAX];
    int header_ok = 0;
    terrain_nav nav;
    if (!path || !shape || !out_nav) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    terrain_nav_init(&nav);
    while (fgets(line, sizeof(line), file)) {
        char* text = terrain_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, TERRAIN_NAV_HEADER) != 0) {
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
        text = terrain_trim(text);
        eq = terrain_trim(eq);
        if (strcmp(text, "pos") == 0) {
            dom_domain_point p;
            if (terrain_parse_point(eq, &p)) {
                terrain_nav_add(&nav, &p);
            }
            continue;
        }
        if (strcmp(text, "latlon") == 0) {
            q16_16 lat;
            q16_16 lon;
            q16_16 alt;
            if (terrain_parse_triplet_q16(eq, &lat, &lon, &alt)) {
                terrain_nav_add_latlon(&nav, shape, lat, lon, alt);
            }
            continue;
        }
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    if (nav.count == 0u) {
        return 0;
    }
    *out_nav = nav;
    return 1;
}

static i32 terrain_floor_div_q16(q16_16 value, q16_16 denom)
{
    i64 v = (i64)value;
    i64 d = (i64)denom;
    i64 q;
    if (d == 0) {
        return 0;
    }
    if (v >= 0) {
        return (i32)(v / d);
    }
    q = (-v) / d;
    if ((-v) % d) {
        q += 1;
    }
    return (i32)(-q);
}

static void terrain_make_tile_bounds(const dom_domain_aabb* bounds,
                                     q16_16 tile_size,
                                     i32 tx,
                                     i32 ty,
                                     i32 tz,
                                     dom_domain_aabb* out_bounds)
{
    dom_domain_point minp;
    dom_domain_point maxp;
    minp.x = (q16_16)(bounds->min.x + (q16_16)((i64)tx * (i64)tile_size));
    minp.y = (q16_16)(bounds->min.y + (q16_16)((i64)ty * (i64)tile_size));
    minp.z = (q16_16)(bounds->min.z + (q16_16)((i64)tz * (i64)tile_size));

    maxp.x = (q16_16)(minp.x + tile_size);
    maxp.y = (q16_16)(minp.y + tile_size);
    maxp.z = (q16_16)(minp.z + tile_size);

    if (maxp.x > bounds->max.x) maxp.x = bounds->max.x;
    if (maxp.y > bounds->max.y) maxp.y = bounds->max.y;
    if (maxp.z > bounds->max.z) maxp.z = bounds->max.z;

    if (minp.x < bounds->min.x) minp.x = bounds->min.x;
    if (minp.y < bounds->min.y) minp.y = bounds->min.y;
    if (minp.z < bounds->min.z) minp.z = bounds->min.z;

    out_bounds->min = minp;
    out_bounds->max = maxp;
}

static void terrain_pick_outside_point(const dom_domain_aabb* tile_bounds,
                                       const dom_domain_aabb* domain_bounds,
                                       const dom_domain_point* origin,
                                       dom_domain_point* out_point)
{
    q16_16 step;
    if (!tile_bounds || !domain_bounds || !origin || !out_point) {
        return;
    }
    step = d_q16_16_from_int(1);
    *out_point = *origin;

    if (d_q16_16_add(tile_bounds->max.x, step) <= domain_bounds->max.x) {
        out_point->x = d_q16_16_add(tile_bounds->max.x, step);
        return;
    }
    if (d_q16_16_sub(tile_bounds->min.x, step) >= domain_bounds->min.x) {
        out_point->x = d_q16_16_sub(tile_bounds->min.x, step);
        return;
    }
    if (d_q16_16_add(tile_bounds->max.y, step) <= domain_bounds->max.y) {
        out_point->y = d_q16_16_add(tile_bounds->max.y, step);
        return;
    }
    if (d_q16_16_sub(tile_bounds->min.y, step) >= domain_bounds->min.y) {
        out_point->y = d_q16_16_sub(tile_bounds->min.y, step);
        return;
    }
    if (d_q16_16_add(tile_bounds->max.z, step) <= domain_bounds->max.z) {
        out_point->z = d_q16_16_add(tile_bounds->max.z, step);
        return;
    }
    if (d_q16_16_sub(tile_bounds->min.z, step) >= domain_bounds->min.z) {
        out_point->z = d_q16_16_sub(tile_bounds->min.z, step);
        return;
    }
}

static int terrain_build_tile_desc(const dom_terrain_domain* domain,
                                   const dom_domain_point* point,
                                   u32 resolution,
                                   dom_domain_tile_desc* out_desc)
{
    const dom_domain_sdf_source* source;
    q16_16 tile_size;
    i32 tx;
    i32 ty;
    i32 tz;
    if (!domain || !point || !out_desc) {
        return 0;
    }
    source = dom_terrain_surface_sdf(&domain->surface);
    if (!source) {
        return 0;
    }
    tile_size = domain->volume.policy.tile_size;
    if (tile_size <= 0) {
        return 0;
    }
    tx = terrain_floor_div_q16((q16_16)(point->x - source->bounds.min.x), tile_size);
    ty = terrain_floor_div_q16((q16_16)(point->y - source->bounds.min.y), tile_size);
    tz = terrain_floor_div_q16((q16_16)(point->z - source->bounds.min.z), tile_size);
    dom_domain_tile_desc_init(out_desc);
    out_desc->resolution = resolution;
    out_desc->sample_dim = (resolution == DOM_DOMAIN_RES_FULL) ? domain->volume.policy.sample_dim_full
                        : (resolution == DOM_DOMAIN_RES_MEDIUM) ? domain->volume.policy.sample_dim_medium
                        : (resolution == DOM_DOMAIN_RES_COARSE) ? domain->volume.policy.sample_dim_coarse
                        : domain->volume.policy.sample_dim_coarse;
    out_desc->tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, resolution);
    out_desc->authoring_version = domain->volume.authoring_version;
    terrain_make_tile_bounds(&source->bounds, tile_size, tx, ty, tz, &out_desc->bounds);
    return 1;
}

static void terrain_domain_init_from_fixture(const terrain_fixture* fixture,
                                             dom_terrain_domain* out_domain)
{
    dom_terrain_domain_init(out_domain, &fixture->desc, fixture->cache_capacity);
    if (fixture->policy_set) {
        dom_terrain_domain_set_policy(out_domain, &fixture->policy);
    }
}

static const char* terrain_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 terrain_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = terrain_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && terrain_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static int terrain_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* value = terrain_find_arg(argc, argv, key);
    if (!value || !out_point) {
        return 0;
    }
    return terrain_parse_point(value, out_point);
}

static int terrain_run_inspect(const terrain_fixture* fixture,
                               const dom_domain_point* point,
                               u32 budget_max)
{
    dom_terrain_domain domain;
    dom_domain_budget budget;
    dom_terrain_sample sample;

    terrain_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    if (dom_terrain_sample_query(&domain, point, &budget, &sample) != 0) {
        dom_terrain_domain_free(&domain);
        return 1;
    }

    printf("%s\n", TERRAIN_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TERRAIN_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("phi_q16=%d\n", (int)sample.phi);
    printf("material_primary=%u\n", (unsigned int)sample.material_primary);
    printf("roughness_q16=%d\n", (int)sample.roughness);
    printf("slope_q16=%d\n", (int)sample.slope);
    printf("travel_cost_q16=%d\n", (int)sample.travel_cost);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("phi_unknown=%u\n", (unsigned int)((sample.flags & DOM_TERRAIN_SAMPLE_PHI_UNKNOWN) ? 1u : 0u));
    printf("fields_unknown=%u\n", (unsigned int)((sample.flags & DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN) ? 1u : 0u));
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_terrain_domain_free(&domain);
    return 0;
}

static int terrain_run_walk(const terrain_fixture* fixture,
                            const terrain_nav* nav,
                            u32 budget_max,
                            u32 inactive_count,
                            int collapse_tile)
{
    dom_terrain_domain domain;
    dom_terrain_domain* inactive = 0;
    u64 hash = 14695981039346656037ULL;
    u32 step_cost_min = 0xFFFFFFFFu;
    u32 step_cost_max = 0u;
    u64 cost_total = 0u;
    u32 fields_unknown = 0u;
    u32 phi_unknown = 0u;

    terrain_domain_init_from_fixture(fixture, &domain);

    if (inactive_count > 0u) {
        inactive = (dom_terrain_domain*)malloc(sizeof(dom_terrain_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                terrain_fixture temp = *fixture;
                temp.desc.domain_id = fixture->desc.domain_id + (u64)(i + 1u);
                terrain_domain_init_from_fixture(&temp, &inactive[i]);
                dom_terrain_domain_set_state(&inactive[i],
                                             DOM_DOMAIN_EXISTENCE_DECLARED,
                                             DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    if (collapse_tile && nav->count > 0u) {
        dom_domain_tile_desc desc;
        if (terrain_build_tile_desc(&domain, &nav->points[0], DOM_DOMAIN_RES_COARSE, &desc)) {
            (void)dom_terrain_domain_collapse_tile(&domain, &desc);
        }
    }

    for (u32 i = 0u; i < nav->count; ++i) {
        dom_domain_budget budget;
        dom_terrain_sample sample;
        dom_domain_budget_init(&budget, budget_max);
        if (dom_terrain_sample_query(&domain, &nav->points[i], &budget, &sample) != 0) {
            dom_terrain_domain_free(&domain);
            free(inactive);
            return 1;
        }
        cost_total += (u64)sample.meta.cost_units;
        if (sample.meta.cost_units < step_cost_min) step_cost_min = sample.meta.cost_units;
        if (sample.meta.cost_units > step_cost_max) step_cost_max = sample.meta.cost_units;
        if (sample.flags & DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN) fields_unknown += 1u;
        if (sample.flags & DOM_TERRAIN_SAMPLE_PHI_UNKNOWN) phi_unknown += 1u;

        hash = terrain_hash_i32(hash, sample.phi);
        hash = terrain_hash_u32(hash, sample.material_primary);
        hash = terrain_hash_i32(hash, sample.roughness);
        hash = terrain_hash_i32(hash, sample.slope);
        hash = terrain_hash_i32(hash, sample.travel_cost);
        hash = terrain_hash_u32(hash, sample.flags);
        hash = terrain_hash_u32(hash, sample.meta.status);
        hash = terrain_hash_u32(hash, sample.meta.resolution);
        hash = terrain_hash_u32(hash, sample.meta.confidence);
        hash = terrain_hash_u32(hash, sample.meta.refusal_reason);
    }

    if (step_cost_min == 0xFFFFFFFFu) {
        step_cost_min = 0u;
    }

    printf("%s\n", TERRAIN_WALK_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TERRAIN_PROVIDER_CHAIN);
    printf("steps=%u\n", (unsigned int)nav->count);
    printf("budget_max=%u\n", (unsigned int)budget_max);
    printf("cost_step_min=%u\n", (unsigned int)step_cost_min);
    printf("cost_step_max=%u\n", (unsigned int)step_cost_max);
    printf("cost_total=%llu\n", (unsigned long long)cost_total);
    printf("phi_unknown_steps=%u\n", (unsigned int)phi_unknown);
    printf("fields_unknown_steps=%u\n", (unsigned int)fields_unknown);
    printf("walk_hash=%llu\n", (unsigned long long)hash);
    printf("cache_entries=%u\n", (unsigned int)domain.cache.count);
    printf("capsule_count=%u\n", (unsigned int)dom_terrain_domain_capsule_count(&domain));

    dom_terrain_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_terrain_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int terrain_run_render(const terrain_fixture* fixture,
                              const dom_domain_point* center,
                              q16_16 radius,
                              u32 sample_dim)
{
    dom_terrain_domain domain;
    const dom_domain_sdf_source* source;
    dom_domain_aabb bounds;
    dom_domain_aabb view_bounds;
    q16_16 tile_size;
    i32 tx_min;
    i32 ty_min;
    i32 tz_min;
    i32 tx_max;
    i32 ty_max;
    i32 tz_max;
    u32 visible = 0u;
    u32 touched = 0u;
    u64 hash = 14695981039346656037ULL;
    u64 tri_total = 0u;
    u64 vert_total = 0u;

    terrain_domain_init_from_fixture(fixture, &domain);
    source = dom_terrain_surface_sdf(&domain.surface);
    if (!source) {
        dom_terrain_domain_free(&domain);
        return 1;
    }
    bounds = source->bounds;
    tile_size = domain.volume.policy.tile_size;
    if (tile_size <= 0) {
        tile_size = d_q16_16_from_int(64);
    }
    view_bounds.min.x = d_q16_16_sub(center->x, radius);
    view_bounds.min.y = d_q16_16_sub(center->y, radius);
    view_bounds.min.z = d_q16_16_sub(center->z, radius);
    view_bounds.max.x = d_q16_16_add(center->x, radius);
    view_bounds.max.y = d_q16_16_add(center->y, radius);
    view_bounds.max.z = d_q16_16_add(center->z, radius);

    tx_min = terrain_floor_div_q16((q16_16)(view_bounds.min.x - bounds.min.x), tile_size);
    ty_min = terrain_floor_div_q16((q16_16)(view_bounds.min.y - bounds.min.y), tile_size);
    tz_min = terrain_floor_div_q16((q16_16)(view_bounds.min.z - bounds.min.z), tile_size);
    tx_max = terrain_floor_div_q16((q16_16)(view_bounds.max.x - bounds.min.x), tile_size);
    ty_max = terrain_floor_div_q16((q16_16)(view_bounds.max.y - bounds.min.y), tile_size);
    tz_max = terrain_floor_div_q16((q16_16)(view_bounds.max.z - bounds.min.z), tile_size);

    for (i32 tz = tz_min; tz <= tz_max; ++tz) {
        for (i32 ty = ty_min; ty <= ty_max; ++ty) {
            for (i32 tx = tx_min; tx <= tx_max; ++tx) {
                dom_domain_aabb tile_bounds;
                dom_terrain_mesh_stats stats;
                u64 tile_id;
                terrain_make_tile_bounds(&bounds, tile_size, tx, ty, tz, &tile_bounds);
                if (tile_bounds.max.x < view_bounds.min.x || tile_bounds.min.x > view_bounds.max.x) continue;
                if (tile_bounds.max.y < view_bounds.min.y || tile_bounds.min.y > view_bounds.max.y) continue;
                if (tile_bounds.max.z < view_bounds.min.z || tile_bounds.min.z > view_bounds.max.z) continue;
                visible += 1u;
                tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, DOM_DOMAIN_RES_COARSE);
                if (dom_terrain_mesh_hash(&domain.surface, &tile_bounds, sample_dim, &stats) != 0) {
                    dom_terrain_domain_free(&domain);
                    return 1;
                }
                touched += 1u;
                tri_total += stats.triangle_count;
                vert_total += stats.vertex_count;
                hash = terrain_hash_u64(hash, tile_id);
                hash = terrain_hash_u64(hash, stats.hash);
            }
        }
    }

    printf("%s\n", TERRAIN_RENDER_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TERRAIN_PROVIDER_CHAIN);
    printf("visible_chunks=%u\n", (unsigned int)visible);
    printf("touched_chunks=%u\n", (unsigned int)touched);
    printf("sample_dim=%u\n", (unsigned int)sample_dim);
    printf("mesh_triangles=%llu\n", (unsigned long long)tri_total);
    printf("mesh_vertices=%llu\n", (unsigned long long)vert_total);
    printf("render_hash=%llu\n", (unsigned long long)hash);

    dom_terrain_domain_free(&domain);
    return 0;
}

static int terrain_run_collapse(const terrain_fixture* fixture,
                                const terrain_nav* nav,
                                u32 budget_max)
{
    dom_terrain_domain domain;
    dom_domain_tile_desc desc;
    dom_domain_budget budget;
    dom_terrain_sample inside;
    dom_terrain_sample outside;
    dom_domain_point outside_point;
    const dom_domain_sdf_source* source;
    u32 count_before;
    u32 count_after;
    u32 count_final;

    if (!nav || nav->count == 0u) {
        return 1;
    }

    terrain_domain_init_from_fixture(fixture, &domain);
    source = dom_terrain_surface_sdf(&domain.surface);
    if (!source) {
        dom_terrain_domain_free(&domain);
        return 1;
    }

    count_before = dom_terrain_domain_capsule_count(&domain);
    if (!terrain_build_tile_desc(&domain, &nav->points[0], DOM_DOMAIN_RES_COARSE, &desc)) {
        dom_terrain_domain_free(&domain);
        return 1;
    }
    (void)dom_terrain_domain_collapse_tile(&domain, &desc);
    count_after = dom_terrain_domain_capsule_count(&domain);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_terrain_sample_query(&domain, &nav->points[0], &budget, &inside);

    terrain_pick_outside_point(&desc.bounds, &source->bounds, &nav->points[0], &outside_point);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_terrain_sample_query(&domain, &outside_point, &budget, &outside);

    (void)dom_terrain_domain_expand_tile(&domain, desc.tile_id);
    count_final = dom_terrain_domain_capsule_count(&domain);

    printf("%s\n", TERRAIN_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TERRAIN_PROVIDER_CHAIN);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);
    printf("capsule_count_final=%u\n", (unsigned int)count_final);
    printf("tile_id=%llu\n", (unsigned long long)desc.tile_id);
    printf("inside_resolution=%u\n", (unsigned int)inside.meta.resolution);
    printf("outside_resolution=%u\n", (unsigned int)outside.meta.resolution);
    printf("inside_confidence=%u\n", (unsigned int)inside.meta.confidence);
    printf("outside_confidence=%u\n", (unsigned int)outside.meta.confidence);

    dom_terrain_domain_free(&domain);
    return 0;
}

static void terrain_usage(void)
{
    printf("dom_tool_terrain commands:\n");
    printf("  inspect --fixture <path> --pos x,y,z [--budget N]\n");
    printf("  inspect --fixture <path> --nav <path> [--index N] [--budget N]\n");
    printf("  walk --fixture <path> --nav <path> [--budget N] [--inactive N] [--collapsed 0|1]\n");
    printf("  render --fixture <path> --center x,y,z --radius R [--sample-dim N]\n");
    printf("  collapse --fixture <path> --nav <path> [--budget N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    const char* fixture_path;
    terrain_fixture fixture;
    if (argc < 2) {
        terrain_usage();
        return 2;
    }
    cmd = argv[1];
    fixture_path = terrain_find_arg(argc, argv, "--fixture");
    if (!fixture_path || !terrain_fixture_load(fixture_path, &fixture)) {
        fprintf(stderr, "terrain: missing or invalid --fixture\n");
        return 2;
    }

    if (strcmp(cmd, "inspect") == 0) {
        dom_domain_point point;
        const char* nav_path = terrain_find_arg(argc, argv, "--nav");
        u32 index = terrain_find_arg_u32(argc, argv, "--index", 0u);
        u32 budget_max = terrain_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
        if (nav_path) {
            terrain_nav nav;
            if (!terrain_nav_load(nav_path, &fixture.desc.shape, &nav) || nav.count == 0u) {
                fprintf(stderr, "terrain: invalid --nav\n");
                return 2;
            }
            if (index >= nav.count) {
                fprintf(stderr, "terrain: --index out of range\n");
                return 2;
            }
            point = nav.points[index];
        } else if (!terrain_parse_arg_point(argc, argv, "--pos", &point)) {
            fprintf(stderr, "terrain: missing --pos or --nav\n");
            return 2;
        }
        return terrain_run_inspect(&fixture, &point, budget_max);
    }

    if (strcmp(cmd, "walk") == 0) {
        const char* nav_path = terrain_find_arg(argc, argv, "--nav");
        u32 budget_max = terrain_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium + fixture.policy.tile_build_cost_medium);
        u32 inactive = terrain_find_arg_u32(argc, argv, "--inactive", 0u);
        u32 collapsed = terrain_find_arg_u32(argc, argv, "--collapsed", 0u);
        terrain_nav nav;
        if (!nav_path || !terrain_nav_load(nav_path, &fixture.desc.shape, &nav)) {
            fprintf(stderr, "terrain: invalid --nav\n");
            return 2;
        }
        return terrain_run_walk(&fixture, &nav, budget_max, inactive, collapsed ? 1 : 0);
    }

    if (strcmp(cmd, "render") == 0) {
        dom_domain_point center;
        q16_16 radius;
        u32 sample_dim = terrain_find_arg_u32(argc, argv, "--sample-dim", fixture.policy.sample_dim_coarse);
        if (!terrain_parse_arg_point(argc, argv, "--center", &center)) {
            fprintf(stderr, "terrain: missing --center\n");
            return 2;
        }
        if (!terrain_parse_q16(terrain_find_arg(argc, argv, "--radius"), &radius)) {
            fprintf(stderr, "terrain: missing --radius\n");
            return 2;
        }
        return terrain_run_render(&fixture, &center, radius, sample_dim);
    }

    if (strcmp(cmd, "collapse") == 0) {
        const char* nav_path = terrain_find_arg(argc, argv, "--nav");
        u32 budget_max = terrain_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
        terrain_nav nav;
        if (!nav_path || !terrain_nav_load(nav_path, &fixture.desc.shape, &nav)) {
            fprintf(stderr, "terrain: invalid --nav\n");
            return 2;
        }
        return terrain_run_collapse(&fixture, &nav, budget_max);
    }

    terrain_usage();
    return 2;
}
