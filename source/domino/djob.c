#include "domino/djob.h"

#include <string.h>

#define DJOB_MAX 1024

static Job   g_jobs[DJOB_MAX];
static bool  g_job_used[DJOB_MAX];
static Q16_16 g_job_progress[DJOB_MAX];
static JobId g_job_count = 0;

JobId djob_create(const Job *def)
{
    U32 i;
    Job *j = 0;
    if (!def) return 0;
    for (i = 0; i < DJOB_MAX; ++i) {
        if (!g_job_used[i]) {
            g_job_used[i] = true;
            j = &g_jobs[i];
            g_job_count = (JobId)((i + 1 > g_job_count) ? (i + 1) : g_job_count);
            break;
        }
    }
    if (!j) return 0;
    memset(j, 0, sizeof(*j));
    *j = *def;
    j->id = (JobId)(i + 1);
    if (j->state == 0) j->state = JOB_PENDING;
    g_job_progress[i] = 0;
    return j->id;
}

Job *djob_get(JobId id)
{
    if (id == 0 || id > g_job_count) return 0;
    if (!g_job_used[id - 1]) return 0;
    return &g_jobs[id - 1];
}

void djob_cancel(JobId id)
{
    Job *j = djob_get(id);
    if (!j) return;
    j->state = JOB_CANCELLED;
}

void djob_mark_complete(JobId id)
{
    Job *j = djob_get(id);
    if (!j) return;
    j->state = JOB_COMPLETE;
}

static bool djob_deps_satisfied(const Job *j)
{
    U8 i;
    if (!j) return false;
    for (i = 0; i < j->dep_count; ++i) {
        Job *dep = djob_get(j->deps[i]);
        if (!dep || dep->state != JOB_COMPLETE) {
            return false;
        }
    }
    return true;
}

void djob_tick(SimTick t)
{
    U32 i;
    Q16_16 dt = g_domino_dt_s;
    (void)t;
    for (i = 0; i < g_job_count; ++i) {
        Job *j = djob_get((JobId)(i + 1));
        if (!j) continue;
        if (j->state == JOB_CANCELLED || j->state == JOB_COMPLETE || j->state == JOB_FAILED) continue;
        if (j->state == JOB_PENDING) {
            if (djob_deps_satisfied(j)) {
                j->state = JOB_PENDING; /* remains pending until assigned */
            }
            continue;
        }
        if (j->state == JOB_IN_PROGRESS) {
            Q16_16 progress = g_job_progress[i];
            progress += dt;
            g_job_progress[i] = progress;
            if (progress >= j->work_time_s) {
                j->state = JOB_COMPLETE;
            }
        }
    }
}
