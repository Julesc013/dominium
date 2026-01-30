/*
FILE: tools/weather/weather_cli.cpp
MODULE: Dominium
PURPOSE: Weather fixture CLI for deterministic weather event checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/world/weather_fields.h"
#include "domino/world/terrain_surface.h"

#define WEATHER_FIXTURE_HEADER "DOMINIUM_WEATHER_FIXTURE_V1"

#define WEATHER_INSPECT_HEADER "DOMINIUM_WEATHER_INSPECT_V1"
#define WEATHER_LIST_HEADER "DOMINIUM_WEATHER_LIST_V1"
#define WEATHER_STEP_HEADER "DOMINIUM_WEATHER_STEP_V1"
#define WEATHER_VALIDATE_HEADER "DOMINIUM_WEATHER_VALIDATE_V1"
#define WEATHER_DIFF_HEADER "DOMINIUM_WEATHER_DIFF_V1"
#define WEATHER_COLLAPSE_HEADER "DOMINIUM_WEATHER_COLLAPSE_V1"
#define WEATHER_CORE_SAMPLE_HEADER "DOMINIUM_WEATHER_CORE_SAMPLE_V1"

#define WEATHER_PROVIDER_CHAIN "climate_envelope->weather_event->cache"

#define WEATHER_LINE_MAX 512u

typedef struct weather_fixture {
    char fixture_id[96];
    dom_weather_surface_desc desc;
    dom_domain_policy policy;
    u32 cache_capacity;
    u32 policy_set;
} weather_fixture;

static u64 weather_hash_u64(u64 h, u64 v)
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

static u64 weather_hash_u32(u64 h, u32 v)
{
    return weather_hash_u64(h, (u64)v);
}

static u64 weather_hash_i32(u64 h, i32 v)
{
    return weather_hash_u64(h, (u64)(u32)v);
}

static char* weather_trim(char* text)
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

static int weather_parse_u32(const char* text, u32* out_value)
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

static int weather_parse_u64(const char* text, u64* out_value)
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

static int weather_parse_q16(const char* text, q16_16* out_value)
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

static int weather_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[WEATHER_LINE_MAX];
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
    if (!weather_parse_q16(weather_trim(first), a)) return 0;
    if (!weather_parse_q16(weather_trim(second), b)) return 0;
    if (!weather_parse_q16(weather_trim(third), c)) return 0;
    return 1;
}

static int weather_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!weather_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static u32 weather_parse_resolution(const char* text)
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

static int weather_event_type_from_name(const char* name, u32* out_type)
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

static void weather_fixture_init(weather_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_weather_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->cache_capacity = 128u;
    fixture->policy_set = 0u;
    strncpy(fixture->fixture_id, "weather.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
    fixture->desc.climate_desc.domain_id = 1u;
    fixture->desc.climate_desc.world_seed = 1u;
}

static int weather_fixture_apply_event(weather_fixture* fixture,
                                       u32 event_type,
                                       const char* field,
                                       const char* value)
{
    dom_weather_event_profile* profile;
    if (!fixture || !field || !value || event_type >= DOM_WEATHER_EVENT_TYPE_COUNT) {
        return 0;
    }
    profile = &fixture->desc.schedule.profiles[event_type];
    if (strcmp(field, "period_ticks") == 0) {
        return weather_parse_u64(value, &profile->period_ticks);
    }
    if (strcmp(field, "duration_ticks") == 0) {
        return weather_parse_u64(value, &profile->duration_ticks);
    }
    if (strcmp(field, "intensity_min") == 0) {
        return weather_parse_q16(value, &profile->intensity_min);
    }
    if (strcmp(field, "intensity_max") == 0) {
        return weather_parse_q16(value, &profile->intensity_max);
    }
    if (strcmp(field, "radius_ratio_min") == 0) {
        return weather_parse_q16(value, &profile->radius_ratio_min);
    }
    if (strcmp(field, "radius_ratio_max") == 0) {
        return weather_parse_q16(value, &profile->radius_ratio_max);
    }
    if (strcmp(field, "temp_scale") == 0) {
        return weather_parse_q16(value, &profile->temp_scale);
    }
    if (strcmp(field, "precip_scale") == 0) {
        return weather_parse_q16(value, &profile->precip_scale);
    }
    if (strcmp(field, "wetness_scale") == 0) {
        return weather_parse_q16(value, &profile->wetness_scale);
    }
    return 0;
}

static int weather_fixture_apply(weather_fixture* fixture, const char* key, const char* value)
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
        return weather_parse_u64(value, &fixture->desc.climate_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return weather_parse_u64(value, &fixture->desc.climate_desc.domain_id);
    }
    if (strcmp(key, "shape") == 0) {
        if (strcmp(value, "sphere") == 0) {
            fixture->desc.climate_desc.shape.kind = DOM_TERRAIN_SHAPE_SPHERE;
            return 1;
        }
        if (strcmp(value, "oblate") == 0) {
            fixture->desc.climate_desc.shape.kind = DOM_TERRAIN_SHAPE_OBLATE;
            return 1;
        }
        if (strcmp(value, "slab") == 0) {
            fixture->desc.climate_desc.shape.kind = DOM_TERRAIN_SHAPE_SLAB;
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "radius_equatorial") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.shape.radius_equatorial);
    }
    if (strcmp(key, "radius_polar") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.shape.radius_polar);
    }
    if (strcmp(key, "slab_half_extent") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.shape.slab_half_extent);
    }
    if (strcmp(key, "slab_half_thickness") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.shape.slab_half_thickness);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.meters_per_unit);
    }
    if (strcmp(key, "noise_seed") == 0) {
        return weather_parse_u64(value, &fixture->desc.climate_desc.noise.seed);
    }
    if (strcmp(key, "noise_amplitude") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.noise.amplitude);
    }
    if (strcmp(key, "noise_cell_size") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.noise.cell_size);
    }
    if (strcmp(key, "temp_equator") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.temp_equator);
    }
    if (strcmp(key, "temp_pole") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.temp_pole);
    }
    if (strcmp(key, "temp_altitude_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.temp_altitude_scale);
    }
    if (strcmp(key, "temp_range_base") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.temp_range_base);
    }
    if (strcmp(key, "temp_range_lat_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.temp_range_lat_scale);
    }
    if (strcmp(key, "precip_equator") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.precip_equator);
    }
    if (strcmp(key, "precip_pole") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.precip_pole);
    }
    if (strcmp(key, "precip_altitude_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.precip_altitude_scale);
    }
    if (strcmp(key, "precip_range_base") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.precip_range_base);
    }
    if (strcmp(key, "precip_range_lat_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.precip_range_lat_scale);
    }
    if (strcmp(key, "seasonality_base") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.seasonality_base);
    }
    if (strcmp(key, "seasonality_lat_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.seasonality_lat_scale);
    }
    if (strcmp(key, "noise_temp_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.noise_temp_scale);
    }
    if (strcmp(key, "noise_precip_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.noise_precip_scale);
    }
    if (strcmp(key, "noise_season_scale") == 0) {
        return weather_parse_q16(value, &fixture->desc.climate_desc.noise_season_scale);
    }
    if (strcmp(key, "wind_band_count") == 0) {
        return weather_parse_u32(value, &fixture->desc.climate_desc.wind_band_count);
    }
    if (strcmp(key, "anchor_mask") == 0) {
        return weather_parse_u32(value, &fixture->desc.climate_desc.anchor.mask);
    }
    if (strcmp(key, "anchor_temperature_mean") == 0) {
        fixture->desc.climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_TEMPERATURE_MEAN;
        return weather_parse_q16(value, &fixture->desc.climate_desc.anchor.temperature_mean);
    }
    if (strcmp(key, "anchor_temperature_range") == 0) {
        fixture->desc.climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_TEMPERATURE_RANGE;
        return weather_parse_q16(value, &fixture->desc.climate_desc.anchor.temperature_range);
    }
    if (strcmp(key, "anchor_precipitation_mean") == 0) {
        fixture->desc.climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_PRECIP_MEAN;
        return weather_parse_q16(value, &fixture->desc.climate_desc.anchor.precipitation_mean);
    }
    if (strcmp(key, "anchor_precipitation_range") == 0) {
        fixture->desc.climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_PRECIP_RANGE;
        return weather_parse_q16(value, &fixture->desc.climate_desc.anchor.precipitation_range);
    }
    if (strcmp(key, "anchor_seasonality") == 0) {
        fixture->desc.climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_SEASONALITY;
        return weather_parse_q16(value, &fixture->desc.climate_desc.anchor.seasonality);
    }
    if (strcmp(key, "anchor_wind_prevailing") == 0) {
        fixture->desc.climate_desc.anchor.mask |= DOM_CLIMATE_ANCHOR_WIND_PREVAILING;
        return weather_parse_u32(value, &fixture->desc.climate_desc.anchor.wind_prevailing);
    }
    if (strcmp(key, "weather_seed") == 0) {
        return weather_parse_u64(value, &fixture->desc.schedule.seed);
    }
    if (strcmp(key, "cache_capacity") == 0) {
        return weather_parse_u32(value, &fixture->cache_capacity);
    }
    if (strcmp(key, "tile_size") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_q16(value, &fixture->policy.tile_size);
    }
    if (strcmp(key, "max_resolution") == 0) {
        fixture->policy_set = 1u;
        fixture->policy.max_resolution = weather_parse_resolution(value);
        return 1;
    }
    if (strcmp(key, "sample_dim_full") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.sample_dim_full);
    }
    if (strcmp(key, "sample_dim_medium") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.sample_dim_medium);
    }
    if (strcmp(key, "sample_dim_coarse") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.sample_dim_coarse);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (strcmp(key, "tile_build_cost_full") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.tile_build_cost_full);
    }
    if (strcmp(key, "tile_build_cost_medium") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.tile_build_cost_medium);
    }
    if (strcmp(key, "tile_build_cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.tile_build_cost_coarse);
    }
    if (strcmp(key, "ray_step") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_q16(value, &fixture->policy.ray_step);
    }
    if (strcmp(key, "max_ray_steps") == 0) {
        fixture->policy_set = 1u;
        return weather_parse_u32(value, &fixture->policy.max_ray_steps);
    }
    if (strncmp(key, "event.", 6) == 0) {
        const char* type_start = key + 6;
        const char* dot = strchr(type_start, '.');
        char type_buf[32];
        size_t type_len;
        u32 event_type = 0u;
        if (!dot) {
            return 0;
        }
        type_len = (size_t)(dot - type_start);
        if (type_len == 0 || type_len >= sizeof(type_buf)) {
            return 0;
        }
        memcpy(type_buf, type_start, type_len);
        type_buf[type_len] = '\0';
        if (!weather_event_type_from_name(type_buf, &event_type)) {
            return 0;
        }
        return weather_fixture_apply_event(fixture, event_type, dot + 1, value);
    }
    return 0;
}

static int weather_fixture_load(const char* path, weather_fixture* out_fixture)
{
    FILE* file;
    char line[WEATHER_LINE_MAX];
    int header_ok = 0;
    weather_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    weather_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = weather_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, WEATHER_FIXTURE_HEADER) != 0) {
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
        weather_fixture_apply(&fixture, weather_trim(text), weather_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static void weather_domain_init_from_fixture(const weather_fixture* fixture,
                                             dom_weather_domain* out_domain)
{
    dom_weather_domain_init(out_domain, &fixture->desc, fixture->cache_capacity);
    if (fixture->policy_set) {
        dom_weather_domain_set_policy(out_domain, &fixture->policy);
        dom_climate_domain_set_policy(&out_domain->climate_domain, &fixture->policy);
    }
}

static const char* weather_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 weather_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = weather_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && weather_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 weather_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = weather_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && weather_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static int weather_parse_arg_point(int argc, char** argv, const char* key, dom_domain_point* out_point)
{
    const char* value = weather_find_arg(argc, argv, key);
    if (!value || !out_point) {
        return 0;
    }
    return weather_parse_point(value, out_point);
}

static u64 weather_event_hash(const dom_weather_event* event)
{
    u64 h = 14695981039346656037ULL;
    if (!event) {
        return 0;
    }
    h = weather_hash_u64(h, event->event_id);
    h = weather_hash_u32(h, event->event_type);
    h = weather_hash_u64(h, event->start_tick);
    h = weather_hash_u64(h, event->duration_ticks);
    h = weather_hash_i32(h, event->intensity);
    h = weather_hash_i32(h, event->radius);
    h = weather_hash_i32(h, event->center.x);
    h = weather_hash_i32(h, event->center.y);
    h = weather_hash_i32(h, event->center.z);
    h = weather_hash_u32(h, event->wind_dir);
    return h;
}

static int weather_run_validate(const weather_fixture* fixture)
{
    u32 enabled = 0u;
    if (!fixture) {
        return 1;
    }
    for (u32 i = 0u; i < DOM_WEATHER_EVENT_TYPE_COUNT; ++i) {
        const dom_weather_event_profile* profile = &fixture->desc.schedule.profiles[i];
        if (profile->period_ticks == 0u || profile->duration_ticks == 0u) {
            continue;
        }
        if (profile->duration_ticks > profile->period_ticks) {
            fprintf(stderr, "weather: event duration exceeds period\n");
            return 1;
        }
        enabled += 1u;
    }
    if (enabled == 0u) {
        fprintf(stderr, "weather: no events enabled\n");
        return 1;
    }
    printf("%s\n", WEATHER_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", WEATHER_PROVIDER_CHAIN);
    printf("event_types=%u\n", (unsigned int)enabled);
    return 0;
}

static int weather_run_inspect(const weather_fixture* fixture,
                               const dom_domain_point* point,
                               u64 tick,
                               u32 budget_max)
{
    dom_weather_domain domain;
    dom_domain_budget budget;
    dom_weather_sample sample;
    dom_weather_event_list events;

    weather_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    if (dom_weather_sample_query(&domain, point, tick, &budget, &sample) != 0) {
        dom_weather_domain_free(&domain);
        return 1;
    }
    (void)dom_weather_events_at(&domain, point, tick, &events);

    printf("%s\n", WEATHER_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", WEATHER_PROVIDER_CHAIN);
    printf("point_q16=%d,%d,%d\n", (int)point->x, (int)point->y, (int)point->z);
    printf("tick=%llu\n", (unsigned long long)tick);
    printf("temperature_current_q16=%d\n", (int)sample.temperature_current);
    printf("precipitation_current_q16=%d\n", (int)sample.precipitation_current);
    printf("surface_wetness_q16=%d\n", (int)sample.surface_wetness);
    printf("wind_current=%u\n", (unsigned int)sample.wind_current);
    printf("active_event_count=%u\n", (unsigned int)sample.active_event_count);
    printf("active_event_mask=%u\n", (unsigned int)sample.active_event_mask);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("fields_unknown=%u\n", (unsigned int)((sample.flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN) ? 1u : 0u));
    printf("wind_unknown=%u\n", (unsigned int)((sample.flags & DOM_WEATHER_SAMPLE_WIND_UNKNOWN) ? 1u : 0u));
    printf("events_unknown=%u\n", (unsigned int)((sample.flags & DOM_WEATHER_SAMPLE_EVENTS_UNKNOWN) ? 1u : 0u));
    printf("collapsed=%u\n", (unsigned int)((sample.flags & DOM_WEATHER_SAMPLE_COLLAPSED) ? 1u : 0u));
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);
    printf("event_count=%u\n", (unsigned int)events.count);
    for (u32 i = 0u; i < events.count; ++i) {
        const dom_weather_event* event = &events.events[i];
        printf("event.%u.type=%u\n", (unsigned int)i, (unsigned int)event->event_type);
        printf("event.%u.start_tick=%llu\n", (unsigned int)i, (unsigned long long)event->start_tick);
        printf("event.%u.duration_ticks=%llu\n", (unsigned int)i, (unsigned long long)event->duration_ticks);
        printf("event.%u.intensity_q16=%d\n", (unsigned int)i, (int)event->intensity);
        printf("event.%u.radius_q16=%d\n", (unsigned int)i, (int)event->radius);
        printf("event.%u.wind_dir=%u\n", (unsigned int)i, (unsigned int)event->wind_dir);
        printf("event.%u.center_q16=%d,%d,%d\n", (unsigned int)i,
               (int)event->center.x, (int)event->center.y, (int)event->center.z);
    }

    dom_weather_domain_free(&domain);
    return 0;
}

static int weather_run_list(const weather_fixture* fixture,
                            u64 start_tick,
                            u64 window_ticks)
{
    dom_weather_domain domain;
    dom_weather_event_list events;
    u64 hash = 14695981039346656037ULL;

    weather_domain_init_from_fixture(fixture, &domain);
    if (dom_weather_events_in_window(&domain, start_tick, window_ticks, &events) != 0) {
        dom_weather_domain_free(&domain);
        return 1;
    }

    for (u32 i = 0u; i < events.count; ++i) {
        hash = weather_hash_u64(hash, weather_event_hash(&events.events[i]));
    }

    printf("%s\n", WEATHER_LIST_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", WEATHER_PROVIDER_CHAIN);
    printf("window_start=%llu\n", (unsigned long long)start_tick);
    printf("window_ticks=%llu\n", (unsigned long long)window_ticks);
    printf("event_count=%u\n", (unsigned int)events.count);
    printf("event_hash=%llu\n", (unsigned long long)hash);
    for (u32 i = 0u; i < events.count; ++i) {
        const dom_weather_event* event = &events.events[i];
        printf("event.%u.type=%u\n", (unsigned int)i, (unsigned int)event->event_type);
        printf("event.%u.start_tick=%llu\n", (unsigned int)i, (unsigned long long)event->start_tick);
        printf("event.%u.duration_ticks=%llu\n", (unsigned int)i, (unsigned long long)event->duration_ticks);
        printf("event.%u.intensity_q16=%d\n", (unsigned int)i, (int)event->intensity);
        printf("event.%u.radius_q16=%d\n", (unsigned int)i, (int)event->radius);
    }

    dom_weather_domain_free(&domain);
    return 0;
}

static int weather_run_step(const weather_fixture* fixture,
                            const dom_domain_point* point,
                            u64 start_tick,
                            u32 steps,
                            u64 step_ticks,
                            u32 budget_max)
{
    dom_weather_domain domain;
    u64 hash = 14695981039346656037ULL;
    u32 unknown_steps = 0u;
    u32 cost_max = 0u;

    weather_domain_init_from_fixture(fixture, &domain);
    if (steps == 0u) {
        steps = 1u;
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_weather_sample sample;
        u64 tick = start_tick + (step_ticks * (u64)i);
        dom_domain_budget_init(&budget, budget_max);
        if (dom_weather_sample_query(&domain, point, tick, &budget, &sample) != 0) {
            dom_weather_domain_free(&domain);
            return 1;
        }
        if (sample.flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN) {
            unknown_steps += 1u;
        }
        if (sample.meta.cost_units > cost_max) {
            cost_max = sample.meta.cost_units;
        }
        hash = weather_hash_i32(hash, sample.temperature_current);
        hash = weather_hash_i32(hash, sample.precipitation_current);
        hash = weather_hash_i32(hash, sample.surface_wetness);
        hash = weather_hash_u32(hash, sample.wind_current);
        hash = weather_hash_u32(hash, sample.active_event_mask);
        hash = weather_hash_u32(hash, sample.flags);
    }

    printf("%s\n", WEATHER_STEP_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", WEATHER_PROVIDER_CHAIN);
    printf("steps=%u\n", (unsigned int)steps);
    printf("start_tick=%llu\n", (unsigned long long)start_tick);
    printf("step_ticks=%llu\n", (unsigned long long)step_ticks);
    printf("budget_max=%u\n", (unsigned int)budget_max);
    printf("unknown_steps=%u\n", (unsigned int)unknown_steps);
    printf("cost_step_max=%u\n", (unsigned int)cost_max);
    printf("sample_hash=%llu\n", (unsigned long long)hash);

    dom_weather_domain_free(&domain);
    return 0;
}

static u64 weather_window_id(u64 start_tick, u64 window_ticks)
{
    u64 h = 14695981039346656037ULL;
    h = weather_hash_u64(h, start_tick);
    h = weather_hash_u64(h, window_ticks);
    return h;
}

static u64 weather_core_sample_hash(const weather_fixture* fixture,
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
    dom_weather_domain domain;
    dom_weather_domain* inactive_domains = 0;
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
    weather_domain_init_from_fixture(fixture, &domain);
    if (inactive > 0u) {
        inactive_domains = (dom_weather_domain*)calloc(inactive, sizeof(dom_weather_domain));
        if (!inactive_domains) {
            dom_weather_domain_free(&domain);
            return 0;
        }
        for (u32 i = 0u; i < inactive; ++i) {
            weather_domain_init_from_fixture(fixture, &inactive_domains[i]);
            dom_weather_domain_set_state(&inactive_domains[i],
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
        u64 window_ticks = step_ticks * (u64)steps;
        (void)dom_weather_domain_collapse_window(&domain, start_tick, window_ticks);
        capsule_count = dom_weather_domain_capsule_count(&domain);
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_weather_sample sample;
        dom_domain_point p = *origin;
        q16_16 t = (steps <= 1u) ? 0 : (q16_16)((i64)step_len * (i64)i);
        u64 tick = start_tick + (step_ticks * (u64)i);
        p.x = d_q16_16_add(p.x, d_q16_16_mul(direction->x, t));
        p.y = d_q16_16_add(p.y, d_q16_16_mul(direction->y, t));
        p.z = d_q16_16_add(p.z, d_q16_16_mul(direction->z, t));
        dom_domain_budget_init(&budget, budget_max);
        if (dom_weather_sample_query(&domain, &p, tick, &budget, &sample) != 0) {
            dom_weather_domain_free(&domain);
            if (inactive_domains) {
                for (u32 j = 0u; j < inactive; ++j) {
                    dom_weather_domain_free(&inactive_domains[j]);
                }
                free(inactive_domains);
            }
            return 0;
        }
        if (sample.flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN) {
            unknown_steps += 1u;
        }
        if (sample.meta.cost_units > cost_max) {
            cost_max = sample.meta.cost_units;
        }
        hash = weather_hash_i32(hash, sample.temperature_current);
        hash = weather_hash_i32(hash, sample.precipitation_current);
        hash = weather_hash_i32(hash, sample.surface_wetness);
        hash = weather_hash_u32(hash, sample.wind_current);
        hash = weather_hash_u32(hash, sample.active_event_mask);
        hash = weather_hash_u32(hash, sample.flags);
    }
    dom_weather_domain_free(&domain);
    if (inactive_domains) {
        for (u32 i = 0u; i < inactive; ++i) {
            dom_weather_domain_free(&inactive_domains[i]);
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

static int weather_run_core_sample(const weather_fixture* fixture,
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
    u64 hash = weather_core_sample_hash(fixture, origin, direction, length, steps,
                                        start_tick, step_ticks, budget_max,
                                        inactive, collapse,
                                        &unknown_steps, &cost_max, &capsule_count, &ok);
    if (!ok) {
        return 1;
    }
    printf("%s\n", WEATHER_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", WEATHER_PROVIDER_CHAIN);
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

static int weather_run_diff(const weather_fixture* fixture_a,
                            const weather_fixture* fixture_b,
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
    u64 hash_a = weather_core_sample_hash(fixture_a, origin, direction, length, steps,
                                          start_tick, step_ticks, budget_max,
                                          0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_a);
    u64 hash_b = weather_core_sample_hash(fixture_b, origin, direction, length, steps,
                                          start_tick, step_ticks, budget_max,
                                          0u, 0, (u32*)0, (u32*)0, (u32*)0, &ok_b);
    if (!ok_a || !ok_b) {
        return 1;
    }
    printf("%s\n", WEATHER_DIFF_HEADER);
    printf("fixture_a=%s\n", fixture_a->fixture_id);
    printf("fixture_b=%s\n", fixture_b->fixture_id);
    printf("hash_a=%llu\n", (unsigned long long)hash_a);
    printf("hash_b=%llu\n", (unsigned long long)hash_b);
    printf("equal=%u\n", (unsigned int)(hash_a == hash_b ? 1u : 0u));
    return 0;
}

static int weather_run_collapse(const weather_fixture* fixture,
                                const dom_domain_point* point,
                                u64 start_tick,
                                u64 window_ticks,
                                u32 budget_max)
{
    dom_weather_domain domain;
    dom_domain_budget budget;
    dom_weather_sample inside;
    dom_weather_sample outside;
    u32 count_before;
    u32 count_after;
    u32 count_final;
    u64 window_id = weather_window_id(start_tick, window_ticks);

    weather_domain_init_from_fixture(fixture, &domain);
    count_before = dom_weather_domain_capsule_count(&domain);
    (void)dom_weather_domain_collapse_window(&domain, start_tick, window_ticks);
    count_after = dom_weather_domain_capsule_count(&domain);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_weather_sample_query(&domain, point, start_tick + 1u, &budget, &inside);

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_weather_sample_query(&domain, point, start_tick + window_ticks + 1u, &budget, &outside);

    (void)dom_weather_domain_expand_window(&domain, window_id);
    count_final = dom_weather_domain_capsule_count(&domain);

    printf("%s\n", WEATHER_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", WEATHER_PROVIDER_CHAIN);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);
    printf("capsule_count_final=%u\n", (unsigned int)count_final);
    printf("window_id=%llu\n", (unsigned long long)window_id);
    printf("inside_flags=%u\n", (unsigned int)inside.flags);
    printf("outside_flags=%u\n", (unsigned int)outside.flags);

    dom_weather_domain_free(&domain);
    return 0;
}

static void weather_usage(void)
{
    printf("dom_tool_weather commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --pos x,y,z --tick T [--budget N]\n");
    printf("  list --fixture <path> --start T --window W\n");
    printf("  step --fixture <path> --pos x,y,z --start T [--steps N] [--step_ticks S] [--budget N]\n");
    printf("  core-sample --fixture <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--budget N] [--inactive N] [--collapsed 0|1]\n");
    printf("  diff --fixture-a <path> --fixture-b <path> --origin x,y,z --dir x,y,z [--length L] [--steps N] [--start T] [--step_ticks S] [--budget N]\n");
    printf("  collapse --fixture <path> --pos x,y,z --start T --window W [--budget N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        weather_usage();
        return 2;
    }
    cmd = argv[1];

    if (strcmp(cmd, "diff") == 0) {
        const char* fixture_a_path = weather_find_arg(argc, argv, "--fixture-a");
        const char* fixture_b_path = weather_find_arg(argc, argv, "--fixture-b");
        weather_fixture fixture_a;
        weather_fixture fixture_b;
        dom_domain_point origin;
        dom_domain_point direction;
        q16_16 length = d_q16_16_from_int(64);
        u32 steps = weather_find_arg_u32(argc, argv, "--steps", 16u);
        u64 start_tick = weather_find_arg_u64(argc, argv, "--start", 0u);
        u64 step_ticks = weather_find_arg_u64(argc, argv, "--step_ticks", 10u);
        u32 budget_max;
        if (!fixture_a_path || !fixture_b_path ||
            !weather_fixture_load(fixture_a_path, &fixture_a) ||
            !weather_fixture_load(fixture_b_path, &fixture_b)) {
            fprintf(stderr, "weather: missing or invalid --fixture-a/--fixture-b\n");
            return 2;
        }
        if (!weather_parse_arg_point(argc, argv, "--origin", &origin) ||
            !weather_parse_arg_point(argc, argv, "--dir", &direction)) {
            fprintf(stderr, "weather: missing --origin or --dir\n");
            return 2;
        }
        if (!weather_parse_q16(weather_find_arg(argc, argv, "--length"), &length)) {
            length = d_q16_16_from_int(64);
        }
        budget_max = weather_find_arg_u32(argc, argv, "--budget", fixture_a.policy.cost_analytic);
        return weather_run_diff(&fixture_a, &fixture_b, &origin, &direction, length, steps,
                                start_tick, step_ticks, budget_max);
    }

    {
        const char* fixture_path = weather_find_arg(argc, argv, "--fixture");
        weather_fixture fixture;
        if (!fixture_path || !weather_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "weather: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return weather_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            dom_domain_point point;
            u64 tick = weather_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = weather_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!weather_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "weather: missing --pos\n");
                return 2;
            }
            return weather_run_inspect(&fixture, &point, tick, budget_max);
        }

        if (strcmp(cmd, "list") == 0) {
            u64 start_tick = weather_find_arg_u64(argc, argv, "--start", 0u);
            u64 window_ticks = weather_find_arg_u64(argc, argv, "--window", 256u);
            return weather_run_list(&fixture, start_tick, window_ticks);
        }

        if (strcmp(cmd, "step") == 0) {
            dom_domain_point point;
            u64 start_tick = weather_find_arg_u64(argc, argv, "--start", 0u);
            u64 step_ticks = weather_find_arg_u64(argc, argv, "--step_ticks", 10u);
            u32 steps = weather_find_arg_u32(argc, argv, "--steps", 16u);
            u32 budget_max = weather_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!weather_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "weather: missing --pos\n");
                return 2;
            }
            return weather_run_step(&fixture, &point, start_tick, steps, step_ticks, budget_max);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_domain_point origin;
            dom_domain_point direction;
            q16_16 length = d_q16_16_from_int(64);
            u32 steps = weather_find_arg_u32(argc, argv, "--steps", 16u);
            u64 start_tick = weather_find_arg_u64(argc, argv, "--start", 0u);
            u64 step_ticks = weather_find_arg_u64(argc, argv, "--step_ticks", 10u);
            u32 budget_max = weather_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            u32 inactive = weather_find_arg_u32(argc, argv, "--inactive", 0u);
            u32 collapsed = weather_find_arg_u32(argc, argv, "--collapsed", 0u);
            if (!weather_parse_arg_point(argc, argv, "--origin", &origin) ||
                !weather_parse_arg_point(argc, argv, "--dir", &direction)) {
                fprintf(stderr, "weather: missing --origin or --dir\n");
                return 2;
            }
            if (!weather_parse_q16(weather_find_arg(argc, argv, "--length"), &length)) {
                length = d_q16_16_from_int(64);
            }
            return weather_run_core_sample(&fixture, &origin, &direction, length, steps,
                                           start_tick, step_ticks, budget_max,
                                           inactive, collapsed ? 1 : 0);
        }

        if (strcmp(cmd, "collapse") == 0) {
            dom_domain_point point;
            u64 start_tick = weather_find_arg_u64(argc, argv, "--start", 0u);
            u64 window_ticks = weather_find_arg_u64(argc, argv, "--window", 256u);
            u32 budget_max = weather_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_analytic);
            if (!weather_parse_arg_point(argc, argv, "--pos", &point)) {
                fprintf(stderr, "weather: missing --pos\n");
                return 2;
            }
            return weather_run_collapse(&fixture, &point, start_tick, window_ticks, budget_max);
        }
    }

    weather_usage();
    return 2;
}
