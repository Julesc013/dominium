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

#include "dom_game_net.h"
#include "dom_instance.h"
#include "runtime/dom_game_net_snapshot.h"
#include "runtime/dom_game_runtime.h"

extern "C" {
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

} // namespace

class DomNetDriverServerAuth : public DomNetDriver {
public:
    DomNetDriverServerAuth(const DomSessionConfig &cfg, const DomNetDriverContext &ctx)
        : DomNetDriver(cfg, ctx),
          m_last_snapshot(),
          m_has_snapshot(false) {
    }

    int start() {
        if (!m_ctx.net) {
            return DOM_NET_DRIVER_ERR;
        }
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
        if (!m_ctx.net || !ensure_runtime_ready(m_ctx)) {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->pump(dom_game_runtime_world(m_ctx.runtime),
                        dom_game_runtime_sim(m_ctx.runtime),
                        *m_ctx.instance);
        return DOM_NET_DRIVER_OK;
    }

    bool ready() const {
        return m_ctx.net ? m_ctx.net->ready() : false;
    }

    int poll_snapshot(std::vector<unsigned char> &out_bytes) {
        if (m_role == DOM_SESSION_ROLE_CLIENT) {
            return DOM_NET_DRIVER_NO_DATA;
        }
        if (!m_ctx.runtime) {
            return DOM_NET_DRIVER_ERR;
        }
        return (dom_game_net_snapshot_build(m_ctx.runtime, out_bytes) == DOM_NET_SNAPSHOT_OK)
                   ? DOM_NET_DRIVER_OK
                   : DOM_NET_DRIVER_ERR;
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

private:
    dom_game_net_snapshot_desc m_last_snapshot;
    bool m_has_snapshot;
};

class DomNetDriverLockstep : public DomNetDriver {
public:
    DomNetDriverLockstep(const DomSessionConfig &cfg, const DomNetDriverContext &ctx)
        : DomNetDriver(cfg, ctx) {
    }

    int start() {
        if (!m_ctx.net) {
            return DOM_NET_DRIVER_ERR;
        }
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
        if (!m_ctx.net || !ensure_runtime_ready(m_ctx)) {
            return DOM_NET_DRIVER_ERR;
        }
        m_ctx.net->pump(dom_game_runtime_world(m_ctx.runtime),
                        dom_game_runtime_sim(m_ctx.runtime),
                        *m_ctx.instance);
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
};

DomNetDriver *dom_net_driver_create(const DomSessionConfig &cfg,
                                    const DomNetDriverContext &ctx,
                                    std::string *out_error) {
    if (out_error) {
        out_error->clear();
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
