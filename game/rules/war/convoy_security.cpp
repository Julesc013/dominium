/*
FILE: game/rules/war/convoy_security.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic convoy security summaries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Convoy security estimates are deterministic.
*/
#include "dominium/rules/war/convoy_security.h"

#include <string.h>

static u32 convoy_security_bucket_u32(u32 value, u32 bucket)
{
    if (bucket == 0u) {
        return value;
    }
    return (value / bucket) * bucket;
}

int convoy_security_from_force(const security_force_registry* forces,
                               const military_cohort_registry* military,
                               const readiness_registry* readiness,
                               const morale_registry* morale,
                               u64 force_id,
                               convoy_security* out)
{
    const security_force* force;
    const military_cohort* cohort;
    const readiness_state* ready;
    const morale_state* mor;
    u32 eq_total = 0u;
    u32 i;
    u64 strength;
    if (!forces || !military || !readiness || !morale || !out) {
        return -1;
    }
    force = security_force_find((security_force_registry*)forces, force_id);
    if (!force) {
        return -2;
    }
    cohort = military_cohort_find((military_cohort_registry*)military, force->cohort_ref);
    ready = readiness_find((readiness_registry*)readiness, force->readiness_state_ref);
    mor = morale_find((morale_registry*)morale, force->morale_state_ref);
    if (!cohort || !ready || !mor) {
        return -3;
    }
    for (i = 0u; i < force->equipment_count; ++i) {
        eq_total += force->equipment_qtys[i];
    }
    strength = (u64)cohort->count * 1000u;
    strength += (u64)eq_total * 500u;
    strength = (strength * (u64)ready->readiness_level) / READINESS_SCALE;
    strength = (strength * (u64)mor->morale_level) / MORALE_SCALE;
    memset(out, 0, sizeof(*out));
    out->escort_force_ref = force_id;
    out->escort_strength = (strength > 0xFFFFFFFFu) ? 0xFFFFFFFFu : (u32)strength;
    out->readiness_level = ready->readiness_level;
    out->morale_level = mor->morale_level;
    return 0;
}

int convoy_security_estimate_from_view(const dom_epistemic_view* view,
                                       const convoy_security* actual,
                                       convoy_security_estimate* out)
{
    int is_known = 0;
    if (!actual || !out) {
        return -1;
    }
    if (view && view->state == DOM_EPI_KNOWN && !view->is_uncertain) {
        is_known = 1;
    }
    if (is_known) {
        out->escort_strength = actual->escort_strength;
        out->readiness_level = actual->readiness_level;
        out->morale_level = actual->morale_level;
        out->uncertainty_q16 = view ? view->uncertainty_q16 : 0u;
        out->is_exact = 1;
        return 0;
    }
    out->escort_strength = convoy_security_bucket_u32(actual->escort_strength, 100u);
    out->readiness_level = convoy_security_bucket_u32(actual->readiness_level, 50u);
    out->morale_level = convoy_security_bucket_u32(actual->morale_level, 50u);
    out->uncertainty_q16 = view ? view->uncertainty_q16 : 0xFFFFu;
    out->is_exact = 0;
    return 0;
}
