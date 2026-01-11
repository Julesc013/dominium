/*
FILE: source/dominium/game/runtime/dom_calendar.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/calendar
RESPONSIBILITY: Calendar registry and deterministic calendar render/parse helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; locale/timezone libraries.
*/
#ifndef DOM_CALENDAR_H
#define DOM_CALENDAR_H

#include "domino/core/dom_time_frames.h"
#include "domino/core/spacetime.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_CALENDAR_OK = 0,
    DOM_CALENDAR_ERR = -1,
    DOM_CALENDAR_INVALID_ARGUMENT = -2,
    DOM_CALENDAR_NOT_IMPLEMENTED = -3,
    DOM_CALENDAR_OVERFLOW = -4,
    DOM_CALENDAR_DUPLICATE_ID = -5,
    DOM_CALENDAR_NOT_FOUND = -6,
    DOM_CALENDAR_UNKNOWN = -7,
    DOM_CALENDAR_BACKWARDS = -8
};

typedef u64 dom_calendar_id;

typedef enum dom_calendar_kind {
    DOM_CALENDAR_KIND_FIXED_PATTERN = 0,
    DOM_CALENDAR_KIND_GREGORIAN = 1,
    DOM_CALENDAR_KIND_JULIAN = 2,
    DOM_CALENDAR_KIND_ISO_WEEK = 3,
    DOM_CALENDAR_KIND_FISCAL_GREGORIAN = 4,
    DOM_CALENDAR_KIND_DAY_COUNT = 5,
    DOM_CALENDAR_KIND_EPOCH_BLOCKS = 6
} dom_calendar_kind;

typedef enum dom_calendar_intercalary {
    DOM_CALENDAR_INTERCALARY_NONE = 0,
    DOM_CALENDAR_INTERCALARY_YEAR_DAY = 1,
    DOM_CALENDAR_INTERCALARY_LEAP_DAY = 2,
    DOM_CALENDAR_INTERCALARY_CORRECTION_DAY = 3,
    DOM_CALENDAR_INTERCALARY_CUSTOM = 4
} dom_calendar_intercalary;

typedef enum dom_calendar_field_mask {
    DOM_CALENDAR_FIELD_YEAR = 1u << 0,
    DOM_CALENDAR_FIELD_MONTH = 1u << 1,
    DOM_CALENDAR_FIELD_DAY = 1u << 2,
    DOM_CALENDAR_FIELD_DAY_OF_YEAR = 1u << 3,
    DOM_CALENDAR_FIELD_WEEKDAY = 1u << 4,
    DOM_CALENDAR_FIELD_WEEK_OF_YEAR = 1u << 5,
    DOM_CALENDAR_FIELD_TIME = 1u << 6,
    DOM_CALENDAR_FIELD_SUBSECOND = 1u << 7,
    DOM_CALENDAR_FIELD_INTERCALARY = 1u << 8
} dom_calendar_field_mask;

typedef struct dom_calendar_date {
    u64 year;
    u32 month;
    u32 day;
    u64 day_of_year; /* 0-based */
    u32 weekday;
    u32 week_of_year;
    u32 hour;
    u32 minute;
    u32 second;
    u32 subsecond_ticks;
    dom_calendar_intercalary intercalary;
    u32 fields_present; /* dom_calendar_field_mask */
} dom_calendar_date;

typedef enum dom_calendar_leap_rule {
    DOM_CALENDAR_LEAP_NONE = 0,
    DOM_CALENDAR_LEAP_GREGORIAN = 1,
    DOM_CALENDAR_LEAP_JULIAN = 2
} dom_calendar_leap_rule;

typedef struct dom_calendar_fixed_pattern {
    const u8 *month_lengths;
    u32 month_count;
    u32 week_length;
    u32 year_days; /* base year days including base intercalary days */
    u32 intercalary_after_month; /* 0 = end of year */
    u32 intercalary_base_days;
    u32 intercalary_leap_days;
    dom_calendar_leap_rule leap_rule;
} dom_calendar_fixed_pattern;

typedef struct dom_calendar_fiscal {
    u32 year_start_month; /* 1-12 */
    u32 year_start_day;   /* 1-31 */
} dom_calendar_fiscal;

typedef struct dom_calendar_epoch_blocks {
    u64 epoch_days;
} dom_calendar_epoch_blocks;

typedef struct dom_calendar_def {
    dom_calendar_id id;
    dom_calendar_kind kind;
    u64 day_seconds;
    union {
        dom_calendar_fixed_pattern fixed;
        dom_calendar_fiscal fiscal;
        dom_calendar_epoch_blocks epoch;
    } u;
    i32 year_offset; /* applied on render and parse (e.g., Holocene) */
} dom_calendar_def;

typedef struct dom_calendar_registry dom_calendar_registry;

dom_calendar_registry *dom_calendar_registry_create(void);
void dom_calendar_registry_destroy(dom_calendar_registry *registry);

int dom_calendar_registry_register(dom_calendar_registry *registry,
                                   const dom_calendar_def *def);
int dom_calendar_registry_get(const dom_calendar_registry *registry,
                              dom_calendar_id id,
                              dom_calendar_def *out_def);

int dom_calendar_registry_register_builtin(dom_calendar_registry *registry);

int dom_calendar_render(const dom_calendar_registry *registry,
                        dom_calendar_id id,
                        dom_time_frame_id frame,
                        dom_tick tick,
                        dom_ups ups,
                        d_bool calendar_known,
                        dom_calendar_date *out_date);

int dom_calendar_parse(const dom_calendar_registry *registry,
                       dom_calendar_id id,
                       const dom_calendar_date *date,
                       dom_time_frame_id frame,
                       dom_act_time_t *out_act,
                       u32 *out_subsecond_ticks);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CALENDAR_H */
