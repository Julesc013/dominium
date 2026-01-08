/*
FILE: source/tests/dom_construction_save_load_roundtrip_test.cpp
MODULE: Repository
PURPOSE: Ensures construction registry round-trips through DMSG save/load.
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
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_save.h"
#include "runtime/dom_construction_registry.h"
#include "runtime/dom_io_guard.h"

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
    return tr.rt != 0;
}

static void teardown_runtime(TestRuntime &tr) {
    if (tr.rt) {
        dom_game_runtime_destroy(tr.rt);
        tr.rt = 0;
    }
    tr.session.shutdown();
}

static bool collect_list(dom_construction_registry *registry,
                         std::vector<dom_construction_instance> &out) {
    u32 count = 0u;
    int rc = dom_construction_list(registry, 0, 0u, &count);
    if (rc != DOM_CONSTRUCTION_OK) {
        return false;
    }
    out.clear();
    if (count == 0u) {
        return true;
    }
    out.resize(count);
    rc = dom_construction_list(registry, &out[0], count, &count);
    if (rc != DOM_CONSTRUCTION_OK) {
        return false;
    }
    if (out.size() != count) {
        out.resize(count);
    }
    return true;
}

static void compare_lists(const std::vector<dom_construction_instance> &a,
                          const std::vector<dom_construction_instance> &b) {
    assert(a.size() == b.size());
    for (size_t i = 0u; i < a.size(); ++i) {
        assert(a[i].instance_id == b[i].instance_id);
        assert(a[i].type_id == b[i].type_id);
        assert(a[i].body_id == b[i].body_id);
        assert(a[i].chunk_key.body_id == b[i].chunk_key.body_id);
        assert(a[i].chunk_key.step_turns_q16 == b[i].chunk_key.step_turns_q16);
        assert(a[i].chunk_key.lat_index == b[i].chunk_key.lat_index);
        assert(a[i].chunk_key.lon_index == b[i].chunk_key.lon_index);
        assert(a[i].local_pos_m[0] == b[i].local_pos_m[0]);
        assert(a[i].local_pos_m[1] == b[i].local_pos_m[1]);
        assert(a[i].local_pos_m[2] == b[i].local_pos_m[2]);
        assert(a[i].orientation == b[i].orientation);
        assert(a[i].cell_x == b[i].cell_x);
        assert(a[i].cell_y == b[i].cell_y);
    }
}

int main(void) {
    const char *path = "tmp_construction_save.dmsg";
    TestRuntime a;
    TestRuntime b;
    dom_construction_registry *reg_a = 0;
    dom_construction_registry *reg_b = 0;
    dom_body_id earth_id = 0ull;
    dom_construction_instance inst;
    std::vector<dom_construction_instance> list_a;
    std::vector<dom_construction_instance> list_b;
    int rc;

    assert(setup_runtime(a));
    assert(setup_runtime(b));

    rc = dom_id_hash64("earth", 5u, &earth_id);
    assert(rc == DOM_SPACETIME_OK);

    reg_a = (dom_construction_registry *)dom_game_runtime_construction_registry(a.rt);
    reg_b = (dom_construction_registry *)dom_game_runtime_construction_registry(b.rt);
    assert(reg_a != 0);
    assert(reg_b != 0);

    std::memset(&inst, 0, sizeof(inst));
    inst.instance_id = 1ull;
    inst.type_id = DOM_CONSTRUCTION_TYPE_HABITAT;
    inst.body_id = earth_id;
    inst.chunk_key.body_id = earth_id;
    inst.chunk_key.step_turns_q16 = 0x0100;
    inst.chunk_key.lat_index = 0;
    inst.chunk_key.lon_index = 0;
    inst.local_pos_m[0] = d_q48_16_from_int(1);
    inst.local_pos_m[1] = d_q48_16_from_int(0);
    inst.local_pos_m[2] = d_q48_16_from_int(0);
    inst.orientation = 0u;
    inst.cell_x = 1;
    inst.cell_y = 0;
    rc = dom_construction_register_instance(reg_a, &inst, 0);
    assert(rc == DOM_CONSTRUCTION_OK);

    inst.instance_id = 2ull;
    inst.type_id = DOM_CONSTRUCTION_TYPE_STORAGE;
    inst.chunk_key.lat_index = 1;
    inst.local_pos_m[0] = d_q48_16_from_int(0);
    inst.local_pos_m[1] = d_q48_16_from_int(2);
    inst.cell_x = 0;
    inst.cell_y = 2;
    rc = dom_construction_register_instance(reg_a, &inst, 0);
    assert(rc == DOM_CONSTRUCTION_OK);

    assert(collect_list(reg_a, list_a));

    dom_io_guard_reset();
    rc = dom_game_runtime_save(a.rt, path);
    assert(rc == DOM_GAME_SAVE_OK);

    rc = dom_game_runtime_load_save(b.rt, path);
    assert(rc == DOM_GAME_SAVE_OK);

    assert(collect_list(reg_b, list_b));
    compare_lists(list_a, list_b);

    teardown_runtime(b);
    teardown_runtime(a);
    std::remove(path);

    std::printf("dom_construction_save_load_roundtrip_test: OK\n");
    return 0;
}
