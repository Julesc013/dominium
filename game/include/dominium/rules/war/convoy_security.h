/*
FILE: include/dominium/rules/war/convoy_security.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic convoy security summaries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Convoy security estimates are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_CONVOY_SECURITY_H
#define DOMINIUM_RULES_WAR_CONVOY_SECURITY_H

#include "domino/core/types.h"
#include "dominium/epistemic.h"
#include "dominium/rules/war/military_cohort.h"
#include "dominium/rules/war/morale_state.h"
#include "dominium/rules/war/readiness_state.h"
#include "dominium/rules/war/security_force.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct convoy_security {
    u64 convoy_id;
    u64 escort_force_ref;
    u32 escort_strength;
    u32 readiness_level;
    u32 morale_level;
} convoy_security;

typedef struct convoy_security_estimate {
    u32 escort_strength;
    u32 readiness_level;
    u32 morale_level;
    u32 uncertainty_q16;
    int is_exact;
} convoy_security_estimate;

int convoy_security_from_force(const security_force_registry* forces,
                               const military_cohort_registry* military,
                               const readiness_registry* readiness,
                               const morale_registry* morale,
                               u64 force_id,
                               convoy_security* out);

int convoy_security_estimate_from_view(const dom_epistemic_view* view,
                                       const convoy_security* actual,
                                       convoy_security_estimate* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_CONVOY_SECURITY_H */
