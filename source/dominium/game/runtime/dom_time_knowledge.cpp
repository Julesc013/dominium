/*
FILE: source/dominium/game/runtime/dom_time_knowledge.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/time_knowledge
RESPONSIBILITY: Epistemic time knowledge state and accessors (no clocks yet).
*/
#include "runtime/dom_time_knowledge.h"

#include "domino/core/dom_time_frames.h"

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

static d_bool is_valid_clock_kind(dom_time_clock_kind kind) {
    return (kind >= DOM_TIME_CLOCK_SUNDIAL && kind <= DOM_TIME_CLOCK_ASTRONOMICAL) ? D_TRUE : D_FALSE;
}

static void insert_clock_sorted(std::vector<dom_time_clock_def> &defs,
                                std::vector<dom_time_clock_state> &states,
                                const dom_time_clock_def &def,
                                const dom_time_clock_state &state) {
    size_t i = 0u;
    while (i < defs.size() && defs[i].clock_id < def.clock_id) {
        ++i;
    }
    defs.insert(defs.begin() + (std::vector<dom_time_clock_def>::difference_type)i, def);
    states.insert(states.begin() + (std::vector<dom_time_clock_state>::difference_type)i, state);
}

static int find_clock_index(const std::vector<dom_time_clock_def> &defs,
                            dom_time_clock_id clock_id) {
    size_t i;
    for (i = 0u; i < defs.size(); ++i) {
        if (defs[i].clock_id == clock_id) {
            return (int)i;
        }
    }
    return -1;
}

static int add_u64(u64 a, u64 b, u64 *out_val) {
    u64 max = (u64)~(u64)0;
    if (!out_val) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (a > (max - b)) {
        return DOM_TIME_KNOWLEDGE_OVERFLOW;
    }
    *out_val = a + b;
    return DOM_TIME_KNOWLEDGE_OK;
}

static int mul_u64(u64 a, u64 b, u64 *out_val) {
    u64 max = (u64)~(u64)0;
    if (!out_val) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (a != 0ull && b > (max / a)) {
        return DOM_TIME_KNOWLEDGE_OVERFLOW;
    }
    *out_val = a * b;
    return DOM_TIME_KNOWLEDGE_OK;
}

} // namespace

struct dom_time_knowledge {
    dom_time_actor_id actor_id;
    u32 known_frames_mask;
    std::vector<dom_calendar_id> calendars;
    std::vector<dom_time_clock_def> clocks;
    std::vector<dom_time_clock_state> clock_states;
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
    knowledge->clocks.clear();
    knowledge->clock_states.clear();
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

int dom_time_knowledge_add_clock(dom_time_knowledge *knowledge,
                                 const dom_time_clock_def *def,
                                 dom_tick calibration_tick) {
    size_t i;
    dom_time_clock_state state;
    if (!knowledge || !def) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (def->clock_id == 0ull || !is_valid_clock_kind(def->kind)) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (!is_valid_frame(def->frame)) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < knowledge->clocks.size(); ++i) {
        if (knowledge->clocks[i].clock_id == def->clock_id) {
            return DOM_TIME_KNOWLEDGE_DUPLICATE_ID;
        }
    }
    state.clock_id = def->clock_id;
    state.state_flags = 0u;
    state.damage_ppm = 0u;
    state.damage_uncertainty_seconds = 0u;
    state.last_calibration_tick = calibration_tick;
    insert_clock_sorted(knowledge->clocks, knowledge->clock_states, *def, state);
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_set_clock_state(dom_time_knowledge *knowledge,
                                       dom_time_clock_id clock_id,
                                       u32 state_flags,
                                       u32 damage_ppm,
                                       u32 damage_uncertainty_seconds) {
    size_t i;
    if (!knowledge || clock_id == 0ull) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < knowledge->clock_states.size(); ++i) {
        if (knowledge->clock_states[i].clock_id == clock_id) {
            knowledge->clock_states[i].state_flags = state_flags;
            knowledge->clock_states[i].damage_ppm = damage_ppm;
            knowledge->clock_states[i].damage_uncertainty_seconds = damage_uncertainty_seconds;
            return DOM_TIME_KNOWLEDGE_OK;
        }
    }
    return DOM_TIME_KNOWLEDGE_NOT_FOUND;
}

int dom_time_knowledge_calibrate_clock(dom_time_knowledge *knowledge,
                                       dom_time_clock_id clock_id,
                                       dom_tick tick) {
    size_t i;
    if (!knowledge || clock_id == 0ull) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < knowledge->clock_states.size(); ++i) {
        if (knowledge->clock_states[i].clock_id == clock_id) {
            if (tick < knowledge->clock_states[i].last_calibration_tick) {
                return DOM_TIME_KNOWLEDGE_BACKWARDS;
            }
            knowledge->clock_states[i].last_calibration_tick = tick;
            return DOM_TIME_KNOWLEDGE_OK;
        }
    }
    return DOM_TIME_KNOWLEDGE_NOT_FOUND;
}

int dom_time_knowledge_sample_clock(const dom_time_knowledge *knowledge,
                                    dom_time_clock_id clock_id,
                                    dom_tick tick,
                                    dom_ups ups,
                                    const dom_time_clock_env *env,
                                    dom_time_clock_reading *out_reading) {
    const dom_time_clock_env default_env = { D_TRUE, D_TRUE, D_TRUE, 0u, 0u };
    const dom_time_clock_env *use_env = env ? env : &default_env;
    int idx;
    dom_time_clock_def def;
    dom_time_clock_state state;
    u64 seconds;
    u32 subsecond_ticks;
    dom_act_time_t act;
    dom_act_time_t frame_act;
    u64 elapsed_seconds;
    u64 drift_seconds = 0ull;
    u64 uncertainty = 0ull;
    u64 total_drift_ppm;
    int rc;

    if (!knowledge || !out_reading) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (ups == 0u) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    idx = find_clock_index(knowledge->clocks, clock_id);
    if (idx < 0) {
        return DOM_TIME_KNOWLEDGE_NOT_FOUND;
    }
    def = knowledge->clocks[(size_t)idx];
    state = knowledge->clock_states[(size_t)idx];

    out_reading->clock_id = def.clock_id;
    out_reading->frame = def.frame;
    out_reading->observed_act = 0;
    out_reading->uncertainty_seconds = 0ull;
    out_reading->flags = 0u;

    if ((def.flags & DOM_TIME_CLOCK_REQUIRES_POWER) && use_env->has_power == D_FALSE) {
        out_reading->flags = DOM_TIME_CLOCK_READING_UNAVAILABLE;
        return DOM_TIME_KNOWLEDGE_UNKNOWN;
    }
    if ((def.flags & DOM_TIME_CLOCK_REQUIRES_DAYLIGHT) && use_env->has_daylight == D_FALSE) {
        out_reading->flags = DOM_TIME_CLOCK_READING_UNAVAILABLE;
        return DOM_TIME_KNOWLEDGE_UNKNOWN;
    }
    if ((def.flags & DOM_TIME_CLOCK_REQUIRES_NETWORK) && use_env->has_network == D_FALSE) {
        out_reading->flags = DOM_TIME_CLOCK_READING_UNAVAILABLE;
        return DOM_TIME_KNOWLEDGE_UNKNOWN;
    }
    if (state.state_flags & DOM_TIME_CLOCK_STATE_JAMMED) {
        out_reading->flags = DOM_TIME_CLOCK_READING_UNAVAILABLE;
        return DOM_TIME_KNOWLEDGE_UNKNOWN;
    }

    if (tick < state.last_calibration_tick) {
        return DOM_TIME_KNOWLEDGE_BACKWARDS;
    }

    seconds = (u64)(tick / (dom_tick)ups);
    subsecond_ticks = (u32)(tick % (dom_tick)ups);
    if (seconds > (u64)DOM_TIME_ACT_MAX) {
        return DOM_TIME_KNOWLEDGE_OVERFLOW;
    }
    act = (dom_act_time_t)seconds;
    rc = dom_time_frame_convert(def.frame, act, &frame_act);
    if (rc != DOM_TIME_OK) {
        return (rc == DOM_TIME_OVERFLOW) ? DOM_TIME_KNOWLEDGE_OVERFLOW : DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (frame_act < 0) {
        return DOM_TIME_KNOWLEDGE_BACKWARDS;
    }

    elapsed_seconds = (u64)((tick - state.last_calibration_tick) / (dom_tick)ups);
    total_drift_ppm = (u64)def.drift_ppm + (u64)state.damage_ppm + (u64)use_env->extra_drift_ppm;
    if (total_drift_ppm > 0ull && elapsed_seconds > 0ull) {
        u64 drift_scaled = 0ull;
        rc = mul_u64(elapsed_seconds, total_drift_ppm, &drift_scaled);
        if (rc != DOM_TIME_KNOWLEDGE_OK) {
            return rc;
        }
        drift_seconds = drift_scaled / 1000000ull;
    }
    {
        u64 frame_u64 = (u64)frame_act;
        u64 reading_u64;
        rc = add_u64(frame_u64, drift_seconds, &reading_u64);
        if (rc != DOM_TIME_KNOWLEDGE_OK || reading_u64 > (u64)DOM_TIME_ACT_MAX) {
            return DOM_TIME_KNOWLEDGE_OVERFLOW;
        }
        out_reading->observed_act = (dom_act_time_t)reading_u64;
    }

    uncertainty = (u64)def.base_accuracy_seconds;
    rc = add_u64(uncertainty, drift_seconds, &uncertainty);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        return rc;
    }
    rc = add_u64(uncertainty, (u64)state.damage_uncertainty_seconds, &uncertainty);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        return rc;
    }
    rc = add_u64(uncertainty, (u64)use_env->extra_uncertainty_seconds, &uncertainty);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        return rc;
    }
    out_reading->uncertainty_seconds = uncertainty;
    out_reading->flags |= DOM_TIME_CLOCK_READING_VALID;
    if (drift_seconds > 0ull || state.damage_ppm > 0u || state.damage_uncertainty_seconds > 0u ||
        use_env->extra_drift_ppm > 0u || use_env->extra_uncertainty_seconds > 0u) {
        out_reading->flags |= DOM_TIME_CLOCK_READING_DEGRADED;
    }
    (void)subsecond_ticks;
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_sample_all(const dom_time_knowledge *knowledge,
                                  dom_tick tick,
                                  dom_ups ups,
                                  const dom_time_clock_env *env,
                                  dom_time_clock_reading *out_readings,
                                  u32 max_readings,
                                  u32 *out_count) {
    if (!knowledge || !out_count) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    *out_count = 0u;
    if (knowledge->clocks.empty()) {
        return DOM_TIME_KNOWLEDGE_UNKNOWN;
    }
    if (!out_readings || max_readings == 0u) {
        return DOM_TIME_KNOWLEDGE_OK;
    }
    for (u32 i = 0u; i < (u32)knowledge->clocks.size() && i < max_readings; ++i) {
        (void)dom_time_knowledge_sample_clock(knowledge,
                                              knowledge->clocks[i].clock_id,
                                              tick,
                                              ups,
                                              env,
                                              &out_readings[i]);
        *out_count += 1u;
    }
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_knowledge_apply_document(dom_time_knowledge *knowledge,
                                      const dom_time_document *doc) {
    if (!knowledge || !doc) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    if (doc->frame_mask != 0u) {
        knowledge->known_frames_mask |= doc->frame_mask;
    }
    if (doc->calendar_id != 0ull) {
        if (dom_time_knowledge_add_calendar(knowledge, doc->calendar_id) != DOM_TIME_KNOWLEDGE_OK) {
            return DOM_TIME_KNOWLEDGE_DUPLICATE_ID;
        }
    }
    return DOM_TIME_KNOWLEDGE_OK;
}

int dom_time_clock_init_sundial(dom_time_clock_id clock_id,
                                dom_time_frame_id frame,
                                dom_time_clock_def *out_def) {
    if (!out_def || clock_id == 0ull || !is_valid_frame(frame)) {
        return DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT;
    }
    out_def->clock_id = clock_id;
    out_def->kind = DOM_TIME_CLOCK_SUNDIAL;
    out_def->frame = frame;
    out_def->base_accuracy_seconds = 600u;
    out_def->drift_ppm = 0u;
    out_def->flags = DOM_TIME_CLOCK_REQUIRES_DAYLIGHT;
    return DOM_TIME_KNOWLEDGE_OK;
}
