#ifndef DOM_SIM_JOBS_H
#define DOM_SIM_JOBS_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"
#include "dom_sim_tick.h"

#define DOM_SIM_JOB_QUEUE_SIZE 256

typedef dom_u32 DomJobType;

typedef struct DomSimJob {
    DomJobType   job_type;
    dom_u32      priority;        /* lower is higher priority */
    dom_entity_id requester;
    dom_entity_id assignee;
    dom_entity_id target;
    DomTickId    tick_created;
    dom_u32      est_ticks;
    dom_u32      payload[8];
} DomSimJob;

dom_err_t dom_sim_jobs_init(void);
void      dom_sim_jobs_reset(void);

dom_err_t dom_sim_jobs_emit_local(dom_entity_id entity, const DomSimJob *job);
dom_err_t dom_sim_jobs_assign_to_worker(dom_entity_id worker_entity, DomSimJob *out_job);

void dom_sim_jobs_phase_simulation(void);
void dom_sim_jobs_phase_post(void);
void dom_sim_jobs_complete(const DomSimJob *job, dom_bool8 success);

#endif /* DOM_SIM_JOBS_H */
