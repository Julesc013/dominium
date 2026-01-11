/*
FILE: source/dominium/game/runtime/dom_time_knowledge.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/time_knowledge
RESPONSIBILITY: Epistemic time knowledge state and accessors (no clocks yet).
*/
#include "runtime/dom_time_knowledge.h"

#include <vector>

namespace {

static void insert_calendar_sorted(std::vector<dom_calendar_id> &list, dom_calendar_id id) {
    size_t i = 0u;
    while (i < list.size() && list[i] < id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<dom_calendar_id>::difference_type)i, id);
}

static int find_calendar_index(const std::vector<dom_calendar_id> &list, dom_calendar_id id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i] == id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool is_valid_frame(dom_time_frame_id frame) {
    return (frame >= DOM_TIME_FRAME_ACT && frame <= DOM_TIME_FRAME_CPT) ? D_TRUE : D_FALSE;
}

} // namespace

struct dom_time_knowledge {
    dom_time_actor_id actor_id;
    u32 known_frames_mask;
    std::vector<dom_calendar_id> calendars;
};

dom_time_knowledge *dom_time_knowledge_create(dom_time_actor_id actor_id) {
    dom_time_knowledge *knowledge = new dom_time_knowledge();
    if (!knowledge) {
        return 0;
    }
    if (dom_time_knowledge_init(knowledge, actor_id) != DOM_TIME_KNOWLEDGE_OK) {
        delete knowledge;
        return 0;
    }
    return knowledge;
}

void dom_time_knowledge_destroy(dom_time_knowledge *knowledge) {
    if (!knowledge) {
        return;
    }
    delete knowledge;
}

int dom_time_knowledge_init(dom_time_knowledge *knowledge, dom_time_actor_id actor_id) {
    if (!knowledge || actor_id == 0ull) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    knowledge->actor_id = actor_id;
    knowledge->known_frames_mask = 0u;
    knowledge->calendars.clear();
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_add_frame(dom_time_knowledge *knowledge, dom_time_frame_id frame) {
    if (!knowledge) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (!is_valid_frame(frame)) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    knowledge->known_frames_mask |= (1u << (u32)frame);
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_has_frame(const dom_time_knowledge *knowledge,
                                 dom_time_frame_id frame,
                                 d_bool *out_known) {
    if (!knowledge || !out_known) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (!is_valid_frame(frame)) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    *out_known = (knowledge->known_frames_mask & (1u << (u32)frame)) ? D_TRUE : D_FALSE;
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_add_calendar(dom_time_knowledge *knowledge, dom_calendar_id id) {
    if (!knowledge || id == 0ull) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (find_calendar_index(knowledge->calendars, id) >= 0) {
        return DOM_TIME_KNOWLEDGE_DUPLICATE_ID;
    }
    insert_calendar_sorted(knowledge->calendars, id);
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_has_calendar(const dom_time_knowledge *knowledge,
                                    dom_calendar_id id,
                                    d_bool *out_known) {
    if (!knowledge || !out_known || id == 0ull) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    *out_known = (find_calendar_index(knowledge->calendars, id) >= 0) ? D_TRUE : D_FALSE;
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_list_calendars(const dom_time_knowledge *knowledge,
                                      dom_calendar_id *out_ids,
                                      u32 max_ids,
                                      u32 *out_count) {
    u32 count;
    if (!knowledge || !out_count) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    count = (u32)knowledge->calendars.size();
    if (out_ids && max_ids > 0u) {
        const u32 limit = (count < max_ids) ? count : max_ids;
        for (u32 i = 0u; i < limit; ++i) {
            out_ids[i] = knowledge->calendars[i];
        }
    }
    *out_count = count;
    return DOM_TIME_KNOWLEDGE_OK;
}
