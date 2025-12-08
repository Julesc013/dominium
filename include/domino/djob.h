#ifndef DOMINO_DJOB_H
#define DOMINO_DJOB_H

#include "dnumeric.h"
#include "dworld.h"
#include "dmatter.h"
#include "dactor.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t JobId;

typedef enum {
    JOB_BUILD = 0,
    JOB_DECONSTRUCT,
    JOB_TRANSPORT,
    JOB_OPERATE_MACHINE,
    JOB_REPAIR,
    JOB_RESEARCH,
    JOB_CUSTOM,
} JobKind;

typedef enum {
    JOB_PENDING = 0,
    JOB_ASSIGNED,
    JOB_IN_PROGRESS,
    JOB_COMPLETE,
    JOB_CANCELLED,
    JOB_FAILED,
} JobState;

typedef struct {
    JobId      id;
    JobKind    kind;
    JobState   state;

    WPosTile   target_tile;

    ItemTypeId required_item;
    U32        required_count;

    Q16_16     work_time_s;

    ActorId    assigned_actor;

    JobId      deps[4];
    U8         dep_count;
} Job;

JobId  djob_create(const Job *def);
Job   *djob_get(JobId id);

void   djob_cancel(JobId id);
void   djob_mark_complete(JobId id);

void   djob_tick(SimTick t);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DJOB_H */
