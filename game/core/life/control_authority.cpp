/*
FILE: game/core/life/control_authority.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements deterministic control authority evaluation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resolution order is fixed and deterministic.
*/
#include "dominium/life/control_authority.h"

static u32 life_authority_precedence(life_authority_source source)
{
    switch (source) {
        case LIFE_AUTH_CONTRACT: return 0u;
        case LIFE_AUTH_ORG: return 1u;
        case LIFE_AUTH_JURISDICTION: return 2u;
        case LIFE_AUTH_GUARDIAN: return 3u;
        case LIFE_AUTH_PERSONAL: return 3u;
        default: return 4u;
    }
}

int life_authority_can_control(const life_authority_set* set,
                               u64 controller_id,
                               u64 target_person_id,
                               life_authority_source* out_source)
{
    u32 i;
    u32 best_prec = 0xFFFFFFFFu;
    life_authority_source best_source = LIFE_AUTH_PERSONAL;
    int found = 0;

    if (!set || !set->records || set->count == 0u) {
        return 0;
    }

    for (i = 0u; i < set->count; ++i) {
        const life_authority_record* rec = &set->records[i];
        u32 prec;
        if (rec->controller_id != controller_id || rec->target_person_id != target_person_id) {
            continue;
        }
        prec = life_authority_precedence((life_authority_source)rec->source);
        if (!found || prec < best_prec) {
            best_prec = prec;
            best_source = (life_authority_source)rec->source;
            found = 1;
        }
    }

    if (found && out_source) {
        *out_source = best_source;
    }
    return found;
}
