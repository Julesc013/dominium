/*
FILE: source/dominium/game/runtime/dom_derived_jobs.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_derived_jobs
RESPONSIBILITY: Implements derived (non-authoritative) job queue with budgeted pumping.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Derived-only; queue state must not affect authoritative hashes.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_derived_jobs.h"

#include <vector>
#include <cstring>
#include <climits>

#include "domino/sys.h"
#include "dom_profiler.h"

struct dom_derived_job {
    u64 id;
    u64 submit_seq;
    u64 submit_us;
    u64 start_us;
    u64 end_us;
    dom_derived_job_kind kind;
    int priority;
    u32 state;
    int last_error;
    u32 hint_work_ms;
    u32 hint_io_bytes;
    std::vector<unsigned char> payload;
};

struct dom_derived_queue {
    u64 next_id;
    u64 submit_seq;
    u32 max_jobs;
    u32 max_payload_bytes;
    u32 flags;
    std::vector<dom_derived_job> jobs;
    dom_derived_stats stats;
};

namespace {

static const u32 DEFAULT_MAX_JOBS = 128u;
static const u32 DEFAULT_MAX_PAYLOAD_BYTES = 256u * 1024u;

static bool is_terminal_state(u32 state) {
    return state == DOM_DERIVED_JOB_DONE ||
           state == DOM_DERIVED_JOB_FAILED ||
           state == DOM_DERIVED_JOB_CANCELED;
}

static bool is_io_kind(dom_derived_job_kind kind) {
    return kind == DERIVED_IO_READ_FILE ||
           kind == DERIVED_IO_READ_CONTAINER_CHUNK;
}

static void extract_budget_hint(const dom_derived_job_payload *payload,
                                u32 *out_ms,
                                u32 *out_io_bytes) {
    dom_derived_job_budget_hint hint;
    if (!out_ms || !out_io_bytes) {
        return;
    }
    *out_ms = 0u;
    *out_io_bytes = 0u;
    if (!payload || !payload->data || payload->size < sizeof(hint)) {
        return;
    }
    std::memcpy(&hint, payload->data, sizeof(hint));
    *out_ms = hint.work_ms;
    *out_io_bytes = hint.io_bytes;
}

static size_t find_reuse_slot(dom_derived_queue *queue) {
    size_t i;
    if (!queue) {
        return (size_t)-1;
    }
    for (i = 0u; i < queue->jobs.size(); ++i) {
        if (is_terminal_state(queue->jobs[i].state)) {
            return i;
        }
    }
    return (size_t)-1;
}

static size_t find_next_job(dom_derived_queue *queue,
                            u64 io_budget_left,
                            bool allow_io) {
    size_t best = (size_t)-1;
    int best_priority = INT_MIN;
    u64 best_seq = 0u;
    size_t i;

    if (!queue) {
        return (size_t)-1;
    }

    for (i = 0u; i < queue->jobs.size(); ++i) {
        const dom_derived_job &job = queue->jobs[i];
        if (job.state != DOM_DERIVED_JOB_PENDING) {
            continue;
        }
        if (is_io_kind(job.kind) && !allow_io) {
            continue;
        }
        if (job.hint_io_bytes > io_budget_left) {
            continue;
        }
        if (best == (size_t)-1 ||
            job.priority > best_priority ||
            (job.priority == best_priority && job.submit_seq < best_seq)) {
            best = i;
            best_priority = job.priority;
            best_seq = job.submit_seq;
        }
    }

    return best;
}

static void update_stats(const dom_derived_queue *queue, dom_derived_stats *out_stats) {
    u32 queued = 0u;
    u32 running = 0u;
    u32 completed = 0u;
    u32 failed = 0u;
    u32 canceled = 0u;
    size_t i;

    if (!queue || !out_stats) {
        return;
    }

    for (i = 0u; i < queue->jobs.size(); ++i) {
        switch (queue->jobs[i].state) {
        case DOM_DERIVED_JOB_PENDING:
            queued += 1u;
            break;
        case DOM_DERIVED_JOB_RUNNING:
            running += 1u;
            break;
        case DOM_DERIVED_JOB_DONE:
            completed += 1u;
            break;
        case DOM_DERIVED_JOB_FAILED:
            failed += 1u;
            break;
        case DOM_DERIVED_JOB_CANCELED:
            canceled += 1u;
            break;
        default:
            break;
        }
    }

    out_stats->queued = queued;
    out_stats->running = running;
    out_stats->completed = completed;
    out_stats->failed = failed;
    out_stats->canceled = canceled;
}

static bool payload_matches(const dom_derived_job &job,
                            const unsigned char *src,
                            u32 size) {
    if (job.payload.size() != size) {
        return false;
    }
    if (size == 0u) {
        return true;
    }
    if (!src) {
        return false;
    }
    return std::memcmp(&job.payload[0], src, size) == 0;
}

static dom_derived_job_id find_coalesced_job(dom_derived_queue *queue,
                                             dom_derived_job_kind kind,
                                             const unsigned char *src,
                                             u32 size) {
    size_t i;
    if (!queue) {
        return 0u;
    }
    for (i = 0u; i < queue->jobs.size(); ++i) {
        const dom_derived_job &job = queue->jobs[i];
        if (job.kind != kind) {
            continue;
        }
        if (job.state != DOM_DERIVED_JOB_PENDING &&
            job.state != DOM_DERIVED_JOB_RUNNING) {
            continue;
        }
        if (payload_matches(job, src, size)) {
            return job.id;
        }
    }
    return 0u;
}

static void fill_status(const dom_derived_job &job, dom_derived_job_status *out_status) {
    if (!out_status) {
        return;
    }
    out_status->struct_size = sizeof(*out_status);
    out_status->struct_version = DOM_DERIVED_STATUS_VERSION;
    out_status->kind = (u32)job.kind;
    out_status->state = job.state;
    out_status->last_error = job.last_error;
    out_status->io_bytes = job.hint_io_bytes;
    out_status->work_ms = job.hint_work_ms;
}

static void execute_job(dom_derived_queue *queue, dom_derived_job &job) {
    const bool allow_io = (queue && (queue->flags & DOM_DERIVED_QUEUE_FLAG_ALLOW_IO) != 0u);
    job.state = DOM_DERIVED_JOB_RUNNING;
    job.last_error = DOM_DERIVED_ERR_NONE;
    job.start_us = dsys_time_now_us();

    switch (job.kind) {
    case DERIVED_DECOMPRESS:
    case DERIVED_BUILD_MESH:
    case DERIVED_BUILD_MAP_TILE:
        job.state = DOM_DERIVED_JOB_DONE;
        job.last_error = DOM_DERIVED_ERR_NONE;
        break;
    case DERIVED_IO_READ_FILE:
    case DERIVED_IO_READ_CONTAINER_CHUNK:
        if (!allow_io) {
            job.state = DOM_DERIVED_JOB_FAILED;
            job.last_error = DOM_DERIVED_ERR_IO_DISABLED;
        } else {
            job.state = DOM_DERIVED_JOB_FAILED;
            job.last_error = DOM_DERIVED_ERR_UNSUPPORTED;
        }
        break;
    default:
        job.state = DOM_DERIVED_JOB_FAILED;
        job.last_error = DOM_DERIVED_ERR_UNSUPPORTED;
        break;
    }

    job.end_us = dsys_time_now_us();
}

} // namespace

extern "C" {

dom_derived_queue *dom_derived_queue_create(const dom_derived_queue_desc *desc) {
    dom_derived_queue *queue;
    u32 max_jobs;
    u32 max_payload;
    u32 flags;

    if (!desc || desc->struct_size != sizeof(dom_derived_queue_desc) ||
        desc->struct_version != DOM_DERIVED_QUEUE_DESC_VERSION) {
        return (dom_derived_queue *)0;
    }

    max_jobs = desc->max_jobs ? desc->max_jobs : DEFAULT_MAX_JOBS;
    max_payload = desc->max_payload_bytes ? desc->max_payload_bytes : DEFAULT_MAX_PAYLOAD_BYTES;
    flags = desc->flags;

    queue = new dom_derived_queue();
    queue->next_id = 1u;
    queue->submit_seq = 1u;
    queue->max_jobs = max_jobs;
    queue->max_payload_bytes = max_payload;
    queue->flags = flags;
    queue->jobs.clear();
    std::memset(&queue->stats, 0, sizeof(queue->stats));
    queue->stats.struct_size = sizeof(queue->stats);
    queue->stats.struct_version = DOM_DERIVED_STATS_VERSION;
    return queue;
}

void dom_derived_queue_destroy(dom_derived_queue *queue) {
    if (!queue) {
        return;
    }
    delete queue;
}

dom_derived_job_id dom_derived_submit(dom_derived_queue *queue,
                                      dom_derived_job_kind kind,
                                      const dom_derived_job_payload *payload,
                                      int priority) {
    dom_derived_job job;
    size_t slot;
    u32 hint_ms = 0u;
    u32 hint_io = 0u;
    const unsigned char *src = (const unsigned char *)0;
    u32 size = 0u;

    if (!queue) {
        return 0u;
    }
    if (payload && payload->data && payload->size > 0u) {
        src = (const unsigned char *)payload->data;
        size = payload->size;
    }
    if (size > queue->max_payload_bytes) {
        return 0u;
    }

    if (kind == DERIVED_BUILD_MAP_TILE || kind == DERIVED_BUILD_MESH) {
        dom_derived_job_id existing = find_coalesced_job(queue, kind, src, size);
        if (existing != 0u) {
            return existing;
        }
    }

    if (queue->jobs.size() >= queue->max_jobs) {
        slot = find_reuse_slot(queue);
        if (slot == (size_t)-1) {
            return 0u;
        }
    } else {
        slot = queue->jobs.size();
    }

    extract_budget_hint(payload, &hint_ms, &hint_io);

    job.id = queue->next_id++;
    job.submit_seq = queue->submit_seq++;
    job.submit_us = dsys_time_now_us();
    job.start_us = 0u;
    job.end_us = 0u;
    job.kind = kind;
    job.priority = priority;
    job.state = DOM_DERIVED_JOB_PENDING;
    job.last_error = DOM_DERIVED_ERR_NONE;
    job.hint_work_ms = hint_ms;
    job.hint_io_bytes = hint_io;
    job.payload.clear();
    if (src && size > 0u) {
        job.payload.assign(src, src + size);
    }

    if (slot == queue->jobs.size()) {
        queue->jobs.push_back(job);
    } else {
        queue->jobs[slot] = job;
    }

    return job.id;
}

int dom_derived_pump(dom_derived_queue *queue,
                     u32 max_ms,
                     u64 max_io_bytes,
                     u32 max_jobs) {
    const u64 start_us = dsys_time_now_us();
    const u64 max_us = max_ms ? ((u64)max_ms * 1000ull) : ~0ull;
    const u64 io_budget = max_io_bytes ? max_io_bytes : ~0ull;
    const u32 job_budget = max_jobs ? max_jobs : 0xffffffffu;
    const bool allow_io = (queue && (queue->flags & DOM_DERIVED_QUEUE_FLAG_ALLOW_IO) != 0u);
    u64 io_used = 0u;
    u32 processed = 0u;

    if (!queue) {
        return 0;
    }

    DOM_PROFILE_SCOPE(DOM_PROFILER_ZONE_DERIVED_PUMP);
    while (processed < job_budget) {
        const u64 now_us = dsys_time_now_us();
        size_t idx;
        if ((now_us - start_us) >= max_us) {
            break;
        }
        idx = find_next_job(queue, io_budget - io_used, allow_io);
        if (idx == (size_t)-1) {
            break;
        }
        dom_derived_job &job = queue->jobs[idx];
        execute_job(queue, job);
        io_used += job.hint_io_bytes;
        processed += 1u;
    }

    queue->stats.last_pump_jobs = processed;
    queue->stats.last_pump_io_bytes = (u32)((io_used > 0xffffffffull) ? 0xffffffffull : io_used);
    queue->stats.last_pump_ms = (u32)((dsys_time_now_us() - start_us) / 1000ull);
    return (int)processed;
}

int dom_derived_poll(dom_derived_queue *queue,
                     dom_derived_job_id job_id,
                     dom_derived_job_status *out_status) {
    size_t i;
    if (!queue || !out_status || job_id == 0u) {
        return -1;
    }
    for (i = 0u; i < queue->jobs.size(); ++i) {
        if (queue->jobs[i].id == job_id) {
            fill_status(queue->jobs[i], out_status);
            return 0;
        }
    }
    return -1;
}

int dom_derived_cancel(dom_derived_queue *queue,
                       dom_derived_job_id job_id) {
    size_t i;
    if (!queue || job_id == 0u) {
        return -1;
    }
    for (i = 0u; i < queue->jobs.size(); ++i) {
        if (queue->jobs[i].id == job_id) {
            if (queue->jobs[i].state == DOM_DERIVED_JOB_PENDING ||
                queue->jobs[i].state == DOM_DERIVED_JOB_RUNNING) {
                queue->jobs[i].state = DOM_DERIVED_JOB_CANCELED;
                queue->jobs[i].last_error = DOM_DERIVED_ERR_NONE;
            }
            return 0;
        }
    }
    return -1;
}

int dom_derived_get_stats(dom_derived_queue *queue,
                          dom_derived_stats *out_stats) {
    if (!queue || !out_stats) {
        return -1;
    }
    out_stats->struct_size = sizeof(*out_stats);
    out_stats->struct_version = DOM_DERIVED_STATS_VERSION;
    out_stats->last_pump_jobs = queue->stats.last_pump_jobs;
    out_stats->last_pump_ms = queue->stats.last_pump_ms;
    out_stats->last_pump_io_bytes = queue->stats.last_pump_io_bytes;
    update_stats(queue, out_stats);
    return 0;
}

} /* extern "C" */
