/*
FILE: include/domino/system/dsys_guard.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / system/dsys_guard
RESPONSIBILITY: Defines public contract for UI/render thread guards and stall watchdog; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: N/A (runtime perf guard).
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_SYSTEM_DSYS_GUARD_H
#define DOMINO_SYSTEM_DSYS_GUARD_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Thread flags */
#define DSYS_THREAD_FLAG_NO_BLOCK 0x1u

/* Purpose: Tag current thread with a name and flags (e.g., UI/render no-block). */
void dsys_thread_tag_current(const char* name, u32 flags);
/* Purpose: Clear tags for current thread. */
void dsys_thread_clear_current(void);
/* Purpose: Get current thread flags. */
u32  dsys_thread_current_flags(void);
/* Purpose: Get current thread name (or "unknown"). */
const char* dsys_thread_current_name(void);
/* Purpose: Get current thread id (platform-dependent). */
u64  dsys_thread_current_id(void);

/* Purpose: Set ACT timestamp (us) used in guard reports. */
void dsys_guard_set_act_time_us(u64 act_us);
/* Purpose: Set current sim tick for guard reports. */
void dsys_guard_set_sim_tick(u64 tick);
/* Purpose: Override run_root for guard reports (NULL clears override). */
void dsys_guard_set_run_root(const char* path);
/* Purpose: Enable/disable IO guard (enabled by default). */
void dsys_guard_set_io_enabled(int enabled);
/* Purpose: Enable fatal IO guard (abort on violation). */
void dsys_guard_set_io_fatal(int fatal);
/* Purpose: Get IO violation count. */
u32  dsys_guard_get_io_violation_count(void);

/* Derived job queue (no-block friendly). */
typedef void (*dsys_derived_job_fn)(void* user);
typedef struct dsys_derived_job_desc {
    dsys_derived_job_fn fn;
    void*               user;
    const char*         tag;
} dsys_derived_job_desc;

/* Purpose: Submit a derived job (non-blocking). Returns 0 on success. */
int dsys_derived_job_submit(const dsys_derived_job_desc* desc);
/* Purpose: Run the next derived job. Returns 1 if a job ran. */
int dsys_derived_job_run_next(void);
/* Purpose: Get pending derived job count. */
u32 dsys_derived_job_pending(void);

/* Stall watchdog */
void dsys_stall_watchdog_set_enabled(int enabled);
void dsys_stall_watchdog_set_threshold_ms(u32 threshold_ms);
void dsys_stall_watchdog_frame_begin(const char* tag);
void dsys_stall_watchdog_frame_end(void);
int  dsys_stall_watchdog_was_triggered(void);
u64  dsys_stall_watchdog_longest_us(void);
u32  dsys_stall_watchdog_report_count(void);
void dsys_stall_watchdog_reset(void);

/* Internal hooks used by sys wrappers. */
int dsys_guard_io_blocked(const char* op, const char* path, const char* file, u32 line);
void dsys_guard_track_file_handle(void* handle, const char* path);
void dsys_guard_untrack_file_handle(void* handle);
const char* dsys_guard_lookup_file_path(void* handle);

void dsys_guard_track_dir_handle(void* handle, const char* path);
void dsys_guard_untrack_dir_handle(void* handle);
const char* dsys_guard_lookup_dir_path(void* handle);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SYSTEM_DSYS_GUARD_H */
