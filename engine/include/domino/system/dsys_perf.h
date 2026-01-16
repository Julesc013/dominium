/*
FILE: include/domino/system/dsys_perf.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / system/dsys_perf
RESPONSIBILITY: Defines public contract for profiling counters, timers, and telemetry output; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Profiling is non-authoritative and MUST NOT influence simulation results.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_SYSTEM_DSYS_PERF_H
#define DOMINO_SYSTEM_DSYS_PERF_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsys_perf_lane {
    DSYS_PERF_LANE_LOCAL = 0,
    DSYS_PERF_LANE_MESO = 1,
    DSYS_PERF_LANE_MACRO = 2,
    DSYS_PERF_LANE_ORBITAL = 3,
    DSYS_PERF_LANE_COUNT = 4
} dsys_perf_lane;

typedef enum dsys_perf_metric {
    DSYS_PERF_METRIC_SIM_TICK_US = 0,
    DSYS_PERF_METRIC_MACRO_SCHED_US,
    DSYS_PERF_METRIC_MACRO_EVENTS,
    DSYS_PERF_METRIC_EVENT_QUEUE_DEPTH,
    DSYS_PERF_METRIC_INTEREST_SET_SIZE,
    DSYS_PERF_METRIC_DERIVED_QUEUE_DEPTH,
    DSYS_PERF_METRIC_DERIVED_JOB_US,
    DSYS_PERF_METRIC_RENDER_SUBMIT_US,
    DSYS_PERF_METRIC_STREAM_BYTES,
    DSYS_PERF_METRIC_NET_MSG_SENT,
    DSYS_PERF_METRIC_NET_MSG_RECV,
    DSYS_PERF_METRIC_NET_BYTES_SENT,
    DSYS_PERF_METRIC_NET_BYTES_RECV,
    DSYS_PERF_METRIC_COUNT
} dsys_perf_metric;

typedef u64 (*dsys_perf_clock_fn)(void* user);

typedef struct dsys_perf_timer {
    dsys_perf_lane   lane;
    dsys_perf_metric metric;
    u64              start_us;
    int              active;
} dsys_perf_timer;

typedef struct dsys_perf_flush_desc {
    const char* run_root;           /* optional override; else DOMINIUM_RUN_ROOT or "." */
    const char* fixture;            /* required for stable output naming */
    const char* tier;               /* optional; used in budget reports */
    u32         emit_telemetry;     /* 0/1 */
    u32         emit_budget_report; /* 0/1 */
} dsys_perf_flush_desc;

/* Enable/disable profiling globally (disabled by default). */
void dsys_perf_set_enabled(int enabled);
int  dsys_perf_is_enabled(void);

/* Set a custom clock (microseconds). NULL uses the manual clock. */
void dsys_perf_set_clock(dsys_perf_clock_fn fn, void* user);
void dsys_perf_set_manual_clock(u64 now_us);
void dsys_perf_advance_manual_clock(u64 delta_us);

/* Override run_root for telemetry output (NULL clears override). */
void dsys_perf_set_run_root(const char* path);

/* Reset counters, samples, and summaries. */
void dsys_perf_reset(void);

/* Tick lifecycle (ACT time + tick index). */
void dsys_perf_tick_begin(dom_act_time_t act, u64 tick_index);
void dsys_perf_tick_end(void);

/* Metric recording. */
void dsys_perf_metric_set(dsys_perf_lane lane, dsys_perf_metric metric, u64 value);
void dsys_perf_metric_add(dsys_perf_lane lane, dsys_perf_metric metric, u64 value);
void dsys_perf_metric_max(dsys_perf_lane lane, dsys_perf_metric metric, u64 value);

u64 dsys_perf_metric_last(dsys_perf_lane lane, dsys_perf_metric metric);
u64 dsys_perf_metric_max_seen(dsys_perf_lane lane, dsys_perf_metric metric);

/* Timer helpers. */
void dsys_perf_timer_begin(dsys_perf_timer* timer, dsys_perf_lane lane, dsys_perf_metric metric);
void dsys_perf_timer_end(dsys_perf_timer* timer);

const char* dsys_perf_metric_name(dsys_perf_metric metric);
const char* dsys_perf_lane_name(dsys_perf_lane lane);

/* Flush buffered telemetry and/or budget reports. */
int dsys_perf_flush(const dsys_perf_flush_desc* desc);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SYSTEM_DSYS_PERF_H */
