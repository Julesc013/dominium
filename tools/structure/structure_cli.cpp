/*
FILE: tools/structure/structure_cli.cpp
MODULE: Dominium
PURPOSE: Structure fixture CLI for deterministic placement, collapse, and stress checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/structure_fields.h"

#define STRUCTURE_FIXTURE_HEADER "DOMINIUM_STRUCTURE_FIXTURE_V1"

#define STRUCTURE_VALIDATE_HEADER "DOMINIUM_STRUCTURE_VALIDATE_V1"
#define STRUCTURE_INSPECT_HEADER "DOMINIUM_STRUCTURE_INSPECT_V1"
#define STRUCTURE_CORE_SAMPLE_HEADER "DOMINIUM_STRUCTURE_CORE_SAMPLE_V1"
#define STRUCTURE_DIFF_HEADER "DOMINIUM_STRUCTURE_DIFF_V1"
#define STRUCTURE_COLLAPSE_HEADER "DOMINIUM_STRUCTURE_COLLAPSE_V1"
#define STRUCTURE_FAILURE_HEADER "DOMINIUM_STRUCTURE_FAILURE_V1"
#define STRUCTURE_RENDER_HEADER "DOMINIUM_STRUCTURE_RENDER_V1"

#define STRUCTURE_PROVIDER_CHAIN "terrain->geology->structure"

#define STRUCTURE_LINE_MAX 512u

typedef struct structure_fixture {
    char fixture_id[96];
    dom_structure_surface_desc desc;
    dom_domain_policy policy;
    u32 cache_capacity;
    u32 policy_set;
    char structure_ids[DOM_STRUCTURE_MAX_SPECS][64];
} structure_fixture;

static int structure_build_tile_desc(const dom_structure_domain* domain,
                                     const dom_domain_point* point,
                                     u32 resolution,
                                     dom_domain_tile_desc* out_desc);

static char* structure_trim(char* text)
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

static int structure_parse_u32(const char* text, u32* out_value)
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

static int structure_parse_u64(const char* text, u64* out_value)
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

static int structure_parse_q16(const char* text, q16_16* out_value)
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

static int structure_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[STRUCTURE_LINE_MAX];
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
    if (!structure_parse_q16(structure_trim(first), a)) return 0;
    if (!structure_parse_q16(structure_trim(second), b)) return 0;
    if (!structure_parse_q16(structure_trim(third), c)) return 0;
    return 1;
}

static int structure_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!structure_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 structure_parse_resolution(const char* text)
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

static q16_16 structure_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static i32 structure_floor_div_q16(q16_16 value, q16_16 denom)
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

static void structure_cell_coord(q16_16 cell_size,
                                 const dom_domain_point* point,
                                 i32* out_x,
                                 i32* out_y,
                                 i32* out_z)
{
    if (!point || !out_x || !out_y || !out_z) {
        return;
    }
    if (cell_size <= 0) {
        cell_size = d_q16_16_from_int(1);
    }
    *out_x = structure_floor_div_q16(point->x, cell_size);
    *out_y = structure_floor_div_q16(point->y, cell_size);
    *out_z = structure_floor_div_q16(point->z, cell_size);
}

static int structure_parse_indexed_key(const char* key,
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

static int structure_parse_anchor_kind(const char* value, u32* out_kind)
{
    if (!value || !out_kind) {
        return 0;
    }
    if (strcmp(value, "terrain") == 0) {
        *out_kind = DOM_STRUCTURE_ANCHOR_TERRAIN;
        return 1;
    }
    if (strcmp(value, "structure") == 0) {
        *out_kind = DOM_STRUCTURE_ANCHOR_STRUCTURE;
        return 1;
    }
    return structure_parse_u32(value, out_kind);
}

static void structure_spec_defaults(dom_structure_spec_desc* spec)
{
    if (!spec) {
        return;
    }
    memset(spec, 0, sizeof(*spec));
    spec->traits.stiffness = d_q16_16_from_double(0.3);
    spec->traits.density = d_q16_16_from_double(0.4);
    spec->traits.brittleness = d_q16_16_from_double(0.2);
    spec->load_capacity = d_q16_16_from_int(1);
    spec->anchor_count = 1u;
    spec->anchors[0].kind = DOM_STRUCTURE_ANCHOR_TERRAIN;
    spec->anchors[0].support_scale = d_q16_16_from_int(1);
    spec->gravity_scale = d_q16_16_from_int(1);
    spec->slope_max = d_q16_16_from_int(1);
    spec->maturity_tag = 0u;
}

static void structure_fixture_init(structure_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_structure_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->cache_capacity = 128u;
    fixture->policy_set = 0u;
    strncpy(fixture->fixture_id, "structure.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
    fixture->desc.cache_capacity = fixture->cache_capacity;
    for (u32 i = 0u; i < DOM_STRUCTURE_MAX_SPECS; ++i) {
        structure_spec_defaults(&fixture->desc.structures[i]);
    }
}

static int structure_fixture_apply_geo_layer(structure_fixture* fixture,
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
        layer->layer_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "thickness") == 0) {
        return structure_parse_q16(value, &layer->thickness);
    }
    if (strcmp(suffix, "hardness") == 0) {
        return structure_parse_q16(value, &layer->hardness);
    }
    if (strcmp(suffix, "fracture") == 0) {
        layer->has_fracture = 1u;
        return structure_parse_q16(value, &layer->fracture_risk);
    }
    return 0;
}

static int structure_fixture_apply_structure(structure_fixture* fixture,
                                             u32 index,
                                             const char* suffix,
                                             const char* value)
{
    dom_structure_spec_desc* spec;
    u32 anchor_index = 0u;
    const char* anchor_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STRUCTURE_MAX_SPECS) {
        return 0;
    }
    if (fixture->desc.structure_count <= index) {
        fixture->desc.structure_count = index + 1u;
    }
    spec = &fixture->desc.structures[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->structure_ids[index], value, sizeof(fixture->structure_ids[index]) - 1);
        fixture->structure_ids[index][sizeof(fixture->structure_ids[index]) - 1] = '\0';
        spec->structure_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "geometry") == 0) {
        spec->geometry_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "stiffness") == 0) {
        return structure_parse_q16(value, &spec->traits.stiffness);
    }
    if (strcmp(suffix, "density") == 0) {
        return structure_parse_q16(value, &spec->traits.density);
    }
    if (strcmp(suffix, "brittleness") == 0) {
        return structure_parse_q16(value, &spec->traits.brittleness);
    }
    if (strcmp(suffix, "load_capacity") == 0) {
        return structure_parse_q16(value, &spec->load_capacity);
    }
    if (strcmp(suffix, "gravity_scale") == 0) {
        return structure_parse_q16(value, &spec->gravity_scale);
    }
    if (strcmp(suffix, "slope_max") == 0) {
        return structure_parse_q16(value, &spec->slope_max);
    }
    if (strcmp(suffix, "anchor_count") == 0) {
        return structure_parse_u32(value, &spec->anchor_count);
    }
    if (strcmp(suffix, "maturity") == 0) {
        if (strcmp(value, "BOUNDED") == 0) {
            spec->maturity_tag = 1u;
            return 1;
        }
        if (strcmp(value, "STRUCTURAL") == 0) {
            spec->maturity_tag = 2u;
            return 1;
        }
        return structure_parse_u32(value, &spec->maturity_tag);
    }
    if (structure_parse_indexed_key(suffix, "anchor", &anchor_index, &anchor_suffix)) {
        if (anchor_index >= DOM_STRUCTURE_MAX_ANCHORS) {
            return 0;
        }
        if (spec->anchor_count <= anchor_index) {
            spec->anchor_count = anchor_index + 1u;
        }
        if (strcmp(anchor_suffix, "kind") == 0) {
            return structure_parse_anchor_kind(value, &spec->anchors[anchor_index].kind);
        }
        if (strcmp(anchor_suffix, "offset") == 0) {
            return structure_parse_triplet_q16(value,
                                               &spec->anchors[anchor_index].offset.x,
                                               &spec->anchors[anchor_index].offset.y,
                                               &spec->anchors[anchor_index].offset.z);
        }
        if (strcmp(anchor_suffix, "support_scale") == 0) {
            return structure_parse_q16(value, &spec->anchors[anchor_index].support_scale);
        }
        if (strcmp(anchor_suffix, "target_id") == 0) {
            spec->anchors[anchor_index].target_id = d_rng_hash_str32(value);
            return 1;
        }
    }
    return 0;
}

static int structure_fixture_apply_instance(structure_fixture* fixture,
                                            u32 index,
                                            const char* suffix,
                                            const char* value)
{
    dom_structure_instance* inst;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STRUCTURE_MAX_INSTANCES) {
        return 0;
    }
    if (fixture->desc.instance_count <= index) {
        fixture->desc.instance_count = index + 1u;
    }
    inst = &fixture->desc.instances[index];
    if (strcmp(suffix, "structure_id") == 0) {
        inst->structure_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "pos") == 0) {
        return structure_parse_triplet_q16(value, &inst->location.x, &inst->location.y, &inst->location.z);
    }
    if (strcmp(suffix, "integrity") == 0) {
        return structure_parse_q16(value, &inst->integrity);
    }
    if (strcmp(suffix, "reinforcement") == 0) {
        return structure_parse_q16(value, &inst->reinforcement);
    }
    if (strcmp(suffix, "flags") == 0) {
        return structure_parse_u32(value, &inst->flags);
    }
    return 0;
}

static int structure_fixture_apply(structure_fixture* fixture, const char* key, const char* value)
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
        if (structure_parse_u64(value, &fixture->desc.world_seed)) {
            fixture->desc.terrain_desc.world_seed = fixture->desc.world_seed;
            fixture->desc.geology_desc.world_seed = fixture->desc.world_seed;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "domain_id") == 0) {
        if (structure_parse_u64(value, &fixture->desc.domain_id)) {
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
        if (structure_parse_q16(value, &fixture->desc.shape.radius_equatorial)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "radius_polar") == 0) {
        if (structure_parse_q16(value, &fixture->desc.shape.radius_polar)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        if (structure_parse_q16(value, &fixture->desc.shape.slab_half_extent)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        if (structure_parse_q16(value, &fixture->desc.shape.slab_half_thickness)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        if (structure_parse_q16(value, &fixture->desc.meters_per_unit)) {
            fixture->desc.terrain_desc.meters_per_unit = fixture->desc.meters_per_unit;
            fixture->desc.geology_desc.meters_per_unit = fixture->desc.meters_per_unit;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "placement_cell_size") == 0) {
        return structure_parse_q16(value, &fixture->desc.placement_cell_size);
    }
    if (strcmp(key, "density_base") == 0) {
        return structure_parse_q16(value, &fixture->desc.density_base);
    }
    if (strcmp(key, "stress_check_period_ticks") == 0) {
        return structure_parse_u64(value, &fixture->desc.stress_check_period_ticks);
    }
    if (strcmp(key, "repair_period_ticks") == 0) {
        return structure_parse_u64(value, &fixture->desc.repair_period_ticks);
    }
    if (strcmp(key, "reinforce_period_ticks") == 0) {
        return structure_parse_u64(value, &fixture->desc.reinforce_period_ticks);
    }
    if (strcmp(key, "cache_capacity") == 0) {
        if (structure_parse_u32(value, &fixture->cache_capacity)) {
            fixture->desc.cache_capacity = fixture->cache_capacity;
            return 1;
        }
        return 0;
    }

    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_q16(value, &fixture->policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->policy.max_resolution = structure_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_q16(value, &fixture->policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return structure_parse_u32(value, &fixture->policy.max_ray_steps);
    }

    if (strcmp(key, "terrain_noise_seed") == 0) {
        return structure_parse_u64(value, &fixture->desc.terrain_desc.noise.seed);
    }
    if (strcmp(key, "terrain_noise_amplitude") == 0) {
        return structure_parse_q16(value, &fixture->desc.terrain_desc.noise.amplitude);
    }
    if (strcmp(key, "terrain_noise_cell_size") == 0) {
        return structure_parse_q16(value, &fixture->desc.terrain_desc.noise.cell_size);
    }
    if (strcmp(key, "terrain_roughness_base") == 0) {
        return structure_parse_q16(value, &fixture->desc.terrain_desc.roughness_base);
    }
    if (strcmp(key, "terrain_travel_cost_base") == 0) {
        return structure_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_base);
    }
    if (strcmp(key, "terrain_travel_cost_slope_scale") == 0) {
        return structure_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_slope_scale);
    }
    if (strcmp(key, "terrain_travel_cost_roughness_scale") == 0) {
        return structure_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_roughness_scale);
    }
    if (strcmp(key, "terrain_material_primary") == 0) {
        return structure_parse_u32(value, &fixture->desc.terrain_desc.material_primary);
    }
    if (strcmp(key, "terrain_walkable_max_slope") == 0) {
        return structure_parse_q16(value, &fixture->desc.terrain_desc.walkable_max_slope);
    }

    if (strcmp(key, "geo_layer_count") == 0) {
        return structure_parse_u32(value, &fixture->desc.geology_desc.layer_count);
    }
    if (strcmp(key, "geo_default_hardness") == 0) {
        return structure_parse_q16(value, &fixture->desc.geology_desc.default_hardness);
    }
    if (strcmp(key, "geo_default_fracture_risk") == 0) {
        return structure_parse_q16(value, &fixture->desc.geology_desc.default_fracture_risk);
    }

    if (strcmp(key, "structure_count") == 0) {
        return structure_parse_u32(value, &fixture->desc.structure_count);
    }
    if (strcmp(key, "instance_count") == 0) {
        return structure_parse_u32(value, &fixture->desc.instance_count);
    }

    if (structure_parse_indexed_key(key, "geo_layer", &index, &suffix)) {
        return structure_fixture_apply_geo_layer(fixture, index, suffix, value);
    }
    if (structure_parse_indexed_key(key, "structure", &index, &suffix)) {
        return structure_fixture_apply_structure(fixture, index, suffix, value);
    }
    if (structure_parse_indexed_key(key, "instance", &index, &suffix)) {
        return structure_fixture_apply_instance(fixture, index, suffix, value);
    }
    return 0;
}

static int structure_fixture_load(const char* path, structure_fixture* out_fixture)
{
    FILE* file;
    char line[STRUCTURE_LINE_MAX];
    int header_ok = 0;
    structure_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    structure_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = structure_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, STRUCTURE_FIXTURE_HEADER) != 0) {
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
        structure_fixture_apply(&fixture, structure_trim(text), structure_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static void structure_domain_init_from_fixture(const structure_fixture* fixture,
                                               dom_structure_domain* out_domain)
{
    dom_structure_domain_init(out_domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_structure_domain_set_policy(out_domain, &fixture->policy);
    }
}

static const char* structure_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 structure_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = structure_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && structure_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 structure_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = structure_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && structure_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static int structure_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* value = structure_find_arg(argc, argv, key);
    if (!value || !out_point) {
        return 0;
    }
    return structure_parse_point(value, out_point);
}

static int structure_run_validate(const structure_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    printf("%s\n", STRUCTURE_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STRUCTURE_PROVIDER_CHAIN);
    printf("structure_count=%u\n", (unsigned int)fixture->desc.structure_count);
    printf("instance_count=%u\n", (unsigned int)fixture->desc.instance_count);
    return 0;
}

static int structure_run_inspect(const structure_fixture* fixture,
                                 const dom_domain_point* point,
                                 u64 tick,
                                 u32 budget_max)
{
    dom_structure_domain domain;
    dom_domain_budget budget;
    dom_structure_sample sample;
    u32 fields_unknown;
    u32 collapsed;
    u32 unstable;
    if (!fixture || !point) {
        return 1;
    }
    structure_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    if (dom_structure_sample_query(&domain, point, tick, &budget, &sample) != 0) {
        dom_structure_domain_free(&domain);
        return 1;
    }
    fields_unknown = (sample.flags & DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN) ? 1u : 0u;
    collapsed = (sample.flags & DOM_STRUCTURE_SAMPLE_COLLAPSED) ? 1u : 0u;
    unstable = (sample.flags & DOM_STRUCTURE_SAMPLE_UNSTABLE) ? 1u : 0u;
    printf("%s\n", STRUCTURE_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STRUCTURE_PROVIDER_CHAIN);
    printf("pos_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("tick=%llu\n", (unsigned long long)tick);
    printf("structure_present=%u\n", (unsigned int)((sample.flags & DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT) ? 1u : 0u));
    printf("structure_id=%u\n", (unsigned int)sample.structure_id);
    printf("support_capacity_q16=%d\n", (int)sample.support_capacity);
    printf("applied_stress_q16=%d\n", (int)sample.applied_stress);
    printf("stress_ratio_q16=%d\n", (int)sample.stress_ratio);
    printf("integrity_q16=%d\n", (int)sample.integrity);
    printf("anchor_required_mask=0x%08x\n", (unsigned int)sample.anchor_required_mask);
    printf("anchor_supported_mask=0x%08x\n", (unsigned int)sample.anchor_supported_mask);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("fields_unknown=%u\n", (unsigned int)fields_unknown);
    printf("collapsed=%u\n", (unsigned int)collapsed);
    printf("unstable=%u\n", (unsigned int)unstable);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);
    dom_structure_domain_free(&domain);
    return 0;
}

static u64 structure_hash_u64(u64 h, u64 v)
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

static u64 structure_hash_u32(u64 h, u32 v)
{
    return structure_hash_u64(h, (u64)v);
}

static u64 structure_hash_i32(u64 h, i32 v)
{
    return structure_hash_u64(h, (u64)(u32)v);
}

static u64 structure_core_sample_hash(const structure_fixture* fixture,
                                      const dom_domain_point* origin,
                                      const dom_domain_point* direction,
                                      q16_16 length,
                                      u32 steps,
                                      u64 start_tick,
                                      u64 step_ticks,
                                      u32 budget_max,
                                      u32 inactive,
                                      int collapse,
                                      u32* out_unknown_steps,
                                      u32* out_cost_max,
                                      u32* out_capsule_count,
                                      int* out_ok)
{
    dom_structure_domain domain;
    dom_structure_domain* inactive_domains = 0;
    u64 hash = 14695981039346656037ULL;
    q16_16 step_len = 0;
    u32 unknown_steps = 0u;
    u32 cost_max = 0u;
    u32 capsule_count = 0u;
    if (out_ok) {
        *out_ok = 0;
    }
    if (!fixture || !origin || !direction) {
        return 0;
    }
    structure_domain_init_from_fixture(fixture, &domain);
    if (inactive > 0u) {
        inactive_domains = (dom_structure_domain*)calloc(inactive, sizeof(dom_structure_domain));
        if (!inactive_domains) {
            dom_structure_domain_free(&domain);
            return 0;
        }
        for (u32 i = 0u; i < inactive; ++i) {
            structure_domain_init_from_fixture(fixture, &inactive_domains[i]);
            dom_structure_domain_set_state(&inactive_domains[i],
                                           DOM_DOMAIN_EXISTENCE_DECLARED,
                                           DOM_DOMAIN_ARCHIVAL_LIVE);
        }
    }
    if (steps == 0u) {
        steps = 1u;
    }
    if (steps > 1u) {
        step_len = (q16_16)((i64)length / (i64)(steps - 1u));
    }
    if (collapse) {
        dom_domain_tile_desc desc;
        if (structure_build_tile_desc(&domain, origin, DOM_DOMAIN_RES_COARSE, &desc)) {
            (void)dom_structure_domain_collapse_tile(&domain, &desc, start_tick);
        }
        capsule_count = dom_structure_domain_capsule_count(&domain);
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_structure_sample sample;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        u64 tick = start_tick + (step_ticks * (u64)i);
        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));
        dom_domain_budget_init(&budget, budget_max);
        if (dom_structure_sample_query(&domain, &p, tick, &budget, &sample) != 0) {
            dom_structure_domain_free(&domain);
            if (inactive_domains) {
                for (u32 j = 0u; j < inactive; ++j) {
                    dom_structure_domain_free(&inactive_domains[j]);
                }
                free(inactive_domains);
            }
            return 0;
        }
        if (sample.flags & DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN) {
            unknown_steps += 1u;
        }
        if (sample.meta.cost_units > cost_max) {
            cost_max = sample.meta.cost_units;
        }
        hash = structure_hash_i32(hash, sample.support_capacity);
        hash = structure_hash_i32(hash, sample.applied_stress);
        hash = structure_hash_i32(hash, sample.stress_ratio);
        hash = structure_hash_i32(hash, sample.integrity);
        hash = structure_hash_u32(hash, sample.structure_id);
        hash = structure_hash_u32(hash, sample.anchor_supported_mask);
        hash = structure_hash_u32(hash, sample.flags);
    }
    dom_structure_domain_free(&domain);
    if (inactive_domains) {
        for (u32 i = 0u; i < inactive; ++i) {
            dom_structure_domain_free(&inactive_domains[i]);
        }
        free(inactive_domains);
    }
    if (out_unknown_steps) {
        *out_unknown_steps = unknown_steps;
    }
    if (out_cost_max) {
        *out_cost_max = cost_max;
    }
    if (out_capsule_count) {
        *out_capsule_count = capsule_count;
    }
    if (out_ok) {
        *out_ok = 1;
    }
    return hash;
}

static int structure_run_core_sample(const structure_fixture* fixture,
                                     const dom_domain_point* origin,
                                     const dom_domain_point* direction,
                                     q16_16 length,
                                     u32 steps,
                                     u64 start_tick,
                                     u64 step_ticks,
                                     u32 budget_max,
                                     u32 inactive,
                                     int collapse)
{
    u32 unknown_steps = 0u;
    u32 cost_max = 0u;
    u32 capsule_count = 0u;
    int ok = 0;
    u64 hash = structure_core_sample_hash(fixture, origin, direction, length, steps,
                                          start_tick, step_ticks, budget_max,
                                          inactive, collapse,
                                          &unknown_steps, &cost_max, &capsule_count, &ok);
    if (!ok) {
        return 1;
    }
    printf("%s\n", STRUCTURE_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STRUCTURE_PROVIDER_CHAIN);
    printf("steps=%u\n", (unsigned int)steps);
    printf("start_tick=%llu\n", (unsigned long long)start_tick);
    printf("step_ticks=%llu\n", (unsigned long long)step_ticks);
    printf("budget_max=%u\n", (unsigned int)budget_max);
    printf("unknown_steps=%u\n", (unsigned int)unknown_steps);
    printf("cost_step_max=%u\n", (unsigned int)cost_max);
    printf("sample_hash=%llu\n", (unsigned long long)hash);
    printf("inactive_domains=%u\n", (unsigned int)inactive);
    printf("capsule_count=%u\n", (unsigned int)capsule_count);
    return 0;
}

static int structure_run_diff(const structure_fixture* fixture_a,
                              const structure_fixture* fixture_b,
                              const dom_domain_point* origin,
                              const dom_domain_point* direction,
                              q16_16 length,
                              u32 steps,
                              u64 start_tick,
                              u64 step_ticks,
                              u32 budget_max)
{
    int ok_a = 0;
    int ok_b = 0;
    u64 hash_a = structure_core_sample_hash(fixture_a, origin, direction, length, steps,
                                            start_tick, step_ticks, budget_max,
                                            0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_a);
    u64 hash_b = structure_core_sample_hash(fixture_b, origin, direction, length, steps,
                                            start_tick, step_ticks, budget_max,
                                            0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_b);
    if (!ok_a || !ok_b) {
        return 1;
    }
    printf("%s\n", STRUCTURE_DIFF_HEADER);
    printf("fixture_a=%s\n", fixture_a->fixture_id);
    printf("fixture_b=%s\n", fixture_b->fixture_id);
    printf("hash_a=%llu\n", (unsigned long long)hash_a);
    printf("hash_b=%llu\n", (unsigned long long)hash_b);
    printf("equal=%u\n", (unsigned int)(hash_a == hash_b ? 1u : 0u));
    return 0;
}

static int structure_build_tile_desc(const dom_structure_domain* domain,
                                     const dom_domain_point* point,
                                     u32 resolution,
                                     dom_domain_tile_desc* out_desc)
{
    const dom_domain_sdf_source* source;
    q16_16 tile_size;
    i32 tx;
    i32 ty;
    i32 tz;
    u32 sample_dim;
    if (!domain || !point || !out_desc) {
        return 0;
    }
    source = dom_terrain_surface_sdf(&domain->terrain_domain.surface);
    if (!source) {
        return 0;
    }
    tile_size = domain->policy.tile_size;
    if (tile_size <= 0) {
        return 0;
    }
    if (resolution == DOM_DOMAIN_RES_FULL) {
        sample_dim = domain->policy.sample_dim_full;
    } else if (resolution == DOM_DOMAIN_RES_MEDIUM) {
        sample_dim = domain->policy.sample_dim_medium;
    } else {
        sample_dim = domain->policy.sample_dim_coarse;
    }
    if (sample_dim == 0u) {
        return 0;
    }
    tx = (i32)(((i64)point->x - (i64)source->bounds.min.x) / (i64)tile_size);
    ty = (i32)(((i64)point->y - (i64)source->bounds.min.y) / (i64)tile_size);
    tz = (i32)(((i64)point->z - (i64)source->bounds.min.z) / (i64)tile_size);
    dom_domain_tile_desc_init(out_desc);
    out_desc->resolution = resolution;
    out_desc->sample_dim = sample_dim;
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

static int structure_run_collapse(const structure_fixture* fixture,
                                  const dom_domain_point* point,
                                  u64 tick,
                                  u32 budget_max)
{
    dom_structure_domain domain;
    dom_domain_tile_desc desc;
    dom_domain_budget budget;
    dom_structure_sample inside;
    dom_structure_sample outside;
    dom_domain_point outside_point;
    u32 count_before;
    u32 count_after;
    u32 count_final;

    structure_domain_init_from_fixture(fixture, &domain);
    if (!structure_build_tile_desc(&domain, point, DOM_DOMAIN_RES_COARSE, &desc)) {
        dom_structure_domain_free(&domain);
        return 1;
    }
    count_before = dom_structure_domain_capsule_count(&domain);
    (void)dom_structure_domain_collapse_tile(&domain, &desc, tick);
    count_after = dom_structure_domain_capsule_count(&domain);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_structure_sample_query(&domain, point, tick, &budget, &inside);

    outside_point = *point;
    outside_point.x = d_q16_16_add(outside_point.x,
                                   d_q16_16_mul(domain.policy.tile_size, d_q16_16_from_int(2)));
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_structure_sample_query(&domain, &outside_point, tick, &budget, &outside);

    (void)dom_structure_domain_expand_tile(&domain, desc.tile_id);
    count_final = dom_structure_domain_capsule_count(&domain);

    printf("%s\n", STRUCTURE_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STRUCTURE_PROVIDER_CHAIN);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);
    printf("capsule_count_final=%u\n", (unsigned int)count_final);
    printf("tile_id=%llu\n", (unsigned long long)desc.tile_id);
    printf("inside_flags=%u\n", (unsigned int)inside.flags);
    printf("outside_flags=%u\n", (unsigned int)outside.flags);

    dom_structure_domain_free(&domain);
    return 0;
}

static int structure_find_instance_index(const dom_structure_domain* domain,
                                         const dom_domain_point* point,
                                         u32* out_index)
{
    i32 cx = 0;
    i32 cy = 0;
    i32 cz = 0;
    u32 best_index = 0u;
    u32 best_id = 0xFFFFFFFFu;
    d_bool found = D_FALSE;
    if (!domain || !point || !out_index) {
        return 0;
    }
    structure_cell_coord(domain->surface.placement_cell_size, point, &cx, &cy, &cz);
    for (u32 i = 0u; i < domain->instance_count && i < DOM_STRUCTURE_MAX_INSTANCES; ++i) {
        const dom_structure_instance* inst = &domain->instances[i];
        if (inst->structure_id == 0u) {
            continue;
        }
        if (inst->cell_x != cx || inst->cell_y != cy || inst->cell_z != cz) {
            continue;
        }
        if (!found || inst->structure_id < best_id) {
            best_id = inst->structure_id;
            best_index = i;
            found = D_TRUE;
        }
    }
    if (!found) {
        return 0;
    }
    *out_index = best_index;
    return 1;
}

static int structure_run_failure(const structure_fixture* fixture,
                                 const dom_domain_point* point,
                                 u64 tick)
{
    dom_structure_domain domain;
    dom_structure_collapse_result result;
    u32 index = 0u;
    structure_domain_init_from_fixture(fixture, &domain);
    if (!structure_find_instance_index(&domain, point, &index)) {
        dom_structure_domain_free(&domain);
        fprintf(stderr, "structure: no instance at point\n");
        return 2;
    }
    if (dom_structure_collapse(&domain, index, tick, &result) != 0) {
        dom_structure_domain_free(&domain);
        fprintf(stderr, "structure: collapse failed\n");
        return 2;
    }
    printf("%s\n", STRUCTURE_FAILURE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STRUCTURE_PROVIDER_CHAIN);
    printf("overlay_kind=%u\n", (unsigned int)result.overlay_kind);
    printf("delta_phi_q16=%d\n", (int)result.delta_phi);
    printf("debris_fill_q16=%d\n", (int)result.debris_fill);
    dom_structure_domain_free(&domain);
    return 0;
}

static int structure_run_render(const structure_fixture* fixture,
                                const dom_domain_point* center,
                                q16_16 radius,
                                u32 dim,
                                u64 tick,
                                u32 budget_max)
{
    dom_structure_domain domain;
    u32 visible_cells = 0u;
    u32 touched_cells = 0u;
    u32 visible_structures = 0u;
    q16_16 step = 0;
    q16_16 span = d_q16_16_mul(radius, d_q16_16_from_int(2));
    q16_16 half = d_fixed_div_q16_16(span, d_q16_16_from_int(2));
    structure_domain_init_from_fixture(fixture, &domain);
    if (dim == 0u) {
        dim = 1u;
    }
    if (dim > 1u) {
        step = (q16_16)((i64)span / (i64)(dim - 1u));
    }
    for (u32 y = 0u; y < dim; ++y) {
        q16_16 yoff = (q16_16)((i64)step * (i64)y);
        yoff = d_q16_16_sub(yoff, half);
        for (u32 x = 0u; x < dim; ++x) {
            q16_16 xoff = (q16_16)((i64)step * (i64)x);
            xoff = d_q16_16_sub(xoff, half);
            if (structure_abs_q16_16(xoff) > radius || structure_abs_q16_16(yoff) > radius) {
                continue;
            }
            {
                dom_domain_point p = *center;
                dom_domain_budget budget;
                dom_structure_sample sample;
                p.x = d_q16_16_add(p.x, xoff);
                p.y = d_q16_16_add(p.y, yoff);
                dom_domain_budget_init(&budget, budget_max);
                (void)dom_structure_sample_query(&domain, &p, tick, &budget, &sample);
                visible_cells += 1u;
                touched_cells += 1u;
                if (sample.flags & DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT) {
                    visible_structures += 1u;
                }
            }
        }
    }
    printf("%s\n", STRUCTURE_RENDER_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STRUCTURE_PROVIDER_CHAIN);
    printf("visible_cells=%u\n", (unsigned int)visible_cells);
    printf("touched_cells=%u\n", (unsigned int)touched_cells);
    printf("visible_structures=%u\n", (unsigned int)visible_structures);
    printf("touched_structures=%u\n", (unsigned int)visible_structures);
    dom_structure_domain_free(&domain);
    return 0;
}

static void structure_usage(void)
{
    printf("dom_tool_structure commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --pos x,y,z --tick T [--budget N]\n");
    printf("  core-sample --fixture <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--budget N] [--inactive N] [--collapsed 0|1]\n");
    printf("  diff --fixture-a <path> --fixture-b <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--budget N]\n");
    printf("  collapse --fixture <path> --pos x,y,z --tick T [--budget N]\n");
    printf("  failure --fixture <path> --pos x,y,z --tick T\n");
    printf("  render --fixture <path> --center x,y,z --radius R [--dim N] [--tick T] [--budget N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        structure_usage();
        return 2;
    }
    cmd = argv[1];

    if (strcmp(cmd, "diff") == 0) {
        const char* fixture_a_path = structure_find_arg(argc, argv, "--fixture-a");
        const char* fixture_b_path = structure_find_arg(argc, argv, "--fixture-b");
        structure_fixture fixture_a;
        structure_fixture fixture_b;
        dom_domain_point origin;
        dom_domain_point direction;
        q16_16 length = d_q16_16_from_int(64);
        u32 steps = structure_find_arg_u32(argc, argv, "--steps", 16u);
        u64 start_tick = structure_find_arg_u64(argc, argv, "--start", 0u);
        u64 step_ticks = structure_find_arg_u64(argc, argv, "--step_ticks", 10u);
        u32 budget_max;
        if (!fixture_a_path || !fixture_b_path ||
            !structure_fixture_load(fixture_a_path, &fixture_a) ||
            !structure_fixture_load(fixture_b_path, &fixture_b)) {
            fprintf(stderr, "structure: missing or invalid --fixture-a/--fixture-b\n");
            return 2;
        }
        if (!structure_parse_arg_point(argc, argv, "--origin", &origin) ||
            !structure_parse_arg_point(argc, argv, "--dir", &direction)) {
            fprintf(stderr, "structure: missing --origin or --dir\n");
            return 2;
        }
        if (!structure_parse_q16(structure_find_arg(argc, argv, "--length"), &length)) {
            length = d_q16_16_from_int(64);
        }
        budget_max = structure_find_arg_u32(argc, argv, "--budget", fixture_a.policy.cost_analytic);
        return structure_run_diff(&fixture_a, &fixture_b, &origin, &direction, length, steps,
                                  start_tick, step_ticks, budget_max);
    }

    {
        const char* fixture_path = structure_find_arg(argc, argv, "--fixture");
        structure_fixture fixture;
        if (!fixture_path || !structure_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "structure: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return structure_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            dom_domain_point point;
            u64 tick = structure_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = structure_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!structure_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "structure: missing --pos\n");
                return 2;
            }
            return structure_run_inspect(&fixture, &point, tick, budget_max);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_domain_point origin;
            dom_domain_point direction;
            q16_16 length = d_q16_16_from_int(64);
            u32 steps = structure_find_arg_u32(argc, argv, "--steps", 16u);
            u64 start_tick = structure_find_arg_u64(argc, argv, "--start", 0u);
            u64 step_ticks = structure_find_arg_u64(argc, argv, "--step_ticks", 10u);
            u32 budget_max = structure_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 inactive = structure_find_arg_u32(argc, argv, "--inactive", 0u);
            u32 collapsed = structure_find_arg_u32(argc, argv, "--collapsed", 0u);
            if (!structure_parse_arg_point(argc, argv, "--origin", &origin) ||
                !structure_parse_arg_point(argc, argv, "--dir", &direction)) {
                fprintf(stderr, "structure: missing --origin or --dir\n");
                return 2;
            }
            if (!structure_parse_q16(structure_find_arg(argc, argv, "--length"), &length)) {
                length = d_q16_16_from_int(64);
            }
            return structure_run_core_sample(&fixture, &origin, &direction, length, steps,
                                             start_tick, step_ticks, budget_max,
                                             inactive, collapsed ? 1 : 0);
        }

        if (strcmp(cmd, "collapse") == 0) {
            dom_domain_point point;
            u64 tick = structure_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = structure_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!structure_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "structure: missing --pos\n");
                return 2;
            }
            return structure_run_collapse(&fixture, &point, tick, budget_max);
        }

        if (strcmp(cmd, "failure") == 0) {
            dom_domain_point point;
            u64 tick = structure_find_arg_u64(argc, argv, "--tick", 0u);
            if (!structure_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "structure: missing --pos\n");
                return 2;
            }
            return structure_run_failure(&fixture, &point, tick);
        }

        if (strcmp(cmd, "render") == 0) {
            dom_domain_point center;
            q16_16 radius;
            u64 tick = structure_find_arg_u64(argc, argv, "--tick", 0u);
            u32 dim = structure_find_arg_u32(argc, argv, "--dim", 8u);
            u32 budget_max = structure_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!structure_parse_arg_point(argc, argv, "--center", &center)) {
                fprintf(stderr, "structure: missing --center\n");
                return 2;
            }
            if (!structure_parse_q16(structure_find_arg(argc, argv, "--radius"), &radius)) {
                fprintf(stderr, "structure: missing --radius\n");
                return 2;
            }
            return structure_run_render(&fixture, &center, radius, dim, tick, budget_max);
        }
    }

    structure_usage();
    return 2;
}
