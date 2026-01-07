/*
FILE: source/dominium/game/runtime/dom_game_runtime.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_runtime
RESPONSIBILITY: Implements the internal runtime kernel; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal struct versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_runtime.h"

#include <cstring>
#include <vector>

#include "dom_game_net.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_cosmo_transit.h"
#include "runtime/dom_game_hash.h"
#include "runtime/dom_game_replay.h"

extern "C" {
#include "ai/d_agent.h"
#include "net/d_net_cmd.h"
#include "net/d_net_transport.h"
#include "struct/d_struct.h"
}

struct dom_game_runtime {
    void *session;
    void *net;
    const void *instance;
    u32 ups;
    double dt_s;
    u64 wall_accum_us;
    void *replay_play;
    u32 replay_last_tick;
    int replay_last_tick_valid;
    u64 run_id;
    std::vector<unsigned char> manifest_hash_bytes;
    dom::dom_cosmo_graph cosmo_graph;
    dom_cosmo_transit_state cosmo_transit;
    u64 cosmo_last_arrival_tick;
};

namespace {

static const u32 DEFAULT_UPS = 60u;

static dom::DomSession *session_of(dom_game_runtime *rt) {
    return rt ? static_cast<dom::DomSession *>(rt->session) : 0;
}

static dom::DomSession *session_of(const dom_game_runtime *rt) {
    return rt ? static_cast<dom::DomSession *>(rt->session) : 0;
}

static dom::DomGameNet *net_of(dom_game_runtime *rt) {
    return rt ? static_cast<dom::DomGameNet *>(rt->net) : 0;
}

static const dom::InstanceInfo *inst_of(const dom_game_runtime *rt) {
    return rt ? static_cast<const dom::InstanceInfo *>(rt->instance) : 0;
}

static u64 compute_seed(dom::DomSession *session, const dom::InstanceInfo *inst) {
    const d_world *w = session ? session->world() : 0;
    if (w) {
        return w->meta.seed;
    }
    return inst ? (u64)inst->world_seed : 0ull;
}

static int inject_replay(dom_game_runtime *rt, d_sim_context *sim) {
    const dom_game_replay_packet *packets = (const dom_game_replay_packet *)0;
    u32 count = 0u;
    const u64 next_tick = (u64)sim->tick_index + 1ull;
    int rc;
    u32 i;

    if (!rt || !sim) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (!rt->replay_play) {
        return DOM_GAME_RUNTIME_OK;
    }

    rc = dom_game_replay_play_next_for_tick((dom_game_replay_play *)rt->replay_play,
                                            next_tick,
                                            &packets,
                                            &count);
    if (rc == DOM_GAME_REPLAY_END) {
        return DOM_GAME_RUNTIME_REPLAY_END;
    }
    if (rc != DOM_GAME_REPLAY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }

    for (i = 0u; i < count; ++i) {
        (void)d_net_receive_packet(0u, 0u, packets[i].payload, packets[i].size);
    }

    if (count == 0u && rt->replay_last_tick_valid && next_tick > (u64)rt->replay_last_tick) {
        return DOM_GAME_RUNTIME_REPLAY_END;
    }

    return DOM_GAME_RUNTIME_OK;
}

} // namespace

dom_game_runtime *dom_game_runtime_create(const dom_game_runtime_init_desc *desc) {
    dom_game_runtime *rt;
    if (!desc || desc->struct_size != sizeof(dom_game_runtime_init_desc) ||
        desc->struct_version != DOM_GAME_RUNTIME_INIT_DESC_VERSION) {
        return 0;
    }
    if (!desc->session || !desc->net) {
        return 0;
    }

    rt = new dom_game_runtime();
    rt->session = desc->session;
    rt->net = desc->net;
    rt->instance = desc->instance;
    rt->ups = desc->ups ? desc->ups : DEFAULT_UPS;
    rt->dt_s = (rt->ups > 0u) ? (1.0 / (double)rt->ups) : (1.0 / 60.0);
    rt->wall_accum_us = 0u;
    rt->replay_play = 0;
    rt->replay_last_tick = 0u;
    rt->replay_last_tick_valid = 0;
    rt->run_id = desc->run_id;
    (void)dom::dom_cosmo_graph_init(&rt->cosmo_graph,
                                    compute_seed(session_of(rt), inst_of(rt)),
                                    0);
    dom_cosmo_transit_reset(&rt->cosmo_transit);
    rt->cosmo_last_arrival_tick = 0ull;
    if (desc->instance_manifest_hash_bytes && desc->instance_manifest_hash_len > 0u) {
        rt->manifest_hash_bytes.assign(desc->instance_manifest_hash_bytes,
                                       desc->instance_manifest_hash_bytes +
                                       desc->instance_manifest_hash_len);
    }
    return rt;
}

void dom_game_runtime_destroy(dom_game_runtime *rt) {
    if (!rt) {
        return;
    }
    delete rt;
}

int dom_game_runtime_set_replay_last_tick(dom_game_runtime *rt, u32 last_tick) {
    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }
    rt->replay_last_tick = last_tick;
    rt->replay_last_tick_valid = (last_tick > 0u) ? 1 : 0;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_set_replay_playback(dom_game_runtime *rt, void *playback) {
    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }
    rt->replay_play = playback;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_cosmo_transit_begin(dom_game_runtime *rt,
                                         u64 src_entity_id,
                                         u64 dst_entity_id,
                                         u64 travel_edge_id,
                                         u64 start_tick,
                                         u64 duration_ticks) {
    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_cosmo_transit_begin(&rt->cosmo_transit,
                                src_entity_id,
                                dst_entity_id,
                                travel_edge_id,
                                start_tick,
                                duration_ticks) != DOM_COSMO_TRANSIT_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    rt->cosmo_last_arrival_tick = 0ull;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_cosmo_transit_get(const dom_game_runtime *rt,
                                       dom_cosmo_transit_state *out_state) {
    if (!rt || !out_state) {
        return DOM_GAME_RUNTIME_ERR;
    }
    *out_state = rt->cosmo_transit;
    return DOM_GAME_RUNTIME_OK;
}

u64 dom_game_runtime_cosmo_last_arrival_tick(const dom_game_runtime *rt) {
    return rt ? rt->cosmo_last_arrival_tick : 0ull;
}

int dom_game_runtime_pump(dom_game_runtime *rt) {
    dom::DomSession *session;
    dom::DomGameNet *net;
    const dom::InstanceInfo *inst;
    d_world *w;
    d_sim_context *sim;

    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }

    session = session_of(rt);
    net = net_of(rt);
    inst = inst_of(rt);
    if (!session || !net || !inst) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (!session->is_initialized()) {
        return DOM_GAME_RUNTIME_OK;
    }
    w = session->world();
    sim = session->sim();
    if (!w || !sim) {
        return DOM_GAME_RUNTIME_ERR;
    }

    net->pump(w, sim, *inst);
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_step(dom_game_runtime *rt) {
    dom::DomSession *session;
    d_world *w;
    d_sim_context *sim;
    int rc;

    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }

    session = session_of(rt);
    if (!session || !session->is_initialized()) {
        return DOM_GAME_RUNTIME_OK;
    }
    w = session->world();
    sim = session->sim();
    if (!w || !sim) {
        return DOM_GAME_RUNTIME_ERR;
    }

    rc = inject_replay(rt, sim);
    if (rc != DOM_GAME_RUNTIME_OK) {
        return rc;
    }

    if (d_sim_step(sim, 1u) != 0) {
        return DOM_GAME_RUNTIME_ERR;
    }
    {
        int arrived = 0;
        (void)dom_cosmo_transit_tick(&rt->cosmo_transit,
                                     (u64)sim->tick_index,
                                     &arrived);
        if (arrived) {
            rt->cosmo_last_arrival_tick = dom_cosmo_transit_arrival_tick(&rt->cosmo_transit);
        }
    }

    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_tick_wall(dom_game_runtime *rt, u64 wall_dt_usec, u32 *out_ticks) {
    const u64 tick_us = (rt && rt->ups > 0u) ? (1000000ull / (u64)rt->ups) : 0ull;
    u32 stepped = 0u;
    int rc = DOM_GAME_RUNTIME_OK;

    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }

    if (tick_us == 0ull) {
        rc = dom_game_runtime_step(rt);
        if (rc == DOM_GAME_RUNTIME_OK || rc == DOM_GAME_RUNTIME_REPLAY_END) {
            stepped = 1u;
        }
        if (out_ticks) {
            *out_ticks = stepped;
        }
        return rc;
    }

    rt->wall_accum_us += wall_dt_usec;

    while (rt->wall_accum_us >= tick_us) {
        rc = dom_game_runtime_step(rt);
        if (rc == DOM_GAME_RUNTIME_ERR) {
            break;
        }
        rt->wall_accum_us -= tick_us;
        stepped += 1u;
        if (rc == DOM_GAME_RUNTIME_REPLAY_END) {
            break;
        }
    }

    if (out_ticks) {
        *out_ticks = stepped;
    }
    return rc;
}

int dom_game_runtime_execute(dom_game_runtime *rt, const dom_game_command *cmd, u32 *out_tick) {
    dom::DomGameNet *net;
    d_net_cmd net_cmd;
    u32 tick;

    if (!rt || !cmd) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (cmd->struct_size != sizeof(dom_game_command) ||
        cmd->struct_version != DOM_GAME_COMMAND_VERSION) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (cmd->schema_id == 0u || cmd->schema_ver == 0u) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (cmd->payload_size > 0u && !cmd->payload) {
        return DOM_GAME_RUNTIME_ERR;
    }

    net = net_of(rt);
    if (!net) {
        return DOM_GAME_RUNTIME_ERR;
    }

    tick = cmd->tick ? cmd->tick : dom_game_runtime_next_cmd_tick(rt);

    std::memset(&net_cmd, 0, sizeof(net_cmd));
    net_cmd.tick = tick;
    net_cmd.schema_id = cmd->schema_id;
    net_cmd.schema_ver = cmd->schema_ver;
    net_cmd.payload.ptr = (unsigned char *)cmd->payload;
    net_cmd.payload.len = cmd->payload_size;

    if (!net->submit_cmd(&net_cmd)) {
        return DOM_GAME_RUNTIME_ERR;
    }

    if (out_tick) {
        *out_tick = tick;
    }
    return DOM_GAME_RUNTIME_OK;
}

u64 dom_game_runtime_get_tick(const dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    const d_sim_context *sim = session ? session->sim() : 0;
    return sim ? (u64)sim->tick_index : 0ull;
}

u64 dom_game_runtime_get_seed(const dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    const dom::InstanceInfo *inst = inst_of(rt);
    return compute_seed(session, inst);
}

u32 dom_game_runtime_get_ups(const dom_game_runtime *rt) {
    return rt ? rt->ups : 0u;
}

u64 dom_game_runtime_get_hash(const dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    const d_world *w = session ? session->world() : 0;
    return (u64)dom_game_hash_world(w);
}

u64 dom_game_runtime_get_run_id(const dom_game_runtime *rt) {
    return rt ? rt->run_id : 0ull;
}

const unsigned char *dom_game_runtime_get_manifest_hash(const dom_game_runtime *rt, u32 *out_len) {
    if (out_len) {
        *out_len = 0u;
    }
    if (!rt || rt->manifest_hash_bytes.empty()) {
        return (const unsigned char *)0;
    }
    if (out_len) {
        *out_len = (u32)rt->manifest_hash_bytes.size();
    }
    return &rt->manifest_hash_bytes[0];
}

int dom_game_runtime_get_counts(const dom_game_runtime *rt, dom_game_counts *out_counts) {
    dom::DomSession *session;
    d_world *w;

    if (!rt || !out_counts) {
        return DOM_GAME_RUNTIME_ERR;
    }

    out_counts->struct_size = sizeof(dom_game_counts);
    out_counts->struct_version = DOM_GAME_QUERY_VERSION;

    session = session_of(rt);
    w = session ? session->world() : 0;
    if (!w) {
        out_counts->entity_count = 0u;
        out_counts->construction_count = 0u;
        return DOM_GAME_RUNTIME_ERR;
    }

    out_counts->entity_count = d_agent_count(w);
    out_counts->construction_count = d_struct_count(w);
    return DOM_GAME_RUNTIME_OK;
}

u32 dom_game_runtime_input_delay(const dom_game_runtime *rt) {
    if (!rt || !rt->net) {
        return 1u;
    }
    return static_cast<const dom::DomGameNet *>(rt->net)->input_delay_ticks();
}

u32 dom_game_runtime_next_cmd_tick(const dom_game_runtime *rt) {
    const u64 now = dom_game_runtime_get_tick(rt);
    u32 delay = dom_game_runtime_input_delay(rt);
    if (delay < 1u) {
        delay = 1u;
    }
    return (u32)now + delay;
}

struct d_world *dom_game_runtime_world(dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    return session ? session->world() : 0;
}

struct d_sim_context *dom_game_runtime_sim(dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    return session ? session->sim() : 0;
}

struct d_replay_context *dom_game_runtime_replay(dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    return session ? session->replay() : 0;
}

const void *dom_game_runtime_session(const dom_game_runtime *rt) {
    return rt ? rt->session : 0;
}

const void *dom_game_runtime_instance(const dom_game_runtime *rt) {
    return rt ? rt->instance : 0;
}

const void *dom_game_runtime_cosmo_graph(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(&rt->cosmo_graph) : 0;
}
