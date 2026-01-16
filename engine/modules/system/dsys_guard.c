/*
FILE: source/domino/system/dsys_guard.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_guard
RESPONSIBILITY: Implements UI/render thread guards, IO ban reporting, derived job queue, and stall watchdog.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: N/A (runtime perf guard).
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/system/dsys_guard.h"

#include "domino/sys.h"

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

#if defined(_WIN32)
#include <windows.h>
#include <direct.h>
#else
#include <sys/stat.h>
#include <pthread.h>
#endif

#define DSYS_GUARD_MAX_THREADS 8u
#define DSYS_GUARD_NAME_MAX 32u
#define DSYS_GUARD_MAX_HANDLES 64u
#define DSYS_GUARD_MAX_PATH 260u
#define DSYS_GUARD_MAX_TAG 64u
#define DSYS_GUARD_MAX_JOBS 64u

typedef struct dsys_thread_tag {
    u64 id;
    u32 flags;
    char name[DSYS_GUARD_NAME_MAX];
    int in_use;
} dsys_thread_tag;

typedef struct dsys_handle_track {
    void* handle;
    char path[DSYS_GUARD_MAX_PATH];
    int in_use;
} dsys_handle_track;

typedef struct dsys_io_counts {
    u32 file_open;
    u32 file_read;
    u32 file_write;
    u32 file_seek;
    u32 file_tell;
    u32 file_close;
    u32 dir_open;
    u32 dir_next;
    u32 dir_close;
} dsys_io_counts;

typedef struct dsys_job_entry {
    dsys_derived_job_fn fn;
    void* user;
    char tag[DSYS_GUARD_MAX_TAG];
    int in_use;
} dsys_job_entry;

static dsys_thread_tag g_thread_tags[DSYS_GUARD_MAX_THREADS];
static dsys_handle_track g_file_tracks[DSYS_GUARD_MAX_HANDLES];
static dsys_handle_track g_dir_tracks[DSYS_GUARD_MAX_HANDLES];
static dsys_io_counts g_io_counts;
static u32 g_io_violation_count = 0u;
static u32 g_io_report_seq = 0u;
static int g_io_guard_enabled = 1;
static int g_io_guard_fatal = 0;

static u64 g_guard_act_us = 0u;
static u64 g_guard_sim_tick = 0u;
static char g_guard_run_root[DSYS_GUARD_MAX_PATH];
static int g_guard_run_root_set = 0;

static dsys_job_entry g_jobs[DSYS_GUARD_MAX_JOBS];
static u32 g_job_head = 0u;
static u32 g_job_tail = 0u;
static u32 g_job_count = 0u;

static int g_stall_enabled = 1;
static u64 g_stall_frame_start_us = 0u;
static u64 g_stall_longest_us = 0u;
static u64 g_stall_threshold_us = 2000u;
static u32 g_stall_report_seq = 0u;
static u32 g_stall_count = 0u;
static int g_stall_triggered = 0;
static char g_stall_tag[DSYS_GUARD_MAX_TAG];
static u64 g_stall_thread_id = 0u;

static u64 dsys_guard_thread_id(void)
{
#if defined(_WIN32)
    return (u64)GetCurrentThreadId();
#elif defined(_POSIX_VERSION)
    return (u64)(size_t)pthread_self();
#else
    return 0u;
#endif
}

u64 dsys_thread_current_id(void)
{
    return dsys_guard_thread_id();
}

static dsys_thread_tag* dsys_guard_find_thread(u64 id)
{
    u32 i;
    for (i = 0u; i < DSYS_GUARD_MAX_THREADS; ++i) {
        if (g_thread_tags[i].in_use && g_thread_tags[i].id == id) {
            return &g_thread_tags[i];
        }
    }
    return NULL;
}

static dsys_thread_tag* dsys_guard_alloc_thread(u64 id)
{
    u32 i;
    for (i = 0u; i < DSYS_GUARD_MAX_THREADS; ++i) {
        if (!g_thread_tags[i].in_use) {
            g_thread_tags[i].in_use = 1;
            g_thread_tags[i].id = id;
            g_thread_tags[i].flags = 0u;
            g_thread_tags[i].name[0] = '\0';
            return &g_thread_tags[i];
        }
    }
    g_thread_tags[0].in_use = 1;
    g_thread_tags[0].id = id;
    g_thread_tags[0].flags = 0u;
    g_thread_tags[0].name[0] = '\0';
    return &g_thread_tags[0];
}

void dsys_thread_tag_current(const char* name, u32 flags)
{
    u64 id = dsys_guard_thread_id();
    dsys_thread_tag* tag = dsys_guard_find_thread(id);
    if (!tag) {
        tag = dsys_guard_alloc_thread(id);
    }
    if (tag) {
        tag->flags = flags;
        if (name && name[0]) {
            strncpy(tag->name, name, DSYS_GUARD_NAME_MAX - 1u);
            tag->name[DSYS_GUARD_NAME_MAX - 1u] = '\0';
        } else {
            tag->name[0] = '\0';
        }
    }
}

void dsys_thread_clear_current(void)
{
    u64 id = dsys_guard_thread_id();
    dsys_thread_tag* tag = dsys_guard_find_thread(id);
    if (tag) {
        tag->in_use = 0;
        tag->id = 0u;
        tag->flags = 0u;
        tag->name[0] = '\0';
    }
}

u32 dsys_thread_current_flags(void)
{
    u64 id = dsys_guard_thread_id();
    dsys_thread_tag* tag = dsys_guard_find_thread(id);
    if (tag) {
        return tag->flags;
    }
    return 0u;
}

const char* dsys_thread_current_name(void)
{
    u64 id = dsys_guard_thread_id();
    dsys_thread_tag* tag = dsys_guard_find_thread(id);
    if (tag && tag->name[0]) {
        return tag->name;
    }
    return "unknown";
}

void dsys_guard_set_act_time_us(u64 act_us)
{
    g_guard_act_us = act_us;
}

void dsys_guard_set_sim_tick(u64 tick)
{
    g_guard_sim_tick = tick;
}

void dsys_guard_set_run_root(const char* path)
{
    if (path && path[0]) {
        strncpy(g_guard_run_root, path, DSYS_GUARD_MAX_PATH - 1u);
        g_guard_run_root[DSYS_GUARD_MAX_PATH - 1u] = '\0';
        g_guard_run_root_set = 1;
    } else {
        g_guard_run_root[0] = '\0';
        g_guard_run_root_set = 0;
    }
}

void dsys_guard_set_io_enabled(int enabled)
{
    g_io_guard_enabled = enabled ? 1 : 0;
}

void dsys_guard_set_io_fatal(int fatal)
{
    g_io_guard_fatal = fatal ? 1 : 0;
}

u32 dsys_guard_get_io_violation_count(void)
{
    return g_io_violation_count;
}

static void dsys_guard_mkdir(const char* path)
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

static size_t dsys_guard_append(char* dst, size_t cap, size_t pos, const char* src)
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

static size_t dsys_guard_append_char(char* dst, size_t cap, size_t pos, char ch)
{
    if (!dst || cap == 0u || pos + 1u >= cap) {
        return pos;
    }
    dst[pos++] = ch;
    dst[pos] = '\0';
    return pos;
}

static size_t dsys_guard_append_u32_pad(char* dst, size_t cap, size_t pos, u32 value, u32 pad)
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
        pos = dsys_guard_append_char(dst, cap, pos, tmp[len - 1u - i]);
    }
    return pos;
}

static size_t dsys_guard_append_u64(char* dst, size_t cap, size_t pos, u64 value)
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
        pos = dsys_guard_append_char(dst, cap, pos, tmp[len - 1u - i]);
    }
    return pos;
}

static const char* dsys_guard_get_run_root_path(void)
{
    const char* env_root;
    if (g_guard_run_root_set && g_guard_run_root[0]) {
        return g_guard_run_root;
    }
    env_root = getenv("DOMINIUM_RUN_ROOT");
    if (env_root && env_root[0]) {
        return env_root;
    }
    return ".";
}

static int dsys_guard_build_report_dir(char* out, size_t cap)
{
    size_t pos = 0u;
    const char* root = dsys_guard_get_run_root_path();
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    pos = dsys_guard_append(out, cap, pos, root);
    if (pos > 0u && out[pos - 1u] != '/' && out[pos - 1u] != '\\') {
        pos = dsys_guard_append_char(out, cap, pos, '/');
    }
    dsys_guard_mkdir(root);
    pos = dsys_guard_append(out, cap, pos, "perf");
    dsys_guard_mkdir(out);
    pos = dsys_guard_append_char(out, cap, pos, '/');
    pos = dsys_guard_append(out, cap, pos, "no_modal_loading");
    dsys_guard_mkdir(out);
    return 1;
}

static int dsys_guard_build_report_path(char* out, size_t cap, const char* prefix, u32 seq)
{
    char dir[DSYS_GUARD_MAX_PATH];
    size_t pos = 0u;
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (!dsys_guard_build_report_dir(dir, sizeof(dir))) {
        return 0;
    }
    pos = dsys_guard_append(out, cap, pos, dir);
    if (pos > 0u && out[pos - 1u] != '/' && out[pos - 1u] != '\\') {
        pos = dsys_guard_append_char(out, cap, pos, '/');
    }
    pos = dsys_guard_append(out, cap, pos, prefix);
    pos = dsys_guard_append_char(out, cap, pos, '_');
    pos = dsys_guard_append_u32_pad(out, cap, pos, seq, 4u);
    pos = dsys_guard_append(out, cap, pos, ".log");
    return (pos > 0u) ? 1 : 0;
}

static void dsys_guard_write_kv(FILE* fp, const char* key, const char* value)
{
    if (!fp || !key || !value) {
        return;
    }
    fputs(key, fp);
    fputs(": ", fp);
    fputs(value, fp);
    fputs("\n", fp);
}

static void dsys_guard_write_kv_u64(FILE* fp, const char* key, u64 value)
{
    char buf[32];
    size_t pos = 0u;
    buf[0] = '\0';
    pos = dsys_guard_append_u64(buf, sizeof(buf), pos, value);
    if (pos == 0u) {
        dsys_guard_write_kv(fp, key, "0");
        return;
    }
    dsys_guard_write_kv(fp, key, buf);
}

static void dsys_guard_write_kv_u32(FILE* fp, const char* key, u32 value)
{
    char buf[16];
    size_t pos = 0u;
    buf[0] = '\0';
    pos = dsys_guard_append_u32_pad(buf, sizeof(buf), pos, value, 0u);
    if (pos == 0u) {
        dsys_guard_write_kv(fp, key, "0");
        return;
    }
    dsys_guard_write_kv(fp, key, buf);
}

static void dsys_guard_write_io_report(const char* op, const char* path, const char* file, u32 line)
{
    char report_path[DSYS_GUARD_MAX_PATH];
    FILE* fp;
    u32 seq = ++g_io_report_seq;
    if (!dsys_guard_build_report_path(report_path, sizeof(report_path), "PERF-IOBAN-001", seq)) {
        return;
    }
    fp = fopen(report_path, "wb");
    if (!fp) {
        return;
    }
    dsys_guard_write_kv(fp, "check_id", "PERF-IOBAN-001");
    dsys_guard_write_kv(fp, "description", "UI/render thread IO ban violation");
    dsys_guard_write_kv_u64(fp, "act_us", g_guard_act_us);
    dsys_guard_write_kv_u64(fp, "sim_tick", g_guard_sim_tick);
    dsys_guard_write_kv_u64(fp, "thread_id", dsys_thread_current_id());
    dsys_guard_write_kv(fp, "thread_name", dsys_thread_current_name());
    dsys_guard_write_kv_u32(fp, "thread_flags", dsys_thread_current_flags());
    dsys_guard_write_kv(fp, "operation", op ? op : "unknown");
    dsys_guard_write_kv(fp, "path", path ? path : "unknown");
    dsys_guard_write_kv(fp, "callsite_file", (file && file[0]) ? file : "unknown");
    dsys_guard_write_kv_u32(fp, "callsite_line", line);
    dsys_guard_write_kv_u32(fp, "violations_total", g_io_violation_count);
    dsys_guard_write_kv_u32(fp, "blocked_total", g_io_violation_count);
    dsys_guard_write_kv_u32(fp, "blocked_file_open", g_io_counts.file_open);
    dsys_guard_write_kv_u32(fp, "blocked_file_read", g_io_counts.file_read);
    dsys_guard_write_kv_u32(fp, "blocked_file_write", g_io_counts.file_write);
    dsys_guard_write_kv_u32(fp, "blocked_file_seek", g_io_counts.file_seek);
    dsys_guard_write_kv_u32(fp, "blocked_file_tell", g_io_counts.file_tell);
    dsys_guard_write_kv_u32(fp, "blocked_file_close", g_io_counts.file_close);
    dsys_guard_write_kv_u32(fp, "blocked_dir_open", g_io_counts.dir_open);
    dsys_guard_write_kv_u32(fp, "blocked_dir_next", g_io_counts.dir_next);
    dsys_guard_write_kv_u32(fp, "blocked_dir_close", g_io_counts.dir_close);
    fclose(fp);
}

static void dsys_guard_write_stall_report(u64 duration_us)
{
    char report_path[DSYS_GUARD_MAX_PATH];
    FILE* fp;
    u32 seq = ++g_stall_report_seq;
    if (!dsys_guard_build_report_path(report_path, sizeof(report_path), "PERF-STALL-001", seq)) {
        return;
    }
    fp = fopen(report_path, "wb");
    if (!fp) {
        return;
    }
    dsys_guard_write_kv(fp, "check_id", "PERF-STALL-001");
    dsys_guard_write_kv(fp, "description", "Render/UI stall watchdog threshold exceeded");
    dsys_guard_write_kv_u64(fp, "act_us", g_guard_act_us);
    dsys_guard_write_kv_u64(fp, "sim_tick", g_guard_sim_tick);
    dsys_guard_write_kv_u64(fp, "thread_id", g_stall_thread_id);
    dsys_guard_write_kv(fp, "thread_name", dsys_thread_current_name());
    dsys_guard_write_kv_u32(fp, "thread_flags", dsys_thread_current_flags());
    dsys_guard_write_kv(fp, "stall_tag", g_stall_tag[0] ? g_stall_tag : "unknown");
    dsys_guard_write_kv_u64(fp, "duration_us", duration_us);
    dsys_guard_write_kv_u64(fp, "threshold_us", g_stall_threshold_us);
    dsys_guard_write_kv_u64(fp, "longest_us", g_stall_longest_us);
    dsys_guard_write_kv_u32(fp, "stall_count", g_stall_count);
    fclose(fp);
}

static void dsys_guard_count_io_op(const char* op)
{
    if (!op) {
        return;
    }
    if (strcmp(op, "file_open") == 0) {
        g_io_counts.file_open++;
    } else if (strcmp(op, "file_read") == 0) {
        g_io_counts.file_read++;
    } else if (strcmp(op, "file_write") == 0) {
        g_io_counts.file_write++;
    } else if (strcmp(op, "file_seek") == 0) {
        g_io_counts.file_seek++;
    } else if (strcmp(op, "file_tell") == 0) {
        g_io_counts.file_tell++;
    } else if (strcmp(op, "file_close") == 0) {
        g_io_counts.file_close++;
    } else if (strcmp(op, "dir_open") == 0) {
        g_io_counts.dir_open++;
    } else if (strcmp(op, "dir_next") == 0) {
        g_io_counts.dir_next++;
    } else if (strcmp(op, "dir_close") == 0) {
        g_io_counts.dir_close++;
    }
}

int dsys_guard_io_blocked(const char* op, const char* path, const char* file, u32 line)
{
    if (!g_io_guard_enabled) {
        return 0;
    }
    if ((dsys_thread_current_flags() & DSYS_THREAD_FLAG_NO_BLOCK) == 0u) {
        return 0;
    }
    g_io_violation_count++;
    dsys_guard_count_io_op(op);
    dsys_guard_write_io_report(op, path, file, line);
    if (g_io_guard_fatal) {
        abort();
    }
    return 1;
}

static dsys_handle_track* dsys_guard_find_handle(dsys_handle_track* table, void* handle)
{
    u32 i;
    for (i = 0u; i < DSYS_GUARD_MAX_HANDLES; ++i) {
        if (table[i].in_use && table[i].handle == handle) {
            return &table[i];
        }
    }
    return NULL;
}

static dsys_handle_track* dsys_guard_alloc_handle(dsys_handle_track* table, void* handle)
{
    u32 i;
    for (i = 0u; i < DSYS_GUARD_MAX_HANDLES; ++i) {
        if (!table[i].in_use) {
            table[i].in_use = 1;
            table[i].handle = handle;
            table[i].path[0] = '\0';
            return &table[i];
        }
    }
    return &table[0];
}

void dsys_guard_track_file_handle(void* handle, const char* path)
{
    dsys_handle_track* slot;
    if (!handle) {
        return;
    }
    slot = dsys_guard_find_handle(g_file_tracks, handle);
    if (!slot) {
        slot = dsys_guard_alloc_handle(g_file_tracks, handle);
    }
    if (slot) {
        slot->handle = handle;
        if (path && path[0]) {
            strncpy(slot->path, path, DSYS_GUARD_MAX_PATH - 1u);
            slot->path[DSYS_GUARD_MAX_PATH - 1u] = '\0';
        } else {
            slot->path[0] = '\0';
        }
    }
}

void dsys_guard_untrack_file_handle(void* handle)
{
    dsys_handle_track* slot;
    if (!handle) {
        return;
    }
    slot = dsys_guard_find_handle(g_file_tracks, handle);
    if (slot) {
        slot->in_use = 0;
        slot->handle = NULL;
        slot->path[0] = '\0';
    }
}

const char* dsys_guard_lookup_file_path(void* handle)
{
    dsys_handle_track* slot;
    if (!handle) {
        return NULL;
    }
    slot = dsys_guard_find_handle(g_file_tracks, handle);
    if (slot && slot->path[0]) {
        return slot->path;
    }
    return NULL;
}

void dsys_guard_track_dir_handle(void* handle, const char* path)
{
    dsys_handle_track* slot;
    if (!handle) {
        return;
    }
    slot = dsys_guard_find_handle(g_dir_tracks, handle);
    if (!slot) {
        slot = dsys_guard_alloc_handle(g_dir_tracks, handle);
    }
    if (slot) {
        slot->handle = handle;
        if (path && path[0]) {
            strncpy(slot->path, path, DSYS_GUARD_MAX_PATH - 1u);
            slot->path[DSYS_GUARD_MAX_PATH - 1u] = '\0';
        } else {
            slot->path[0] = '\0';
        }
    }
}

void dsys_guard_untrack_dir_handle(void* handle)
{
    dsys_handle_track* slot;
    if (!handle) {
        return;
    }
    slot = dsys_guard_find_handle(g_dir_tracks, handle);
    if (slot) {
        slot->in_use = 0;
        slot->handle = NULL;
        slot->path[0] = '\0';
    }
}

const char* dsys_guard_lookup_dir_path(void* handle)
{
    dsys_handle_track* slot;
    if (!handle) {
        return NULL;
    }
    slot = dsys_guard_find_handle(g_dir_tracks, handle);
    if (slot && slot->path[0]) {
        return slot->path;
    }
    return NULL;
}

int dsys_derived_job_submit(const dsys_derived_job_desc* desc)
{
    dsys_job_entry* slot;
    if (!desc || !desc->fn) {
        return -1;
    }
    if (g_job_count >= DSYS_GUARD_MAX_JOBS) {
        return -1;
    }
    slot = &g_jobs[g_job_tail];
    slot->fn = desc->fn;
    slot->user = desc->user;
    slot->in_use = 1;
    if (desc->tag && desc->tag[0]) {
        strncpy(slot->tag, desc->tag, DSYS_GUARD_MAX_TAG - 1u);
        slot->tag[DSYS_GUARD_MAX_TAG - 1u] = '\0';
    } else {
        slot->tag[0] = '\0';
    }
    g_job_tail = (g_job_tail + 1u) % DSYS_GUARD_MAX_JOBS;
    g_job_count++;
    return 0;
}

int dsys_derived_job_run_next(void)
{
    dsys_job_entry job;
    if (g_job_count == 0u) {
        return 0;
    }
    job = g_jobs[g_job_head];
    g_jobs[g_job_head].in_use = 0;
    g_jobs[g_job_head].fn = NULL;
    g_jobs[g_job_head].user = NULL;
    g_jobs[g_job_head].tag[0] = '\0';
    g_job_head = (g_job_head + 1u) % DSYS_GUARD_MAX_JOBS;
    g_job_count--;
    if (job.fn) {
        job.fn(job.user);
        return 1;
    }
    return 0;
}

u32 dsys_derived_job_pending(void)
{
    return g_job_count;
}

void dsys_stall_watchdog_set_enabled(int enabled)
{
    g_stall_enabled = enabled ? 1 : 0;
}

void dsys_stall_watchdog_set_threshold_ms(u32 threshold_ms)
{
    g_stall_threshold_us = (u64)threshold_ms * 1000u;
}

void dsys_stall_watchdog_frame_begin(const char* tag)
{
    if (!g_stall_enabled) {
        return;
    }
    if ((dsys_thread_current_flags() & DSYS_THREAD_FLAG_NO_BLOCK) == 0u) {
        return;
    }
    g_stall_frame_start_us = dsys_time_now_us();
    g_stall_thread_id = dsys_thread_current_id();
    if (tag && tag[0]) {
        strncpy(g_stall_tag, tag, DSYS_GUARD_MAX_TAG - 1u);
        g_stall_tag[DSYS_GUARD_MAX_TAG - 1u] = '\0';
    } else {
        g_stall_tag[0] = '\0';
    }
}

void dsys_stall_watchdog_frame_end(void)
{
    u64 end_us;
    u64 delta;
    if (!g_stall_enabled) {
        return;
    }
    if (g_stall_frame_start_us == 0u) {
        return;
    }
    end_us = dsys_time_now_us();
    if (end_us < g_stall_frame_start_us) {
        g_stall_frame_start_us = 0u;
        return;
    }
    delta = end_us - g_stall_frame_start_us;
    g_stall_frame_start_us = 0u;
    if (delta > g_stall_longest_us) {
        g_stall_longest_us = delta;
    }
    if (delta > g_stall_threshold_us) {
        g_stall_count++;
        g_stall_triggered = 1;
        dsys_guard_write_stall_report(delta);
        if (g_io_guard_fatal) {
            abort();
        }
    }
}

int dsys_stall_watchdog_was_triggered(void)
{
    return g_stall_triggered ? 1 : 0;
}

u64 dsys_stall_watchdog_longest_us(void)
{
    return g_stall_longest_us;
}

u32 dsys_stall_watchdog_report_count(void)
{
    return g_stall_report_seq;
}

void dsys_stall_watchdog_reset(void)
{
    g_stall_frame_start_us = 0u;
    g_stall_longest_us = 0u;
    g_stall_triggered = 0;
    g_stall_count = 0u;
    g_stall_tag[0] = '\0';
    g_stall_thread_id = 0u;
}
