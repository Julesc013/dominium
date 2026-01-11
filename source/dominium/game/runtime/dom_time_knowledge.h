/*
FILE: source/dominium/game/runtime/dom_time_knowledge.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/time_knowledge
RESPONSIBILITY: Epistemic time knowledge state and accessors (no clocks yet).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; locale/timezone libraries.
*/
#ifndef DOM_TIME_KNOWLEDGE_H
#define DOM_TIME_KNOWLEDGE_H

#include "domino/core/dom_time_core.h"
#include "runtime/dom_calendar.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_TIME_KNOWLEDGE_OK = 0,
    DOM_TIME_KNOWLEDGE_ERR = -1,
    DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT = -2,
    DOM_TIME_KNOWLEDGE_DUPLICATE_ID = -3,
    DOM_TIME_KNOWLEDGE_NOT_FOUND = -4,
    DOM_TIME_KNOWLEDGE_OVERFLOW = -5,
    DOM_TIME_KNOWLEDGE_UNKNOWN = -6,
    DOM_TIME_KNOWLEDGE_NOT_IMPLEMENTED = -7,
    DOM_TIME_KNOWLEDGE_BACKWARDS = -8
};

typedef u64 dom_time_actor_id;
typedef u64 dom_time_clock_id;
typedef u64 dom_time_document_id;

typedef enum dom_time_clock_kind {
    DOM_TIME_CLOCK_SUNDIAL = 0,
    DOM_TIME_CLOCK_MECHANICAL = 1,
    DOM_TIME_CLOCK_QUARTZ = 2,
    DOM_TIME_CLOCK_ATOMIC = 3,
    DOM_TIME_CLOCK_NETWORK = 4,
    DOM_TIME_CLOCK_ASTRONOMICAL = 5
} dom_time_clock_kind;

enum dom_time_clock_flags {
    DOM_TIME_CLOCK_REQUIRES_DAYLIGHT = 1u << 0,
    DOM_TIME_CLOCK_REQUIRES_POWER = 1u << 1,
    DOM_TIME_CLOCK_REQUIRES_NETWORK = 1u << 2
};

enum dom_time_clock_state_flags {
    DOM_TIME_CLOCK_STATE_POWERED = 1u << 0,
    DOM_TIME_CLOCK_STATE_DAMAGED = 1u << 1,
    DOM_TIME_CLOCK_STATE_JAMMED = 1u << 2
};

enum dom_time_clock_reading_flags {
    DOM_TIME_CLOCK_READING_VALID = 1u << 0,
    DOM_TIME_CLOCK_READING_UNKNOWN = 1u << 1,
    DOM_TIME_CLOCK_READING_UNAVAILABLE = 1u << 2,
    DOM_TIME_CLOCK_READING_DEGRADED = 1u << 3
};

typedef struct dom_time_clock_def {
    dom_time_clock_id clock_id;
    dom_time_clock_kind kind;
    dom_time_frame_id frame;
    u32 base_accuracy_seconds;
    u32 drift_ppm;
    u32 flags;
} dom_time_clock_def;

typedef struct dom_time_clock_state {
    dom_time_clock_id clock_id;
    u32 state_flags;
    u32 damage_ppm;
    u32 damage_uncertainty_seconds;
    dom_tick last_calibration_tick;
} dom_time_clock_state;

typedef struct dom_time_clock_env {
    d_bool has_daylight;
    d_bool has_power;
    d_bool has_network;
    u32 extra_drift_ppm;
    u32 extra_uncertainty_seconds;
} dom_time_clock_env;

typedef struct dom_time_clock_reading {
    dom_time_clock_id clock_id;
    dom_time_frame_id frame;
    dom_act_time_t observed_act;
    u64 uncertainty_seconds;
    u32 flags;
} dom_time_clock_reading;

typedef struct dom_time_document {
    dom_time_document_id document_id;
    u32 frame_mask;
    dom_calendar_id calendar_id;
} dom_time_document;

typedef struct dom_time_knowledge dom_time_knowledge;

dom_time_knowledge *dom_time_knowledge_create(dom_time_actor_id actor_id);
void dom_time_knowledge_destroy(dom_time_knowledge *knowledge);
int dom_time_knowledge_init(dom_time_knowledge *knowledge, dom_time_actor_id actor_id);

int dom_time_knowledge_add_frame(dom_time_knowledge *knowledge, dom_time_frame_id frame);
int dom_time_knowledge_has_frame(const dom_time_knowledge *knowledge,
                                 dom_time_frame_id frame,
                                 d_bool *out_known);

int dom_time_knowledge_add_calendar(dom_time_knowledge *knowledge, dom_calendar_id id);
int dom_time_knowledge_has_calendar(const dom_time_knowledge *knowledge,
                                    dom_calendar_id id,
                                    d_bool *out_known);
int dom_time_knowledge_list_calendars(const dom_time_knowledge *knowledge,
                                      dom_calendar_id *out_ids,
                                      u32 max_ids,
                                      u32 *out_count);

int dom_time_knowledge_add_clock(dom_time_knowledge *knowledge,
                                 const dom_time_clock_def *def,
                                 dom_tick calibration_tick);
int dom_time_knowledge_set_clock_state(dom_time_knowledge *knowledge,
                                       dom_time_clock_id clock_id,
                                       u32 state_flags,
                                       u32 damage_ppm,
                                       u32 damage_uncertainty_seconds);
int dom_time_knowledge_calibrate_clock(dom_time_knowledge *knowledge,
                                       dom_time_clock_id clock_id,
                                       dom_tick tick);
int dom_time_knowledge_sample_clock(const dom_time_knowledge *knowledge,
                                    dom_time_clock_id clock_id,
                                    dom_tick tick,
                                    dom_ups ups,
                                    const dom_time_clock_env *env,
                                    dom_time_clock_reading *out_reading);
int dom_time_knowledge_sample_all(const dom_time_knowledge *knowledge,
                                  dom_tick tick,
                                  dom_ups ups,
                                  const dom_time_clock_env *env,
                                  dom_time_clock_reading *out_readings,
                                  u32 max_readings,
                                  u32 *out_count);

int dom_time_knowledge_apply_document(dom_time_knowledge *knowledge,
                                      const dom_time_document *doc);

int dom_time_clock_init_sundial(dom_time_clock_id clock_id,
                                dom_time_frame_id frame,
                                dom_time_clock_def *out_def);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_TIME_KNOWLEDGE_H */
