/*
FILE: source/domino/system/dsys_perf.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_perf
RESPONSIBILITY: Implements profiling counters, timers, and telemetry output.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89 headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Profiling is non-authoritative and must not influence simulation.
*/
#include "domino/system/dsys_perf.h"

#include <string.h>
#include <stdlib.h>

#define DSYS_PERF_MAX_SAMPLES 256u
#define DSYS_PERF_MAX_PATH 260u
#define DSYS_PERF_MAX_NAME 64u

typedef struct dsys_perf_sample {
    dom_act_time_t act;
    u64 tick_index;
    u64 values[DSYS_PERF_LANE_COUNT][DSYS_PERF_METRIC_COUNT];
} dsys_perf_sample;

static int g_perf_enabled = 0;
static dsys_perf_clock_fn g_perf_clock_fn = NULL;
static void* g_perf_clock_user = NULL;
static u64 g_perf_manual_time_us = 0u;

static char g_perf_run_root[DSYS_PERF_MAX_PATH];
static int g_perf_run_root_set = 0;

static dom_act_time_t g_perf_current_act = 0;
static u64 g_perf_current_tick = 0u;
static u64 g_perf_current[DSYS_PERF_LANE_COUNT][DSYS_PERF_METRIC_COUNT];
static u64 g_perf_last[DSYS_PERF_LANE_COUNT][DSYS_PERF_METRIC_COUNT];
static u64 g_perf_max[DSYS_PERF_LANE_COUNT][DSYS_PERF_METRIC_COUNT];
static u64 g_perf_sum[DSYS_PERF_LANE_COUNT][DSYS_PERF_METRIC_COUNT];

static dsys_perf_sample g_perf_samples[DSYS_PERF_MAX_SAMPLES];
static u32 g_perf_sample_count = 0u;
static u32 g_perf_sample_overflow = 0u;

static const char* g_lane_names[DSYS_PERF_LANE_COUNT] = {
    "local",
    "meso",
    "macro",
    "orbital"
};

static const char* g_metric_names[DSYS_PERF_METRIC_COUNT] = {
    "sim_tick_us",
    "macro_sched_us",
    "macro_events",
    "event_queue_depth",
    "interest_set_size",
    "derived_queue_depth",
    "derived_job_us",
    "render_submit_us",
    "stream_bytes",
    "net_msg_sent",
    "net_msg_recv",
    "net_bytes_sent",
    "net_bytes_recv"
};

static u64 dsys_perf_clock_now(void)
{
    if (g_perf_clock_fn) {
        return g_perf_clock_fn(g_perf_clock_user);
    }
    return g_perf_manual_time_us;
}

void dsys_perf_set_enabled(int enabled)
{
    g_perf_enabled = enabled ? 1 : 0;
}

int dsys_perf_is_enabled(void)
{
    return g_perf_enabled ? 1 : 0;
}

void dsys_perf_set_clock(dsys_perf_clock_fn fn, void* user)
{
    g_perf_clock_fn = fn;
    g_perf_clock_user = user;
}

void dsys_perf_set_manual_clock(u64 now_us)
{
    g_perf_manual_time_us = now_us;
}

void dsys_perf_advance_manual_clock(u64 delta_us)
{
    g_perf_manual_time_us += delta_us;
}

void dsys_perf_set_run_root(const char* path)
{
    if (path && path[0]) {
        strncpy(g_perf_run_root, path, DSYS_PERF_MAX_PATH - 1u);
        g_perf_run_root[DSYS_PERF_MAX_PATH - 1u] = '\0';
        g_perf_run_root_set = 1;
    } else {
        g_perf_run_root[0] = '\0';
        g_perf_run_root_set = 0;
    }
}

void dsys_perf_reset(void)
{
    memset(g_perf_current, 0, sizeof(g_perf_current));
    memset(g_perf_last, 0, sizeof(g_perf_last));
    memset(g_perf_max, 0, sizeof(g_perf_max));
    memset(g_perf_sum, 0, sizeof(g_perf_sum));
    memset(g_perf_samples, 0, sizeof(g_perf_samples));
    g_perf_current_act = 0;
    g_perf_current_tick = 0u;
    g_perf_sample_count = 0u;
    g_perf_sample_overflow = 0u;
}

void dsys_perf_tick_begin(dom_act_time_t act, u64 tick_index)
{
    if (!g_perf_enabled) {
        return;
    }
    g_perf_current_act = act;
    g_perf_current_tick = tick_index;
    memset(g_perf_current, 0, sizeof(g_perf_current));
}

void dsys_perf_tick_end(void)
{
    u32 lane;
    u32 metric;

    if (!g_perf_enabled) {
        return;
    }

    if (g_perf_sample_count < DSYS_PERF_MAX_SAMPLES) {
        dsys_perf_sample* sample = &g_perf_samples[g_perf_sample_count++];
        sample->act = g_perf_current_act;
        sample->tick_index = g_perf_current_tick;
        memcpy(sample->values, g_perf_current, sizeof(g_perf_current));
    } else {
        g_perf_sample_overflow = 1u;
    }

    for (lane = 0u; lane < DSYS_PERF_LANE_COUNT; ++lane) {
        for (metric = 0u; metric < DSYS_PERF_METRIC_COUNT; ++metric) {
            u64 value = g_perf_current[lane][metric];
            g_perf_last[lane][metric] = value;
            g_perf_sum[lane][metric] += value;
            if (value > g_perf_max[lane][metric]) {
                g_perf_max[lane][metric] = value;
            }
        }
    }
}

void dsys_perf_metric_set(dsys_perf_lane lane, dsys_perf_metric metric, u64 value)
{
    if (!g_perf_enabled) {
        return;
    }
    if ((u32)lane >= DSYS_PERF_LANE_COUNT || (u32)metric >= DSYS_PERF_METRIC_COUNT) {
        return;
    }
    g_perf_current[lane][metric] = value;
}

void dsys_perf_metric_add(dsys_perf_lane lane, dsys_perf_metric metric, u64 value)
{
    if (!g_perf_enabled) {
        return;
    }
    if ((u32)lane >= DSYS_PERF_LANE_COUNT || (u32)metric >= DSYS_PERF_METRIC_COUNT) {
        return;
    }
    g_perf_current[lane][metric] += value;
}

void dsys_perf_metric_max(dsys_perf_lane lane, dsys_perf_metric metric, u64 value)
{
    u64 current;
    if (!g_perf_enabled) {
        return;
    }
    if ((u32)lane >= DSYS_PERF_LANE_COUNT || (u32)metric >= DSYS_PERF_METRIC_COUNT) {
        return;
    }
    current = g_perf_current[lane][metric];
    if (value > current) {
        g_perf_current[lane][metric] = value;
    }
}

u64 dsys_perf_metric_last(dsys_perf_lane lane, dsys_perf_metric metric)
{
    if ((u32)lane >= DSYS_PERF_LANE_COUNT || (u32)metric >= DSYS_PERF_METRIC_COUNT) {
        return 0u;
    }
    return g_perf_last[lane][metric];
}

u64 dsys_perf_metric_max_seen(dsys_perf_lane lane, dsys_perf_metric metric)
{
    if ((u32)lane >= DSYS_PERF_LANE_COUNT || (u32)metric >= DSYS_PERF_METRIC_COUNT) {
        return 0u;
    }
    return g_perf_max[lane][metric];
}

void dsys_perf_timer_begin(dsys_perf_timer* timer, dsys_perf_lane lane, dsys_perf_metric metric)
{
    if (!timer) {
        return;
    }
    if (!g_perf_enabled) {
        timer->active = 0;
        timer->start_us = 0u;
        timer->lane = lane;
        timer->metric = metric;
        return;
    }
    timer->lane = lane;
    timer->metric = metric;
    timer->start_us = dsys_perf_clock_now();
    timer->active = 1;
}

void dsys_perf_timer_end(dsys_perf_timer* timer)
{
    u64 end_us;
    if (!timer || !timer->active || !g_perf_enabled) {
        return;
    }
    end_us = dsys_perf_clock_now();
    if (end_us >= timer->start_us) {
        dsys_perf_metric_add(timer->lane, timer->metric, end_us - timer->start_us);
    }
    timer->active = 0;
}

const char* dsys_perf_metric_name(dsys_perf_metric metric)
{
    if ((u32)metric >= DSYS_PERF_METRIC_COUNT) {
        return "unknown";
    }
    return g_metric_names[metric];
}

const char* dsys_perf_lane_name(dsys_perf_lane lane)
{
    if ((u32)lane >= DSYS_PERF_LANE_COUNT) {
        return "unknown";
    }
    return g_lane_names[lane];
}

int dsys_perf_flush(const dsys_perf_flush_desc* desc)
{
    (void)desc;
    return 0;
}
