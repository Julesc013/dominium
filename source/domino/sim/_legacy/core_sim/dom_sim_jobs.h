/*
FILE: source/domino/sim/_legacy/core_sim/dom_sim_jobs.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/dom_sim_jobs
RESPONSIBILITY: Implements `dom_sim_jobs`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
