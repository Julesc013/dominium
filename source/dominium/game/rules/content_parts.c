/*
FILE: source/dominium/game/rules/content_parts.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/rules/content_parts
RESPONSIBILITY: Implements `content_parts`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/content_parts.h"

dom_status dom_parts_register(const dom_part_desc* desc, dom_part_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

const dom_part_desc* dom_parts_get(dom_part_id id)
{
    (void)id;
    return (const dom_part_desc*)0;
}

uint32_t dom_parts_count(void)
{
    return 0;
}

dom_status dom_parts_visit(dom_part_visit_fn fn, void* user)
{
    (void)fn;
    (void)user;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_parts_reset(void)
{
}
