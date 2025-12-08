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
