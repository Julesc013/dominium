/*
FILE: source/domino/job/d_job_planner.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / job/d_job_planner
RESPONSIBILITY: Defines internal contract for `d_job_planner`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

