/*
FILE: source/tests/dom_construction_replay_test.cpp
MODULE: Repository Tests
PURPOSE: Ensures construction placement/removal replay determinism.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
}

#include "dom_session.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_game_net.h"
#include "dominium/core_tlv.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_replay.h"
#include "runtime/dom_lane_scheduler.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_construction_registry.h"

extern "C" {
#include "net/d_net_schema.h"
#include "net/d_net_proto.h"
}

namespace {

static void init_paths(dom::Paths &paths) {
    paths.root = ".";
    paths.products = ".";
    paths.mods = ".";
    paths.packs = ".";
    paths.instances = ".";
    paths.temp = ".";
}

static void init_instance(dom::InstanceInfo &inst) {
    inst.id = "test_instance";
    inst.world_seed = 123u;
    inst.world_size_m = 1024u;
    inst.vertical_min_m = -64;
    inst.vertical_max_m = 64;
    inst.suite_version = 1u;
    inst.core_version = 1u;
    inst.packs.clear();
    inst.mods.clear();
}

static void append_u32(std::vector<unsigned char> &out, u32 v) {
    out.push_back((unsigned char)(v & 0xffu));
    out.push_back((unsigned char)((v >> 8u) & 0xffu));
    out.push_back((unsigned char)((v >> 16u) & 0xffu));
    out.push_back((unsigned char)((v >> 24u) & 0xffu));
}

static void append_u64(std::vector<unsigned char> &out, u64 v) {
    append_u32(out, (u32)(v & 0xffffffffu));
    append_u32(out, (u32)((v >> 32u) & 0xffffffffu));
}

static void append_tlv_u32(std::vector<unsigned char> &out, u32 tag, u32 v) {
    append_u32(out, tag);
    append_u32(out, 4u);
    append_u32(out, v);
}

static void append_tlv_u64(std::vector<unsigned char> &out, u32 tag, u64 v) {
    append_u32(out, tag);
    append_u32(out, 8u);
    append_u64(out, v);
}

static void append_tlv_q16(std::vector<unsigned char> &out, u32 tag, q16_16 v) {
    append_u32(out, tag);
    append_u32(out, 4u);
    append_u32(out, (u32)v);
}

static void build_place_payload(std::vector<unsigned char> &out,
                                u32 type_id,
                                u64 body_id,
                                q16_16 lat_turns,
                                q16_16 lon_turns,
                                u32 orientation) {
    out.clear();
    append_tlv_u32(out, D_NET_TLV_CONSTRUCTION_TYPE_ID, type_id);
    append_tlv_u64(out, D_NET_TLV_CONSTRUCTION_BODY_ID, body_id);
    append_tlv_q16(out, D_NET_TLV_CONSTRUCTION_LAT_TURNS, lat_turns);
    append_tlv_q16(out, D_NET_TLV_CONSTRUCTION_LON_TURNS, lon_turns);
    append_tlv_u32(out, D_NET_TLV_CONSTRUCTION_ORIENT, orientation);
}

static void build_remove_payload(std::vector<unsigned char> &out, u64 instance_id) {
    out.clear();
    append_tlv_u64(out, D_NET_TLV_CONSTRUCTION_INSTANCE_ID, instance_id);
}

static bool encode_cmd_packet(u32 schema_id,
                              const std::vector<unsigned char> &payload,
                              u32 tick,
                              std::vector<unsigned char> &out_packet) {
    unsigned char tmp[2048];
    d_net_cmd cmd;
    u32 out_size = 0u;
    int rc;

    std::memset(&cmd, 0, sizeof(cmd));
    cmd.id = 1u;
    cmd.source_peer = 1u;
    cmd.tick = tick;
    cmd.schema_id = schema_id;
    cmd.schema_ver = 1u;
    cmd.payload.ptr = payload.empty() ? (unsigned char *)0 : (unsigned char *)&payload[0];
    cmd.payload.len = (u32)payload.size();

    rc = d_net_encode_cmd(&cmd, tmp, (u32)sizeof(tmp), &out_size);
    if (rc != 0 || out_size == 0u) {
        return false;
    }
    out_packet.assign(tmp, tmp + out_size);
    return true;
}

static u64 registry_hash(dom_construction_registry *registry) {
    std::vector<unsigned char> bytes;
    u32 count = 0u;
    int rc = dom_construction_list(registry, 0, 0u, &count);
    if (rc != DOM_CONSTRUCTION_OK) {
        return 0ull;
    }
    append_u32(bytes, count);
    if (count == 0u) {
        return 0ull;
    }
    {
        std::vector<dom_construction_instance> list;
        list.resize(count);
        rc = dom_construction_list(registry, &list[0], count, &count);
        if (rc != DOM_CONSTRUCTION_OK) {
            return 0ull;
        }
        if (list.size() != count) {
            list.resize(count);
        }
        for (u32 i = 0u; i < count; ++i) {
            const dom_construction_instance &inst = list[i];
            append_u64(bytes, inst.instance_id);
            append_u32(bytes, inst.type_id);
            append_u32(bytes, inst.orientation);
            append_u64(bytes, inst.body_id);
            append_u32(bytes, (u32)inst.chunk_key.step_turns_q16);
            append_u32(bytes, (u32)inst.chunk_key.lat_index);
            append_u32(bytes, (u32)inst.chunk_key.lon_index);
            append_u64(bytes, (u64)(i64)inst.local_pos_m[0]);
            append_u64(bytes, (u64)(i64)inst.local_pos_m[1]);
            append_u64(bytes, (u64)(i64)inst.local_pos_m[2]);
            append_u32(bytes, (u32)inst.cell_x);
            append_u32(bytes, (u32)inst.cell_y);
        }
    }
    return dom::core_tlv::tlv_fnv1a64(&bytes[0], bytes.size());
}

struct TestRuntime {
    dom::Paths paths;
    dom::InstanceInfo inst;
    dom::SessionConfig cfg;
    dom::DomSession session;
    dom::DomGameNet net;
    dom_game_runtime *rt;

    TestRuntime() : rt(0) {}
};

static bool setup_runtime(TestRuntime &tr) {
    dom_game_runtime_init_desc desc;
    dom_lane_scheduler *sched = 0;
    dom_body_registry *bodies = 0;
    dom_body_id earth_id = 0ull;
    dom_body_info earth_info;
    dom_lane_vessel_desc vdesc;
    dom_activation_bubble bubble;
    int bubble_active = 0;

    init_paths(tr.paths);
    init_instance(tr.inst);

    tr.cfg.platform_backend = "null";
    tr.cfg.gfx_backend = "null";
    tr.cfg.audio_backend = "null";
    tr.cfg.headless = true;
    tr.cfg.tui = false;
    tr.cfg.allow_missing_content = true;

    if (!tr.session.init(tr.paths, tr.inst, tr.cfg)) {
        return false;
    }

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_GAME_RUNTIME_INIT_DESC_VERSION;
    desc.session = &tr.session;
    desc.net = &tr.net;
    desc.instance = &tr.inst;
    desc.ups = 60u;
    desc.run_id = 1u;

    tr.rt = dom_game_runtime_create(&desc);
    if (!tr.rt) {
        return false;
    }

    sched = (dom_lane_scheduler *)dom_game_runtime_lane_scheduler(tr.rt);
    bodies = (dom_body_registry *)dom_game_runtime_body_registry(tr.rt);
    if (!sched || !bodies) {
        return false;
    }
    if (dom_id_hash64("earth", 5u, &earth_id) != DOM_SPACETIME_OK) {
        return false;
    }
    if (dom_body_registry_get(bodies, earth_id, &earth_info) != DOM_BODY_REGISTRY_OK) {
        return false;
    }

    std::memset(&vdesc, 0, sizeof(vdesc));
    vdesc.vessel_id = 1ull;
    vdesc.lane_type = DOM_LANE_ORBITAL;
    vdesc.orbit.primary_body_id = earth_id;
    vdesc.orbit.semi_major_axis_m = d_q48_16_add(earth_info.radius_m,
                                                 d_q48_16_from_int(100));
    vdesc.orbit.ups = 60u;
    if (dom_lane_scheduler_register_vessel(sched, &vdesc) != DOM_LANE_OK) {
        return false;
    }
    if (dom_lane_scheduler_set_active_vessel(sched, vdesc.vessel_id) != DOM_LANE_OK) {
        return false;
    }
    if (dom_lane_scheduler_update(sched, tr.rt, 0u) != DOM_LANE_OK) {
        return false;
    }
    if (dom_lane_scheduler_get_bubble(sched, &bubble, &bubble_active, 0, 0) != DOM_LANE_OK) {
        return false;
    }
    if (!bubble_active) {
        return false;
    }
    return true;
}

static void teardown_runtime(TestRuntime &tr) {
    if (tr.rt) {
        dom_game_runtime_destroy(tr.rt);
        tr.rt = 0;
    }
    tr.session.shutdown();
}

static u64 run_replay_and_hash(dom_game_replay_play *playback) {
    TestRuntime tr;
    dom_construction_registry *registry = 0;
    std::vector<dom_construction_instance> list;
    u32 count = 0u;
    u64 hash = 0ull;

    if (!setup_runtime(tr)) {
        teardown_runtime(tr);
        return 0ull;
    }
    (void)dom_game_runtime_set_replay_playback(tr.rt, playback);
    (void)dom_game_runtime_set_replay_last_tick(tr.rt, 6u);
    for (u32 i = 0u; i < 6u; ++i) {
        (void)dom_game_runtime_step(tr.rt);
    }

    registry = (dom_construction_registry *)dom_game_runtime_construction_registry(tr.rt);
    if (!registry) {
        teardown_runtime(tr);
        return 0ull;
    }
    if (dom_construction_list(registry, 0, 0u, &count) != DOM_CONSTRUCTION_OK) {
        teardown_runtime(tr);
        return 0ull;
    }
    list.resize(count);
    if (count > 0u) {
        if (dom_construction_list(registry, &list[0], count, &count) != DOM_CONSTRUCTION_OK) {
            teardown_runtime(tr);
            return 0ull;
        }
        if (list.size() != count) {
            list.resize(count);
        }
    }
    assert(count == 1u);
    assert(list[0].instance_id == 2ull);
    hash = registry_hash(registry);

    teardown_runtime(tr);
    return hash;
}

} // namespace

namespace dom {

DomGameNet::DomGameNet()
    : m_local_peer(1u),
      m_cmd_seq(1u),
      m_ready(true),
      m_dedicated(false),
      m_handshake_sent(true),
      m_impl(0),
      m_hash_events(),
      m_qos_events() {
    std::memset(&m_session, 0, sizeof(m_session));
}

DomGameNet::~DomGameNet() {
    shutdown();
}

bool DomGameNet::init_single(u32 tick_rate) {
    (void)tick_rate;
    m_ready = true;
    return true;
}

bool DomGameNet::init_listen(u32 tick_rate, unsigned port) {
    (void)tick_rate;
    (void)port;
    m_ready = true;
    return true;
}

bool DomGameNet::init_dedicated(u32 tick_rate, unsigned port) {
    (void)tick_rate;
    (void)port;
    m_ready = true;
    return true;
}

bool DomGameNet::init_client(u32 tick_rate, const std::string &addr_port) {
    (void)tick_rate;
    (void)addr_port;
    m_ready = true;
    return true;
}

void DomGameNet::shutdown() {
    m_ready = false;
    m_hash_events.clear();
    m_qos_events.clear();
}

void DomGameNet::pump(d_world *world, d_sim_context *sim, const InstanceInfo &inst) {
    (void)world;
    (void)sim;
    (void)inst;
}

bool DomGameNet::submit_cmd(d_net_cmd *in_out_cmd) {
    (void)in_out_cmd;
    return true;
}

bool DomGameNet::poll_hash(d_net_hash *out_hash) {
    (void)out_hash;
    return false;
}

bool DomGameNet::poll_qos(d_peer_id *out_peer, std::vector<unsigned char> &out_bytes) {
    (void)out_peer;
    out_bytes.clear();
    return false;
}

} // namespace dom

int main(void) {
    const char *path = "tmp_construction_replay.dmrp";
    dom_game_replay_record *rec = 0;
    dom_game_replay_play *play_a = 0;
    dom_game_replay_play *play_b = 0;
    dom_game_replay_desc desc;
    std::vector<unsigned char> payload;
    std::vector<unsigned char> packet;
    u64 hash_a = 0ull;
    u64 hash_b = 0ull;
    dom_body_id earth_id = 0ull;

    d_net_register_schemas();
    assert(dom_id_hash64("earth", 5u, &earth_id) == DOM_SPACETIME_OK);

    rec = dom_game_replay_record_open(path, 60u, 1ull, "inst", 1ull,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u,
                                      (const unsigned char *)0, 0u);
    assert(rec);

    build_place_payload(payload,
                        DOM_CONSTRUCTION_TYPE_HABITAT,
                        earth_id,
                        0,
                        0,
                        0u);
    assert(encode_cmd_packet(D_NET_SCHEMA_CMD_CONSTRUCTION_PLACE_V1, payload, 2u, packet));
    assert(dom_game_replay_record_write_cmd(rec, 2u, &packet[0], (u32)packet.size())
           == DOM_GAME_REPLAY_OK);

    build_place_payload(payload,
                        DOM_CONSTRUCTION_TYPE_STORAGE,
                        earth_id,
                        0,
                        (q16_16)0x0100,
                        1u);
    assert(encode_cmd_packet(D_NET_SCHEMA_CMD_CONSTRUCTION_PLACE_V1, payload, 3u, packet));
    assert(dom_game_replay_record_write_cmd(rec, 3u, &packet[0], (u32)packet.size())
           == DOM_GAME_REPLAY_OK);

    build_remove_payload(payload, 1ull);
    assert(encode_cmd_packet(D_NET_SCHEMA_CMD_CONSTRUCTION_REMOVE_V1, payload, 4u, packet));
    assert(dom_game_replay_record_write_cmd(rec, 4u, &packet[0], (u32)packet.size())
           == DOM_GAME_REPLAY_OK);

    dom_game_replay_record_close(rec);

    std::memset(&desc, 0, sizeof(desc));
    play_a = dom_game_replay_play_open(path, &desc);
    assert(play_a);
    play_b = dom_game_replay_play_open(path, &desc);
    assert(play_b);

    hash_a = run_replay_and_hash(play_a);
    hash_b = run_replay_and_hash(play_b);
    assert(hash_a != 0ull);
    assert(hash_a == hash_b);

    dom_game_replay_play_close(play_b);
    dom_game_replay_play_close(play_a);
    std::remove(path);

    std::printf("dom_construction_replay_test: OK\n");
    return 0;
}
