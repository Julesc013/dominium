/*
FILE: source/dominium/game/runtime/dom_ai_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ai_scheduler
RESPONSIBILITY: Budgeted, deterministic AI scheduler for faction planners.
*/
#include "runtime/dom_ai_scheduler.h"

#include <vector>
#include <string>
#include <cstdio>
#include <cstring>

#include "dom_paths.h"
#include "dom_session.h"
#include "runtime/dom_game_paths.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_faction_registry.h"
#include "runtime/dom_ai_planner_logistics.h"
#include "runtime/dom_ai_planner_events.h"
#include "runtime/dom_macro_events.h"
#include "runtime/dom_game_hash.h"
#include "dominium/core_tlv.h"

namespace {

static const u32 DEFAULT_PERIOD_TICKS = 60u;
static const u32 DEFAULT_MAX_OPS = 8u;
static const u32 DEFAULT_MAX_FACTIONS = 4u;

enum {
    AI_TRACE_SCHEMA_VERSION = 1u,
    AI_TRACE_TAG_PLAN_ID = 0x10u,
    AI_TRACE_TAG_FACTION_ID = 0x11u,
    AI_TRACE_TAG_TICK = 0x12u,
    AI_TRACE_TAG_INPUT_DIGEST = 0x13u,
    AI_TRACE_TAG_OUTPUT_DIGEST = 0x14u,
    AI_TRACE_TAG_OUTPUT_COUNT = 0x15u,
    AI_TRACE_TAG_REASON_CODE = 0x16u,
    AI_TRACE_TAG_OPS_USED = 0x17u,
    AI_TRACE_TAG_BUDGET_HIT = 0x18u
};

struct AiStateEntry {
    dom_ai_faction_state state;
};

struct FactionListCtx {
    std::vector<dom_faction_id> ids;
};

static void collect_faction_id(const dom_faction_info *info, void *user) {
    FactionListCtx *ctx = static_cast<FactionListCtx *>(user);
    if (!ctx || !info) {
        return;
    }
    ctx->ids.push_back(info->faction_id);
}

static int find_state_index(const std::vector<AiStateEntry> &list, u64 faction_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].state.faction_id == faction_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_state_sorted(std::vector<AiStateEntry> &list,
                                const AiStateEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].state.faction_id < entry.state.faction_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<AiStateEntry>::difference_type)i, entry);
}

static u64 hash_u64x4(u64 a, u64 b, u64 c, u64 d) {
    unsigned char buf[32];
    dom::core_tlv::tlv_write_u64_le(&buf[0], a);
    dom::core_tlv::tlv_write_u64_le(&buf[8], b);
    dom::core_tlv::tlv_write_u64_le(&buf[16], c);
    dom::core_tlv::tlv_write_u64_le(&buf[24], d);
    return dom::core_tlv::tlv_fnv1a64(buf, sizeof(buf));
}

static u64 hash_combine(u64 seed, u64 value) {
    return hash_u64x4(seed, value, 0ull, 0ull);
}

static u64 hash_cmd(const dom_ai_planned_cmd &cmd, u64 seed) {
    u64 h = seed;
    h = hash_u64x4(h, cmd.schema_id, cmd.schema_ver, cmd.tick);
    if (!cmd.payload.empty()) {
        h = hash_combine(h,
                         dom::core_tlv::tlv_fnv1a64(&cmd.payload[0], cmd.payload.size()));
    }
    return h;
}

static u64 hash_event(const dom_ai_planned_event &evt, u64 seed) {
    u64 h = seed;
    h = hash_u64x4(h, evt.desc.event_id, evt.desc.scope_id, evt.desc.trigger_tick);
    h = hash_u64x4(h, evt.desc.scope_kind, evt.desc.effect_count, 0ull);
    if (!evt.effects.empty()) {
        const unsigned char *bytes =
            reinterpret_cast<const unsigned char *>(&evt.effects[0]);
        h = hash_combine(h,
                         dom::core_tlv::tlv_fnv1a64(bytes,
                                                    evt.effects.size() *
                                                        sizeof(dom_macro_event_effect)));
    }
    return h;
}

static bool build_trace_path(dom_ai_scheduler *sched,
                             dom_game_runtime *runtime,
                             u64 tick,
                             u64 faction_id,
                             u64 plan_id,
                             std::string &out_path) {
    dom::DomSession *session;
    dom::DomGamePaths paths;
    const dom::InstanceInfo *inst;
    char name_buf[128];
    std::string dir;

    if (!sched || !runtime) {
        return false;
    }
    session = static_cast<dom::DomSession *>(
        const_cast<void *>(dom_game_runtime_session(runtime)));
    inst = session ? &session->instance() : 0;
    if (!session || !inst) {
        return false;
    }

    if (!dom::dom_game_paths_init_from_env(paths,
                                           inst->id,
                                           dom_game_runtime_get_run_id(runtime),
                                           DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED)) {
        return false;
    }
    dir = dom::dom_game_paths_get_log_dir(paths);
    if (dir.empty()) {
        dir = dom::dom_game_paths_get_run_root(paths);
    }
    if (dir.empty()) {
        return false;
    }

    std::snprintf(name_buf,
                  sizeof(name_buf),
                  "ai_trace_%llu_%llu_%llu_%llu.tlv",
                  (unsigned long long)dom_game_runtime_get_run_id(runtime),
                  (unsigned long long)tick,
                  (unsigned long long)faction_id,
                  (unsigned long long)plan_id);
    out_path = dom::join(dir, name_buf);
    return true;
}

static void write_trace(dom_ai_scheduler *sched,
                        dom_game_runtime *runtime,
                        const dom_ai_faction_state &state,
                        u64 tick,
                        u64 input_digest,
                        u64 output_digest,
                        u32 output_count,
                        u32 reason_code,
                        u32 ops_used,
                        u32 budget_hit) {
    std::string path;
    if (!sched || !runtime || !sched->enable_traces) {
        return;
    }
    if (!build_trace_path(sched, runtime, tick, state.faction_id, state.last_plan_id, path)) {
        return;
    }
    dom::core_tlv::TlvWriter writer;
    writer.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, AI_TRACE_SCHEMA_VERSION);
    writer.add_u64(AI_TRACE_TAG_PLAN_ID, state.last_plan_id);
    writer.add_u64(AI_TRACE_TAG_FACTION_ID, state.faction_id);
    writer.add_u64(AI_TRACE_TAG_TICK, tick);
    writer.add_u64(AI_TRACE_TAG_INPUT_DIGEST, input_digest);
    writer.add_u64(AI_TRACE_TAG_OUTPUT_DIGEST, output_digest);
    writer.add_u32(AI_TRACE_TAG_OUTPUT_COUNT, output_count);
    writer.add_u32(AI_TRACE_TAG_REASON_CODE, reason_code);
    writer.add_u32(AI_TRACE_TAG_OPS_USED, ops_used);
    writer.add_u32(AI_TRACE_TAG_BUDGET_HIT, budget_hit);
    const std::vector<unsigned char> &bytes = writer.bytes();
    if (bytes.empty()) {
        return;
    }
    FILE *fh = std::fopen(path.c_str(), "wb");
    if (!fh) {
        return;
    }
    (void)std::fwrite(&bytes[0], 1u, bytes.size(), fh);
    (void)std::fclose(fh);
}

} // namespace

struct dom_ai_scheduler {
    u32 period_ticks;
    u32 max_ops_per_tick;
    u32 max_factions_per_tick;
    u32 enable_traces;
    std::vector<AiStateEntry> states;
};

dom_ai_scheduler *dom_ai_scheduler_create(void) {
    dom_ai_scheduler *sched = new dom_ai_scheduler();
    if (!sched) {
        return 0;
    }
    (void)dom_ai_scheduler_init(sched, 0);
    return sched;
}

void dom_ai_scheduler_destroy(dom_ai_scheduler *sched) {
    if (!sched) {
        return;
    }
    delete sched;
}

int dom_ai_scheduler_init(dom_ai_scheduler *sched,
                          const dom_ai_scheduler_config *cfg) {
    if (!sched) {
        return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
    }
    sched->period_ticks = DEFAULT_PERIOD_TICKS;
    sched->max_ops_per_tick = DEFAULT_MAX_OPS;
    sched->max_factions_per_tick = DEFAULT_MAX_FACTIONS;
    sched->enable_traces = 1u;
    if (cfg) {
        if (cfg->struct_size != sizeof(dom_ai_scheduler_config) ||
            cfg->struct_version != DOM_AI_SCHEDULER_CONFIG_VERSION) {
            return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
        }
        if (cfg->period_ticks > 0u) {
            sched->period_ticks = cfg->period_ticks;
        }
        if (cfg->max_ops_per_tick > 0u) {
            sched->max_ops_per_tick = cfg->max_ops_per_tick;
        }
        if (cfg->max_factions_per_tick > 0u) {
            sched->max_factions_per_tick = cfg->max_factions_per_tick;
        }
        sched->enable_traces = cfg->enable_traces ? 1u : 0u;
    }
    sched->states.clear();
    return DOM_AI_SCHEDULER_OK;
}

int dom_ai_scheduler_set_budget(dom_ai_scheduler *sched,
                                u32 max_ops_per_tick,
                                u32 max_factions_per_tick) {
    if (!sched) {
        return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
    }
    if (max_ops_per_tick > 0u) {
        sched->max_ops_per_tick = max_ops_per_tick;
    }
    if (max_factions_per_tick > 0u) {
        sched->max_factions_per_tick = max_factions_per_tick;
    }
    return DOM_AI_SCHEDULER_OK;
}

int dom_ai_scheduler_tick(dom_ai_scheduler *sched,
                          dom_game_runtime *runtime,
                          u64 tick) {
    dom_faction_registry *factions;
    dom_macro_economy *economy;
    dom_macro_events *events;
    dom_station_registry *stations;
    dom_route_graph *routes;
    dom_body_registry *bodies;
    dom_system_registry *systems;
    FactionListCtx list_ctx;
    u32 ops_remaining;
    u32 factions_remaining;

    if (!sched || !runtime) {
        return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
    }

    factions = (dom_faction_registry *)dom_game_runtime_faction_registry(runtime);
    economy = (dom_macro_economy *)dom_game_runtime_macro_economy(runtime);
    events = (dom_macro_events *)dom_game_runtime_macro_events(runtime);
    stations = (dom_station_registry *)dom_game_runtime_station_registry(runtime);
    routes = (dom_route_graph *)dom_game_runtime_route_graph(runtime);
    bodies = (dom_body_registry *)dom_game_runtime_body_registry(runtime);
    systems = (dom_system_registry *)dom_game_runtime_system_registry(runtime);
    if (!factions || !economy || !events || !stations || !routes || !bodies || !systems) {
        return DOM_AI_SCHEDULER_OK;
    }

    (void)dom_faction_iterate(factions, collect_faction_id, &list_ctx);
    if (list_ctx.ids.empty()) {
        return DOM_AI_SCHEDULER_OK;
    }

    {
        std::vector<AiStateEntry> next_states;
        next_states.reserve(list_ctx.ids.size());
        for (size_t i = 0u; i < list_ctx.ids.size(); ++i) {
            const u64 id = list_ctx.ids[i];
            AiStateEntry entry;
            int idx = find_state_index(sched->states, id);
            if (idx >= 0) {
                entry = sched->states[(size_t)idx];
            } else {
                entry.state.faction_id = id;
                entry.state.next_decision_tick = tick;
                entry.state.last_plan_id = 0ull;
                entry.state.last_output_count = 0u;
                entry.state.last_reason_code = DOM_AI_REASON_NONE;
                entry.state.last_budget_hit = 0u;
            }
            insert_state_sorted(next_states, entry);
        }
        sched->states.swap(next_states);
    }

    ops_remaining = sched->max_ops_per_tick;
    factions_remaining = sched->max_factions_per_tick;

    for (size_t i = 0u; i < sched->states.size(); ++i) {
        AiStateEntry &entry = sched->states[i];
        dom_faction_info faction;
        dom_ai_planner_logistics_result log_res;
        dom_ai_planner_events_result evt_res;
        u32 ops_used = 0u;
        u32 output_count = 0u;
        u32 reason_code = DOM_AI_REASON_NONE;
        u32 budget_hit = 0u;
        u64 input_digest = 0ull;
        u64 output_digest = 0ull;

        if (factions_remaining == 0u) {
            break;
        }
        if (tick < entry.state.next_decision_tick) {
            continue;
        }
        if (ops_remaining == 0u) {
            budget_hit = 1u;
            reason_code = DOM_AI_REASON_BUDGET_HIT;
            entry.state.last_plan_id += 1ull;
            entry.state.last_output_count = 0u;
            entry.state.last_reason_code = reason_code;
            entry.state.last_budget_hit = budget_hit;
            entry.state.next_decision_tick = tick + sched->period_ticks;
            if (sched->enable_traces) {
                input_digest = hash_u64x4(dom_game_runtime_get_hash(runtime),
                                          entry.state.faction_id,
                                          entry.state.last_plan_id,
                                          tick);
                output_digest = 0ull;
                write_trace(sched,
                            runtime,
                            entry.state,
                            tick,
                            input_digest,
                            output_digest,
                            0u,
                            reason_code,
                            0u,
                            budget_hit);
            }
            factions_remaining -= 1u;
            continue;
        }

        if (dom_faction_get(factions, entry.state.faction_id, &faction) != DOM_FACTION_OK) {
            entry.state.last_plan_id += 1ull;
            entry.state.last_output_count = 0u;
            entry.state.last_reason_code = DOM_AI_REASON_INVALID_INPUT;
            entry.state.last_budget_hit = 0u;
            entry.state.next_decision_tick = tick + sched->period_ticks;
            factions_remaining -= 1u;
            continue;
        }

        input_digest = hash_u64x4(dom_game_runtime_get_hash(runtime),
                                  entry.state.faction_id,
                                  faction.ai_seed,
                                  tick);

        (void)dom_ai_planner_logistics_run(&faction,
                                           economy,
                                           stations,
                                           routes,
                                           bodies,
                                           systems,
                                           tick,
                                           ops_remaining,
                                           &log_res);
        if (log_res.reason_code == DOM_AI_REASON_BUDGET_HIT) {
            budget_hit = 1u;
        }
        ops_remaining = (ops_remaining > log_res.ops_used)
                            ? (ops_remaining - log_res.ops_used)
                            : 0u;
        ops_used += log_res.ops_used;

        if (ops_remaining > 0u) {
            (void)dom_ai_planner_events_run(&faction,
                                            economy,
                                            events,
                                            systems,
                                            tick,
                                            ops_remaining,
                                            &evt_res);
            if (evt_res.reason_code == DOM_AI_REASON_BUDGET_HIT) {
                budget_hit = 1u;
            }
            ops_remaining = (ops_remaining > evt_res.ops_used)
                                ? (ops_remaining - evt_res.ops_used)
                                : 0u;
            ops_used += evt_res.ops_used;
        } else {
            evt_res.events.clear();
            evt_res.ops_used = 0u;
            evt_res.reason_code = DOM_AI_REASON_NONE;
        }

        for (size_t c = 0u; c < log_res.commands.size(); ++c) {
            const dom_ai_planned_cmd &cmd = log_res.commands[c];
            dom_game_command runtime_cmd;
            u32 applied_tick = 0u;
            std::memset(&runtime_cmd, 0, sizeof(runtime_cmd));
            runtime_cmd.struct_size = sizeof(runtime_cmd);
            runtime_cmd.struct_version = DOM_GAME_COMMAND_VERSION;
            runtime_cmd.tick = cmd.tick;
            runtime_cmd.schema_id = cmd.schema_id;
            runtime_cmd.schema_ver = cmd.schema_ver;
            runtime_cmd.payload = cmd.payload.empty() ? 0 : &cmd.payload[0];
            runtime_cmd.payload_size = (u32)cmd.payload.size();
            if (dom_game_runtime_execute(runtime, &runtime_cmd, &applied_tick) == DOM_GAME_RUNTIME_OK) {
                output_count += 1u;
            }
            output_digest = hash_cmd(cmd, output_digest);
        }

        for (size_t e = 0u; e < evt_res.events.size(); ++e) {
            dom_ai_planned_event &evt = evt_res.events[e];
            if (evt.desc.effect_count > 0u && evt.effects.empty()) {
                continue;
            }
            evt.desc.effects = evt.effects.empty() ? 0 : &evt.effects[0];
            if (dom_macro_events_schedule(events, &evt.desc) == DOM_MACRO_EVENTS_OK) {
                output_count += 1u;
            }
            output_digest = hash_event(evt, output_digest);
        }

        if (budget_hit) {
            reason_code = DOM_AI_REASON_BUDGET_HIT;
        } else if (output_count > 0u) {
            reason_code = DOM_AI_REASON_ACTIONS;
        } else {
            reason_code = DOM_AI_REASON_NONE;
        }

        entry.state.last_plan_id += 1ull;
        entry.state.last_output_count = output_count;
        entry.state.last_reason_code = reason_code;
        entry.state.last_budget_hit = budget_hit;
        entry.state.next_decision_tick = tick + sched->period_ticks;

        if (sched->enable_traces && (output_count > 0u || budget_hit)) {
            write_trace(sched,
                        runtime,
                        entry.state,
                        tick,
                        input_digest,
                        output_digest,
                        output_count,
                        reason_code,
                        ops_used,
                        budget_hit);
        }

        factions_remaining -= 1u;
    }

    return DOM_AI_SCHEDULER_OK;
}

int dom_ai_scheduler_list_states(const dom_ai_scheduler *sched,
                                 dom_ai_faction_state *out_states,
                                 u32 max_states,
                                 u32 *out_count) {
    if (!sched || !out_count) {
        return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
    }
    const u32 count = (u32)sched->states.size();
    if (out_states && max_states > 0u) {
        const u32 limit = (count < max_states) ? count : max_states;
        for (u32 i = 0u; i < limit; ++i) {
            out_states[i] = sched->states[i].state;
        }
    }
    *out_count = count;
    return DOM_AI_SCHEDULER_OK;
}

int dom_ai_scheduler_get_state(const dom_ai_scheduler *sched,
                               u64 faction_id,
                               dom_ai_faction_state *out_state) {
    int idx;
    if (!sched || !out_state || faction_id == 0ull) {
        return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
    }
    idx = find_state_index(sched->states, faction_id);
    if (idx < 0) {
        return DOM_AI_SCHEDULER_ERR;
    }
    *out_state = sched->states[(size_t)idx].state;
    return DOM_AI_SCHEDULER_OK;
}
