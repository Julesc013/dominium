/*
FILE: source/dominium/game/runtime/dom_game_net_driver.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_net_driver
RESPONSIBILITY: Implements net driver adapters for lockstep and server-auth modes.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Network drivers must not mutate authoritative state outside the runtime tick pipeline.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_net_driver.h"

#include <cstdio>
#include <cstring>

#include "dom_paths.h"
#include "dom_game_net.h"
#include "dom_instance.h"
#include "dominium/core_tlv.h"
#include "runtime/dom_game_net_snapshot.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_qos.h"
#include "runtime/dom_io_guard.h"

extern "C" {
#include "domino/sys.h"
#include "net/d_net_cmd.h"
#include "net/d_net_transport.h"
}

namespace dom {

DomNetDriverContext::DomNetDriverContext()
    : net(0),
      runtime(0),
      instance(0),
      paths(0) {
}

DomNetDriver::DomNetDriver(const DomSessionConfig &cfg, const DomNetDriverContext &ctx)
    : m_role(cfg.role),
      m_authority(cfg.authority),
      m_cfg(cfg),
      m_ctx(ctx) {
}

DomNetDriver::~DomNetDriver() {
}

int DomNetDriver::submit_local_command(const dom_game_command *cmd, u32 *out_tick) {
    if (!m_ctx.runtime || !cmd) {
        return DOM_NET_DRIVER_ERR;
    }
    if (dom_game_runtime_execute(m_ctx.runtime, cmd, out_tick) != DOM_GAME_RUNTIME_OK) {
        return DOM_NET_DRIVER_ERR;
    }
    return DOM_NET_DRIVER_OK;
}

int DomNetDriver::poll_snapshot(std::vector<unsigned char> &out_bytes) {
    (void)out_bytes;
    return DOM_NET_DRIVER_NOT_IMPLEMENTED;
}

int DomNetDriver::consume_snapshot(const unsigned char *data, size_t len) {
    (void)data;
    (void)len;
    return DOM_NET_DRIVER_NOT_IMPLEMENTED;
}

int DomNetDriver::get_last_snapshot(dom_game_net_snapshot_desc *out_desc) {
    (void)out_desc;
    return DOM_NET_DRIVER_NO_DATA;
}

int DomNetDriver::submit_tick_hash(u64 tick, u64 hash) {
    (void)tick;
    (void)hash;
    return DOM_NET_DRIVER_NOT_IMPLEMENTED;
}

int DomNetDriver::poll_peer_hash(u64 *out_tick, u64 *out_hash) {
    (void)out_tick;
    (void)out_hash;
    return DOM_NET_DRIVER_NOT_IMPLEMENTED;
}

namespace {

static bool ensure_runtime_ready(const DomNetDriverContext &ctx) {
    if (!ctx.runtime || !ctx.instance) {
        return false;
    }
    if (!dom_game_runtime_world(ctx.runtime) || !dom_game_runtime_sim(ctx.runtime)) {
        return false;
    }
    return true;
}

static std::string make_connect_addr(const DomSessionConfig &cfg) {
    if (cfg.connect_addr.empty()) {
        return std::string();
    }
    if (cfg.connect_addr.find(':') != std::string::npos) {
        return cfg.connect_addr;
    }
    {
        char buf[32];
        std::snprintf(buf, sizeof(buf), ":%u", (unsigned)cfg.net_port);
        return cfg.connect_addr + buf;
    }
}

static bool qos_policy_equal(const dom_qos_policy &a, const dom_qos_policy &b) {
    return a.snapshot_hz == b.snapshot_hz &&
           a.delta_detail == b.delta_detail &&
           a.interest_radius_m == b.interest_radius_m &&
           a.recommended_profile == b.recommended_profile &&
           a.server_load_hint == b.server_load_hint &&
           a.assist_flags == b.assist_flags;
}

static void qos_default_policy(u32 tick_rate_hz, dom_qos_policy &out) {
    std::memset(&out, 0, sizeof(out));
    out.snapshot_hz = (tick_rate_hz > 0u) ? tick_rate_hz : 60u;
    out.delta_detail = 100u;
    out.interest_radius_m = 1024u;
    out.recommended_profile = 0u;
    out.server_load_hint = DOM_QOS_SERVER_LOAD_NOMINAL;
    out.assist_flags = DOM_QOS_ASSIST_LOCAL_MESH | DOM_QOS_ASSIST_LOCAL_CACHE;
}

static u32 qos_stride_from_rate_hz(u32 tick_rate_hz, u32 cadence_hz) {
    if (cadence_hz == 0u) {
        return 0u;
    }
    if (tick_rate_hz == 0u) {
        return 1u;
    }
    if (cadence_hz >= tick_rate_hz) {
        return 1u;
    }
    {
        u32 stride = tick_rate_hz / cadence_hz;
        return (stride > 0u) ? stride : 1u;
    }
}

enum {
    DOM_GAME_DESYNC_TLV_VERSION = 1u,
    DOM_GAME_DESYNC_TLV_TAG_TICK = 2u,
    DOM_GAME_DESYNC_TLV_TAG_LOCAL_HASH = 3u,
    DOM_GAME_DESYNC_TLV_TAG_PEER_HASH = 4u
};

static bool write_desync_bundle(const DomGamePaths &paths,
                                u64 tick,
                                u64 local_hash,
                                u64 peer_hash) {
    if (paths.run_root.empty()) {
        return false;
    }

    core_tlv::TlvWriter w;
    w.add_u32(core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_GAME_DESYNC_TLV_VERSION);
    w.add_u64(DOM_GAME_DESYNC_TLV_TAG_TICK, tick);
    w.add_u64(DOM_GAME_DESYNC_TLV_TAG_LOCAL_HASH, local_hash);
    w.add_u64(DOM_GAME_DESYNC_TLV_TAG_PEER_HASH, peer_hash);

    {
        char name[64];
        const std::vector<unsigned char> &bytes = w.bytes();
        std::snprintf(name, sizeof(name), "desync_bundle_%llu.tlv", (unsigned long long)tick);
        const std::string path = join(paths.run_root, name);
        if (!dom_io_guard_io_allowed()) {
            dom_io_guard_note_violation("desync_bundle_write", path.c_str());
            return false;
        }
        void *fh = dsys_file_open(path.c_str(), "wb");
        size_t wrote = 0u;
        if (!fh) {
            return false;
        }
        if (!bytes.empty()) {
            wrote = dsys_file_write(fh, &bytes[0], bytes.size());
        }
        dsys_file_close(fh);
        return wrote == bytes.size();
    }
}

} // namespace

class DomNetDriverServerAuth : public DomNetDriver {
public:
    DomNetDriverServerAuth(const DomSessionConfig &cfg, const DomNetDriverContext &ctx)
        : DomNetDriver(cfg, ctx),
          m_default_policy(),
          m_effective_policy(),
          m_client_state(),
          m_client_status(),
          m_client_hello_sent(false),
          m_last_status_tick(0u),
          m_last_snapshot_tick(0u),
          m_snapshot_stride(1u),
          m_peer_qos(),
          m_last_snapshot(),
          m_has_snapshot(false) {
        std::memset(&m_default_policy, 0, sizeof(m_default_policy));
        std::memset(&m_effective_policy, 0, sizeof(m_effective_policy));
        std::memset(&m_client_state, 0, sizeof(m_client_state));
        std::memset(&m_client_status, 0, sizeof(m_client_status));
    }

    int start() {
        if (!m_ctx.net) {
            return DOM_NET_DRIVER_ERR;
        }
        init_qos_defaults();
        if (m_role == DOM_SESSION_ROLE_SINGLE) {
            return DOM_NET_DRIVER_NOT_IMPLEMENTED;
        }
        if (m_role == DOM_SESSION_ROLE_HOST) {
            if (!m_ctx.net->init_listen(m_cfg.tick_rate_hz, m_cfg.net_port)) {
                return DOM_NET_DRIVER_ERR;
            }
        } else if (m_role == DOM_SESSION_ROLE_DEDICATED_SERVER) {
            if (!m_ctx.net->init_dedicated(m_cfg.tick_rate_hz, m_cfg.net_port)) {
                return DOM_NET_DRIVER_ERR;
            }
        } else if (m_role == DOM_SESSION_ROLE_CLIENT) {
            std::string addr = make_connect_addr(m_cfg);
            if (addr.empty() || !m_ctx.net->init_client(m_cfg.tick_rate_hz, addr)) {
                return DOM_NET_DRIVER_ERR;
            }
        } else {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->set_input_delay_ticks(m_cfg.input_delay_ticks);
        (void)d_net_cmd_queue_init();
        return DOM_NET_DRIVER_OK;
    }

    void stop() {
        if (m_ctx.net) {
            m_ctx.net->shutdown();
        }
        d_net_cmd_queue_shutdown();
        m_peer_qos.clear();
    }

    int pump_network() {
        if (!m_ctx.net || !ensure_runtime_ready(m_ctx)) {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->pump(dom_game_runtime_world(m_ctx.runtime),
                        dom_game_runtime_sim(m_ctx.runtime),
                        *m_ctx.instance);
        if (m_role == DOM_SESSION_ROLE_CLIENT) {
            handle_qos_client();
            maybe_send_client_hello();
            maybe_send_client_status();
        } else {
            handle_qos_server();
        }
        return DOM_NET_DRIVER_OK;
    }

    bool ready() const {
        return m_ctx.net ? m_ctx.net->ready() : false;
    }

    int poll_snapshot(std::vector<unsigned char> &out_bytes) {
        u64 tick = 0ull;
        if (m_role == DOM_SESSION_ROLE_CLIENT) {
            return DOM_NET_DRIVER_NO_DATA;
        }
        if (!m_ctx.runtime) {
            return DOM_NET_DRIVER_ERR;
        }
        if (m_snapshot_stride == 0u) {
            return DOM_NET_DRIVER_NO_DATA;
        }
        {
            tick = dom_game_runtime_get_tick(m_ctx.runtime);
            if (tick < (m_last_snapshot_tick + (u64)m_snapshot_stride)) {
                return DOM_NET_DRIVER_NO_DATA;
            }
        }
        {
            dom_game_net_snapshot_opts opts;
            std::memset(&opts, 0, sizeof(opts));
            opts.struct_size = sizeof(opts);
            opts.struct_version = DOM_GAME_NET_SNAPSHOT_OPTS_VERSION;
            opts.detail_level = m_effective_policy.delta_detail;
            opts.interest_radius_m = m_effective_policy.interest_radius_m;
            opts.assist_flags = 0u;
            if ((m_effective_policy.assist_flags & DOM_QOS_ASSIST_LOCAL_MESH) != 0u) {
                opts.assist_flags |= DOM_NET_SNAPSHOT_ASSIST_LOCAL_MESH;
            }
            if ((m_effective_policy.assist_flags & DOM_QOS_ASSIST_LOCAL_CACHE) != 0u) {
                opts.assist_flags |= DOM_NET_SNAPSHOT_ASSIST_LOCAL_CACHE;
            }
            if (dom_game_net_snapshot_build(m_ctx.runtime, &opts, out_bytes) == DOM_NET_SNAPSHOT_OK) {
                m_last_snapshot_tick = tick;
                return DOM_NET_DRIVER_OK;
            }
        }
        return DOM_NET_DRIVER_ERR;
    }

    int consume_snapshot(const unsigned char *data, size_t len) {
        dom_game_net_snapshot_desc desc;
        if (!data || len == 0u) {
            return DOM_NET_DRIVER_ERR;
        }
        if (dom_game_net_snapshot_parse(data, len, &desc) != DOM_NET_SNAPSHOT_OK) {
            return DOM_NET_DRIVER_ERR;
        }
        m_last_snapshot = desc;
        m_has_snapshot = true;
        return DOM_NET_DRIVER_OK;
    }

    int get_last_snapshot(dom_game_net_snapshot_desc *out_desc) {
        if (!out_desc) {
            return DOM_NET_DRIVER_ERR;
        }
        if (!m_has_snapshot) {
            return DOM_NET_DRIVER_NO_DATA;
        }
        *out_desc = m_last_snapshot;
        return DOM_NET_DRIVER_OK;
    }

private:
    struct PeerQos {
        d_peer_id peer;
        dom_qos_state state;
        dom_qos_policy last_sent;
        bool have_last_sent;
    };

    void init_qos_defaults() {
        qos_default_policy(m_cfg.tick_rate_hz, m_default_policy);
        m_effective_policy = m_default_policy;
        (void)dom_qos_init(&m_client_state, &m_default_policy);
        std::memset(&m_client_status, 0, sizeof(m_client_status));
        m_client_state.caps.perf_caps_digest64 = 0ull;
        m_client_state.caps.preferred_profile = 0u;
        m_client_state.caps.max_snapshot_hz = m_default_policy.snapshot_hz;
        m_client_state.caps.max_delta_detail = 100u;
        m_client_state.caps.max_interest_radius_m = 1024u;
        m_client_state.caps.diagnostic_rate_cap = 0u;
        m_client_state.caps.assist_flags = DOM_QOS_ASSIST_LOCAL_MESH | DOM_QOS_ASSIST_LOCAL_CACHE;
        m_client_status.render_fps_avg = 60u;
        m_client_status.frame_time_ms_avg = 16u;
        m_client_status.backlog_jobs = 0u;
        m_client_status.derived_queue_pressure = 0u;
        m_client_status.request_detail_reduction = 0u;
        m_client_hello_sent = false;
        m_last_status_tick = 0u;
        m_last_snapshot_tick = 0u;
        m_snapshot_stride = qos_stride_from_rate_hz(m_cfg.tick_rate_hz, m_effective_policy.snapshot_hz);
        m_peer_qos.clear();
    }

    PeerQos *find_peer(d_peer_id peer) {
        size_t i;
        for (i = 0u; i < m_peer_qos.size(); ++i) {
            if (m_peer_qos[i].peer == peer) {
                return &m_peer_qos[i];
            }
        }
        return 0;
    }

    PeerQos *ensure_peer(d_peer_id peer) {
        PeerQos *found = find_peer(peer);
        if (found) {
            return found;
        }
        {
            PeerQos entry;
            std::memset(&entry, 0, sizeof(entry));
            entry.peer = peer;
            entry.have_last_sent = false;
            (void)dom_qos_init(&entry.state, &m_default_policy);
            m_peer_qos.push_back(entry);
            return &m_peer_qos.back();
        }
    }

    void refresh_server_load_hint() {
        const size_t peers = m_peer_qos.size();
        u32 hint = DOM_QOS_SERVER_LOAD_NOMINAL;
        if (peers >= 8u) {
            hint = DOM_QOS_SERVER_LOAD_OVERLOADED;
        } else if (peers >= 4u) {
            hint = DOM_QOS_SERVER_LOAD_BUSY;
        }
        if (hint != m_default_policy.server_load_hint) {
            size_t i;
            m_default_policy.server_load_hint = hint;
            for (i = 0u; i < m_peer_qos.size(); ++i) {
                (void)dom_qos_apply_server_policy(&m_peer_qos[i].state, &m_default_policy);
            }
        }
    }

    void update_effective_policy() {
        size_t i;
        refresh_server_load_hint();
        dom_qos_policy combined = m_default_policy;
        for (i = 0u; i < m_peer_qos.size(); ++i) {
            dom_qos_policy peer_policy;
            if (dom_qos_get_effective_params(&m_peer_qos[i].state, &peer_policy) != DOM_QOS_OK) {
                continue;
            }
            if (peer_policy.snapshot_hz > 0u &&
                (combined.snapshot_hz == 0u || peer_policy.snapshot_hz < combined.snapshot_hz)) {
                combined.snapshot_hz = peer_policy.snapshot_hz;
            }
            if (peer_policy.delta_detail < combined.delta_detail) {
                combined.delta_detail = peer_policy.delta_detail;
            }
            if (peer_policy.interest_radius_m < combined.interest_radius_m) {
                combined.interest_radius_m = peer_policy.interest_radius_m;
            }
            combined.assist_flags &= peer_policy.assist_flags;
        }
        m_effective_policy = combined;
        m_snapshot_stride = qos_stride_from_rate_hz(m_cfg.tick_rate_hz, m_effective_policy.snapshot_hz);
    }

    void send_policy_if_needed(PeerQos &peer) {
        dom_qos_policy policy;
        if (dom_qos_get_effective_params(&peer.state, &policy) != DOM_QOS_OK) {
            return;
        }
        if (peer.have_last_sent && qos_policy_equal(peer.last_sent, policy)) {
            return;
        }
        {
            std::vector<unsigned char> bytes;
            if (dom_qos_build_server_policy(&policy, bytes) != DOM_QOS_OK || bytes.empty()) {
                return;
            }
            {
                d_net_qos q;
                q.data.ptr = &bytes[0];
                q.data.len = (u32)bytes.size();
                (void)d_net_send_qos(peer.peer, &q);
            }
            peer.last_sent = policy;
            peer.have_last_sent = true;
        }
    }

    void handle_qos_server() {
        d_peer_id peer = 0u;
        std::vector<unsigned char> bytes;
        while (m_ctx.net && m_ctx.net->poll_qos(&peer, bytes)) {
            dom_qos_message msg;
            if (bytes.empty()) {
                continue;
            }
            if (dom_qos_parse_message(&bytes[0], bytes.size(), &msg) != DOM_QOS_OK) {
                continue;
            }
            if (msg.kind == DOM_QOS_KIND_CLIENT_HELLO) {
                PeerQos *p = ensure_peer(peer);
                if (!p) {
                    continue;
                }
                (void)dom_qos_apply_client_caps(&p->state, &msg.caps);
                send_policy_if_needed(*p);
                update_effective_policy();
            } else if (msg.kind == DOM_QOS_KIND_CLIENT_STATUS) {
                PeerQos *p = ensure_peer(peer);
                if (!p) {
                    continue;
                }
                (void)dom_qos_apply_client_status(&p->state, &msg.status);
                send_policy_if_needed(*p);
                update_effective_policy();
            }
        }
    }

    void handle_qos_client() {
        d_peer_id peer = 0u;
        std::vector<unsigned char> bytes;
        while (m_ctx.net && m_ctx.net->poll_qos(&peer, bytes)) {
            dom_qos_message msg;
            if (bytes.empty()) {
                continue;
            }
            if (dom_qos_parse_message(&bytes[0], bytes.size(), &msg) != DOM_QOS_OK) {
                continue;
            }
            if (msg.kind == DOM_QOS_KIND_SERVER_POLICY) {
                (void)dom_qos_apply_server_policy(&m_client_state, &msg.policy);
                (void)dom_qos_get_effective_params(&m_client_state, &m_effective_policy);
                m_snapshot_stride = qos_stride_from_rate_hz(m_cfg.tick_rate_hz, m_effective_policy.snapshot_hz);
            }
        }
    }

    void maybe_send_client_hello() {
        if (m_client_hello_sent || !m_ctx.net || !m_ctx.net->ready()) {
            return;
        }
        {
            std::vector<unsigned char> bytes;
            if (dom_qos_build_client_hello(&m_client_state.caps, bytes) != DOM_QOS_OK ||
                bytes.empty()) {
                return;
            }
            {
                d_net_qos q;
                q.data.ptr = &bytes[0];
                q.data.len = (u32)bytes.size();
                if (d_net_send_qos(1u, &q) == 0) {
                    m_client_hello_sent = true;
                }
            }
        }
    }

    void maybe_send_client_status() {
        if (!m_client_hello_sent || !m_ctx.net || !m_ctx.net->ready()) {
            return;
        }
        {
            const u64 tick = m_ctx.runtime ? dom_game_runtime_get_tick(m_ctx.runtime) : 0ull;
            const u64 interval = (m_cfg.tick_rate_hz > 0u) ? m_cfg.tick_rate_hz : 60u;
            if (m_last_status_tick != 0u && tick < (m_last_status_tick + interval)) {
                return;
            }
            m_last_status_tick = tick;
        }
        {
            std::vector<unsigned char> bytes;
            if (dom_qos_build_client_status(&m_client_status, bytes) != DOM_QOS_OK ||
                bytes.empty()) {
                return;
            }
            d_net_qos q;
            q.data.ptr = &bytes[0];
            q.data.len = (u32)bytes.size();
            (void)d_net_send_qos(1u, &q);
        }
    }

    dom_qos_policy m_default_policy;
    dom_qos_policy m_effective_policy;
    dom_qos_state m_client_state;
    dom_qos_status m_client_status;
    bool m_client_hello_sent;
    u64 m_last_status_tick;
    u64 m_last_snapshot_tick;
    u32 m_snapshot_stride;
    std::vector<PeerQos> m_peer_qos;
    dom_game_net_snapshot_desc m_last_snapshot;
    bool m_has_snapshot;
};

class DomNetDriverLoopback : public DomNetDriver {
public:
    DomNetDriverLoopback(const DomSessionConfig &cfg, const DomNetDriverContext &ctx)
        : DomNetDriver(cfg, ctx),
          m_last_snapshot(),
          m_has_snapshot(false) {
    }

    int start() {
        if (!m_ctx.net || !ensure_runtime_ready(m_ctx)) {
            return DOM_NET_DRIVER_ERR;
        }
        if (!m_ctx.net->init_single(m_cfg.tick_rate_hz)) {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->set_input_delay_ticks(m_cfg.input_delay_ticks);
        (void)d_net_cmd_queue_init();
        return DOM_NET_DRIVER_OK;
    }

    void stop() {
        if (m_ctx.net) {
            m_ctx.net->shutdown();
        }
        d_net_cmd_queue_shutdown();
    }

    int pump_network() {
        std::vector<unsigned char> bytes;
        if (!m_ctx.net || !ensure_runtime_ready(m_ctx)) {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->pump(dom_game_runtime_world(m_ctx.runtime),
                        dom_game_runtime_sim(m_ctx.runtime),
                        *m_ctx.instance);
        if (poll_snapshot(bytes) == DOM_NET_DRIVER_OK && !bytes.empty()) {
            (void)consume_snapshot(&bytes[0], bytes.size());
        }
        return DOM_NET_DRIVER_OK;
    }

    bool ready() const {
        return m_ctx.net ? m_ctx.net->ready() : false;
    }

    int poll_snapshot(std::vector<unsigned char> &out_bytes) {
        if (!m_ctx.runtime) {
            return DOM_NET_DRIVER_ERR;
        }
        {
            dom_game_net_snapshot_opts opts;
            std::memset(&opts, 0, sizeof(opts));
            opts.struct_size = sizeof(opts);
            opts.struct_version = DOM_GAME_NET_SNAPSHOT_OPTS_VERSION;
            opts.detail_level = 100u;
            opts.interest_radius_m = 1024u;
            opts.assist_flags = 0u;
            return (dom_game_net_snapshot_build(m_ctx.runtime, &opts, out_bytes) == DOM_NET_SNAPSHOT_OK)
                       ? DOM_NET_DRIVER_OK
                       : DOM_NET_DRIVER_ERR;
        }
    }

    int consume_snapshot(const unsigned char *data, size_t len) {
        dom_game_net_snapshot_desc desc;
        if (!data || len == 0u) {
            return DOM_NET_DRIVER_ERR;
        }
        if (dom_game_net_snapshot_parse(data, len, &desc) != DOM_NET_SNAPSHOT_OK) {
            return DOM_NET_DRIVER_ERR;
        }
        m_last_snapshot = desc;
        m_has_snapshot = true;
        return DOM_NET_DRIVER_OK;
    }

    int get_last_snapshot(dom_game_net_snapshot_desc *out_desc) {
        if (!out_desc) {
            return DOM_NET_DRIVER_ERR;
        }
        if (!m_has_snapshot) {
            return DOM_NET_DRIVER_NO_DATA;
        }
        *out_desc = m_last_snapshot;
        return DOM_NET_DRIVER_OK;
    }

private:
    dom_game_net_snapshot_desc m_last_snapshot;
    bool m_has_snapshot;
};

class DomNetDriverLockstep : public DomNetDriver {
public:
    DomNetDriverLockstep(const DomSessionConfig &cfg, const DomNetDriverContext &ctx)
        : DomNetDriver(cfg, ctx),
          m_default_policy(),
          m_effective_policy(),
          m_client_state(),
          m_client_status(),
          m_client_hello_sent(false),
          m_last_status_tick(0u),
          m_last_hash_sent_tick(0u),
          m_hash_stride(1u),
          m_peer_qos(),
          m_desync_written(false) {
        std::memset(&m_default_policy, 0, sizeof(m_default_policy));
        std::memset(&m_effective_policy, 0, sizeof(m_effective_policy));
        std::memset(&m_client_state, 0, sizeof(m_client_state));
        std::memset(&m_client_status, 0, sizeof(m_client_status));
    }

    int start() {
        if (!m_ctx.net) {
            return DOM_NET_DRIVER_ERR;
        }
        init_qos_defaults();
        if (m_role == DOM_SESSION_ROLE_DEDICATED_SERVER) {
            return DOM_NET_DRIVER_ERR;
        }
        if (m_role == DOM_SESSION_ROLE_SINGLE) {
            return DOM_NET_DRIVER_NOT_IMPLEMENTED;
        }
        if (m_role == DOM_SESSION_ROLE_HOST) {
            if (!m_ctx.net->init_listen(m_cfg.tick_rate_hz, m_cfg.net_port)) {
                return DOM_NET_DRIVER_ERR;
            }
        } else if (m_role == DOM_SESSION_ROLE_CLIENT) {
            std::string addr = make_connect_addr(m_cfg);
            if (addr.empty() || !m_ctx.net->init_client(m_cfg.tick_rate_hz, addr)) {
                return DOM_NET_DRIVER_ERR;
            }
        } else {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->set_input_delay_ticks(m_cfg.input_delay_ticks);
        (void)d_net_cmd_queue_init();
        return DOM_NET_DRIVER_OK;
    }

    void stop() {
        if (m_ctx.net) {
            m_ctx.net->shutdown();
        }
        d_net_cmd_queue_shutdown();
        m_peer_qos.clear();
    }

    int pump_network() {
        if (!m_ctx.net || !ensure_runtime_ready(m_ctx)) {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->pump(dom_game_runtime_world(m_ctx.runtime),
                        dom_game_runtime_sim(m_ctx.runtime),
                        *m_ctx.instance);
        if (m_role == DOM_SESSION_ROLE_CLIENT) {
            handle_qos_client();
            maybe_send_client_hello();
            maybe_send_client_status();
        } else {
            handle_qos_server();
        }
        if (m_ctx.runtime) {
            u64 local_tick = dom_game_runtime_get_tick(m_ctx.runtime);
            u64 local_hash = dom_game_runtime_get_hash(m_ctx.runtime);
            u64 peer_tick = 0ull;
            u64 peer_hash = 0ull;
            while (poll_peer_hash(&peer_tick, &peer_hash) == DOM_NET_DRIVER_OK) {
                if (!m_desync_written &&
                    m_ctx.paths &&
                    peer_tick == local_tick &&
                    peer_hash != local_hash) {
                    (void)write_desync_bundle(*m_ctx.paths, local_tick, local_hash, peer_hash);
                    m_desync_written = true;
                }
            }
        }
        return DOM_NET_DRIVER_OK;
    }

    bool ready() const {
        return m_ctx.net ? m_ctx.net->ready() : false;
    }

    int submit_tick_hash(u64 tick, u64 hash) {
        d_net_hash h;
        const d_net_session &session = m_ctx.net->session();
        h.tick = (u32)tick;
        h.world_hash = hash;

        if (m_hash_stride == 0u) {
            return DOM_NET_DRIVER_OK;
        }
        if (m_last_hash_sent_tick != 0u &&
            tick < (m_last_hash_sent_tick + (u64)m_hash_stride)) {
            return DOM_NET_DRIVER_OK;
        }
        m_last_hash_sent_tick = tick;

        if (session.role == D_NET_ROLE_CLIENT) {
            return (d_net_send_hash(1u, &h) == 0) ? DOM_NET_DRIVER_OK : DOM_NET_DRIVER_ERR;
        }
        if (session.role == D_NET_ROLE_HOST) {
            u32 i;
            for (i = 0u; i < session.peer_count; ++i) {
                const d_net_peer &peer = session.peers[i];
                if (peer.id == m_ctx.net->local_peer()) {
                    continue;
                }
                (void)d_net_send_hash(peer.id, &h);
            }
            return DOM_NET_DRIVER_OK;
        }
        return DOM_NET_DRIVER_ERR;
    }

    int poll_peer_hash(u64 *out_tick, u64 *out_hash) {
        d_net_hash h;
        if (!out_tick || !out_hash) {
            return DOM_NET_DRIVER_ERR;
        }
        if (!m_ctx.net || !m_ctx.net->poll_hash(&h)) {
            return DOM_NET_DRIVER_NO_DATA;
        }
        *out_tick = (u64)h.tick;
        *out_hash = h.world_hash;
        return DOM_NET_DRIVER_OK;
    }

private:
    struct PeerQos {
        d_peer_id peer;
        dom_qos_state state;
        dom_qos_policy last_sent;
        bool have_last_sent;
    };

    void init_qos_defaults() {
        qos_default_policy(m_cfg.tick_rate_hz, m_default_policy);
        m_effective_policy = m_default_policy;
        (void)dom_qos_init(&m_client_state, &m_default_policy);
        std::memset(&m_client_status, 0, sizeof(m_client_status));
        m_client_state.caps.perf_caps_digest64 = 0ull;
        m_client_state.caps.preferred_profile = 0u;
        m_client_state.caps.max_snapshot_hz = 0u;
        m_client_state.caps.max_delta_detail = 100u;
        m_client_state.caps.max_interest_radius_m = 1024u;
        m_client_state.caps.diagnostic_rate_cap = m_default_policy.snapshot_hz;
        m_client_state.caps.assist_flags = DOM_QOS_ASSIST_LOCAL_MESH | DOM_QOS_ASSIST_LOCAL_CACHE;
        m_client_status.render_fps_avg = 60u;
        m_client_status.frame_time_ms_avg = 16u;
        m_client_status.backlog_jobs = 0u;
        m_client_status.derived_queue_pressure = 0u;
        m_client_status.request_detail_reduction = 0u;
        m_client_hello_sent = false;
        m_last_status_tick = 0u;
        m_last_hash_sent_tick = 0u;
        m_hash_stride = qos_stride_from_rate_hz(m_cfg.tick_rate_hz, m_effective_policy.snapshot_hz);
        m_peer_qos.clear();
    }

    PeerQos *find_peer(d_peer_id peer) {
        size_t i;
        for (i = 0u; i < m_peer_qos.size(); ++i) {
            if (m_peer_qos[i].peer == peer) {
                return &m_peer_qos[i];
            }
        }
        return 0;
    }

    PeerQos *ensure_peer(d_peer_id peer) {
        PeerQos *found = find_peer(peer);
        if (found) {
            return found;
        }
        {
            PeerQos entry;
            std::memset(&entry, 0, sizeof(entry));
            entry.peer = peer;
            entry.have_last_sent = false;
            (void)dom_qos_init(&entry.state, &m_default_policy);
            m_peer_qos.push_back(entry);
            return &m_peer_qos.back();
        }
    }

    void refresh_server_load_hint() {
        const size_t peers = m_peer_qos.size();
        u32 hint = DOM_QOS_SERVER_LOAD_NOMINAL;
        if (peers >= 8u) {
            hint = DOM_QOS_SERVER_LOAD_OVERLOADED;
        } else if (peers >= 4u) {
            hint = DOM_QOS_SERVER_LOAD_BUSY;
        }
        if (hint != m_default_policy.server_load_hint) {
            size_t i;
            m_default_policy.server_load_hint = hint;
            for (i = 0u; i < m_peer_qos.size(); ++i) {
                (void)dom_qos_apply_server_policy(&m_peer_qos[i].state, &m_default_policy);
            }
        }
    }

    void update_effective_policy() {
        size_t i;
        refresh_server_load_hint();
        dom_qos_policy combined = m_default_policy;
        for (i = 0u; i < m_peer_qos.size(); ++i) {
            dom_qos_policy peer_policy;
            if (dom_qos_get_effective_params(&m_peer_qos[i].state, &peer_policy) != DOM_QOS_OK) {
                continue;
            }
            if (peer_policy.snapshot_hz > 0u &&
                (combined.snapshot_hz == 0u || peer_policy.snapshot_hz < combined.snapshot_hz)) {
                combined.snapshot_hz = peer_policy.snapshot_hz;
            }
            if (peer_policy.delta_detail < combined.delta_detail) {
                combined.delta_detail = peer_policy.delta_detail;
            }
            if (peer_policy.interest_radius_m < combined.interest_radius_m) {
                combined.interest_radius_m = peer_policy.interest_radius_m;
            }
            combined.assist_flags &= peer_policy.assist_flags;
        }
        m_effective_policy = combined;
        m_hash_stride = qos_stride_from_rate_hz(m_cfg.tick_rate_hz, m_effective_policy.snapshot_hz);
    }

    void send_policy_if_needed(PeerQos &peer) {
        dom_qos_policy policy;
        if (dom_qos_get_effective_params(&peer.state, &policy) != DOM_QOS_OK) {
            return;
        }
        if (peer.have_last_sent && qos_policy_equal(peer.last_sent, policy)) {
            return;
        }
        {
            std::vector<unsigned char> bytes;
            if (dom_qos_build_server_policy(&policy, bytes) != DOM_QOS_OK || bytes.empty()) {
                return;
            }
            {
                d_net_qos q;
                q.data.ptr = &bytes[0];
                q.data.len = (u32)bytes.size();
                (void)d_net_send_qos(peer.peer, &q);
            }
            peer.last_sent = policy;
            peer.have_last_sent = true;
        }
    }

    void handle_qos_server() {
        d_peer_id peer = 0u;
        std::vector<unsigned char> bytes;
        while (m_ctx.net && m_ctx.net->poll_qos(&peer, bytes)) {
            dom_qos_message msg;
            if (bytes.empty()) {
                continue;
            }
            if (dom_qos_parse_message(&bytes[0], bytes.size(), &msg) != DOM_QOS_OK) {
                continue;
            }
            if (msg.kind == DOM_QOS_KIND_CLIENT_HELLO) {
                PeerQos *p = ensure_peer(peer);
                if (!p) {
                    continue;
                }
                (void)dom_qos_apply_client_caps(&p->state, &msg.caps);
                send_policy_if_needed(*p);
                update_effective_policy();
            } else if (msg.kind == DOM_QOS_KIND_CLIENT_STATUS) {
                PeerQos *p = ensure_peer(peer);
                if (!p) {
                    continue;
                }
                (void)dom_qos_apply_client_status(&p->state, &msg.status);
                send_policy_if_needed(*p);
                update_effective_policy();
            }
        }
    }

    void handle_qos_client() {
        d_peer_id peer = 0u;
        std::vector<unsigned char> bytes;
        while (m_ctx.net && m_ctx.net->poll_qos(&peer, bytes)) {
            dom_qos_message msg;
            if (bytes.empty()) {
                continue;
            }
            if (dom_qos_parse_message(&bytes[0], bytes.size(), &msg) != DOM_QOS_OK) {
                continue;
            }
            if (msg.kind == DOM_QOS_KIND_SERVER_POLICY) {
                (void)dom_qos_apply_server_policy(&m_client_state, &msg.policy);
                (void)dom_qos_get_effective_params(&m_client_state, &m_effective_policy);
                m_hash_stride = qos_stride_from_rate_hz(m_cfg.tick_rate_hz, m_effective_policy.snapshot_hz);
            }
        }
    }

    void maybe_send_client_hello() {
        if (m_client_hello_sent || !m_ctx.net || !m_ctx.net->ready()) {
            return;
        }
        {
            std::vector<unsigned char> bytes;
            if (dom_qos_build_client_hello(&m_client_state.caps, bytes) != DOM_QOS_OK ||
                bytes.empty()) {
                return;
            }
            {
                d_net_qos q;
                q.data.ptr = &bytes[0];
                q.data.len = (u32)bytes.size();
                if (d_net_send_qos(1u, &q) == 0) {
                    m_client_hello_sent = true;
                }
            }
        }
    }

    void maybe_send_client_status() {
        if (!m_client_hello_sent || !m_ctx.net || !m_ctx.net->ready()) {
            return;
        }
        {
            const u64 tick = m_ctx.runtime ? dom_game_runtime_get_tick(m_ctx.runtime) : 0ull;
            const u64 interval = (m_cfg.tick_rate_hz > 0u) ? m_cfg.tick_rate_hz : 60u;
            if (m_last_status_tick != 0u && tick < (m_last_status_tick + interval)) {
                return;
            }
            m_last_status_tick = tick;
        }
        {
            std::vector<unsigned char> bytes;
            if (dom_qos_build_client_status(&m_client_status, bytes) != DOM_QOS_OK ||
                bytes.empty()) {
                return;
            }
            d_net_qos q;
            q.data.ptr = &bytes[0];
            q.data.len = (u32)bytes.size();
            (void)d_net_send_qos(1u, &q);
        }
    }

    dom_qos_policy m_default_policy;
    dom_qos_policy m_effective_policy;
    dom_qos_state m_client_state;
    dom_qos_status m_client_status;
    bool m_client_hello_sent;
    u64 m_last_status_tick;
    u64 m_last_hash_sent_tick;
    u32 m_hash_stride;
    std::vector<PeerQos> m_peer_qos;
    bool m_desync_written;
};

DomNetDriver *dom_net_driver_create(const DomSessionConfig &cfg,
                                    const DomNetDriverContext &ctx,
                                    std::string *out_error) {
    if (out_error) {
        out_error->clear();
    }
    if (cfg.role == DOM_SESSION_ROLE_SINGLE) {
        if (cfg.authority != DOM_SESSION_AUTH_SERVER_AUTH) {
            if (out_error) {
                *out_error = "single_requires_server_auth";
            }
            return 0;
        }
        return new DomNetDriverLoopback(cfg, ctx);
    }
    if (cfg.authority == DOM_SESSION_AUTH_LOCKSTEP) {
        return new DomNetDriverLockstep(cfg, ctx);
    }
    if (cfg.authority == DOM_SESSION_AUTH_SERVER_AUTH) {
        return new DomNetDriverServerAuth(cfg, ctx);
    }
    if (out_error) {
        *out_error = "unsupported_authority";
    }
    return 0;
}

void dom_net_driver_destroy(DomNetDriver *driver) {
    if (!driver) {
        return;
    }
    delete driver;
}

} // namespace dom
