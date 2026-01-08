/*
FILE: source/dominium/game/runtime/dom_macro_events.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/macro_events
RESPONSIBILITY: Deterministic macro event scheduler.
*/
#include "runtime/dom_macro_events.h"

#include <vector>

namespace {

struct MacroEventEntry {
    u64 event_id;
    u32 scope_kind;
    u64 scope_id;
    u64 trigger_tick;
    std::vector<dom_macro_event_effect> effects;
};

static int find_event_index(const std::vector<MacroEventEntry> &list, u64 event_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].event_id == event_id) {
            return (int)i;
        }
    }
    return -1;
}

static bool event_less(const MacroEventEntry &a, const MacroEventEntry &b) {
    if (a.trigger_tick != b.trigger_tick) {
        return a.trigger_tick < b.trigger_tick;
    }
    return a.event_id < b.event_id;
}

static void insert_event_sorted(std::vector<MacroEventEntry> &list,
                                const MacroEventEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && event_less(list[i], entry)) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<MacroEventEntry>::difference_type)i, entry);
}

static bool scope_kind_valid(u32 scope_kind) {
    return scope_kind == DOM_MACRO_SCOPE_SYSTEM || scope_kind == DOM_MACRO_SCOPE_GALAXY;
}

} // namespace

struct dom_macro_events {
    std::vector<MacroEventEntry> events;
    size_t cursor;
    u64 last_tick;
    int has_last_tick;
};

dom_macro_events *dom_macro_events_create(void) {
    dom_macro_events *events = new dom_macro_events();
    if (!events) {
        return 0;
    }
    (void)dom_macro_events_init(events);
    return events;
}

void dom_macro_events_destroy(dom_macro_events *events) {
    if (!events) {
        return;
    }
    delete events;
}

int dom_macro_events_init(dom_macro_events *events) {
    if (!events) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    events->events.clear();
    events->cursor = 0u;
    events->last_tick = 0ull;
    events->has_last_tick = 0;
    return DOM_MACRO_EVENTS_OK;
}

int dom_macro_events_schedule(dom_macro_events *events,
                              const dom_macro_event_desc *desc) {
    MacroEventEntry entry;
    size_t i;
    if (!events || !desc || desc->event_id == 0ull ||
        desc->scope_id == 0ull || !scope_kind_valid(desc->scope_kind)) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    if (desc->effect_count > 0u && !desc->effects) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    if (find_event_index(events->events, desc->event_id) >= 0) {
        return DOM_MACRO_EVENTS_DUPLICATE_ID;
    }
    if (events->has_last_tick && desc->trigger_tick <= events->last_tick) {
        return DOM_MACRO_EVENTS_TOO_EARLY;
    }
    entry.event_id = desc->event_id;
    entry.scope_kind = desc->scope_kind;
    entry.scope_id = desc->scope_id;
    entry.trigger_tick = desc->trigger_tick;
    entry.effects.clear();
    if (desc->effect_count > 0u) {
        entry.effects.reserve(desc->effect_count);
        for (i = 0u; i < desc->effect_count; ++i) {
            dom_macro_event_effect effect = desc->effects[i];
            if (effect.resource_id == 0ull) {
                return DOM_MACRO_EVENTS_INVALID_DATA;
            }
            entry.effects.push_back(effect);
        }
    }
    insert_event_sorted(events->events, entry);
    if (events->cursor > events->events.size()) {
        events->cursor = events->events.size();
    }
    return DOM_MACRO_EVENTS_OK;
}

int dom_macro_events_iterate(const dom_macro_events *events,
                             dom_macro_event_iter_fn fn,
                             void *user) {
    size_t i;
    if (!events || !fn) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    for (i = 0u; i < events->events.size(); ++i) {
        const MacroEventEntry &entry = events->events[i];
        dom_macro_event_info info;
        info.event_id = entry.event_id;
        info.scope_kind = entry.scope_kind;
        info.scope_id = entry.scope_id;
        info.trigger_tick = entry.trigger_tick;
        info.effect_count = (u32)entry.effects.size();
        fn(&info, user);
    }
    return DOM_MACRO_EVENTS_OK;
}

int dom_macro_events_list(const dom_macro_events *events,
                          dom_macro_event_info *out_infos,
                          u32 max_infos,
                          u32 *out_count) {
    if (!events || !out_count) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    *out_count = (u32)events->events.size();
    if (out_infos && max_infos > 0u) {
        const u32 limit = (*out_count < max_infos) ? *out_count : max_infos;
        for (u32 i = 0u; i < limit; ++i) {
            const MacroEventEntry &entry = events->events[i];
            out_infos[i].event_id = entry.event_id;
            out_infos[i].scope_kind = entry.scope_kind;
            out_infos[i].scope_id = entry.scope_id;
            out_infos[i].trigger_tick = entry.trigger_tick;
            out_infos[i].effect_count = (u32)entry.effects.size();
        }
    }
    return DOM_MACRO_EVENTS_OK;
}

int dom_macro_events_list_effects(const dom_macro_events *events,
                                  u64 event_id,
                                  dom_macro_event_effect *out_effects,
                                  u32 max_effects,
                                  u32 *out_count) {
    int idx;
    if (!events || !out_count || event_id == 0ull) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    idx = find_event_index(events->events, event_id);
    if (idx < 0) {
        return DOM_MACRO_EVENTS_NOT_FOUND;
    }
    {
        const MacroEventEntry &entry = events->events[(size_t)idx];
        u32 count = (u32)entry.effects.size();
        if (out_effects && max_effects > 0u) {
            const u32 limit = (count < max_effects) ? count : max_effects;
            for (u32 i = 0u; i < limit; ++i) {
                out_effects[i] = entry.effects[i];
            }
        }
        *out_count = count;
    }
    return DOM_MACRO_EVENTS_OK;
}

u32 dom_macro_events_count(const dom_macro_events *events) {
    if (!events) {
        return 0u;
    }
    return (u32)events->events.size();
}

int dom_macro_events_update(dom_macro_events *events,
                            dom_macro_economy *economy,
                            u64 current_tick) {
    if (!events) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    if (events->has_last_tick && current_tick < events->last_tick) {
        return DOM_MACRO_EVENTS_INVALID_DATA;
    }
    while (events->cursor < events->events.size()) {
        MacroEventEntry &entry = events->events[events->cursor];
        if (entry.trigger_tick > current_tick) {
            break;
        }
        if (economy) {
            const size_t effect_count = entry.effects.size();
            for (size_t i = 0u; i < effect_count; ++i) {
                const dom_macro_event_effect &effect = entry.effects[i];
                (void)dom_macro_economy_rate_delta(economy,
                                                   entry.scope_kind,
                                                   entry.scope_id,
                                                   effect.resource_id,
                                                   effect.production_delta,
                                                   effect.demand_delta);
                (void)dom_macro_economy_flags_apply(economy,
                                                    entry.scope_kind,
                                                    entry.scope_id,
                                                    effect.flags_set,
                                                    effect.flags_clear);
            }
        }
        events->cursor += 1u;
    }
    events->last_tick = current_tick;
    events->has_last_tick = 1;
    return DOM_MACRO_EVENTS_OK;
}

int dom_macro_events_seek(dom_macro_events *events, u64 tick) {
    size_t i;
    if (!events) {
        return DOM_MACRO_EVENTS_INVALID_ARGUMENT;
    }
    for (i = 0u; i < events->events.size(); ++i) {
        if (events->events[i].trigger_tick > tick) {
            break;
        }
    }
    events->cursor = i;
    events->last_tick = tick;
    events->has_last_tick = 1;
    return DOM_MACRO_EVENTS_OK;
}

u64 dom_macro_events_last_tick(const dom_macro_events *events) {
    if (!events || !events->has_last_tick) {
        return 0ull;
    }
    return events->last_tick;
}
