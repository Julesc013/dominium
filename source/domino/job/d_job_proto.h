/* Job template prototypes (C89). */
#ifndef D_JOB_PROTO_H
#define D_JOB_PROTO_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_job_template_id;

#define DJOB_MAX_PROFILES 8

typedef struct d_proto_job_template {
    d_job_template_id id;
    const char       *name;

    u32               purpose;            /* RESOURCE_EXTRACTION, OPERATE_MACHINE, LOGISTICS_MOVE, etc. */

    u32               required_profile_ids[DJOB_MAX_PROFILES]; /* e.g. extraction profiles, process profiles */
    u16               required_profile_count;

    u32               allowed_agents;     /* bitmask: HUMAN_WORKER, VEHICLE_MINER, BOT, etc. */

    u32               required_equipment_tags;

    d_tlv_blob        params;             /* priority, batch size, etc. */
} d_proto_job_template;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_JOB_PROTO_H */
