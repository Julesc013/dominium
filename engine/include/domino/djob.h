/*
FILE: include/domino/djob.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / djob
RESPONSIBILITY: Defines the public contract for `djob` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DJOB_H
#define DOMINO_DJOB_H

#include "dnumeric.h"
#include "dworld.h"
#include "dmatter.h"
#include "dactor.h"

#ifdef __cplusplus
extern "C" {
#endif

/* JobId: Identifier type for Job objects in `djob`. */
typedef uint32_t JobId;

/* JobKind: Enumeration/classifier for Job in `djob`. */
typedef enum {
    JOB_BUILD = 0,
    JOB_DECONSTRUCT,
    JOB_TRANSPORT,
    JOB_OPERATE_MACHINE,
    JOB_REPAIR,
    JOB_RESEARCH,
    JOB_CUSTOM,
} JobKind;

/* JobState: Public type used by `djob`. */
typedef enum {
    JOB_PENDING = 0,
    JOB_ASSIGNED,
    JOB_IN_PROGRESS,
    JOB_COMPLETE,
    JOB_CANCELLED,
    JOB_FAILED,
} JobState;

/* Job: Public type used by `djob`. */
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

/* Purpose: Create djob.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
JobId  djob_create(const Job *def);
/* Purpose: Get djob.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
Job   *djob_get(JobId id);

/* Purpose: Cancel djob.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void   djob_cancel(JobId id);
/* Purpose: Mark complete.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void   djob_mark_complete(JobId id);

/* Purpose: Tick djob.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void   djob_tick(SimTick t);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DJOB_H */
