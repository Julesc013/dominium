/*
FILE: source/domino/policy/d_policy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / policy/d_policy
RESPONSIBILITY: Defines internal contract for `d_policy`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Policy and constraint evaluation (C89).
 * Policies are data-driven rules that can allow/forbid actions and apply multipliers/caps.
 */
#ifndef D_POLICY_H
#define D_POLICY_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "content/d_content.h"
#include "core/d_org.h"

#ifdef __cplusplus
extern "C" {
#endif

int d_policy_system_init(void);
void d_policy_system_shutdown(void);

enum {
    D_POLICY_SUBJECT_NONE          = 0u,
    D_POLICY_SUBJECT_PROCESS       = 1u,
    D_POLICY_SUBJECT_JOB_TEMPLATE  = 2u,
    D_POLICY_SUBJECT_STRUCTURE     = 3u,
    D_POLICY_SUBJECT_SPLINE_PROFILE = 4u
};

typedef struct d_policy_context_s {
    d_org_id      org_id;
    u32           subject_kind;   /* D_POLICY_SUBJECT_* */
    u32           subject_id;     /* id of process/job/struct proto */
    d_content_tag subject_tags;

    /* Optional generic environment values. */
    q16_16        env_values[8];
} d_policy_context;

typedef struct d_policy_effect_result_s {
    q16_16 multiplier; /* throughput/rate multiplier */
    q16_16 cap;        /* optional cap (interpretation is data-driven) */
    u8     allowed;    /* 0=forbidden,1=allowed */
} d_policy_effect_result;

int d_policy_evaluate(
    const d_policy_context    *ctx,
    d_policy_effect_result    *out
);

struct d_world;

/* Subsystem registration hook (called once at startup). */
void d_policy_register_subsystem(void);

/* World-state validator hook. */
int d_policy_validate(const struct d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_POLICY_H */
