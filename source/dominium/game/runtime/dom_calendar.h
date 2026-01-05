/*
FILE: source/dominium/game/runtime/dom_calendar.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/calendar
RESPONSIBILITY: Calendar registry and deterministic fixed-ratio conversion helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; locale/timezone libraries.
*/
#ifndef DOM_CALENDAR_H
#define DOM_CALENDAR_H

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
    DOM_CALENDAR_NOT_FOUND = -6
};

typedef u64 dom_calendar_id;

typedef enum dom_calendar_kind {
    DOM_CALENDAR_FIXED_RATIO = 0,
    DOM_CALENDAR_ORBIT_SYNCED = 1,
    DOM_CALENDAR_HYBRID = 2
} dom_calendar_kind;

typedef struct dom_calendar_desc {
    dom_calendar_kind kind;
    u64 day_seconds_num;
    u64 day_seconds_den;
    u64 year_seconds_num;
    u64 year_seconds_den;
} dom_calendar_desc;

typedef struct dom_calendar_time {
    u64 year;
    u32 day_of_year; /* 0-based */
    u32 hour;
    u32 minute;
    u32 second;
    u32 subsecond_ticks;
} dom_calendar_time;

typedef struct dom_calendar_registry dom_calendar_registry;

dom_calendar_registry *dom_calendar_registry_create(void);
void dom_calendar_registry_destroy(dom_calendar_registry *registry);

int dom_calendar_registry_register(dom_calendar_registry *registry,
                                   dom_calendar_id id,
                                   const dom_calendar_desc *desc);
int dom_calendar_registry_get(const dom_calendar_registry *registry,
                              dom_calendar_id id,
                              dom_calendar_desc *out_desc);

int dom_calendar_ticks_to_time(const dom_calendar_desc *desc,
                               dom_tick tick,
                               dom_ups ups,
                               dom_calendar_time *out_time);

int dom_calendar_format_basic(const dom_calendar_time *t,
                              char *out,
                              u32 out_cap);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CALENDAR_H */
