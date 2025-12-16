/*
FILE: source/dominium/game/rules/content_materials.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/rules/content_materials
RESPONSIBILITY: Implements `content_materials`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/content_materials.h"

dom_status dom_materials_register(const dom_material_desc* desc,
                                  dom_material_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

const dom_material_desc* dom_materials_get(dom_material_id id)
{
    (void)id;
    return (const dom_material_desc*)0;
}

uint32_t dom_materials_count(void)
{
    return 0;
}

dom_status dom_materials_visit(dom_material_visit_fn fn, void* user)
{
    (void)fn;
    (void)user;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_materials_reset(void)
{
}
