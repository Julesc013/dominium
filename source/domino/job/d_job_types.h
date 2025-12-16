/*
FILE: source/domino/job/d_job_types.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / job/d_job_types
RESPONSIBILITY: Implements `d_job_types`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Shared job/agent identifier typedefs (C89). */
#ifndef D_JOB_TYPES_H
#define D_JOB_TYPES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_job_id;
typedef u32 d_agent_id;

#ifdef __cplusplus
}
#endif

#endif /* D_JOB_TYPES_H */

