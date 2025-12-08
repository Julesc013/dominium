#include "core_internal.h"

static void dom_event_publish_internal(dom_core* core, const dom_event* evt)
{
    uint32_t i;

    if (!core || !evt) {
        return;
    }

    for (i = 0; i < core->sub_count; ++i) {
        if (core->subs[i].kind == evt->kind && core->subs[i].handler) {
            core->subs[i].handler(core, evt, core->subs[i].user);
        }
    }
}

bool dom_event_subscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user)
{
    if (!core || !fn) {
        return false;
    }

    /* Silence unused warning until we start publishing events. */
    if (0) {
        dom_event_publish_internal(core, NULL);
    }

    if (core->sub_count >= DOM_MAX_EVENT_SUBS) {
        return false;
    }

    core->subs[core->sub_count].kind = kind;
    core->subs[core->sub_count].handler = fn;
    core->subs[core->sub_count].user = user;
    core->sub_count += 1;
    return true;
}

bool dom_event_unsubscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user)
{
    uint32_t i;

    if (!core || !fn) {
        return false;
    }

    for (i = 0; i < core->sub_count; ++i) {
        if (core->subs[i].handler == fn &&
            core->subs[i].kind == kind &&
            core->subs[i].user == user) {
            for (; i + 1 < core->sub_count; ++i) {
                core->subs[i] = core->subs[i + 1];
            }
            core->sub_count -= 1;
            return true;
        }
    }

    return false;
}
