/*
FILE: source/dominium/game/rules/content_prefabs.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/rules/content_prefabs
RESPONSIBILITY: Implements `content_prefabs`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/content_prefabs.h"

dom_status dom_prefabs_register(const dom_prefab_desc* desc,
                                dom_prefab_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

const dom_prefab_desc* dom_prefabs_get(dom_prefab_id id)
{
    (void)id;
    return (const dom_prefab_desc*)0;
}

uint32_t dom_prefabs_count(void)
{
    return 0;
}

dom_status dom_prefabs_visit(dom_prefab_visit_fn fn, void* user)
{
    (void)fn;
    (void)user;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_prefabs_reset(void)
{
}
