/*
FILE: tools/travel/travel_cli.cpp
MODULE: Dominium
PURPOSE: Travel fixture CLI for deterministic cost and bounded pathfinding checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/travel_fields.h"

#define TRAVEL_FIXTURE_HEADER "DOMINIUM_TRAVEL_FIXTURE_V1"

#define TRAVEL_VALIDATE_HEADER "DOMINIUM_TRAVEL_VALIDATE_V1"
#define TRAVEL_INSPECT_HEADER "DOMINIUM_TRAVEL_INSPECT_V1"
#define TRAVEL_CORE_SAMPLE_HEADER "DOMINIUM_TRAVEL_CORE_SAMPLE_V1"
#define TRAVEL_DIFF_HEADER "DOMINIUM_TRAVEL_DIFF_V1"
#define TRAVEL_COLLAPSE_HEADER "DOMINIUM_TRAVEL_COLLAPSE_V1"
#define TRAVEL_PATH_HEADER "DOMINIUM_TRAVEL_PATH_V1"
#define TRAVEL_RENDER_HEADER "DOMINIUM_TRAVEL_RENDER_V1"

#define TRAVEL_PROVIDER_CHAIN "terrain->structure->weather->travel"

#define TRAVEL_LINE_MAX 512u

typedef struct travel_fixture {
    char fixture_id[96];
    dom_travel_surface_desc desc;
    dom_domain_policy policy;
    u32 cache_capacity;
    u32 policy_set;
    char mode_ids[DOM_TRAVEL_MAX_MODES][64];
    char structure_ids[DOM_STRUCTURE_MAX_SPECS][64];
} travel_fixture;

static void travel_structure_spec_defaults(dom_structure_spec_desc* spec);

static u64 travel_hash_u64(u64 h, u64 v)
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

static u64 travel_hash_u32(u64 h, u32 v)
{
    return travel_hash_u64(h, (u64)v);
}

static u64 travel_hash_i32(u64 h, i32 v)
{
    return travel_hash_u64(h, (u64)(u32)v);
}

static char* travel_trim(char* text)
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

static int travel_parse_u32(const char* text, u32* out_value)
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

static int travel_parse_u64(const char* text, u64* out_value)
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

static int travel_parse_q16(const char* text, q16_16* out_value)
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

static int travel_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[TRAVEL_LINE_MAX];
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
    if (!travel_parse_q16(travel_trim(first), a)) return 0;
    if (!travel_parse_q16(travel_trim(second), b)) return 0;
    if (!travel_parse_q16(travel_trim(third), c)) return 0;
    return 1;
}

static int travel_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!travel_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 travel_parse_resolution(const char* text)
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

static int travel_parse_indexed_key(const char* key,
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

static q16_16 travel_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static int travel_parse_mode_kind(const char* value, u32* out_kind)
{
    if (!value || !out_kind) {
        return 0;
    }
    if (strcmp(value, "walk") == 0) {
        *out_kind = DOM_TRAVEL_MODE_WALK;
        return 1;
    }
    if (strcmp(value, "swim") == 0) {
        *out_kind = DOM_TRAVEL_MODE_SWIM;
        return 1;
    }
    if (strcmp(value, "vehicle") == 0) {
        *out_kind = DOM_TRAVEL_MODE_VEHICLE;
        return 1;
    }
    return travel_parse_u32(value, out_kind);
}

static int travel_parse_event_type(const char* value, u32* out_type)
{
    if (!value || !out_type) {
        return 0;
    }
    if (strcmp(value, "rain") == 0) {
        *out_type = DOM_WEATHER_EVENT_RAIN;
        return 1;
    }
    if (strcmp(value, "snow") == 0) {
        *out_type = DOM_WEATHER_EVENT_SNOW;
        return 1;
    }
    if (strcmp(value, "heatwave") == 0) {
        *out_type = DOM_WEATHER_EVENT_HEATWAVE;
        return 1;
    }
    if (strcmp(value, "cold_snap") == 0) {
        *out_type = DOM_WEATHER_EVENT_COLD_SNAP;
        return 1;
    }
    if (strcmp(value, "wind_shift") == 0) {
        *out_type = DOM_WEATHER_EVENT_WIND_SHIFT;
        return 1;
    }
    return travel_parse_u32(value, out_type);
}

static void travel_mode_defaults(dom_travel_mode_desc* mode)
{
    if (!mode) {
        return;
    }
    memset(mode, 0, sizeof(*mode));
    mode->mode_id = 1u;
    mode->mode_kind = DOM_TRAVEL_MODE_WALK;
    mode->slope_max = d_q16_16_from_int(1);
    mode->cost_scale = d_q16_16_from_int(1);
    mode->cost_add = 0;
    mode->mass = 0;
    mode->inertia = d_q16_16_from_int(1);
    mode->damage_threshold = d_q16_16_from_int(1);
    mode->vehicle_structure_id = 0u;
    mode->maturity_tag = 1u;
}

static void travel_fixture_init(travel_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_travel_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->cache_capacity = fixture->desc.cache_capacity;
    fixture->policy_set = 0u;
    strncpy(fixture->fixture_id, "travel.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
    for (u32 i = 0u; i < DOM_TRAVEL_MAX_MODES; ++i) {
        travel_mode_defaults(&fixture->desc.modes[i]);
    }
    for (u32 i = 0u; i < DOM_STRUCTURE_MAX_SPECS; ++i) {
        travel_structure_spec_defaults(&fixture->desc.structure_desc.structures[i]);
    }
}

static int travel_parse_anchor_kind(const char* value, u32* out_kind)
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
    return travel_parse_u32(value, out_kind);
}

static void travel_structure_spec_defaults(dom_structure_spec_desc* spec)
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
    spec->maturity_tag = 1u;
}

static int travel_fixture_apply_event_profile(travel_fixture* fixture,
                                              const char* key,
                                              const char* value)
{
    char buffer[TRAVEL_LINE_MAX];
    char* dot;
    u32 event_type = 0u;
    dom_weather_event_profile* profile;
    if (!fixture || !key || !value) {
        return 0;
    }
    if (strncmp(key, "event.", 6) != 0) {
        return 0;
    }
    strncpy(buffer, key + 6, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    dot = strchr(buffer, '.');
    if (!dot) {
        return 0;
    }
    *dot++ = '\0';
    if (!travel_parse_event_type(buffer, &event_type)) {
        return 0;
    }
    if (event_type >= DOM_WEATHER_EVENT_TYPE_COUNT) {
        return 0;
    }
    profile = &fixture->desc.weather_desc.schedule.profiles[event_type];
    if (strcmp(dot, "period_ticks") == 0) {
        return travel_parse_u64(value, &profile->period_ticks);
    }
    if (strcmp(dot, "duration_ticks") == 0) {
        return travel_parse_u64(value, &profile->duration_ticks);
    }
    if (strcmp(dot, "intensity_min") == 0) {
        return travel_parse_q16(value, &profile->intensity_min);
    }
    if (strcmp(dot, "intensity_max") == 0) {
        return travel_parse_q16(value, &profile->intensity_max);
    }
    if (strcmp(dot, "radius_ratio_min") == 0) {
        return travel_parse_q16(value, &profile->radius_ratio_min);
    }
    if (strcmp(dot, "radius_ratio_max") == 0) {
        return travel_parse_q16(value, &profile->radius_ratio_max);
    }
    if (strcmp(dot, "temp_scale") == 0) {
        return travel_parse_q16(value, &profile->temp_scale);
    }
    if (strcmp(dot, "precip_scale") == 0) {
        return travel_parse_q16(value, &profile->precip_scale);
    }
    if (strcmp(dot, "wetness_scale") == 0) {
        return travel_parse_q16(value, &profile->wetness_scale);
    }
    return 0;
}

static int travel_fixture_apply_mode(travel_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_travel_mode_desc* mode;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_TRAVEL_MAX_MODES) {
        return 0;
    }
    if (fixture->desc.mode_count <= index) {
        fixture->desc.mode_count = index + 1u;
    }
    mode = &fixture->desc.modes[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->mode_ids[index], value, sizeof(fixture->mode_ids[index]) - 1);
        fixture->mode_ids[index][sizeof(fixture->mode_ids[index]) - 1] = '\0';
        mode->mode_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "kind") == 0) {
        return travel_parse_mode_kind(value, &mode->mode_kind);
    }
    if (strcmp(suffix, "slope_max") == 0) {
        return travel_parse_q16(value, &mode->slope_max);
    }
    if (strcmp(suffix, "cost_scale") == 0) {
        return travel_parse_q16(value, &mode->cost_scale);
    }
    if (strcmp(suffix, "cost_add") == 0) {
        return travel_parse_q16(value, &mode->cost_add);
    }
    if (strcmp(suffix, "mass") == 0) {
        return travel_parse_q16(value, &mode->mass);
    }
    if (strcmp(suffix, "inertia") == 0) {
        return travel_parse_q16(value, &mode->inertia);
    }
    if (strcmp(suffix, "damage_threshold") == 0) {
        return travel_parse_q16(value, &mode->damage_threshold);
    }
    if (strcmp(suffix, "vehicle_structure_id") == 0) {
        mode->vehicle_structure_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "maturity") == 0) {
        if (strcmp(value, "BOUNDED") == 0) {
            mode->maturity_tag = 1u;
            return 1;
        }
        if (strcmp(value, "STRUCTURAL") == 0) {
            mode->maturity_tag = 2u;
            return 1;
        }
        return travel_parse_u32(value, &mode->maturity_tag);
    }
    return 0;
}

static int travel_fixture_apply_structure(travel_fixture* fixture,
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
    if (fixture->desc.structure_desc.structure_count <= index) {
        fixture->desc.structure_desc.structure_count = index + 1u;
    }
    spec = &fixture->desc.structure_desc.structures[index];
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
        return travel_parse_q16(value, &spec->traits.stiffness);
    }
    if (strcmp(suffix, "density") == 0) {
        return travel_parse_q16(value, &spec->traits.density);
    }
    if (strcmp(suffix, "brittleness") == 0) {
        return travel_parse_q16(value, &spec->traits.brittleness);
    }
    if (strcmp(suffix, "load_capacity") == 0) {
        return travel_parse_q16(value, &spec->load_capacity);
    }
    if (strcmp(suffix, "gravity_scale") == 0) {
        return travel_parse_q16(value, &spec->gravity_scale);
    }
    if (strcmp(suffix, "slope_max") == 0) {
        return travel_parse_q16(value, &spec->slope_max);
    }
    if (strcmp(suffix, "anchor_count") == 0) {
        return travel_parse_u32(value, &spec->anchor_count);
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
        return travel_parse_u32(value, &spec->maturity_tag);
    }
    if (travel_parse_indexed_key(suffix, "anchor", &anchor_index, &anchor_suffix)) {
        if (anchor_index >= DOM_STRUCTURE_MAX_ANCHORS) {
            return 0;
        }
        if (spec->anchor_count <= anchor_index) {
            spec->anchor_count = anchor_index + 1u;
        }
        if (strcmp(anchor_suffix, "kind") == 0) {
            return travel_parse_anchor_kind(value, &spec->anchors[anchor_index].kind);
        }
        if (strcmp(anchor_suffix, "offset") == 0) {
            return travel_parse_triplet_q16(value,
                                            &spec->anchors[anchor_index].offset.x,
                                            &spec->anchors[anchor_index].offset.y,
                                            &spec->anchors[anchor_index].offset.z);
        }
        if (strcmp(anchor_suffix, "support_scale") == 0) {
            return travel_parse_q16(value, &spec->anchors[anchor_index].support_scale);
        }
        if (strcmp(anchor_suffix, "target_id") == 0) {
            spec->anchors[anchor_index].target_id = d_rng_hash_str32(value);
            return 1;
        }
    }
    return 0;
}

static int travel_fixture_apply_instance(travel_fixture* fixture,
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
    if (fixture->desc.structure_desc.instance_count <= index) {
        fixture->desc.structure_desc.instance_count = index + 1u;
    }
    inst = &fixture->desc.structure_desc.instances[index];
    if (strcmp(suffix, "structure_id") == 0) {
        inst->structure_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "pos") == 0) {
        return travel_parse_triplet_q16(value, &inst->location.x, &inst->location.y, &inst->location.z);
    }
    if (strcmp(suffix, "integrity") == 0) {
        return travel_parse_q16(value, &inst->integrity);
    }
    if (strcmp(suffix, "reinforcement") == 0) {
        return travel_parse_q16(value, &inst->reinforcement);
    }
    if (strcmp(suffix, "flags") == 0) {
        return travel_parse_u32(value, &inst->flags);
    }
    return 0;
}

static int travel_fixture_apply_geo_layer(travel_fixture* fixture,
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
    if (fixture->desc.structure_desc.geology_desc.layer_count <= index) {
        fixture->desc.structure_desc.geology_desc.layer_count = index + 1u;
    }
    layer = &fixture->desc.structure_desc.geology_desc.layers[index];
    if (strcmp(suffix, "id") == 0) {
        layer->layer_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "thickness") == 0) {
        return travel_parse_q16(value, &layer->thickness);
    }
    if (strcmp(suffix, "hardness") == 0) {
        return travel_parse_q16(value, &layer->hardness);
    }
    if (strcmp(suffix, "fracture") == 0) {
        layer->has_fracture = 1u;
        return travel_parse_q16(value, &layer->fracture_risk);
    }
    return 0;
}

static int travel_fixture_apply(travel_fixture* fixture, const char* key, const char* value)
{
    u32 index = 0u;
    const char* suffix = 0;
    if (!fixture || !key || !value) {
        return 0;
    }
    if (travel_fixture_apply_event_profile(fixture, key, value)) {
        return 1;
    }
    if (travel_parse_indexed_key(key, "mode", &index, &suffix)) {
        return travel_fixture_apply_mode(fixture, index, suffix, value);
    }
    if (travel_parse_indexed_key(key, "structure", &index, &suffix)) {
        return travel_fixture_apply_structure(fixture, index, suffix, value);
    }
    if (travel_parse_indexed_key(key, "instance", &index, &suffix)) {
        return travel_fixture_apply_instance(fixture, index, suffix, value);
    }
    if (travel_parse_indexed_key(key, "geo_layer", &index, &suffix)) {
        return travel_fixture_apply_geo_layer(fixture, index, suffix, value);
    }
    if (travel_parse_indexed_key(key, "road", &index, &suffix)) {
        if (index >= DOM_TRAVEL_MAX_ROADS) {
            return 0;
        }
        if (fixture->desc.road_count <= index) {
            fixture->desc.road_count = index + 1u;
        }
        if (strcmp(suffix, "id") == 0) {
            fixture->desc.road_structure_ids[index] = d_rng_hash_str32(value);
            return 1;
        }
        return 0;
    }
    if (travel_parse_indexed_key(key, "bridge", &index, &suffix)) {
        if (index >= DOM_TRAVEL_MAX_BRIDGES) {
            return 0;
        }
        if (fixture->desc.bridge_count <= index) {
            fixture->desc.bridge_count = index + 1u;
        }
        if (strcmp(suffix, "id") == 0) {
            fixture->desc.bridge_structure_ids[index] = d_rng_hash_str32(value);
            return 1;
        }
        return 0;
    }
    if (travel_parse_indexed_key(key, "obstacle", &index, &suffix)) {
        if (index >= DOM_TRAVEL_MAX_OBSTACLES) {
            return 0;
        }
        if (fixture->desc.obstacle_count <= index) {
            fixture->desc.obstacle_count = index + 1u;
        }
        if (strcmp(suffix, "id") == 0) {
            fixture->desc.obstacle_structure_ids[index] = d_rng_hash_str32(value);
            return 1;
        }
        return 0;
    }

    if (strcmp(key, "fixture_id") == 0) {
        strncpy(fixture->fixture_id, value, sizeof(fixture->fixture_id) - 1);
        fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
        return 1;
    }
    if (strcmp(key, "world_seed") == 0) {
        if (travel_parse_u64(value, &fixture->desc.world_seed)) {
            fixture->desc.terrain_desc.world_seed = fixture->desc.world_seed;
            fixture->desc.weather_desc.climate_desc.world_seed = fixture->desc.world_seed;
            fixture->desc.structure_desc.world_seed = fixture->desc.world_seed;
            fixture->desc.structure_desc.terrain_desc.world_seed = fixture->desc.world_seed;
            fixture->desc.structure_desc.geology_desc.world_seed = fixture->desc.world_seed;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "domain_id") == 0) {
        if (travel_parse_u64(value, &fixture->desc.domain_id)) {
            fixture->desc.terrain_desc.domain_id = fixture->desc.domain_id;
            fixture->desc.weather_desc.climate_desc.domain_id = fixture->desc.domain_id;
            fixture->desc.structure_desc.domain_id = fixture->desc.domain_id;
            fixture->desc.structure_desc.terrain_desc.domain_id = fixture->desc.domain_id;
            fixture->desc.structure_desc.geology_desc.domain_id = fixture->desc.domain_id;
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
        fixture->desc.weather_desc.climate_desc.shape = fixture->desc.shape;
        fixture->desc.structure_desc.shape = fixture->desc.shape;
        fixture->desc.structure_desc.terrain_desc.shape = fixture->desc.shape;
        fixture->desc.structure_desc.geology_desc.shape = fixture->desc.shape;
        return 1;
    }
    if (strcmp(key, "radius_equatorial") == 0) {
        if (travel_parse_q16(value, &fixture->desc.shape.radius_equatorial)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.weather_desc.climate_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "radius_polar") == 0) {
        if (travel_parse_q16(value, &fixture->desc.shape.radius_polar)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.weather_desc.climate_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        if (travel_parse_q16(value, &fixture->desc.shape.slab_half_extent)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.weather_desc.climate_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        if (travel_parse_q16(value, &fixture->desc.shape.slab_half_thickness)) {
            fixture->desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.weather_desc.climate_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.terrain_desc.shape = fixture->desc.shape;
            fixture->desc.structure_desc.geology_desc.shape = fixture->desc.shape;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        if (travel_parse_q16(value, &fixture->desc.meters_per_unit)) {
            fixture->desc.terrain_desc.meters_per_unit = fixture->desc.meters_per_unit;
            fixture->desc.weather_desc.climate_desc.meters_per_unit = fixture->desc.meters_per_unit;
            fixture->desc.structure_desc.meters_per_unit = fixture->desc.meters_per_unit;
            fixture->desc.structure_desc.terrain_desc.meters_per_unit = fixture->desc.meters_per_unit;
            fixture->desc.structure_desc.geology_desc.meters_per_unit = fixture->desc.meters_per_unit;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "cache_capacity") == 0) {
        if (travel_parse_u32(value, &fixture->cache_capacity)) {
            fixture->desc.cache_capacity = fixture->cache_capacity;
            fixture->desc.terrain_cache_capacity = fixture->cache_capacity;
            fixture->desc.weather_cache_capacity = fixture->cache_capacity;
            fixture->desc.structure_cache_capacity = fixture->cache_capacity;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "terrain_cache_capacity") == 0) {
        return travel_parse_u32(value, &fixture->desc.terrain_cache_capacity);
    }
    if (strcmp(key, "weather_cache_capacity") == 0) {
        return travel_parse_u32(value, &fixture->desc.weather_cache_capacity);
    }
    if (strcmp(key, "structure_cache_capacity") == 0) {
        return travel_parse_u32(value, &fixture->desc.structure_cache_capacity);
    }

    if (strcmp(key, "road_cost_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.road_cost_scale);
    }
    if (strcmp(key, "bridge_cost_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.bridge_cost_scale);
    }
    if (strcmp(key, "weather_precip_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_precip_scale);
    }
    if (strcmp(key, "weather_wetness_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_wetness_scale);
    }
    if (strcmp(key, "weather_temp_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_temp_scale);
    }
    if (strcmp(key, "comfort_temp_min") == 0) {
        return travel_parse_q16(value, &fixture->desc.comfort_temp_min);
    }
    if (strcmp(key, "comfort_temp_max") == 0) {
        return travel_parse_q16(value, &fixture->desc.comfort_temp_max);
    }
    if (strcmp(key, "weather_wind_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_wind_scale);
    }
    if (strcmp(key, "path_step") == 0) {
        return travel_parse_q16(value, &fixture->desc.path_step);
    }
    if (strcmp(key, "path_coarse_step") == 0) {
        return travel_parse_q16(value, &fixture->desc.path_coarse_step);
    }
    if (strcmp(key, "path_max_distance") == 0) {
        return travel_parse_q16(value, &fixture->desc.path_max_distance);
    }
    if (strcmp(key, "path_max_nodes") == 0) {
        return travel_parse_u32(value, &fixture->desc.path_max_nodes);
    }
    if (strcmp(key, "path_max_points") == 0) {
        return travel_parse_u32(value, &fixture->desc.path_max_points);
    }

    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_q16(value, &fixture->policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->policy.max_resolution = travel_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_q16(value, &fixture->policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return travel_parse_u32(value, &fixture->policy.max_ray_steps);
    }

    if (strcmp(key, "terrain_noise_seed") == 0) {
        return travel_parse_u64(value, &fixture->desc.terrain_desc.noise.seed);
    }
    if (strcmp(key, "terrain_noise_amplitude") == 0) {
        return travel_parse_q16(value, &fixture->desc.terrain_desc.noise.amplitude);
    }
    if (strcmp(key, "terrain_noise_cell_size") == 0) {
        return travel_parse_q16(value, &fixture->desc.terrain_desc.noise.cell_size);
    }
    if (strcmp(key, "terrain_roughness_base") == 0) {
        return travel_parse_q16(value, &fixture->desc.terrain_desc.roughness_base);
    }
    if (strcmp(key, "terrain_travel_cost_base") == 0) {
        return travel_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_base);
    }
    if (strcmp(key, "terrain_travel_cost_slope_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_slope_scale);
    }
    if (strcmp(key, "terrain_travel_cost_roughness_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.terrain_desc.travel_cost_roughness_scale);
    }
    if (strcmp(key, "terrain_material_primary") == 0) {
        return travel_parse_u32(value, &fixture->desc.terrain_desc.material_primary);
    }
    if (strcmp(key, "terrain_walkable_max_slope") == 0) {
        return travel_parse_q16(value, &fixture->desc.terrain_desc.walkable_max_slope);
    }

    if (strcmp(key, "noise_seed") == 0) {
        return travel_parse_u64(value, &fixture->desc.weather_desc.climate_desc.noise.seed);
    }
    if (strcmp(key, "noise_amplitude") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.noise.amplitude);
    }
    if (strcmp(key, "noise_cell_size") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.noise.cell_size);
    }
    if (strcmp(key, "temp_equator") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.temp_equator);
    }
    if (strcmp(key, "temp_pole") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.temp_pole);
    }
    if (strcmp(key, "temp_altitude_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.temp_altitude_scale);
    }
    if (strcmp(key, "temp_range_base") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.temp_range_base);
    }
    if (strcmp(key, "temp_range_lat_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.temp_range_lat_scale);
    }
    if (strcmp(key, "precip_equator") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.precip_equator);
    }
    if (strcmp(key, "precip_pole") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.precip_pole);
    }
    if (strcmp(key, "precip_altitude_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.precip_altitude_scale);
    }
    if (strcmp(key, "precip_range_base") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.precip_range_base);
    }
    if (strcmp(key, "precip_range_lat_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.precip_range_lat_scale);
    }
    if (strcmp(key, "seasonality_base") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.seasonality_base);
    }
    if (strcmp(key, "seasonality_lat_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.seasonality_lat_scale);
    }
    if (strcmp(key, "noise_temp_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.noise_temp_scale);
    }
    if (strcmp(key, "noise_precip_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.noise_precip_scale);
    }
    if (strcmp(key, "noise_season_scale") == 0) {
        return travel_parse_q16(value, &fixture->desc.weather_desc.climate_desc.noise_season_scale);
    }
    if (strcmp(key, "wind_band_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.weather_desc.climate_desc.wind_band_count);
    }
    if (strcmp(key, "weather_seed") == 0) {
        return travel_parse_u64(value, &fixture->desc.weather_desc.schedule.seed);
    }

    if (strcmp(key, "placement_cell_size") == 0) {
        return travel_parse_q16(value, &fixture->desc.structure_desc.placement_cell_size);
    }
    if (strcmp(key, "density_base") == 0) {
        return travel_parse_q16(value, &fixture->desc.structure_desc.density_base);
    }
    if (strcmp(key, "stress_check_period_ticks") == 0) {
        return travel_parse_u64(value, &fixture->desc.structure_desc.stress_check_period_ticks);
    }
    if (strcmp(key, "repair_period_ticks") == 0) {
        return travel_parse_u64(value, &fixture->desc.structure_desc.repair_period_ticks);
    }
    if (strcmp(key, "reinforce_period_ticks") == 0) {
        return travel_parse_u64(value, &fixture->desc.structure_desc.reinforce_period_ticks);
    }
    if (strcmp(key, "structure_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.structure_desc.structure_count);
    }
    if (strcmp(key, "instance_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.structure_desc.instance_count);
    }
    if (strcmp(key, "geo_layer_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.structure_desc.geology_desc.layer_count);
    }
    if (strcmp(key, "geo_default_hardness") == 0) {
        return travel_parse_q16(value, &fixture->desc.structure_desc.geology_desc.default_hardness);
    }
    if (strcmp(key, "geo_default_fracture_risk") == 0) {
        return travel_parse_q16(value, &fixture->desc.structure_desc.geology_desc.default_fracture_risk);
    }

    if (strcmp(key, "mode_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.mode_count);
    }
    if (strcmp(key, "road_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.road_count);
    }
    if (strcmp(key, "bridge_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.bridge_count);
    }
    if (strcmp(key, "obstacle_count") == 0) {
        return travel_parse_u32(value, &fixture->desc.obstacle_count);
    }

    return 0;
}

static int travel_fixture_load(const char* path, travel_fixture* fixture)
{
    FILE* handle;
    char line[TRAVEL_LINE_MAX];
    if (!path || !fixture) {
        return 0;
    }
    travel_fixture_init(fixture);
    handle = fopen(path, "r");
    if (!handle) {
        return 0;
    }
    if (!fgets(line, sizeof(line), handle)) {
        fclose(handle);
        return 0;
    }
    if (strncmp(travel_trim(line), TRAVEL_FIXTURE_HEADER, strlen(TRAVEL_FIXTURE_HEADER)) != 0) {
        fclose(handle);
        return 0;
    }
    while (fgets(line, sizeof(line), handle)) {
        char* trimmed = travel_trim(line);
        char* eq = strchr(trimmed, '=');
        if (!trimmed || !*trimmed || trimmed[0] == '#') {
            continue;
        }
        if (!eq) {
            continue;
        }
        *eq++ = '\0';
        if (!travel_fixture_apply(fixture, trimmed, eq)) {
            continue;
        }
    }
    fclose(handle);
    return 1;
}

static const char* travel_find_arg(int argc, char** argv, const char* key)
{
    if (!key) {
        return 0;
    }
    for (int i = 1; i + 1 < argc; ++i) {
        if (strcmp(argv[i], key) == 0) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 travel_find_arg_u32(int argc, char** argv, const char* key, u32 default_value)
{
    u32 value = 0u;
    const char* text = travel_find_arg(argc, argv, key);
    if (!text) {
        return default_value;
    }
    if (!travel_parse_u32(text, &value)) {
        return default_value;
    }
    return value;
}

static u64 travel_find_arg_u64(int argc, char** argv, const char* key, u64 default_value)
{
    u64 value = 0u;
    const char* text = travel_find_arg(argc, argv, key);
    if (!text) {
        return default_value;
    }
    if (!travel_parse_u64(text, &value)) {
        return default_value;
    }
    return value;
}

static int travel_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* text = travel_find_arg(argc, argv, key);
    if (!text) {
        return 0;
    }
    return travel_parse_point(text, out_point);
}

static u32 travel_parse_mode_id(const char* text)
{
    u32 value = 0u;
    if (!text) {
        return 0u;
    }
    if (travel_parse_u32(text, &value)) {
        return value;
    }
    return d_rng_hash_str32(text);
}

static void travel_domain_init_from_fixture(const travel_fixture* fixture,
                                            dom_travel_domain* out_domain)
{
    if (!fixture || !out_domain) {
        return;
    }
    dom_travel_domain_init(out_domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_travel_domain_set_policy(out_domain, &fixture->policy);
    }
}

static int travel_build_tile_desc(const dom_travel_domain* domain,
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

static int travel_run_validate(const travel_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    printf("%s\n", TRAVEL_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRAVEL_PROVIDER_CHAIN);
    printf("mode_count=%u\n", (unsigned int)fixture->desc.mode_count);
    printf("road_count=%u\n", (unsigned int)fixture->desc.road_count);
    printf("bridge_count=%u\n", (unsigned int)fixture->desc.bridge_count);
    printf("obstacle_count=%u\n", (unsigned int)fixture->desc.obstacle_count);
    printf("structure_count=%u\n", (unsigned int)fixture->desc.structure_desc.structure_count);
    printf("instance_count=%u\n", (unsigned int)fixture->desc.structure_desc.instance_count);
    return 0;
}

static int travel_run_inspect(const travel_fixture* fixture,
                              const dom_domain_point* point,
                              u64 tick,
                              u32 mode_id,
                              u32 budget_max)
{
    dom_travel_domain domain;
    dom_domain_budget budget;
    dom_travel_sample sample;
    if (!fixture || !point) {
        return 1;
    }
    travel_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_travel_sample_query(&domain, point, tick, mode_id, &budget, &sample);

    printf("%s\n", TRAVEL_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRAVEL_PROVIDER_CHAIN);
    printf("mode_id=%u\n", (unsigned int)sample.mode_id);
    printf("structure_id=%u\n", (unsigned int)sample.structure_id);
    printf("travel_cost_q16=%d\n", (int)sample.travel_cost);
    printf("weather_modifier_q16=%d\n", (int)sample.weather_modifier);
    printf("mode_modifier_q16=%d\n", (int)sample.mode_modifier);
    printf("total_cost_q16=%d\n", (int)sample.total_cost);
    printf("obstacle_q16=%d\n", (int)sample.obstacle);
    printf("slope_q16=%d\n", (int)sample.slope);
    printf("roughness_q16=%d\n", (int)sample.roughness);
    printf("material_primary=%u\n", (unsigned int)sample.material_primary);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("fields_unknown=%u\n", (unsigned int)((sample.flags & DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN) != 0));
    printf("on_road=%u\n", (unsigned int)((sample.flags & DOM_TRAVEL_SAMPLE_ON_ROAD) != 0));
    printf("on_bridge=%u\n", (unsigned int)((sample.flags & DOM_TRAVEL_SAMPLE_ON_BRIDGE) != 0));
    printf("obstacle=%u\n", (unsigned int)((sample.flags & DOM_TRAVEL_SAMPLE_OBSTACLE) != 0));
    printf("collapsed=%u\n", (unsigned int)((sample.flags & DOM_TRAVEL_SAMPLE_COLLAPSED) != 0));
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);

    dom_travel_domain_free(&domain);
    return 0;
}

static u64 travel_core_sample_hash(const travel_fixture* fixture,
                                   const dom_domain_point* origin,
                                   const dom_domain_point* direction,
                                   q16_16 length,
                                   u32 steps,
                                   u64 start_tick,
                                   u64 step_ticks,
                                   u32 mode_id,
                                   u32 budget_max,
                                   u32 inactive,
                                   int collapse,
                                   u32* out_unknown_steps,
                                   u32* out_cost_max,
                                   u32* out_capsule_count,
                                   int* out_ok)
{
    dom_travel_domain domain;
    dom_travel_domain* inactive_domains = 0;
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
    travel_domain_init_from_fixture(fixture, &domain);
    if (inactive > 0u) {
        inactive_domains = (dom_travel_domain*)calloc(inactive, sizeof(dom_travel_domain));
        if (!inactive_domains) {
            dom_travel_domain_free(&domain);
            return 0;
        }
        for (u32 i = 0u; i < inactive; ++i) {
            travel_domain_init_from_fixture(fixture, &inactive_domains[i]);
            dom_travel_domain_set_state(&inactive_domains[i],
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
        if (travel_build_tile_desc(&domain, origin, DOM_DOMAIN_RES_COARSE, &desc)) {
            (void)dom_travel_domain_collapse_tile(&domain, &desc, start_tick);
        }
        capsule_count = dom_travel_domain_capsule_count(&domain);
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_travel_sample sample;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        u64 tick = start_tick + (step_ticks * (u64)i);
        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));
        dom_domain_budget_init(&budget, budget_max);
        if (dom_travel_sample_query(&domain, &p, tick, mode_id, &budget, &sample) != 0) {
            dom_travel_domain_free(&domain);
            if (inactive_domains) {
                for (u32 j = 0u; j < inactive; ++j) {
                    dom_travel_domain_free(&inactive_domains[j]);
                }
                free(inactive_domains);
            }
            return 0;
        }
        if (sample.flags & DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN) {
            unknown_steps += 1u;
        }
        if (sample.meta.cost_units > cost_max) {
            cost_max = sample.meta.cost_units;
        }
        hash = travel_hash_i32(hash, sample.travel_cost);
        hash = travel_hash_i32(hash, sample.weather_modifier);
        hash = travel_hash_i32(hash, sample.mode_modifier);
        hash = travel_hash_i32(hash, sample.total_cost);
        hash = travel_hash_i32(hash, sample.obstacle);
        hash = travel_hash_u32(hash, sample.structure_id);
        hash = travel_hash_u32(hash, sample.mode_id);
        hash = travel_hash_u32(hash, sample.flags);
    }
    dom_travel_domain_free(&domain);
    if (inactive_domains) {
        for (u32 i = 0u; i < inactive; ++i) {
            dom_travel_domain_free(&inactive_domains[i]);
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

static int travel_run_core_sample(const travel_fixture* fixture,
                                  const dom_domain_point* origin,
                                  const dom_domain_point* direction,
                                  q16_16 length,
                                  u32 steps,
                                  u64 start_tick,
                                  u64 step_ticks,
                                  u32 mode_id,
                                  u32 budget_max,
                                  u32 inactive,
                                  int collapse)
{
    u32 unknown_steps = 0u;
    u32 cost_max = 0u;
    u32 capsule_count = 0u;
    int ok = 0;
    u64 hash = travel_core_sample_hash(fixture, origin, direction, length, steps,
                                       start_tick, step_ticks, mode_id, budget_max,
                                       inactive, collapse,
                                       &unknown_steps, &cost_max, &capsule_count, &ok);
    if (!ok) {
        return 1;
    }
    printf("%s\n", TRAVEL_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRAVEL_PROVIDER_CHAIN);
    printf("mode_id=%u\n", (unsigned int)mode_id);
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

static int travel_run_diff(const travel_fixture* fixture_a,
                           const travel_fixture* fixture_b,
                           const dom_domain_point* origin,
                           const dom_domain_point* direction,
                           q16_16 length,
                           u32 steps,
                           u64 start_tick,
                           u64 step_ticks,
                           u32 mode_id,
                           u32 budget_max)
{
    int ok_a = 0;
    int ok_b = 0;
    u64 hash_a = travel_core_sample_hash(fixture_a, origin, direction, length, steps,
                                         start_tick, step_ticks, mode_id, budget_max,
                                         0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_a);
    u64 hash_b = travel_core_sample_hash(fixture_b, origin, direction, length, steps,
                                         start_tick, step_ticks, mode_id, budget_max,
                                         0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_b);
    if (!ok_a || !ok_b) {
        return 1;
    }
    printf("%s\n", TRAVEL_DIFF_HEADER);
    printf("fixture_a=%s\n", fixture_a->fixture_id);
    printf("fixture_b=%s\n", fixture_b->fixture_id);
    printf("hash_a=%llu\n", (unsigned long long)hash_a);
    printf("hash_b=%llu\n", (unsigned long long)hash_b);
    printf("equal=%u\n", (unsigned int)(hash_a == hash_b ? 1u : 0u));
    return 0;
}

static int travel_run_collapse(const travel_fixture* fixture,
                               const dom_domain_point* point,
                               u64 tick,
                               u32 mode_id,
                               u32 budget_max)
{
    dom_travel_domain domain;
    dom_domain_tile_desc desc;
    dom_domain_budget budget;
    dom_travel_sample inside;
    dom_travel_sample outside;
    dom_domain_point outside_point;
    u32 count_before;
    u32 count_after;
    u32 count_final;

    travel_domain_init_from_fixture(fixture, &domain);
    if (!travel_build_tile_desc(&domain, point, DOM_DOMAIN_RES_COARSE, &desc)) {
        dom_travel_domain_free(&domain);
        return 1;
    }
    count_before = dom_travel_domain_capsule_count(&domain);
    (void)dom_travel_domain_collapse_tile(&domain, &desc, tick);
    count_after = dom_travel_domain_capsule_count(&domain);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_travel_sample_query(&domain, point, tick, mode_id, &budget, &inside);

    outside_point = *point;
    outside_point.x = d_q16_16_add(outside_point.x,
                                   d_q16_16_mul(domain.policy.tile_size, d_q16_16_from_int(2)));
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_travel_sample_query(&domain, &outside_point, tick, mode_id, &budget, &outside);

    (void)dom_travel_domain_expand_tile(&domain, desc.tile_id);
    count_final = dom_travel_domain_capsule_count(&domain);

    printf("%s\n", TRAVEL_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRAVEL_PROVIDER_CHAIN);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);
    printf("capsule_count_final=%u\n", (unsigned int)count_final);
    printf("tile_id=%llu\n", (unsigned long long)desc.tile_id);
    printf("inside_flags=%u\n", (unsigned int)inside.flags);
    printf("outside_flags=%u\n", (unsigned int)outside.flags);

    dom_travel_domain_free(&domain);
    return 0;
}

static int travel_run_pathfind(const travel_fixture* fixture,
                               const dom_domain_point* origin,
                               const dom_domain_point* target,
                               u64 tick,
                               u32 mode_id,
                               u32 budget_max)
{
    dom_travel_domain domain;
    dom_domain_budget budget;
    dom_travel_path path;
    u64 hash = 14695981039346656037ULL;
    travel_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_travel_pathfind(&domain, origin, target, tick, mode_id, &budget, &path);
    for (u32 i = 0u; i < path.point_count; ++i) {
        hash = travel_hash_i32(hash, path.points[i].x);
        hash = travel_hash_i32(hash, path.points[i].y);
        hash = travel_hash_i32(hash, path.points[i].z);
    }
    printf("%s\n", TRAVEL_PATH_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRAVEL_PROVIDER_CHAIN);
    printf("mode_id=%u\n", (unsigned int)mode_id);
    printf("point_count=%u\n", (unsigned int)path.point_count);
    printf("total_cost_q16=%d\n", (int)path.total_cost);
    printf("visited_nodes=%u\n", (unsigned int)path.visited_nodes);
    printf("path_hash=%llu\n", (unsigned long long)hash);
    printf("flags=%u\n", (unsigned int)path.flags);
    printf("meta.status=%u\n", (unsigned int)path.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)path.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)path.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)path.meta.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    dom_travel_domain_free(&domain);
    return 0;
}

static int travel_run_render(const travel_fixture* fixture,
                             const dom_domain_point* center,
                             q16_16 radius,
                             u32 dim,
                             u64 tick,
                             u32 mode_id,
                             u32 budget_max)
{
    dom_travel_domain domain;
    u32 visible_cells = 0u;
    u32 touched_cells = 0u;
    q16_16 step = 0;
    q16_16 span = d_q16_16_mul(radius, d_q16_16_from_int(2));
    q16_16 half = d_fixed_div_q16_16(span, d_q16_16_from_int(2));
    travel_domain_init_from_fixture(fixture, &domain);
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
            if (travel_abs_q16_16(xoff) > radius || travel_abs_q16_16(yoff) > radius) {
                continue;
            }
            {
                dom_domain_point p = *center;
                dom_domain_budget budget;
                dom_travel_sample sample;
                p.x = d_q16_16_add(p.x, xoff);
                p.y = d_q16_16_add(p.y, yoff);
                dom_domain_budget_init(&budget, budget_max);
                (void)dom_travel_sample_query(&domain, &p, tick, mode_id, &budget, &sample);
                visible_cells += 1u;
                touched_cells += 1u;
            }
        }
    }
    printf("%s\n", TRAVEL_RENDER_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRAVEL_PROVIDER_CHAIN);
    printf("visible_cells=%u\n", (unsigned int)visible_cells);
    printf("touched_cells=%u\n", (unsigned int)touched_cells);
    dom_travel_domain_free(&domain);
    return 0;
}

static void travel_usage(void)
{
    printf("dom_tool_travel commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --pos x,y,z --tick T [--mode M] [--budget N]\n");
    printf("  core-sample --fixture <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--mode M] [--budget N] [--inactive N] [--collapsed 0|1]\n");
    printf("  diff --fixture-a <path> --fixture-b <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--mode M] [--budget N]\n");
    printf("  collapse --fixture <path> --pos x,y,z --tick T [--mode M] [--budget N]\n");
    printf("  pathfind --fixture <path> --origin x,y,z --target x,y,z --tick T [--mode M] [--budget N]\n");
    printf("  render --fixture <path> --center x,y,z --radius R [--dim N] [--tick T] [--mode M] [--budget N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        travel_usage();
        return 2;
    }
    cmd = argv[1];

    if (strcmp(cmd, "diff") == 0) {
        const char* fixture_a_path = travel_find_arg(argc, argv, "--fixture-a");
        const char* fixture_b_path = travel_find_arg(argc, argv, "--fixture-b");
        travel_fixture fixture_a;
        travel_fixture fixture_b;
        dom_domain_point origin;
        dom_domain_point direction;
        q16_16 length = d_q16_16_from_int(64);
        u32 steps = travel_find_arg_u32(argc, argv, "--steps", 16u);
        u64 start_tick = travel_find_arg_u64(argc, argv, "--start", 0u);
        u64 step_ticks = travel_find_arg_u64(argc, argv, "--step_ticks", 10u);
        u32 budget_max;
        u32 mode_id = travel_parse_mode_id(travel_find_arg(argc, argv, "--mode"));
        if (!fixture_a_path || !fixture_b_path ||
            !travel_fixture_load(fixture_a_path, &fixture_a) ||
            !travel_fixture_load(fixture_b_path, &fixture_b)) {
            fprintf(stderr, "travel: missing or invalid --fixture-a/--fixture-b\n");
            return 2;
        }
        if (!travel_parse_arg_point(argc, argv, "--origin", &origin) ||
            !travel_parse_arg_point(argc, argv, "--dir", &direction)) {
            fprintf(stderr, "travel: missing --origin or --dir\n");
            return 2;
        }
        if (!travel_parse_q16(travel_find_arg(argc, argv, "--length"), &length)) {
            length = d_q16_16_from_int(64);
        }
        budget_max = travel_find_arg_u32(argc, argv, "--budget", fixture_a.policy.cost_analytic);
        return travel_run_diff(&fixture_a, &fixture_b, &origin, &direction, length, steps,
                               start_tick, step_ticks, mode_id, budget_max);
    }

    {
        const char* fixture_path = travel_find_arg(argc, argv, "--fixture");
        travel_fixture fixture;
        if (!fixture_path || !travel_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "travel: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return travel_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            dom_domain_point point;
            u64 tick = travel_find_arg_u64(argc, argv, "--tick", 0u);
            u32 mode_id = travel_parse_mode_id(travel_find_arg(argc, argv, "--mode"));
            u32 budget_max = travel_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!travel_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "travel: missing --pos\n");
                return 2;
            }
            return travel_run_inspect(&fixture, &point, tick, mode_id, budget_max);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_domain_point origin;
            dom_domain_point direction;
            q16_16 length = d_q16_16_from_int(64);
            u32 steps = travel_find_arg_u32(argc, argv, "--steps", 16u);
            u64 start_tick = travel_find_arg_u64(argc, argv, "--start", 0u);
            u64 step_ticks = travel_find_arg_u64(argc, argv, "--step_ticks", 10u);
            u32 budget_max = travel_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 inactive = travel_find_arg_u32(argc, argv, "--inactive", 0u);
            u32 collapsed = travel_find_arg_u32(argc, argv, "--collapsed", 0u);
            u32 mode_id = travel_parse_mode_id(travel_find_arg(argc, argv, "--mode"));
            if (!travel_parse_arg_point(argc, argv, "--origin", &origin) ||
                !travel_parse_arg_point(argc, argv, "--dir", &direction)) {
                fprintf(stderr, "travel: missing --origin or --dir\n");
                return 2;
            }
            if (!travel_parse_q16(travel_find_arg(argc, argv, "--length"), &length)) {
                length = d_q16_16_from_int(64);
            }
            return travel_run_core_sample(&fixture, &origin, &direction, length, steps,
                                          start_tick, step_ticks, mode_id, budget_max,
                                          inactive, collapsed ? 1 : 0);
        }

        if (strcmp(cmd, "collapse") == 0) {
            dom_domain_point point;
            u64 tick = travel_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = travel_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 mode_id = travel_parse_mode_id(travel_find_arg(argc, argv, "--mode"));
            if (!travel_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "travel: missing --pos\n");
                return 2;
            }
            return travel_run_collapse(&fixture, &point, tick, mode_id, budget_max);
        }

        if (strcmp(cmd, "pathfind") == 0) {
            dom_domain_point origin;
            dom_domain_point target;
            u64 tick = travel_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = travel_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 mode_id = travel_parse_mode_id(travel_find_arg(argc, argv, "--mode"));
            if (!travel_parse_arg_point(argc, argv, "--origin", &origin) ||
                !travel_parse_arg_point(argc, argv, "--target", &target)) {
                fprintf(stderr, "travel: missing --origin or --target\n");
                return 2;
            }
            return travel_run_pathfind(&fixture, &origin, &target, tick, mode_id, budget_max);
        }

        if (strcmp(cmd, "render") == 0) {
            dom_domain_point center;
            q16_16 radius;
            u64 tick = travel_find_arg_u64(argc, argv, "--tick", 0u);
            u32 dim = travel_find_arg_u32(argc, argv, "--dim", 8u);
            u32 budget_max = travel_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 mode_id = travel_parse_mode_id(travel_find_arg(argc, argv, "--mode"));
            if (!travel_parse_arg_point(argc, argv, "--center", &center)) {
                fprintf(stderr, "travel: missing --center\n");
                return 2;
            }
            if (!travel_parse_q16(travel_find_arg(argc, argv, "--radius"), &radius)) {
                fprintf(stderr, "travel: missing --radius\n");
                return 2;
            }
            return travel_run_render(&fixture, &center, radius, dim, tick, mode_id, budget_max);
        }
    }

    travel_usage();
    return 2;
}
