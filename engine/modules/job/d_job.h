/*
FILE: source/domino/job/d_job.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / job/d_job
RESPONSIBILITY: Defines internal contract for `d_job`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Job subsystem public interface (C89). */
#ifndef D_JOB_H
#define D_JOB_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "content/d_content.h"
#include "trans/d_trans_spline.h"
#include "job/d_job_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum d_job_state_e {
    D_JOB_STATE_PENDING = 0,
    D_JOB_STATE_ASSIGNED,
    D_JOB_STATE_RUNNING,
    D_JOB_STATE_COMPLETED,
    D_JOB_STATE_CANCELLED
} d_job_state;

enum {
    D_JOB_PURPOSE_OPERATE_PROCESS = 1u,
    D_JOB_PURPOSE_HAUL_ITEMS      = 2u,
    D_JOB_PURPOSE_BUILD_STRUCTURE = 3u
};

typedef struct d_job_record_s {
    d_job_id          id;
    d_job_template_id template_id;
    d_job_state       state;

    d_agent_id        assigned_agent;

    /* Target references: structure, spline, position. */
    u32               target_struct_eid;
    d_spline_id       target_spline_id;
    q32_32            target_x;
    q32_32            target_y;
    q32_32            target_z;

    /* Progress tracking: generic. */
    q16_16            progress;
} d_job_record;

int d_job_system_init(d_world *w);
void d_job_system_shutdown(d_world *w);

d_job_id d_job_create(d_world *w, const d_job_record *init);
int      d_job_cancel(d_world *w, d_job_id id);

int d_job_get(const d_world *w, d_job_id id, d_job_record *out);
int d_job_update(d_world *w, const d_job_record *jr);

u32 d_job_count(const d_world *w);
int d_job_get_by_index(const d_world *w, u32 index, d_job_record *out);

void d_job_tick(d_world *w, u32 ticks);

/* Subsystem registration hook */
void d_job_init(void);
int d_job_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_JOB_H */
