/*
FILE: tools/animal/animal_cli.cpp
MODULE: Dominium
PURPOSE: Animal fixture CLI for deterministic agent sampling and lifecycle checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/animal_agents.h"

#define ANIMAL_FIXTURE_HEADER "DOMINIUM_ANIMAL_FIXTURE_V1"

#define ANIMAL_VALIDATE_HEADER "DOMINIUM_ANIMAL_VALIDATE_V1"
#define ANIMAL_INSPECT_HEADER "DOMINIUM_ANIMAL_INSPECT_V1"
#define ANIMAL_CORE_SAMPLE_HEADER "DOMINIUM_ANIMAL_CORE_SAMPLE_V1"
#define ANIMAL_DIFF_HEADER "DOMINIUM_ANIMAL_DIFF_V1"
#define ANIMAL_COLLAPSE_HEADER "DOMINIUM_ANIMAL_COLLAPSE_V1"

#define ANIMAL_PROVIDER_CHAIN "terrain->climate->weather->geology->vegetation->animal"

#define ANIMAL_LINE_MAX 512u

typedef struct animal_fixture {
    char fixture_id[96];
    dom_animal_surface_desc desc;
    dom_domain_policy policy;
    u32 cache_capacity;
    u32 policy_set;
} animal_fixture;

static u64 animal_hash_u64(u64 h, u64 v)
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

static u64 animal_hash_u32(u64 h, u32 v)
{
    return animal_hash_u64(h, (u64)v);
}

static u64 animal_hash_i32(u64 h, i32 v)
{
    return animal_hash_u64(h, (u64)(u32)v);
}

static char* animal_trim(char* text)
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

static int animal_parse_u32(const char* text, u32* out_value)
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

static int animal_parse_u64(const char* text, u64* out_value)
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

static int animal_parse_q16(const char* text, q16_16* out_value)
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

static i32 animal_floor_div_q16(q16_16 value, q16_16 denom)
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

static int animal_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[ANIMAL_LINE_MAX];
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
    if (!animal_parse_q16(animal_trim(first), a)) return 0;
    if (!animal_parse_q16(animal_trim(second), b)) return 0;
    if (!animal_parse_q16(animal_trim(third), c)) return 0;
    return 1;
}

static int animal_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!animal_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 animal_parse_resolution(const char* text)
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

static int animal_parse_indexed_key(const char* key,
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

static void animal_biome_rule_init(dom_climate_biome_rule* rule)
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

static void animal_species_defaults(dom_animal_species_desc* species)
{
    if (!species) {
        return;
    }
    memset(species, 0, sizeof(*species));
    species->climate_tolerance.temperature_min = d_q16_16_from_int(0);
    species->climate_tolerance.temperature_max = d_q16_16_from_int(1);
    species->climate_tolerance.moisture_min = d_q16_16_from_int(0);
    species->climate_tolerance.moisture_max = d_q16_16_from_int(1);
    species->movement_mode = DOM_ANIMAL_MOVE_LAND;
    species->metabolism.energy_consumption_rate = d_q16_16_from_double(0.1);
    species->metabolism.rest_requirement = d_q16_16_from_double(0.4);
    species->reproduction.maturity_age_ticks = 400u;
    species->reproduction.gestation_ticks = 200u;
    species->reproduction.offspring_min = 1u;
    species->reproduction.offspring_max = 2u;
    species->reproduction.reproduction_chance = d_q16_16_from_double(0.5);
    species->lifespan_ticks = 1600u;
    species->movement_speed = d_q16_16_from_double(0.2);
    species->slope_max = d_q16_16_from_double(0.8);
    species->death_rate = d_q16_16_from_double(0.1);
    species->maturity_tag = 0u;
}

static void animal_fixture_init(animal_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_animal_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->cache_capacity = 128u;
    fixture->policy_set = 0u;
    strncpy(fixture->fixture_id, "animal.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
    fixture->desc.cache_capacity = fixture->cache_capacity;
    fixture->desc.vegetation_desc.cache_capacity = fixture->cache_capacity;
    for (u32 i = 0u; i < DOM_ANIMAL_MAX_SPECIES; ++i) {
        animal_species_defaults(&fixture->desc.species[i]);
    }
    for (u32 i = 0u; i < DOM_CLIMATE_MAX_BIOMES; ++i) {
        animal_biome_rule_init(&fixture->desc.vegetation_desc.biome_catalog.rules[i]);
    }
}

static int animal_fixture_apply_biome(animal_fixture* fixture,
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
    if (fixture->desc.vegetation_desc.biome_catalog.biome_count <= index) {
        fixture->desc.vegetation_desc.biome_catalog.biome_count = index + 1u;
    }
    rule = &fixture->desc.vegetation_desc.biome_catalog.rules[index];
    if (strcmp(suffix, "id") == 0) {
        rule->biome_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "temp_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_TEMP;
        return animal_parse_q16(value, &rule->temp_min);
    }
    if (strcmp(suffix, "temp_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_TEMP;
        return animal_parse_q16(value, &rule->temp_max);
    }
    if (strcmp(suffix, "precip_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_PRECIP;
        return animal_parse_q16(value, &rule->precip_min);
    }
    if (strcmp(suffix, "precip_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_PRECIP;
        return animal_parse_q16(value, &rule->precip_max);
    }
    if (strcmp(suffix, "season_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_SEASON;
        return animal_parse_q16(value, &rule->season_min);
    }
    if (strcmp(suffix, "season_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_SEASON;
        return animal_parse_q16(value, &rule->season_max);
    }
    if (strcmp(suffix, "elevation_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_ELEVATION;
        return animal_parse_q16(value, &rule->elevation_min);
    }
    if (strcmp(suffix, "elevation_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_ELEVATION;
        return animal_parse_q16(value, &rule->elevation_max);
    }
    if (strcmp(suffix, "moisture_min") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_MOISTURE;
        return animal_parse_q16(value, &rule->moisture_min);
    }
    if (strcmp(suffix, "moisture_max") == 0) {
        rule->mask |= DOM_CLIMATE_BIOME_RULE_MOISTURE;
        return animal_parse_q16(value, &rule->moisture_max);
    }
    return 0;
}

static int animal_parse_movement_mode(const char* value, u32* out_mode)
{
    if (!value || !out_mode) {
        return 0;
    }
    if (strcmp(value, "land") == 0) {
        *out_mode = DOM_ANIMAL_MOVE_LAND;
        return 1;
    }
    if (strcmp(value, "water") == 0) {
        *out_mode = DOM_ANIMAL_MOVE_WATER;
        return 1;
    }
    if (strcmp(value, "air") == 0) {
        *out_mode = DOM_ANIMAL_MOVE_AIR;
        return 1;
    }
    return animal_parse_u32(value, out_mode);
}

static int animal_species_apply(animal_fixture* fixture,
                                u32 index,
                                const char* suffix,
                                const char* value)
{
    dom_animal_species_desc* species;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ANIMAL_MAX_SPECIES) {
        return 0;
    }
    if (fixture->desc.species_count <= index) {
        fixture->desc.species_count = index + 1u;
    }
    species = &fixture->desc.species[index];
    if (strcmp(suffix, "id") == 0) {
        species->species_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "biome_count") == 0) {
        return animal_parse_u32(value, &species->preferred_biome_count);
    }
    if (strncmp(suffix, "biome", 5) == 0) {
        u32 biome_index = 0u;
        if (animal_parse_u32(suffix + 5, &biome_index) && biome_index < DOM_ANIMAL_MAX_BIOMES) {
            species->preferred_biomes[biome_index] = d_rng_hash_str32(value);
            if (species->preferred_biome_count <= biome_index) {
                species->preferred_biome_count = biome_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "temp_min") == 0) {
        return animal_parse_q16(value, &species->climate_tolerance.temperature_min);
    }
    if (strcmp(suffix, "temp_max") == 0) {
        return animal_parse_q16(value, &species->climate_tolerance.temperature_max);
    }
    if (strcmp(suffix, "moisture_min") == 0) {
        return animal_parse_q16(value, &species->climate_tolerance.moisture_min);
    }
    if (strcmp(suffix, "moisture_max") == 0) {
        return animal_parse_q16(value, &species->climate_tolerance.moisture_max);
    }
    if (strcmp(suffix, "movement_mode") == 0) {
        return animal_parse_movement_mode(value, &species->movement_mode);
    }
    if (strcmp(suffix, "diet_count") == 0) {
        return animal_parse_u32(value, &species->diet_count);
    }
    if (strncmp(suffix, "diet", 4) == 0) {
        u32 diet_index = 0u;
        if (animal_parse_u32(suffix + 4, &diet_index) && diet_index < DOM_ANIMAL_MAX_DIET) {
            species->diet_species[diet_index] = d_rng_hash_str32(value);
            if (species->diet_count <= diet_index) {
                species->diet_count = diet_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "energy_rate") == 0) {
        return animal_parse_q16(value, &species->metabolism.energy_consumption_rate);
    }
    if (strcmp(suffix, "rest_requirement") == 0) {
        return animal_parse_q16(value, &species->metabolism.rest_requirement);
    }
    if (strcmp(suffix, "maturity_age_ticks") == 0) {
        return animal_parse_u64(value, &species->reproduction.maturity_age_ticks);
    }
    if (strcmp(suffix, "gestation_ticks") == 0) {
        return animal_parse_u64(value, &species->reproduction.gestation_ticks);
    }
    if (strcmp(suffix, "offspring_min") == 0) {
        return animal_parse_u32(value, &species->reproduction.offspring_min);
    }
    if (strcmp(suffix, "offspring_max") == 0) {
        return animal_parse_u32(value, &species->reproduction.offspring_max);
    }
    if (strcmp(suffix, "reproduction_chance") == 0) {
        return animal_parse_q16(value, &species->reproduction.reproduction_chance);
    }
    if (strcmp(suffix, "lifespan_ticks") == 0) {
        return animal_parse_u64(value, &species->lifespan_ticks);
    }
    if (strcmp(suffix, "size_class") == 0) {
        return animal_parse_u32(value, &species->size_class);
    }
    if (strcmp(suffix, "movement_speed") == 0) {
        return animal_parse_q16(value, &species->movement_speed);
    }
    if (strcmp(suffix, "slope_max") == 0) {
        return animal_parse_q16(value, &species->slope_max);
    }
    if (strcmp(suffix, "death_rate") == 0) {
        return animal_parse_q16(value, &species->death_rate);
    }
    if (strcmp(suffix, "maturity") == 0) {
        if (strcmp(value, "BOUNDED") == 0) {
            species->maturity_tag = 1u;
            return 1;
        }
        if (strcmp(value, "STRUCTURAL") == 0) {
            species->maturity_tag = 2u;
            return 1;
        }
        return animal_parse_u32(value, &species->maturity_tag);
    }
    return 0;
}

static int animal_event_type_from_name(const char* name, u32* out_type)
{
    if (!name || !out_type) {
        return 0;
    }
    if (strcmp(name, "rain") == 0) {
        *out_type = DOM_WEATHER_EVENT_RAIN;
        return 1;
    }
    if (strcmp(name, "snow") == 0) {
        *out_type = DOM_WEATHER_EVENT_SNOW;
        return 1;
    }
    if (strcmp(name, "heatwave") == 0) {
        *out_type = DOM_WEATHER_EVENT_HEATWAVE;
        return 1;
    }
    if (strcmp(name, "cold_snap") == 0) {
        *out_type = DOM_WEATHER_EVENT_COLD_SNAP;
        return 1;
    }
    if (strcmp(name, "wind_shift") == 0) {
        *out_type = DOM_WEATHER_EVENT_WIND_SHIFT;
        return 1;
    }
    return 0;
}

static int animal_fixture_apply_event(animal_fixture* fixture,
                                      u32 event_type,
                                      const char* field,
                                      const char* value)
{
    dom_weather_event_profile* profile;
    if (!fixture || !field || !value || event_type >= DOM_WEATHER_EVENT_TYPE_COUNT) {
        return 0;
    }
    profile = &fixture->desc.vegetation_desc.weather_schedule.profiles[event_type];
    if (strcmp(field, "period_ticks") == 0) {
        return animal_parse_u64(value, &profile->period_ticks);
    }
    if (strcmp(field, "duration_ticks") == 0) {
        return animal_parse_u64(value, &profile->duration_ticks);
    }
    if (strcmp(field, "intensity_min") == 0) {
        return animal_parse_q16(value, &profile->intensity_min);
    }
    if (strcmp(field, "intensity_max") == 0) {
        return animal_parse_q16(value, &profile->intensity_max);
    }
    if (strcmp(field, "radius_ratio_min") == 0) {
        return animal_parse_q16(value, &profile->radius_ratio_min);
    }
    if (strcmp(field, "radius_ratio_max") == 0) {
        return animal_parse_q16(value, &profile->radius_ratio_max);
    }
    if (strcmp(field, "temp_scale") == 0) {
        return animal_parse_q16(value, &profile->temp_scale);
    }
    if (strcmp(field, "precip_scale") == 0) {
        return animal_parse_q16(value, &profile->precip_scale);
    }
    if (strcmp(field, "wetness_scale") == 0) {
        return animal_parse_q16(value, &profile->wetness_scale);
    }
    return 0;
}

static int animal_fixture_apply(animal_fixture* fixture, const char* key, const char* value)
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
        return animal_parse_u64(value, &fixture->desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return animal_parse_u64(value, &fixture->desc.domain_id);
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
        return animal_parse_q16(value, &fixture->desc.shape.radius_equatorial);
    }
    if (strcmp(key, "radius_polar") == 0) {
        return animal_parse_q16(value, &fixture->desc.shape.radius_polar);
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        return animal_parse_q16(value, &fixture->desc.shape.slab_half_extent);
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        return animal_parse_q16(value, &fixture->desc.shape.slab_half_thickness);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return animal_parse_q16(value, &fixture->desc.meters_per_unit);
    }
    if (strcmp(key, "placement_cell_size") == 0) {
        return animal_parse_q16(value, &fixture->desc.placement_cell_size);
    }
    if (strcmp(key, "density_base") == 0) {
        return animal_parse_q16(value, &fixture->desc.density_base);
    }
    if (strcmp(key, "decision_period_ticks") == 0) {
        return animal_parse_u64(value, &fixture->desc.decision_period_ticks);
    }
    if (strcmp(key, "cache_capacity") == 0) {
        if (animal_parse_u32(value, &fixture->cache_capacity)) {
            fixture->desc.cache_capacity = fixture->cache_capacity;
            fixture->desc.vegetation_desc.cache_capacity = fixture->cache_capacity;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_q16(value, &fixture->policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->policy.max_resolution = animal_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_q16(value, &fixture->policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return animal_parse_u32(value, &fixture->policy.max_ray_steps);
    }
    if (strcmp(key, "terrain_noise_seed") == 0) {
        return animal_parse_u64(value, &fixture->desc.vegetation_desc.terrain_desc.noise.seed);
    }
    if (strcmp(key, "terrain_noise_amplitude") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.terrain_desc.noise.amplitude);
    }
    if (strcmp(key, "terrain_noise_cell_size") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.terrain_desc.noise.cell_size);
    }
    if (strcmp(key, "terrain_roughness_base") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.terrain_desc.roughness_base);
    }
    if (strcmp(key, "terrain_travel_cost_base") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.terrain_desc.travel_cost_base);
    }
    if (strcmp(key, "terrain_travel_cost_slope_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.terrain_desc.travel_cost_slope_scale);
    }
    if (strcmp(key, "terrain_travel_cost_roughness_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.terrain_desc.travel_cost_roughness_scale);
    }
    if (strcmp(key, "terrain_material_primary") == 0) {
        return animal_parse_u32(value, &fixture->desc.vegetation_desc.terrain_desc.material_primary);
    }
    if (strcmp(key, "terrain_walkable_max_slope") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.terrain_desc.walkable_max_slope);
    }
    if (strcmp(key, "noise_seed") == 0) {
        return animal_parse_u64(value, &fixture->desc.vegetation_desc.climate_desc.noise.seed);
    }
    if (strcmp(key, "noise_amplitude") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.noise.amplitude);
    }
    if (strcmp(key, "noise_cell_size") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.noise.cell_size);
    }
    if (strcmp(key, "temp_equator") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.temp_equator);
    }
    if (strcmp(key, "temp_pole") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.temp_pole);
    }
    if (strcmp(key, "temp_altitude_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.temp_altitude_scale);
    }
    if (strcmp(key, "temp_range_base") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.temp_range_base);
    }
    if (strcmp(key, "temp_range_lat_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.temp_range_lat_scale);
    }
    if (strcmp(key, "precip_equator") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.precip_equator);
    }
    if (strcmp(key, "precip_pole") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.precip_pole);
    }
    if (strcmp(key, "precip_altitude_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.precip_altitude_scale);
    }
    if (strcmp(key, "precip_range_base") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.precip_range_base);
    }
    if (strcmp(key, "precip_range_lat_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.precip_range_lat_scale);
    }
    if (strcmp(key, "seasonality_base") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.seasonality_base);
    }
    if (strcmp(key, "seasonality_lat_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.seasonality_lat_scale);
    }
    if (strcmp(key, "noise_temp_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.noise_temp_scale);
    }
    if (strcmp(key, "noise_precip_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.noise_precip_scale);
    }
    if (strcmp(key, "noise_season_scale") == 0) {
        return animal_parse_q16(value, &fixture->desc.vegetation_desc.climate_desc.noise_season_scale);
    }
    if (strcmp(key, "wind_band_count") == 0) {
        return animal_parse_u32(value, &fixture->desc.vegetation_desc.climate_desc.wind_band_count);
    }
    if (strcmp(key, "weather_seed") == 0) {
        return animal_parse_u64(value, &fixture->desc.vegetation_desc.weather_schedule.seed);
    }
    if (strcmp(key, "biome_count") == 0) {
        return animal_parse_u32(value, &fixture->desc.vegetation_desc.biome_catalog.biome_count);
    }
    if (strcmp(key, "species_count") == 0) {
        return animal_parse_u32(value, &fixture->desc.species_count);
    }
    if (animal_parse_indexed_key(key, "biome", &index, &suffix)) {
        return animal_fixture_apply_biome(fixture, index, suffix, value);
    }
    if (animal_parse_indexed_key(key, "species", &index, &suffix)) {
        return animal_species_apply(fixture, index, suffix, value);
    }
    if (strncmp(key, "event.", 6) == 0) {
        const char* name = key + 6;
        const char* field = strchr(name, '.');
        if (!field) {
            return 0;
        }
        {
            u32 event_type = 0u;
            char event_name[64];
            size_t name_len = (size_t)(field - name);
            if (name_len >= sizeof(event_name)) {
                return 0;
            }
            memcpy(event_name, name, name_len);
            event_name[name_len] = '\0';
            if (!animal_event_type_from_name(event_name, &event_type)) {
                return 0;
            }
            return animal_fixture_apply_event(fixture, event_type, field + 1, value);
        }
    }
    return 0;
}

static int animal_fixture_load(const char* path, animal_fixture* out_fixture)
{
    FILE* handle;
    char line[ANIMAL_LINE_MAX];
    u32 line_no = 0u;
    if (!path || !out_fixture) {
        return 0;
    }
    handle = fopen(path, "r");
    if (!handle) {
        return 0;
    }
    animal_fixture_init(out_fixture);
    while (fgets(line, sizeof(line), handle)) {
        char* cursor;
        char* eq;
        line_no += 1u;
        cursor = animal_trim(line);
        if (!cursor[0] || cursor[0] == '#') {
            continue;
        }
        if (line_no == 1u) {
            if (strcmp(cursor, ANIMAL_FIXTURE_HEADER) != 0) {
                fclose(handle);
                return 0;
            }
            continue;
        }
        eq = strchr(cursor, '=');
        if (!eq) {
            fclose(handle);
            return 0;
        }
        *eq++ = '\0';
        if (!animal_fixture_apply(out_fixture, animal_trim(cursor), animal_trim(eq))) {
            fclose(handle);
            return 0;
        }
    }
    fclose(handle);
    return 1;
}

static void animal_domain_init_from_fixture(const animal_fixture* fixture,
                                            dom_animal_domain* out_domain)
{
    dom_animal_surface_desc desc;
    if (!fixture || !out_domain) {
        return;
    }
    desc = fixture->desc;
    desc.domain_id = fixture->desc.domain_id;
    desc.world_seed = fixture->desc.world_seed;
    desc.meters_per_unit = fixture->desc.meters_per_unit;
    desc.shape = fixture->desc.shape;
    desc.cache_capacity = fixture->cache_capacity;
    desc.vegetation_desc.cache_capacity = fixture->cache_capacity;

    desc.vegetation_desc.domain_id = desc.domain_id;
    desc.vegetation_desc.world_seed = desc.world_seed;
    desc.vegetation_desc.meters_per_unit = desc.meters_per_unit;
    desc.vegetation_desc.shape = desc.shape;
    desc.vegetation_desc.terrain_desc.domain_id = desc.domain_id;
    desc.vegetation_desc.terrain_desc.world_seed = desc.world_seed;
    desc.vegetation_desc.terrain_desc.meters_per_unit = desc.meters_per_unit;
    desc.vegetation_desc.terrain_desc.shape = desc.shape;
    desc.vegetation_desc.climate_desc.domain_id = desc.domain_id;
    desc.vegetation_desc.climate_desc.world_seed = desc.world_seed;
    desc.vegetation_desc.climate_desc.meters_per_unit = desc.meters_per_unit;
    desc.vegetation_desc.climate_desc.shape = desc.shape;
    desc.vegetation_desc.geology_desc.domain_id = desc.domain_id;
    desc.vegetation_desc.geology_desc.world_seed = desc.world_seed;
    desc.vegetation_desc.geology_desc.meters_per_unit = desc.meters_per_unit;
    desc.vegetation_desc.geology_desc.shape = desc.shape;

    dom_animal_domain_init(out_domain, &desc);
    if (fixture->policy_set) {
        dom_animal_domain_set_policy(out_domain, &fixture->policy);
    }
}

static const char* animal_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 1; i < argc - 1; ++i) {
        if (strcmp(argv[i], key) == 0) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 animal_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = animal_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && animal_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 animal_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = animal_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && animal_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static int animal_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* value = animal_find_arg(argc, argv, key);
    if (!value || !out_point) {
        return 0;
    }
    return animal_parse_point(value, out_point);
}

static int animal_build_tile_desc(const dom_animal_domain* domain,
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
    source = dom_terrain_surface_sdf(&domain->vegetation_domain.terrain_domain.surface);
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
    tx = animal_floor_div_q16((q16_16)(point->x - source->bounds.min.x), tile_size);
    ty = animal_floor_div_q16((q16_16)(point->y - source->bounds.min.y), tile_size);
    tz = animal_floor_div_q16((q16_16)(point->z - source->bounds.min.z), tile_size);
    dom_domain_tile_desc_init(out_desc);
    out_desc->resolution = resolution;
    out_desc->sample_dim = sample_dim;
    out_desc->tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, resolution);
    out_desc->authoring_version = domain->authoring_version;

    {
        dom_domain_point minp;
        dom_domain_point maxp;
        minp.x = (q16_16)(source->bounds.min.x + (q16_16)((i64)tx * (i64)tile_size));
        minp.y = (q16_16)(source->bounds.min.y + (q16_16)((i64)ty * (i64)tile_size));
        minp.z = (q16_16)(source->bounds.min.z + (q16_16)((i64)tz * (i64)tile_size));

        maxp.x = (q16_16)(minp.x + tile_size);
        maxp.y = (q16_16)(minp.y + tile_size);
        maxp.z = (q16_16)(minp.z + tile_size);

        if (maxp.x > source->bounds.max.x) maxp.x = source->bounds.max.x;
        if (maxp.y > source->bounds.max.y) maxp.y = source->bounds.max.y;
        if (maxp.z > source->bounds.max.z) maxp.z = source->bounds.max.z;

        if (minp.x < source->bounds.min.x) minp.x = source->bounds.min.x;
        if (minp.y < source->bounds.min.y) minp.y = source->bounds.min.y;
        if (minp.z < source->bounds.min.z) minp.z = source->bounds.min.z;

        out_desc->bounds.min = minp;
        out_desc->bounds.max = maxp;
    }
    return 1;
}

static int animal_run_validate(const animal_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    printf("%s\n", ANIMAL_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ANIMAL_PROVIDER_CHAIN);
    printf("species_count=%u\n", (unsigned int)fixture->desc.species_count);
    printf("biome_count=%u\n", (unsigned int)fixture->desc.vegetation_desc.biome_catalog.biome_count);
    return 0;
}

static int animal_run_inspect(const animal_fixture* fixture,
                              const dom_domain_point* point,
                              u64 tick,
                              u32 budget_max)
{
    dom_animal_domain domain;
    dom_domain_budget budget;
    dom_animal_sample sample;
    u32 fields_unknown;
    u32 collapsed;
    if (!fixture || !point) {
        return 1;
    }
    animal_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    if (dom_animal_sample_query(&domain, point, tick, &budget, &sample) != 0) {
        dom_animal_domain_free(&domain);
        return 1;
    }
    fields_unknown = (sample.flags & DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN) ? 1u : 0u;
    collapsed = (sample.flags & DOM_ANIMAL_SAMPLE_COLLAPSED) ? 1u : 0u;
    printf("%s\n", ANIMAL_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ANIMAL_PROVIDER_CHAIN);
    printf("pos_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("tick=%llu\n", (unsigned long long)tick);
    printf("suitability_q16=%d\n", (int)sample.suitability);
    printf("biome_id=%u\n", (unsigned int)sample.biome_id);
    printf("vegetation_coverage_q16=%d\n", (int)sample.vegetation_coverage);
    printf("vegetation_consumed_q16=%d\n", (int)sample.vegetation_consumed);
    printf("agent_present=%u\n", (unsigned int)((sample.flags & DOM_ANIMAL_SAMPLE_AGENT_PRESENT) ? 1u : 0u));
    printf("species_id=%u\n", (unsigned int)sample.agent.species_id);
    printf("energy_q16=%d\n", (int)sample.agent.energy);
    printf("health_q16=%d\n", (int)sample.agent.health);
    printf("age_ticks=%llu\n", (unsigned long long)sample.agent.age_ticks);
    printf("need=%u\n", (unsigned int)sample.agent.current_need);
    printf("death_reason=%u\n", (unsigned int)sample.death_reason);
    printf("agent_pos_q16=%d,%d,%d\n", (int)sample.agent.location.x,
           (int)sample.agent.location.y,
           (int)sample.agent.location.z);
    printf("fields_unknown=%u\n", (unsigned int)fields_unknown);
    printf("collapsed=%u\n", (unsigned int)collapsed);
    dom_animal_domain_free(&domain);
    return 0;
}

static u64 animal_core_sample_hash(const animal_fixture* fixture,
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
    dom_animal_domain domain;
    dom_animal_domain* inactive_domains = 0;
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
    animal_domain_init_from_fixture(fixture, &domain);
    if (inactive > 0u) {
        inactive_domains = (dom_animal_domain*)calloc(inactive, sizeof(dom_animal_domain));
        if (!inactive_domains) {
            dom_animal_domain_free(&domain);
            return 0;
        }
        for (u32 i = 0u; i < inactive; ++i) {
            animal_domain_init_from_fixture(fixture, &inactive_domains[i]);
            dom_animal_domain_set_state(&inactive_domains[i],
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
        if (animal_build_tile_desc(&domain, origin, DOM_DOMAIN_RES_COARSE, &desc)) {
            (void)dom_animal_domain_collapse_tile(&domain, &desc, start_tick);
        }
        capsule_count = dom_animal_domain_capsule_count(&domain);
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_animal_sample sample;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        u64 tick = start_tick + (step_ticks * (u64)i);
        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));
        dom_domain_budget_init(&budget, budget_max);
        if (dom_animal_sample_query(&domain, &p, tick, &budget, &sample) != 0) {
            dom_animal_domain_free(&domain);
            if (inactive_domains) {
                for (u32 j = 0u; j < inactive; ++j) {
                    dom_animal_domain_free(&inactive_domains[j]);
                }
                free(inactive_domains);
            }
            return 0;
        }
        if (sample.flags & DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN) {
            unknown_steps += 1u;
        }
        if (sample.meta.cost_units > cost_max) {
            cost_max = sample.meta.cost_units;
        }
        hash = animal_hash_i32(hash, sample.suitability);
        hash = animal_hash_u32(hash, sample.biome_id);
        hash = animal_hash_i32(hash, sample.vegetation_coverage);
        hash = animal_hash_i32(hash, sample.vegetation_consumed);
        hash = animal_hash_u32(hash, sample.flags);
        hash = animal_hash_u32(hash, sample.agent.species_id);
        hash = animal_hash_i32(hash, sample.agent.energy);
        hash = animal_hash_i32(hash, sample.agent.health);
        hash = animal_hash_u32(hash, sample.agent.current_need);
        hash = animal_hash_u32(hash, sample.death_reason);
    }
    dom_animal_domain_free(&domain);
    if (inactive_domains) {
        for (u32 i = 0u; i < inactive; ++i) {
            dom_animal_domain_free(&inactive_domains[i]);
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

static int animal_run_core_sample(const animal_fixture* fixture,
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
    u64 hash = animal_core_sample_hash(fixture, origin, direction, length, steps,
                                       start_tick, step_ticks, budget_max,
                                       inactive, collapse,
                                       &unknown_steps, &cost_max, &capsule_count, &ok);
    if (!ok) {
        return 1;
    }
    printf("%s\n", ANIMAL_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ANIMAL_PROVIDER_CHAIN);
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

static int animal_run_diff(const animal_fixture* fixture_a,
                           const animal_fixture* fixture_b,
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
    u64 hash_a = animal_core_sample_hash(fixture_a, origin, direction, length, steps,
                                         start_tick, step_ticks, budget_max,
                                         0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_a);
    u64 hash_b = animal_core_sample_hash(fixture_b, origin, direction, length, steps,
                                         start_tick, step_ticks, budget_max,
                                         0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_b);
    if (!ok_a || !ok_b) {
        return 1;
    }
    printf("%s\n", ANIMAL_DIFF_HEADER);
    printf("fixture_a=%s\n", fixture_a->fixture_id);
    printf("fixture_b=%s\n", fixture_b->fixture_id);
    printf("hash_a=%llu\n", (unsigned long long)hash_a);
    printf("hash_b=%llu\n", (unsigned long long)hash_b);
    printf("equal=%u\n", (unsigned int)(hash_a == hash_b ? 1u : 0u));
    return 0;
}

static int animal_run_collapse(const animal_fixture* fixture,
                               const dom_domain_point* point,
                               u64 tick,
                               u32 budget_max)
{
    dom_animal_domain domain;
    dom_domain_tile_desc desc;
    dom_domain_budget budget;
    dom_animal_sample inside;
    dom_animal_sample outside;
    dom_domain_point outside_point;
    u32 count_before;
    u32 count_after;
    u32 count_final;

    animal_domain_init_from_fixture(fixture, &domain);
    if (!animal_build_tile_desc(&domain, point, DOM_DOMAIN_RES_COARSE, &desc)) {
        dom_animal_domain_free(&domain);
        return 1;
    }
    count_before = dom_animal_domain_capsule_count(&domain);
    (void)dom_animal_domain_collapse_tile(&domain, &desc, tick);
    count_after = dom_animal_domain_capsule_count(&domain);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_animal_sample_query(&domain, point, tick, &budget, &inside);

    outside_point = *point;
    outside_point.x = d_q16_16_add(outside_point.x,
                                   d_q16_16_mul(domain.policy.tile_size, d_q16_16_from_int(2)));
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_animal_sample_query(&domain, &outside_point, tick, &budget, &outside);

    (void)dom_animal_domain_expand_tile(&domain, desc.tile_id);
    count_final = dom_animal_domain_capsule_count(&domain);

    printf("%s\n", ANIMAL_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ANIMAL_PROVIDER_CHAIN);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);
    printf("capsule_count_final=%u\n", (unsigned int)count_final);
    printf("tile_id=%llu\n", (unsigned long long)desc.tile_id);
    printf("inside_flags=%u\n", (unsigned int)inside.flags);
    printf("outside_flags=%u\n", (unsigned int)outside.flags);

    dom_animal_domain_free(&domain);
    return 0;
}

static void animal_usage(void)
{
    printf("dom_tool_animal commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --pos x,y,z --tick T [--budget N]\n");
    printf("  core-sample --fixture <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--budget N] [--inactive N] [--collapsed 0|1]\n");
    printf("  diff --fixture-a <path> --fixture-b <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--budget N]\n");
    printf("  collapse --fixture <path> --pos x,y,z --tick T [--budget N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        animal_usage();
        return 2;
    }
    cmd = argv[1];

    if (strcmp(cmd, "diff") == 0) {
        const char* fixture_a_path = animal_find_arg(argc, argv, "--fixture-a");
        const char* fixture_b_path = animal_find_arg(argc, argv, "--fixture-b");
        animal_fixture fixture_a;
        animal_fixture fixture_b;
        dom_domain_point origin;
        dom_domain_point direction;
        q16_16 length = d_q16_16_from_int(64);
        u32 steps = animal_find_arg_u32(argc, argv, "--steps", 16u);
        u64 start_tick = animal_find_arg_u64(argc, argv, "--start", 0u);
        u64 step_ticks = animal_find_arg_u64(argc, argv, "--step_ticks", 10u);
        u32 budget_max;
        if (!fixture_a_path || !fixture_b_path ||
            !animal_fixture_load(fixture_a_path, &fixture_a) ||
            !animal_fixture_load(fixture_b_path, &fixture_b)) {
            fprintf(stderr, "animal: missing or invalid --fixture-a/--fixture-b\n");
            return 2;
        }
        if (!animal_parse_arg_point(argc, argv, "--origin", &origin) ||
            !animal_parse_arg_point(argc, argv, "--dir", &direction)) {
            fprintf(stderr, "animal: missing --origin or --dir\n");
            return 2;
        }
        if (!animal_parse_q16(animal_find_arg(argc, argv, "--length"), &length)) {
            length = d_q16_16_from_int(64);
        }
        budget_max = animal_find_arg_u32(argc, argv, "--budget", fixture_a.policy.cost_analytic);
        return animal_run_diff(&fixture_a, &fixture_b, &origin, &direction, length, steps,
                               start_tick, step_ticks, budget_max);
    }

    {
        const char* fixture_path = animal_find_arg(argc, argv, "--fixture");
        animal_fixture fixture;
        if (!fixture_path || !animal_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "animal: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return animal_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            dom_domain_point point;
            u64 tick = animal_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = animal_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!animal_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "animal: missing --pos\n");
                return 2;
            }
            return animal_run_inspect(&fixture, &point, tick, budget_max);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_domain_point origin;
            dom_domain_point direction;
            q16_16 length = d_q16_16_from_int(64);
            u32 steps = animal_find_arg_u32(argc, argv, "--steps", 16u);
            u64 start_tick = animal_find_arg_u64(argc, argv, "--start", 0u);
            u64 step_ticks = animal_find_arg_u64(argc, argv, "--step_ticks", 10u);
            u32 budget_max = animal_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 inactive = animal_find_arg_u32(argc, argv, "--inactive", 0u);
            u32 collapsed = animal_find_arg_u32(argc, argv, "--collapsed", 0u);
            if (!animal_parse_arg_point(argc, argv, "--origin", &origin) ||
                !animal_parse_arg_point(argc, argv, "--dir", &direction)) {
                fprintf(stderr, "animal: missing --origin or --dir\n");
                return 2;
            }
            if (!animal_parse_q16(animal_find_arg(argc, argv, "--length"), &length)) {
                length = d_q16_16_from_int(64);
            }
            return animal_run_core_sample(&fixture, &origin, &direction, length, steps,
                                          start_tick, step_ticks, budget_max,
                                          inactive, collapsed ? 1 : 0);
        }

        if (strcmp(cmd, "collapse") == 0) {
            dom_domain_point point;
            u64 tick = animal_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = animal_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!animal_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "animal: missing --pos\n");
                return 2;
            }
            return animal_run_collapse(&fixture, &point, tick, budget_max);
        }
    }

    animal_usage();
    return 2;
}
