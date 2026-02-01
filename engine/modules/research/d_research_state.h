/*
FILE: source/domino/research/d_research_state.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / research/d_research_state
RESPONSIBILITY: Defines internal contract for `d_research_state`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Research/tech progression state (C89).
 * Generic and deterministic: concrete semantics live in content and product code.
 */
#ifndef D_RESEARCH_STATE_H
#define D_RESEARCH_STATE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "content/d_content.h"
#include "core/d_org.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_research_progress_s {
    d_research_id id;
    q32_32        progress;  /* accumulated points */
    u8            state;     /* 0=PENDING,1=ACTIVE,2=COMPLETED,3=LOCKED */
} d_research_progress;

typedef struct d_research_org_state_s {
    d_org_id             org_id;
    u16                  research_count;
    d_research_progress *researches;
} d_research_org_state;

enum {
    D_RESEARCH_STATE_PENDING   = 0u,
    D_RESEARCH_STATE_ACTIVE    = 1u,
    D_RESEARCH_STATE_COMPLETED = 2u,
    D_RESEARCH_STATE_LOCKED    = 3u
};

int d_research_system_init(void);
void d_research_system_shutdown(void);

int d_research_org_init(d_org_id org_id);
int d_research_org_shutdown(d_org_id org_id);

int d_research_tick(d_org_id org_id, u32 ticks);

/* Query/modify state */
int d_research_get_org_state(d_org_id org_id, d_research_org_state *out);
int d_research_set_active(d_org_id org_id, d_research_id id);
int d_research_add_progress(
    d_org_id       org_id,
    d_research_id  id,
    q32_32         amount
);

int d_research_is_unlocked(d_org_id org_id, d_research_id id);
int d_research_is_completed(d_org_id org_id, d_research_id id);

/* Apply point yields from deterministic simulation events. */
void d_research_apply_process_completion(d_org_id org_id, d_process_id process_id);
void d_research_apply_job_completion(d_org_id org_id, d_job_template_id template_id);

struct d_world;

/* Subsystem registration hook (called once at startup). */
void d_research_register_subsystem(void);

/* World-state validator hook. */
int d_research_validate(const struct d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_RESEARCH_STATE_H */
