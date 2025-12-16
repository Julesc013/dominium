/*
FILE: source/domino/core/event.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/event
RESPONSIBILITY: Implements `event`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "core_internal.h"

void dom_event__publish(dom_core* core, const dom_event* ev)
{
    uint32_t i;

    if (!core || !ev) {
        return;
    }

    for (i = 0; i < core->event_sub_count; ++i) {
        if (core->event_subs[i].kind == ev->kind && core->event_subs[i].fn) {
            core->event_subs[i].fn(core, ev, core->event_subs[i].user);
        }
    }
}

bool dom_event_subscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user)
{
    if (!core || !fn) {
        return false;
    }

    if (core->event_sub_count >= DOM_MAX_EVENT_HANDLERS) {
        return false;
    }

    core->event_subs[core->event_sub_count].kind = kind;
    core->event_subs[core->event_sub_count].fn = fn;
    core->event_subs[core->event_sub_count].user = user;
    core->event_sub_count += 1;
    return true;
}

bool dom_event_unsubscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user)
{
    uint32_t i;

    if (!core || !fn) {
        return false;
    }

    for (i = 0; i < core->event_sub_count; ++i) {
        if (core->event_subs[i].fn == fn &&
            core->event_subs[i].kind == kind &&
            core->event_subs[i].user == user) {
            for (; i + 1 < core->event_sub_count; ++i) {
                core->event_subs[i] = core->event_subs[i + 1];
            }
            core->event_sub_count -= 1;
            return true;
        }
    }

    return false;
}
