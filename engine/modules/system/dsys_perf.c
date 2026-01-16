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
#include <stdio.h>
#include <errno.h>
#include <ctype.h>

#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#endif

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
static u32 g_perf_report_seq = 0u;

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

static void dsys_perf_mkdir(const char* path)
{
    if (!path || !path[0]) {
        return;
    }
#if defined(_WIN32)
    if (_mkdir(path) != 0) {
        if (errno == EEXIST) {
            return;
        }
    }
#else
    if (mkdir(path, 0755) != 0) {
        if (errno == EEXIST) {
            return;
        }
    }
#endif
}

static size_t dsys_perf_append(char* dst, size_t cap, size_t pos, const char* src)
{
    size_t len;
    if (!dst || cap == 0u || pos >= cap) {
        return pos;
    }
    if (!src) {
        return pos;
    }
    len = strlen(src);
    if (len + pos >= cap) {
        len = cap - pos - 1u;
    }
    memcpy(dst + pos, src, len);
    dst[pos + len] = '\0';
    return pos + len;
}

static size_t dsys_perf_append_char(char* dst, size_t cap, size_t pos, char ch)
{
    if (!dst || cap == 0u || pos + 1u >= cap) {
        return pos;
    }
    dst[pos++] = ch;
    dst[pos] = '\0';
    return pos;
}

static size_t dsys_perf_append_u64(char* dst, size_t cap, size_t pos, u64 value)
{
    char tmp[24];
    u32 len = 0u;
    u32 i;
    if (value == 0u) {
        tmp[len++] = '0';
    } else {
        while (value > 0u && len < sizeof(tmp)) {
            tmp[len++] = (char)('0' + (value % 10u));
            value /= 10u;
        }
    }
    for (i = 0u; i < len; ++i) {
        pos = dsys_perf_append_char(dst, cap, pos, tmp[len - 1u - i]);
    }
    return pos;
}

static size_t dsys_perf_append_i64(char* dst, size_t cap, size_t pos, i64 value)
{
    if (value < 0) {
        pos = dsys_perf_append_char(dst, cap, pos, '-');
        return dsys_perf_append_u64(dst, cap, pos, (u64)(-value));
    }
    return dsys_perf_append_u64(dst, cap, pos, (u64)value);
}

static const char* dsys_perf_get_run_root(const dsys_perf_flush_desc* desc)
{
    const char* env_root;
    if (desc && desc->run_root && desc->run_root[0]) {
        return desc->run_root;
    }
    if (g_perf_run_root_set && g_perf_run_root[0]) {
        return g_perf_run_root;
    }
    env_root = getenv("DOMINIUM_RUN_ROOT");
    if (env_root && env_root[0]) {
        return env_root;
    }
    return ".";
}

static void dsys_perf_sanitize_name(const char* src, char* out, size_t cap)
{
    size_t i = 0u;
    size_t pos = 0u;
    if (!out || cap == 0u) {
        return;
    }
    if (!src || !src[0]) {
        dsys_perf_append(out, cap, 0u, "unknown");
        return;
    }
    out[0] = '\0';
    while (src[i] && pos + 1u < cap) {
        unsigned char ch = (unsigned char)src[i++];
        if (isalnum(ch) || ch == '_' || ch == '-') {
            out[pos++] = (char)ch;
        } else {
            out[pos++] = '_';
        }
    }
    out[pos] = '\0';
}

static int dsys_perf_build_dir(char* out, size_t cap, const char* root, const char* leaf)
{
    size_t pos = 0u;
    if (!out || cap == 0u || !root || !root[0]) {
        return 0;
    }
    out[0] = '\0';
    pos = dsys_perf_append(out, cap, pos, root);
    if (pos > 0u && out[pos - 1u] != '/' && out[pos - 1u] != '\\') {
        pos = dsys_perf_append_char(out, cap, pos, '/');
    }
    dsys_perf_mkdir(root);
    pos = dsys_perf_append(out, cap, pos, "perf");
    dsys_perf_mkdir(out);
    if (leaf && leaf[0]) {
        pos = dsys_perf_append_char(out, cap, pos, '/');
        pos = dsys_perf_append(out, cap, pos, leaf);
        dsys_perf_mkdir(out);
    }
    return pos > 0u ? 1 : 0;
}

static size_t dsys_perf_append_u32_pad(char* dst, size_t cap, size_t pos, u32 value, u32 pad)
{
    char tmp[16];
    u32 len = 0u;
    u32 i;
    if (value == 0u) {
        tmp[len++] = '0';
    } else {
        while (value > 0u && len < sizeof(tmp)) {
            tmp[len++] = (char)('0' + (value % 10u));
            value /= 10u;
        }
    }
    while (len < pad && len < sizeof(tmp)) {
        tmp[len++] = '0';
    }
    for (i = 0u; i < len; ++i) {
        pos = dsys_perf_append_char(dst, cap, pos, tmp[len - 1u - i]);
    }
    return pos;
}

static int dsys_perf_build_report_path(
    char* out,
    size_t cap,
    const char* dir,
    const char* prefix,
    const char* fixture,
    u32 seq,
    const char* ext
)
{
    size_t pos = 0u;
    char safe_fixture[DSYS_PERF_MAX_NAME];
    if (!out || cap == 0u || !dir || !prefix || !ext) {
        return 0;
    }
    dsys_perf_sanitize_name(fixture, safe_fixture, sizeof(safe_fixture));
    out[0] = '\0';
    pos = dsys_perf_append(out, cap, pos, dir);
    if (pos > 0u && out[pos - 1u] != '/' && out[pos - 1u] != '\\') {
        pos = dsys_perf_append_char(out, cap, pos, '/');
    }
    pos = dsys_perf_append(out, cap, pos, prefix);
    pos = dsys_perf_append_char(out, cap, pos, '_');
    pos = dsys_perf_append(out, cap, pos, safe_fixture);
    pos = dsys_perf_append_char(out, cap, pos, '_');
    pos = dsys_perf_append_u32_pad(out, cap, pos, seq, 4u);
    pos = dsys_perf_append(out, cap, pos, ext);
    return pos > 0u ? 1 : 0;
}

static void dsys_perf_write_json_u64(FILE* fp, const char* key, u64 value, int comma)
{
    char line[160];
    size_t pos = 0u;
    if (!fp || !key) {
        return;
    }
    line[0] = '\0';
    pos = dsys_perf_append(line, sizeof(line), pos, "  \"");
    pos = dsys_perf_append(line, sizeof(line), pos, key);
    pos = dsys_perf_append(line, sizeof(line), pos, "\": ");
    pos = dsys_perf_append_u64(line, sizeof(line), pos, value);
    if (comma) {
        pos = dsys_perf_append_char(line, sizeof(line), pos, ',');
    }
    pos = dsys_perf_append_char(line, sizeof(line), pos, '\n');
    (void)pos;
    fputs(line, fp);
}

static void dsys_perf_write_json_str(FILE* fp, const char* key, const char* value, int comma)
{
    char line[200];
    size_t pos = 0u;
    if (!fp || !key) {
        return;
    }
    line[0] = '\0';
    pos = dsys_perf_append(line, sizeof(line), pos, "  \"");
    pos = dsys_perf_append(line, sizeof(line), pos, key);
    pos = dsys_perf_append(line, sizeof(line), pos, "\": \"");
    pos = dsys_perf_append(line, sizeof(line), pos, value ? value : "unknown");
    pos = dsys_perf_append(line, sizeof(line), pos, "\"");
    if (comma) {
        pos = dsys_perf_append_char(line, sizeof(line), pos, ',');
    }
    pos = dsys_perf_append_char(line, sizeof(line), pos, '\n');
    (void)pos;
    fputs(line, fp);
}

static void dsys_perf_write_telemetry(FILE* fp, const char* fixture, const char* tier)
{
    u32 s;
    u32 lane;
    u32 metric;
    char line[2048];

    if (!fp) {
        return;
    }

    for (s = 0u; s < g_perf_sample_count; ++s) {
        const dsys_perf_sample* sample = &g_perf_samples[s];
        for (lane = 0u; lane < DSYS_PERF_LANE_COUNT; ++lane) {
            size_t pos = 0u;
            line[0] = '\0';
            pos = dsys_perf_append(line, sizeof(line), pos, "{\"tick\":");
            pos = dsys_perf_append_u64(line, sizeof(line), pos, sample->tick_index);
            pos = dsys_perf_append(line, sizeof(line), pos, ",\"act\":");
            pos = dsys_perf_append_i64(line, sizeof(line), pos, (i64)sample->act);
            pos = dsys_perf_append(line, sizeof(line), pos, ",\"lane\":\"");
            pos = dsys_perf_append(line, sizeof(line), pos, dsys_perf_lane_name((dsys_perf_lane)lane));
            pos = dsys_perf_append(line, sizeof(line), pos, "\"");
            if (fixture && fixture[0]) {
                pos = dsys_perf_append(line, sizeof(line), pos, ",\"fixture\":\"");
                pos = dsys_perf_append(line, sizeof(line), pos, fixture);
                pos = dsys_perf_append(line, sizeof(line), pos, "\"");
            }
            if (tier && tier[0]) {
                pos = dsys_perf_append(line, sizeof(line), pos, ",\"tier\":\"");
                pos = dsys_perf_append(line, sizeof(line), pos, tier);
                pos = dsys_perf_append(line, sizeof(line), pos, "\"");
            }
            for (metric = 0u; metric < DSYS_PERF_METRIC_COUNT; ++metric) {
                pos = dsys_perf_append(line, sizeof(line), pos, ",\"");
                pos = dsys_perf_append(line, sizeof(line), pos, dsys_perf_metric_name((dsys_perf_metric)metric));
                pos = dsys_perf_append(line, sizeof(line), pos, "\":");
                pos = dsys_perf_append_u64(line, sizeof(line), pos, sample->values[lane][metric]);
            }
            pos = dsys_perf_append_char(line, sizeof(line), pos, '}');
            pos = dsys_perf_append_char(line, sizeof(line), pos, '\n');
            (void)pos;
            fputs(line, fp);
        }
    }
}

static void dsys_perf_write_budget_report(FILE* fp, const char* fixture, const char* tier)
{
    u32 lane;
    u32 metric;
    char key[DSYS_PERF_MAX_NAME];

    if (!fp) {
        return;
    }

    fputs("{\n", fp);
    dsys_perf_write_json_str(fp, "check_id", "PERF-BUDGET-002", 1);
    dsys_perf_write_json_str(fp, "fixture", fixture ? fixture : "unknown", 1);
    dsys_perf_write_json_str(fp, "tier", tier ? tier : "unknown", 1);
    dsys_perf_write_json_u64(fp, "samples", g_perf_sample_count, 1);
    dsys_perf_write_json_u64(fp, "overflow", g_perf_sample_overflow, 1);
    fputs("  \"metrics\": {\n", fp);

    for (lane = 0u; lane < DSYS_PERF_LANE_COUNT; ++lane) {
        for (metric = 0u; metric < DSYS_PERF_METRIC_COUNT; ++metric) {
            size_t pos = 0u;
            key[0] = '\0';
            pos = dsys_perf_append(key, sizeof(key), pos, dsys_perf_lane_name((dsys_perf_lane)lane));
            pos = dsys_perf_append_char(key, sizeof(key), pos, '_');
            pos = dsys_perf_append(key, sizeof(key), pos, dsys_perf_metric_name((dsys_perf_metric)metric));
            pos = dsys_perf_append(key, sizeof(key), pos, "_max");
            (void)pos;
            dsys_perf_write_json_u64(
                fp,
                key,
                g_perf_max[lane][metric],
                (lane != (DSYS_PERF_LANE_COUNT - 1u) || metric != (DSYS_PERF_METRIC_COUNT - 1u))
            );
        }
    }

    fputs("  }\n", fp);
    fputs("}\n", fp);
}

int dsys_perf_flush(const dsys_perf_flush_desc* desc)
{
    char telemetry_dir[DSYS_PERF_MAX_PATH];
    char budget_dir[DSYS_PERF_MAX_PATH];
    char telemetry_path[DSYS_PERF_MAX_PATH];
    char budget_path[DSYS_PERF_MAX_PATH];
    const char* root;
    const char* fixture;
    const char* tier;
    u32 seq;
    FILE* fp;

    if (!desc) {
        return -1;
    }

    root = dsys_perf_get_run_root(desc);
    fixture = desc->fixture && desc->fixture[0] ? desc->fixture : "unknown";
    tier = desc->tier && desc->tier[0] ? desc->tier : "unknown";
    seq = ++g_perf_report_seq;

    if (!dsys_perf_build_dir(telemetry_dir, sizeof(telemetry_dir), root, "telemetry")) {
        return -2;
    }
    if (!dsys_perf_build_dir(budget_dir, sizeof(budget_dir), root, "budgets")) {
        return -3;
    }

    if (desc->emit_telemetry) {
        if (!dsys_perf_build_report_path(telemetry_path, sizeof(telemetry_path), telemetry_dir, "telemetry", fixture, seq, ".jsonl")) {
            return -4;
        }
        fp = fopen(telemetry_path, "wb");
        if (!fp) {
            return -5;
        }
        dsys_perf_write_telemetry(fp, fixture, tier);
        fclose(fp);
    }

    if (desc->emit_budget_report) {
        if (!dsys_perf_build_report_path(budget_path, sizeof(budget_path), budget_dir, "PERF-BUDGET-002", fixture, seq, ".json")) {
            return -6;
        }
        fp = fopen(budget_path, "wb");
        if (!fp) {
            return -7;
        }
        dsys_perf_write_budget_report(fp, fixture, tier);
        fclose(fp);
    }

    return 0;
}
