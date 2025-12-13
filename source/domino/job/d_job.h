/* Job/AI subsystem types (C89). */
#ifndef D_JOB_H
#define D_JOB_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"
#include "job/d_job_proto.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_job_instance_id;

typedef struct d_job_instance {
    d_job_instance_id  id;
    d_job_template_id  template_id;

    u32                flags;     /* PENDING, ASSIGNED, RUNNING, COMPLETED, FAILED */

    /* Subject(s) of the job: structure, vehicle, resource, etc. */
    u32                subject_entity_id;
    u32                target_entity_id;

    q16_16             target_x, target_y, target_z;

    d_tlv_blob         params;    /* additional parameters; template-specific */
} d_job_instance;

/* Generic flag bits (engine-level only). */
#define D_JOB_FLAG_ENV_UNSUITABLE (1u << 16) /* environment constraints not met */

/* Create a new job instance using a template. */
d_job_instance_id d_job_create(
    d_world           *w,
    d_job_template_id  template_id,
    q16_16            x, q16_16 y, q16_16 z
);

int d_job_destroy(
    d_world          *w,
    d_job_instance_id id
);

/* Subsystem registration hook */
void d_job_init(void);
int d_job_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_JOB_H */
