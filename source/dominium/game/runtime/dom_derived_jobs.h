/*
FILE: source/dominium/game/runtime/dom_derived_jobs.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_derived_jobs
RESPONSIBILITY: Defines derived (non-authoritative) job queue contract for budgeted work.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Derived-only; job completion order must not affect sim determinism.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_DERIVED_JOBS_H
#define DOM_DERIVED_JOBS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_DERIVED_QUEUE_DESC_VERSION = 1u
};

enum {
    DOM_DERIVED_QUEUE_FLAG_ALLOW_IO = 1u
};

typedef struct dom_derived_queue dom_derived_queue;

typedef struct dom_derived_queue_desc {
    u32 struct_size;
    u32 struct_version;
    u32 max_jobs;
    u32 max_payload_bytes;
    u32 flags;
} dom_derived_queue_desc;

typedef enum dom_derived_job_kind {
    DERIVED_IO_READ_FILE = 1,
    DERIVED_IO_READ_CONTAINER_CHUNK = 2,
    DERIVED_DECOMPRESS = 3,
    DERIVED_BUILD_MESH = 4,
    DERIVED_BUILD_MAP_TILE = 5
} dom_derived_job_kind;

typedef struct dom_derived_job_payload {
    const void *data;
    u32 size;
} dom_derived_job_payload;

typedef struct dom_derived_job_budget_hint {
    u32 work_ms;
    u32 io_bytes;
} dom_derived_job_budget_hint;

typedef u64 dom_derived_job_id;

typedef enum dom_derived_job_state {
    DOM_DERIVED_JOB_PENDING = 0,
    DOM_DERIVED_JOB_RUNNING = 1,
    DOM_DERIVED_JOB_DONE = 2,
    DOM_DERIVED_JOB_FAILED = 3,
    DOM_DERIVED_JOB_CANCELED = 4
} dom_derived_job_state;

enum {
    DOM_DERIVED_ERR_NONE = 0,
    DOM_DERIVED_ERR_UNSUPPORTED = 1,
    DOM_DERIVED_ERR_IO_DISABLED = 2,
    DOM_DERIVED_ERR_BAD_INPUT = 3,
    DOM_DERIVED_ERR_QUEUE_FULL = 4
};

enum {
    DOM_DERIVED_STATUS_VERSION = 1u,
    DOM_DERIVED_STATS_VERSION = 1u
};

typedef struct dom_derived_job_status {
    u32 struct_size;
    u32 struct_version;
    u32 kind;
    u32 state;
    int last_error;
    u32 io_bytes;
    u32 work_ms;
} dom_derived_job_status;

typedef struct dom_derived_stats {
    u32 struct_size;
    u32 struct_version;
    u32 queued;
    u32 running;
    u32 completed;
    u32 failed;
    u32 canceled;
    u32 last_pump_jobs;
    u32 last_pump_ms;
    u32 last_pump_io_bytes;
} dom_derived_stats;

dom_derived_queue *dom_derived_queue_create(const dom_derived_queue_desc *desc);
void dom_derived_queue_destroy(dom_derived_queue *queue);

dom_derived_job_id dom_derived_submit(dom_derived_queue *queue,
                                      dom_derived_job_kind kind,
                                      const dom_derived_job_payload *payload,
                                      int priority);

int dom_derived_pump(dom_derived_queue *queue,
                     u32 max_ms,
                     u64 max_io_bytes,
                     u32 max_jobs);

int dom_derived_poll(dom_derived_queue *queue,
                     dom_derived_job_id job_id,
                     dom_derived_job_status *out_status);

int dom_derived_cancel(dom_derived_queue *queue,
                       dom_derived_job_id job_id);

int dom_derived_get_stats(dom_derived_queue *queue,
                          dom_derived_stats *out_stats);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_DERIVED_JOBS_H */
