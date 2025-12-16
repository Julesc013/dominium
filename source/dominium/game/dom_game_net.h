/*
FILE: source/dominium/game/dom_game_net.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_net
RESPONSIBILITY: Defines internal contract for `dom_game_net`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_NET_H
#define DOM_GAME_NET_H

#include <string>
#include <vector>

#include "dom_instance.h"

extern "C" {
#include "net/d_net_session.h"
#include "net/d_net_transport.h"
#include "net/d_net_cmd.h"
#include "sim/d_sim.h"
#include "world/d_world.h"
}

namespace dom {

class DomGameNet {
public:
    DomGameNet();
    ~DomGameNet();

    bool init_single(u32 tick_rate);
    bool init_listen(u32 tick_rate, unsigned port);
    bool init_dedicated(u32 tick_rate, unsigned port);
    bool init_client(u32 tick_rate, const std::string &addr_port);

    void shutdown();
    void pump(d_world *world, d_sim_context *sim, const InstanceInfo &inst);

    bool ready() const { return m_ready; }

    const d_net_session& session() const { return m_session; }
    d_peer_id local_peer() const { return m_local_peer; }

    u32 input_delay_ticks() const { return m_session.input_delay_ticks; }

    /* Submit a locally authored command; assigns source_peer and cmd id. */
    bool submit_cmd(d_net_cmd *in_out_cmd);

private:
    DomGameNet(const DomGameNet &);
    DomGameNet &operator=(const DomGameNet &);

private:
    struct Conn;

    bool init_host_common(u32 tick_rate, unsigned port, bool dedicated);
    void update_session_tick(d_world *world);
    void accept_new_peers();
    void recv_packets(d_world *world, d_sim_context *sim, const InstanceInfo &inst);
    void flush_sends();
    void handle_events(d_world *world, d_sim_context *sim, const InstanceInfo &inst);

    int queue_send_to_peer(d_peer_id peer, const void *data, u32 size);
    int queue_broadcast(const void *data, u32 size);

    bool send_handshake(const InstanceInfo &inst);

private:
    d_net_session m_session;
    d_peer_id     m_local_peer;
    u32           m_cmd_seq;

    bool          m_ready;
    bool          m_dedicated;
    bool          m_handshake_sent;

    /* Networking state (opaque; implemented in .cpp). */
    void         *m_impl;
};

} // namespace dom

#endif
