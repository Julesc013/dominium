#include "dom_sim_jobs.h"
#include <string.h>

#define DOM_SIM_JOB_LOCAL_BUCKETS 64
#define DOM_SIM_JOB_LANE_CAPACITY 128
#define DOM_SIM_JOB_GLOBAL_CAPACITY 128

typedef struct DomSimJobQueue {
    DomSimJob *buffer;
    dom_u32    capacity;
    dom_u32    count;
} DomSimJobQueue;

static struct {
    DomSimJobQueue local[DOM_SIM_JOB_LOCAL_BUCKETS];
    DomSimJob      local_storage[DOM_SIM_JOB_LOCAL_BUCKETS][DOM_SIM_JOB_QUEUE_SIZE];

    DomSimJobQueue lane[DOM_SIM_MAX_LANES];
    DomSimJob      lane_storage[DOM_SIM_MAX_LANES][DOM_SIM_JOB_LANE_CAPACITY];

    DomSimJobQueue global;
    DomSimJob      global_storage[DOM_SIM_JOB_GLOBAL_CAPACITY];
} g_jobs;

static void dom_sim_job_queue_init(DomSimJobQueue *q, DomSimJob *storage, dom_u32 capacity)
{
    if (!q) return;
    q->buffer = storage;
    q->capacity = capacity;
    q->count = 0;
}

static void dom_sim_job_queue_clear(DomSimJobQueue *q)
{
    if (!q) return;
    q->count = 0;
}

static dom_bool8 dom_sim_job_precedes(const DomSimJob *a, const DomSimJob *b, dom_entity_id worker)
{
    if (a->priority != b->priority) return a->priority < b->priority;
    if (a->job_type != b->job_type) return a->job_type < b->job_type;
    if (a->requester != b->requester) return a->requester < b->requester;
    if (a->tick_created != b->tick_created) return a->tick_created < b->tick_created;
    if (worker != 0 && b->assignee != worker && a->assignee == worker) return 1;
    if (worker != 0 && a->assignee != worker && b->assignee == worker) return 0;
    return a->assignee < b->assignee;
}

static dom_err_t dom_sim_job_queue_push(DomSimJobQueue *q, const DomSimJob *job)
{
    dom_u32 pos;
    dom_u32 i;
    if (!q || !job) return DOM_ERR_INVALID_ARG;
    pos = q->count;
    for (i = 0; i < q->count; ++i) {
        if (dom_sim_job_precedes(job, &q->buffer[i], 0)) {
            pos = i;
            break;
        }
    }
    if (pos < q->count) {
        if (q->count < q->capacity) {
            memmove(&q->buffer[pos + 1], &q->buffer[pos], (q->count - pos) * sizeof(DomSimJob));
            q->buffer[pos] = *job;
            q->count += 1;
            return DOM_OK;
        } else {
            /* queue full: insert and drop last deterministically */
            memmove(&q->buffer[pos + 1], &q->buffer[pos], (q->count - pos - 1) * sizeof(DomSimJob));
            q->buffer[pos] = *job;
            return DOM_ERR_OVERFLOW;
        }
    }
    if (q->count < q->capacity) {
        q->buffer[q->count] = *job;
        q->count += 1;
        return DOM_OK;
    }
    return DOM_ERR_OVERFLOW;
}

static dom_bool8 dom_sim_job_queue_pop(DomSimJobQueue *q, DomSimJob *out_job)
{
    dom_u32 i;
    if (!q || !out_job) return 0;
    if (q->count == 0) return 0;
    *out_job = q->buffer[0];
    if (q->count > 1) {
        memmove(&q->buffer[0], &q->buffer[1], (q->count - 1) * sizeof(DomSimJob));
    }
    q->count -= 1;
    /* clear trailing slot deterministically */
    for (i = q->count; i < q->count + 1 && i < q->capacity; ++i) {
        memset(&q->buffer[i], 0, sizeof(DomSimJob));
    }
    return 1;
}

static dom_u32 dom_sim_jobs_local_bucket(dom_entity_id entity)
{
    dom_u32 idx = dom_entity_index(entity);
    return idx % DOM_SIM_JOB_LOCAL_BUCKETS;
}

static dom_u32 dom_sim_jobs_lane_limit(void)
{
    dom_u32 lanes = dom_sim_tick_lane_count();
    if (lanes == 0) lanes = 1;
    if (lanes > DOM_SIM_MAX_LANES) lanes = DOM_SIM_MAX_LANES;
    return lanes;
}

dom_err_t dom_sim_jobs_init(void)
{
    dom_u32 i;
    dom_u32 lanes = dom_sim_jobs_lane_limit();
    for (i = 0; i < DOM_SIM_JOB_LOCAL_BUCKETS; ++i) {
        dom_sim_job_queue_init(&g_jobs.local[i], g_jobs.local_storage[i], DOM_SIM_JOB_QUEUE_SIZE);
    }
    for (i = 0; i < DOM_SIM_MAX_LANES; ++i) {
        dom_sim_job_queue_init(&g_jobs.lane[i], g_jobs.lane_storage[i], DOM_SIM_JOB_LANE_CAPACITY);
    }
    dom_sim_job_queue_init(&g_jobs.global, g_jobs.global_storage, DOM_SIM_JOB_GLOBAL_CAPACITY);
    (void)lanes;
    return DOM_OK;
}

void dom_sim_jobs_reset(void)
{
    dom_u32 i;
    for (i = 0; i < DOM_SIM_JOB_LOCAL_BUCKETS; ++i) {
        dom_sim_job_queue_clear(&g_jobs.local[i]);
    }
    for (i = 0; i < DOM_SIM_MAX_LANES; ++i) {
        dom_sim_job_queue_clear(&g_jobs.lane[i]);
    }
    dom_sim_job_queue_clear(&g_jobs.global);
}

dom_err_t dom_sim_jobs_emit_local(dom_entity_id entity, const DomSimJob *job)
{
    dom_u32 bucket;
    dom_err_t err;
    DomSimJob copy;
    if (!job) return DOM_ERR_INVALID_ARG;
    copy = *job;
    copy.requester = entity;
    bucket = dom_sim_jobs_local_bucket(entity);
    err = dom_sim_job_queue_push(&g_jobs.local[bucket], &copy);
    return err;
}

static dom_err_t dom_sim_jobs_promote_local(void)
{
    dom_u32 bucket;
    dom_u32 lanes = dom_sim_jobs_lane_limit();
    for (bucket = 0; bucket < DOM_SIM_JOB_LOCAL_BUCKETS; ++bucket) {
        while (g_jobs.local[bucket].count > 0) {
            DomSimJob job;
            dom_sim_job_queue_pop(&g_jobs.local[bucket], &job);
            {
                DomLaneId lane = dom_sim_tick_lane_for_entity(job.requester);
                if (lane >= lanes) lane = (DomLaneId)(lane % lanes);
                dom_sim_job_queue_push(&g_jobs.lane[lane], &job);
            }
        }
    }
    return DOM_OK;
}

void dom_sim_jobs_phase_simulation(void)
{
    dom_sim_jobs_promote_local();
}

void dom_sim_jobs_phase_post(void)
{
    /* Placeholder: future cleanup or completion sweep can be placed here. */
}

dom_err_t dom_sim_jobs_assign_to_worker(dom_entity_id worker_entity, DomSimJob *out_job)
{
    DomLaneId lane;
    DomSimJob lane_job;
    DomSimJob global_job;
    dom_bool8 has_lane;
    dom_bool8 has_global;
    if (!out_job) return DOM_ERR_INVALID_ARG;
    lane = dom_sim_tick_lane_for_entity(worker_entity);
    has_lane = dom_sim_job_queue_pop(&g_jobs.lane[lane], &lane_job);
    has_global = dom_sim_job_queue_pop(&g_jobs.global, &global_job);
    if (!has_lane && !has_global) return DOM_ERR_NOT_FOUND;
    if (has_lane && has_global) {
        if (dom_sim_job_precedes(&lane_job, &global_job, worker_entity)) {
            *out_job = lane_job;
            dom_sim_job_queue_push(&g_jobs.global, &global_job);
        } else {
            *out_job = global_job;
            dom_sim_job_queue_push(&g_jobs.lane[lane], &lane_job);
        }
    } else if (has_lane) {
        *out_job = lane_job;
    } else {
        *out_job = global_job;
    }
    out_job->assignee = worker_entity;
    return DOM_OK;
}

void dom_sim_jobs_complete(const DomSimJob *job, dom_bool8 success)
{
    (void)job;
    (void)success;
}
