/* Deterministic job planner/assignment (C89). */
#ifndef D_JOB_PLANNER_H
#define D_JOB_PLANNER_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "content/d_content.h"
#include "trans/d_trans_spline.h"
#include "job/d_job_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Planner tick: assigns pending jobs to eligible agents. */
void d_job_planner_tick(d_world *w, u32 ticks);

/* Request a job instance (creates a pending job). */
int d_job_request(
    d_world           *w,
    d_job_template_id  tmpl_id,
    u32                target_struct_eid,
    d_spline_id        target_spline_id,
    q32_32             x,
    q32_32             y,
    q32_32             z,
    d_job_id          *out_job_id
);

#ifdef __cplusplus
}
#endif

#endif /* D_JOB_PLANNER_H */

