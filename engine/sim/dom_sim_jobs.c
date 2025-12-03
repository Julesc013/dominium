#include "dom_sim_jobs.h"
#include <string.h>

static DomSimJob g_jobs[DOM_SIM_JOB_QUEUE_SIZE];
static dom_u32 g_job_count = 0;

dom_err_t dom_sim_jobs_init(void)
{
    g_job_count = 0;
    memset(g_jobs, 0, sizeof(g_jobs));
    return DOM_OK;
}

dom_err_t dom_sim_jobs_emit(const DomSimJob *job)
{
    if (!job) return DOM_ERR_INVALID_ARG;
    if (g_job_count >= DOM_SIM_JOB_QUEUE_SIZE) return DOM_ERR_BOUNDS;
    g_jobs[g_job_count] = *job;
    g_job_count++;
    return DOM_OK;
}

dom_err_t dom_sim_jobs_pop(DomSimJob *out_job)
{
    dom_u32 i;
    if (!out_job) return DOM_ERR_INVALID_ARG;
    if (g_job_count == 0) return DOM_ERR_NOT_FOUND;

    /* Deterministic selection: lowest priority, then oldest index */
    {
        dom_u32 best = 0;
        dom_u32 best_prio = g_jobs[0].priority;
        for (i = 1; i < g_job_count; ++i) {
            if (g_jobs[i].priority < best_prio) {
                best_prio = g_jobs[i].priority;
                best = i;
            }
        }
        *out_job = g_jobs[best];
        for (i = best + 1; i < g_job_count; ++i) {
            g_jobs[i - 1] = g_jobs[i];
        }
        g_job_count--;
    }
    return DOM_OK;
}
