/*
FILE: source/domino/core/view.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/view
RESPONSIBILITY: Implements `view`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "core_internal.h"

uint32_t dom_ui_list_views(dom_core* core, dom_view_desc* out, uint32_t max_out)
{
    uint32_t i;
    uint32_t count;

    if (!core) {
        return 0;
    }

    count = core->view_count;
    if (!out || max_out == 0u) {
        return count;
    }
    if (count > max_out) {
        count = max_out;
    }

    for (i = 0; i < count; ++i) {
        out[i] = core->views[i];
    }

    return count;
}

bool dom_view_register(dom_core* core, const dom_view_desc* desc)
{
    dom_view_desc* dst;

    if (!core || !desc || !desc->id || !desc->model_id) {
        return false;
    }
    if (core->view_count >= DOM_MAX_VIEWS) {
        return false;
    }
    dst = &core->views[core->view_count];
    *dst = *desc;
    core->view_count += 1u;
    return true;
}
