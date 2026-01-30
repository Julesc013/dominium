/*
FILE: include/domino/world/weather_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/weather_fields
RESPONSIBILITY: Deterministic weather event sampling and climate perturbations.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by WEATHER0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_WEATHER_FIELDS_H
#define DOMINO_WORLD_WEATHER_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/climate_fields.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_WEATHER_EVENT_TYPE_COUNT 5u
#define DOM_WEATHER_MAX_EVENTS 64u
#define DOM_WEATHER_MAX_CAPSULES 128u
#define DOM_WEATHER_HIST_BINS 4u

#define DOM_WEATHER_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_weather_event_type {
    DOM_WEATHER_EVENT_RAIN = 0u,
    DOM_WEATHER_EVENT_SNOW = 1u,
    DOM_WEATHER_EVENT_HEATWAVE = 2u,
    DOM_WEATHER_EVENT_COLD_SNAP = 3u,
    DOM_WEATHER_EVENT_WIND_SHIFT = 4u
};

enum dom_weather_wind_dir {
    DOM_WEATHER_WIND_UNKNOWN = 0u,
    DOM_WEATHER_WIND_NORTH = 1u,
    DOM_WEATHER_WIND_NORTHEAST = 2u,
    DOM_WEATHER_WIND_EAST = 3u,
    DOM_WEATHER_WIND_SOUTHEAST = 4u,
    DOM_WEATHER_WIND_SOUTH = 5u,
    DOM_WEATHER_WIND_SOUTHWEST = 6u,
    DOM_WEATHER_WIND_WEST = 7u,
    DOM_WEATHER_WIND_NORTHWEST = 8u
};

typedef struct dom_weather_event_profile {
    u64 period_ticks;
    u64 duration_ticks;
    q16_16 intensity_min;
    q16_16 intensity_max;
    q16_16 radius_ratio_min;
    q16_16 radius_ratio_max;
    q16_16 temp_scale;
    q16_16 precip_scale;
    q16_16 wetness_scale;
} dom_weather_event_profile;

typedef struct dom_weather_schedule_desc {
    u64 seed;
    dom_weather_event_profile profiles[DOM_WEATHER_EVENT_TYPE_COUNT];
} dom_weather_schedule_desc;

typedef struct dom_weather_surface_desc {
    dom_climate_surface_desc climate_desc;
    dom_weather_schedule_desc schedule;
} dom_weather_surface_desc;

typedef struct dom_weather_event {
    u64 event_id;
    u32 event_type; /* dom_weather_event_type */
    dom_domain_id domain_id;
    u64 start_tick;
    u64 duration_ticks;
    q16_16 intensity;
    dom_domain_point center;
    q16_16 radius;
    u32 wind_dir; /* dom_weather_wind_dir */
} dom_weather_event;

typedef struct dom_weather_event_list {
    u32 count;
    dom_weather_event events[DOM_WEATHER_MAX_EVENTS];
} dom_weather_event_list;

enum dom_weather_sample_flags {
    DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN = 1u << 0u,
    DOM_WEATHER_SAMPLE_WIND_UNKNOWN = 1u << 1u,
    DOM_WEATHER_SAMPLE_EVENTS_UNKNOWN = 1u << 2u,
    DOM_WEATHER_SAMPLE_COLLAPSED = 1u << 3u
};

typedef struct dom_weather_sample {
    q16_16 temperature_current;
    q16_16 precipitation_current;
    q16_16 surface_wetness;
    u32 wind_current; /* dom_weather_wind_dir */
    u32 active_event_mask;
    u32 active_event_count;
    u32 flags; /* dom_weather_sample_flags */
    dom_domain_query_meta meta;
} dom_weather_sample;

typedef struct dom_weather_cache_entry {
    dom_domain_id domain_id;
    u64 window_id;
    u64 start_tick;
    u64 window_ticks;
    u32 authoring_version;
    u64 last_used;
    u64 insert_order;
    d_bool valid;
    dom_weather_event_list events;
} dom_weather_cache_entry;

typedef struct dom_weather_cache {
    dom_weather_cache_entry* entries;
    u32 capacity;
    u32 count;
    u64 use_counter;
    u64 next_insert_order;
} dom_weather_cache;

typedef struct dom_weather_macro_capsule {
    u64 capsule_id;
    u64 window_id;
    u64 start_tick;
    u64 window_ticks;
    i64 cumulative_precip_q16;
    i64 cumulative_temp_dev_q16;
    u32 event_counts[DOM_WEATHER_EVENT_TYPE_COUNT];
    q16_16 intensity_hist[DOM_WEATHER_EVENT_TYPE_COUNT][DOM_WEATHER_HIST_BINS];
    u32 rng_cursor[DOM_WEATHER_EVENT_TYPE_COUNT];
} dom_weather_macro_capsule;

typedef struct dom_weather_domain {
    dom_climate_domain climate_domain;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_weather_schedule_desc schedule;
    dom_weather_cache cache;
    dom_weather_macro_capsule capsules[DOM_WEATHER_MAX_CAPSULES];
    u32 capsule_count;
} dom_weather_domain;

void dom_weather_surface_desc_init(dom_weather_surface_desc* desc);
void dom_weather_domain_init(dom_weather_domain* domain,
                             const dom_weather_surface_desc* desc,
                             u32 cache_capacity);
void dom_weather_domain_free(dom_weather_domain* domain);
void dom_weather_domain_set_state(dom_weather_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state);
void dom_weather_domain_set_policy(dom_weather_domain* domain,
                                   const dom_domain_policy* policy);

int dom_weather_sample_query(const dom_weather_domain* domain,
                             const dom_domain_point* point,
                             u64 tick,
                             dom_domain_budget* budget,
                             dom_weather_sample* out_sample);

int dom_weather_events_at(const dom_weather_domain* domain,
                          const dom_domain_point* point,
                          u64 tick,
                          dom_weather_event_list* out_list);

int dom_weather_events_in_window(const dom_weather_domain* domain,
                                 u64 start_tick,
                                 u64 window_ticks,
                                 dom_weather_event_list* out_list);

int dom_weather_domain_collapse_window(dom_weather_domain* domain,
                                       u64 start_tick,
                                       u64 window_ticks);
int dom_weather_domain_expand_window(dom_weather_domain* domain,
                                     u64 window_id);

u32 dom_weather_domain_capsule_count(const dom_weather_domain* domain);
const dom_weather_macro_capsule* dom_weather_domain_capsule_at(const dom_weather_domain* domain,
                                                               u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_WEATHER_FIELDS_H */
