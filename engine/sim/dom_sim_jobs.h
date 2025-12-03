#ifndef DOM_SIM_JOBS_H
#define DOM_SIM_JOBS_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"

#define DOM_SIM_JOB_QUEUE_SIZE 256

typedef dom_u32 DomJobType;

typedef struct DomSimJob {
    DomJobType job_type;
    dom_u32    priority;
    dom_entity_id requester;
    dom_entity_id assignee;
    dom_entity_id target;
    dom_u64    tick_created;
    dom_u32    est_ticks;
    dom_u32    payload[8];
} DomSimJob;

dom_err_t dom_sim_jobs_init(void);
dom_err_t dom_sim_jobs_emit(const DomSimJob *job);
dom_err_t dom_sim_jobs_pop(DomSimJob *out_job);

#endif /* DOM_SIM_JOBS_H */
