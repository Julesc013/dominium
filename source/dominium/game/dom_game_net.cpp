#include "dom_game_net.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "dom_game_save.h"
#include "dom_compat.h"

extern "C" {
#include "net/d_net_schema.h"
}

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
typedef SOCKET dom_sock_t;
static const dom_sock_t DOM_INVALID_SOCK = INVALID_SOCKET;
#else
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
typedef int dom_sock_t;
static const dom_sock_t DOM_INVALID_SOCK = -1;
#endif

namespace dom {

namespace {

static bool dom_net_platform_init() {
#ifdef _WIN32
    static bool wsa_ok = false;
    if (!wsa_ok) {
        WSADATA wsa;
        if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
            return false;
        }
        wsa_ok = true;
    }
#endif
    return true;
}

static void dom_net_close(dom_sock_t s) {
    if (s == DOM_INVALID_SOCK) {
        return;
    }
#ifdef _WIN32
    closesocket(s);
#else
    close(s);
#endif
}

static bool dom_net_set_nonblocking(dom_sock_t s) {
#ifdef _WIN32
    u_long mode = 1;
    return ioctlsocket(s, FIONBIO, &mode) == 0;
#else
    int flags;
    if (s < 0) return false;
    flags = fcntl(s, F_GETFL, 0);
    if (flags < 0) return false;
    return fcntl(s, F_SETFL, flags | O_NONBLOCK) == 0;
#endif
}

static bool dom_net_would_block() {
#ifdef _WIN32
    int err = WSAGetLastError();
    return err == WSAEWOULDBLOCK;
#else
    return errno == EAGAIN || errno == EWOULDBLOCK;
#endif
}

static bool dom_parse_addr_port(const std::string &addr_port, std::string &out_addr, unsigned &out_port) {
    out_addr.clear();
    out_port = 0u;
    if (addr_port.empty()) {
        return false;
    }
    {
        const std::string s = addr_port;
        const std::string::size_type pos = s.rfind(':');
        if (pos != std::string::npos && pos + 1u < s.size()) {
            const std::string host = s.substr(0u, pos);
            const std::string port_str = s.substr(pos + 1u);
            char *endp = 0;
            unsigned long p = std::strtoul(port_str.c_str(), &endp, 10);
            if (endp && *endp == '\0' && p > 0ul && p <= 65535ul) {
                out_addr = host.empty() ? std::string("127.0.0.1") : host;
                out_port = static_cast<unsigned>(p);
                return true;
            }
        }
        out_addr = s;
        out_port = 7777u;
        if (out_addr == "localhost") {
            out_addr = "127.0.0.1";
        }
        return true;
    }
}

static dom_sock_t dom_create_listen_socket(unsigned port) {
    dom_sock_t s;
    sockaddr_in addr;
    int yes = 1;

    s = (dom_sock_t)socket(AF_INET, SOCK_STREAM, 0);
    if (s == DOM_INVALID_SOCK) {
        return DOM_INVALID_SOCK;
    }

#ifdef _WIN32
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, (const char *)&yes, sizeof(yes));
#else
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &yes, (socklen_t)sizeof(yes));
#endif

    std::memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((unsigned short)port);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(s, (sockaddr *)&addr, sizeof(addr)) != 0) {
        dom_net_close(s);
        return DOM_INVALID_SOCK;
    }
    if (listen(s, 8) != 0) {
        dom_net_close(s);
        return DOM_INVALID_SOCK;
    }
    (void)dom_net_set_nonblocking(s);
    return s;
}

static dom_sock_t dom_connect_socket(const std::string &addr, unsigned port) {
    dom_sock_t s;
    sockaddr_in sa;
    std::memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port = htons((unsigned short)port);

    if (addr == "localhost") {
        sa.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    } else {
#ifdef _WIN32
        sa.sin_addr.s_addr = inet_addr(addr.c_str());
#else
        if (inet_pton(AF_INET, addr.c_str(), &sa.sin_addr) != 1) {
            return DOM_INVALID_SOCK;
        }
#endif
    }

    s = (dom_sock_t)socket(AF_INET, SOCK_STREAM, 0);
    if (s == DOM_INVALID_SOCK) {
        return DOM_INVALID_SOCK;
    }

    if (connect(s, (sockaddr *)&sa, sizeof(sa)) != 0) {
#ifdef _WIN32
        if (WSAGetLastError() != WSAEISCONN) {
            dom_net_close(s);
            return DOM_INVALID_SOCK;
        }
#else
        dom_net_close(s);
        return DOM_INVALID_SOCK;
#endif
    }

    (void)dom_net_set_nonblocking(s);
    return s;
}

struct DomConn {
    dom_sock_t sock;
    d_peer_id  peer_id;
    bool       active;
    bool       handshake_done;

    std::vector<unsigned char> inbuf;
    size_t in_ofs;

    std::vector<unsigned char> outbuf;
    size_t out_ofs;

    DomConn()
        : sock(DOM_INVALID_SOCK),
          peer_id(0u),
          active(false),
          handshake_done(false),
          in_ofs(0u),
          out_ofs(0u) {}
};

struct DomNetImpl {
    enum Mode {
        MODE_NONE = 0,
        MODE_HOST,
        MODE_CLIENT
    };

    Mode mode;
    dom_sock_t listen_sock;
    dom_sock_t client_sock;

    std::vector<DomConn> conns; /* host: clients; client: empty */

    DomConn host_conn;          /* client: connection to host */

    d_peer_id next_peer_id;

    DomNetImpl()
        : mode(MODE_NONE),
          listen_sock(DOM_INVALID_SOCK),
          client_sock(DOM_INVALID_SOCK),
          next_peer_id(2u) {}
};

static DomNetImpl *impl_of(void *p) {
    return (DomNetImpl *)p;
}

extern "C" int dom_net_send_to_peer_cb(void *user, d_peer_id peer, const void *data, u32 size) {
    DomNetImpl *impl = impl_of(user);
    size_t i;
    if (!impl || !data || size == 0u) {
        return -1;
    }
    if (impl->mode == DomNetImpl::MODE_CLIENT) {
        if (peer != 1u) {
            return -1;
        }
        {
            const size_t base = impl->host_conn.outbuf.size();
            impl->host_conn.outbuf.resize(base + (size_t)size);
            std::memcpy(&impl->host_conn.outbuf[base], data, (size_t)size);
        }
        return 0;
    }
    if (impl->mode != DomNetImpl::MODE_HOST) {
        return -1;
    }
    for (i = 0u; i < impl->conns.size(); ++i) {
        if (impl->conns[i].active && impl->conns[i].peer_id == peer) {
            const size_t base = impl->conns[i].outbuf.size();
            impl->conns[i].outbuf.resize(base + (size_t)size);
            std::memcpy(&impl->conns[i].outbuf[base], data, (size_t)size);
            return 0;
        }
    }
    return -1;
}

extern "C" int dom_net_broadcast_cb(void *user, const void *data, u32 size) {
    DomNetImpl *impl = impl_of(user);
    size_t i;
    if (!impl || !data || size == 0u) {
        return -1;
    }
    if (impl->mode == DomNetImpl::MODE_CLIENT) {
        const size_t base = impl->host_conn.outbuf.size();
        impl->host_conn.outbuf.resize(base + (size_t)size);
        std::memcpy(&impl->host_conn.outbuf[base], data, (size_t)size);
        return 0;
    }
    if (impl->mode != DomNetImpl::MODE_HOST) {
        return -1;
    }
    for (i = 0u; i < impl->conns.size(); ++i) {
        if (!impl->conns[i].active) {
            continue;
        }
        {
            const size_t base = impl->conns[i].outbuf.size();
            impl->conns[i].outbuf.resize(base + (size_t)size);
            std::memcpy(&impl->conns[i].outbuf[base], data, (size_t)size);
        }
    }
    return 0;
}

static bool dom_peek_packet_len(const unsigned char *buf, size_t buf_len, size_t &out_total_len) {
    u32 payload_len = 0u;
    if (!buf || buf_len < 12u) {
        return false;
    }
    if (buf[0] != 'D' || buf[1] != 'N' || buf[2] != 'M' || buf[3] != 1u) {
        return false;
    }
    std::memcpy(&payload_len, buf + 8u, sizeof(u32));
    out_total_len = 12u + (size_t)payload_len;
    return out_total_len >= 12u;
}

static void dom_compact_inbuf(DomConn &c) {
    if (c.in_ofs == 0u) {
        return;
    }
    if (c.in_ofs >= c.inbuf.size()) {
        c.inbuf.clear();
        c.in_ofs = 0u;
        return;
    }
    if (c.in_ofs > 4096u || c.in_ofs > c.inbuf.size() / 2u) {
        const size_t remaining = c.inbuf.size() - c.in_ofs;
        std::memmove(&c.inbuf[0], &c.inbuf[c.in_ofs], remaining);
        c.inbuf.resize(remaining);
        c.in_ofs = 0u;
    }
}

static void dom_compact_outbuf(DomConn &c) {
    if (c.out_ofs == 0u) {
        return;
    }
    if (c.out_ofs >= c.outbuf.size()) {
        c.outbuf.clear();
        c.out_ofs = 0u;
        return;
    }
    if (c.out_ofs > 4096u || c.out_ofs > c.outbuf.size() / 2u) {
        const size_t remaining = c.outbuf.size() - c.out_ofs;
        std::memmove(&c.outbuf[0], &c.outbuf[c.out_ofs], remaining);
        c.outbuf.resize(remaining);
        c.out_ofs = 0u;
    }
}

} // namespace

DomGameNet::DomGameNet()
    : m_local_peer(1u),
      m_cmd_seq(1u),
      m_ready(true),
      m_dedicated(false),
      m_handshake_sent(true),
      m_impl(0) {
    std::memset(&m_session, 0, sizeof(m_session));
}

DomGameNet::~DomGameNet() {
    shutdown();
}

bool DomGameNet::init_single(u32 tick_rate) {
    shutdown();
    if (d_net_session_init(&m_session, D_NET_ROLE_SINGLE, tick_rate) != 0) {
        return false;
    }
    m_local_peer = 1u;
    (void)d_net_session_add_peer(&m_session, m_local_peer);
    m_ready = true;
    m_dedicated = false;
    m_handshake_sent = true;
    m_cmd_seq = 1u;
    return true;
}

bool DomGameNet::init_host_common(u32 tick_rate, unsigned port, bool dedicated) {
    DomNetImpl *impl;
    d_net_transport t;
    shutdown();

    if (!dom_net_platform_init()) {
        return false;
    }

    if (d_net_session_init(&m_session, D_NET_ROLE_HOST, tick_rate) != 0) {
        return false;
    }
    m_local_peer = 1u;
    (void)d_net_session_add_peer(&m_session, m_local_peer);
    m_ready = true;
    m_dedicated = dedicated;
    m_handshake_sent = true;
    m_cmd_seq = 1u;

    impl = new DomNetImpl();
    impl->mode = DomNetImpl::MODE_HOST;
    impl->listen_sock = dom_create_listen_socket(port);
    if (impl->listen_sock == DOM_INVALID_SOCK) {
        delete impl;
        return false;
    }
    m_impl = impl;

    std::memset(&t, 0, sizeof(t));
    t.user_ctx = impl;
    t.send_to_peer = dom_net_send_to_peer_cb;
    t.broadcast = dom_net_broadcast_cb;
    (void)d_net_set_transport(&t);

    std::printf("Net: host listening on port %u\n", port);
    return true;
}

bool DomGameNet::init_listen(u32 tick_rate, unsigned port) {
    return init_host_common(tick_rate, port, false);
}

bool DomGameNet::init_dedicated(u32 tick_rate, unsigned port) {
    return init_host_common(tick_rate, port, true);
}

bool DomGameNet::init_client(u32 tick_rate, const std::string &addr_port) {
    DomNetImpl *impl;
    d_net_transport t;
    std::string addr;
    unsigned port;

    shutdown();
    if (!dom_net_platform_init()) {
        return false;
    }
    if (!dom_parse_addr_port(addr_port, addr, port)) {
        return false;
    }

    if (d_net_session_init(&m_session, D_NET_ROLE_CLIENT, tick_rate) != 0) {
        return false;
    }
    (void)d_net_session_add_peer(&m_session, 1u);
    m_local_peer = 0u;
    m_ready = false;
    m_dedicated = false;
    m_handshake_sent = false;
    m_cmd_seq = 1u;

    impl = new DomNetImpl();
    impl->mode = DomNetImpl::MODE_CLIENT;
    impl->host_conn.peer_id = 1u;
    impl->host_conn.sock = dom_connect_socket(addr, port);
    if (impl->host_conn.sock == DOM_INVALID_SOCK) {
        delete impl;
        return false;
    }
    impl->host_conn.active = true;
    m_impl = impl;

    std::memset(&t, 0, sizeof(t));
    t.user_ctx = impl;
    t.send_to_peer = dom_net_send_to_peer_cb;
    t.broadcast = dom_net_broadcast_cb;
    (void)d_net_set_transport(&t);

    std::printf("Net: connecting to %s:%u\n", addr.c_str(), port);
    return true;
}

void DomGameNet::shutdown() {
    DomNetImpl *impl = (DomNetImpl *)m_impl;
    if (impl) {
        size_t i;
        if (impl->listen_sock != DOM_INVALID_SOCK) {
            dom_net_close(impl->listen_sock);
            impl->listen_sock = DOM_INVALID_SOCK;
        }
        for (i = 0u; i < impl->conns.size(); ++i) {
            if (impl->conns[i].sock != DOM_INVALID_SOCK) {
                dom_net_close(impl->conns[i].sock);
                impl->conns[i].sock = DOM_INVALID_SOCK;
            }
            impl->conns[i].active = false;
        }
        if (impl->host_conn.sock != DOM_INVALID_SOCK) {
            dom_net_close(impl->host_conn.sock);
            impl->host_conn.sock = DOM_INVALID_SOCK;
        }
        impl->host_conn.active = false;

        delete impl;
        m_impl = 0;
    }

    d_net_session_shutdown(&m_session);
    std::memset(&m_session, 0, sizeof(m_session));
    m_local_peer = 1u;
    m_cmd_seq = 1u;
    m_ready = true;
    m_dedicated = false;
    m_handshake_sent = true;
}

void DomGameNet::pump(d_world *world, d_sim_context *sim, const InstanceInfo &inst) {
    if (!m_impl) {
        update_session_tick(world);
        return;
    }
    if (m_session.role == D_NET_ROLE_CLIENT && !m_handshake_sent) {
        m_handshake_sent = send_handshake(inst);
    }
    accept_new_peers();
    recv_packets(world, sim, inst);
    handle_events(world, sim, inst);
    flush_sends();
    update_session_tick(world);
}

void DomGameNet::update_session_tick(d_world *world) {
    if (!world) {
        return;
    }
    m_session.tick = world->tick_count;
}

void DomGameNet::accept_new_peers() {
    DomNetImpl *impl = (DomNetImpl *)m_impl;
    if (!impl || impl->mode != DomNetImpl::MODE_HOST) {
        return;
    }
    for (;;) {
        sockaddr_in addr;
        socklen_t addrlen = (socklen_t)sizeof(addr);
        dom_sock_t s = accept(impl->listen_sock, (sockaddr *)&addr, &addrlen);
        if (s == DOM_INVALID_SOCK) {
            if (dom_net_would_block()) {
                return;
            }
            return;
        }
        (void)dom_net_set_nonblocking(s);

        DomConn c;
        c.sock = s;
        c.peer_id = impl->next_peer_id++;
        c.active = true;
        c.handshake_done = false;
        impl->conns.push_back(c);

        (void)d_net_session_add_peer(&m_session, c.peer_id);
        std::printf("Net: peer %u connected\n", (unsigned)c.peer_id);
    }
}

static void dom_recv_into(DomConn &c) {
    unsigned char tmp[4096];
    for (;;) {
#ifdef _WIN32
        int n = recv(c.sock, (char *)tmp, (int)sizeof(tmp), 0);
#else
        int n = (int)recv(c.sock, tmp, sizeof(tmp), 0);
#endif
        if (n > 0) {
            const size_t base = c.inbuf.size();
            c.inbuf.resize(base + (size_t)n);
            std::memcpy(&c.inbuf[base], tmp, (size_t)n);
            continue;
        }
        if (n == 0) {
            c.active = false;
            return;
        }
        if (dom_net_would_block()) {
            return;
        }
        c.active = false;
        return;
    }
}

static void dom_process_incoming(
    DomGameNet &net,
    DomNetImpl &impl,
    DomConn    &c,
    d_world    *world,
    d_sim_context *sim,
    const InstanceInfo &inst
) {
    (void)world;
    (void)sim;
    (void)inst;

    while (c.active) {
        size_t available;
        size_t pkt_len = 0u;
        const unsigned char *p;

        dom_compact_inbuf(c);
        if (c.in_ofs >= c.inbuf.size()) {
            return;
        }
        available = c.inbuf.size() - c.in_ofs;
        p = &c.inbuf[c.in_ofs];
        if (available < 12u) {
            return;
        }
        if (!dom_peek_packet_len(p, available, pkt_len)) {
            c.active = false;
            return;
        }
        if (available < pkt_len) {
            return;
        }

        /* Forward command packets from peers to all peers (host mode). */
        if (impl.mode == DomNetImpl::MODE_HOST) {
            const unsigned char msg_type = p[4];
            if (msg_type == (unsigned char)D_NET_MSG_CMD) {
                (void)dom_net_broadcast_cb(&impl, p, (u32)pkt_len);
            }
        }

        (void)d_net_receive_packet(net.session().id, c.peer_id, p, (u32)pkt_len);
        c.in_ofs += pkt_len;
    }
}

void DomGameNet::recv_packets(d_world *world, d_sim_context *sim, const InstanceInfo &inst) {
    DomNetImpl *impl = (DomNetImpl *)m_impl;
    size_t i;
    if (!impl) {
        return;
    }

    if (impl->mode == DomNetImpl::MODE_CLIENT) {
        if (!impl->host_conn.active) {
            return;
        }
        dom_recv_into(impl->host_conn);
        dom_process_incoming(*this, *impl, impl->host_conn, world, sim, inst);
        return;
    }

    if (impl->mode != DomNetImpl::MODE_HOST) {
        return;
    }

    for (i = 0u; i < impl->conns.size(); ++i) {
        if (!impl->conns[i].active) {
            continue;
        }
        dom_recv_into(impl->conns[i]);
        dom_process_incoming(*this, *impl, impl->conns[i], world, sim, inst);
    }
}

void DomGameNet::flush_sends() {
    DomNetImpl *impl = (DomNetImpl *)m_impl;
    size_t i;
    if (!impl) {
        return;
    }

    if (impl->mode == DomNetImpl::MODE_CLIENT) {
        DomConn &c = impl->host_conn;
        dom_compact_outbuf(c);
        while (c.active && c.out_ofs < c.outbuf.size()) {
            const unsigned char *p = &c.outbuf[c.out_ofs];
            const size_t remain = c.outbuf.size() - c.out_ofs;
#ifdef _WIN32
            int n = send(c.sock, (const char *)p, (int)remain, 0);
#else
            int n = (int)send(c.sock, p, remain, 0);
#endif
            if (n > 0) {
                c.out_ofs += (size_t)n;
                dom_compact_outbuf(c);
                continue;
            }
            if (dom_net_would_block()) {
                break;
            }
            c.active = false;
            break;
        }
        return;
    }

    if (impl->mode != DomNetImpl::MODE_HOST) {
        return;
    }

    for (i = 0u; i < impl->conns.size(); ++i) {
        DomConn &c = impl->conns[i];
        if (!c.active) {
            continue;
        }
        dom_compact_outbuf(c);
        while (c.active && c.out_ofs < c.outbuf.size()) {
            const unsigned char *p = &c.outbuf[c.out_ofs];
            const size_t remain = c.outbuf.size() - c.out_ofs;
#ifdef _WIN32
            int n = send(c.sock, (const char *)p, (int)remain, 0);
#else
            int n = (int)send(c.sock, p, remain, 0);
#endif
            if (n > 0) {
                c.out_ofs += (size_t)n;
                dom_compact_outbuf(c);
                continue;
            }
            if (dom_net_would_block()) {
                break;
            }
            c.active = false;
            break;
        }
    }
}

bool DomGameNet::send_handshake(const InstanceInfo &inst) {
    d_net_handshake hs;
    std::memset(&hs, 0, sizeof(hs));
    hs.suite_version = inst.suite_version;
    hs.core_version = inst.core_version;
    hs.net_proto_version = D_NET_PROTO_VERSION;
    hs.compat_profile = 0u;
    hs.role = (u32)D_NET_ROLE_CLIENT;
    return d_net_send_handshake(1u, &hs) == 0;
}

void DomGameNet::handle_events(d_world *world, d_sim_context *sim, const InstanceInfo &inst) {
    d_net_event ev;

    while (d_net_poll_event(&ev) == 0) {
        /* During client bootstrap, accept events from the pre-assigned local session id. */
        if (!(m_session.role == D_NET_ROLE_CLIENT && !m_ready)) {
            if (ev.session != m_session.id) {
                d_net_event_free(&ev);
                continue;
            }
        }

        if (m_session.role == D_NET_ROLE_HOST && ev.type == D_NET_EVENT_HANDSHAKE) {
            d_net_handshake_reply reply;
            CompatResult cres;
            ProductInfo prod;

            std::memset(&prod, 0, sizeof(prod));
            prod.product = "game";
            prod.role_detail = "client";
            prod.product_version = ev.u.handshake.suite_version;
            prod.core_version = ev.u.handshake.core_version;
            prod.suite_version = ev.u.handshake.suite_version;

            cres = evaluate_compat(prod, inst);

            std::memset(&reply, 0, sizeof(reply));
            reply.reason_code = (u32)cres;
            reply.assigned_peer = ev.source_peer;
            reply.session_id = m_session.id;
            reply.tick_rate = m_session.tick_rate;
            reply.tick = world ? world->tick_count : 0u;
            reply.result = (cres == COMPAT_INCOMPATIBLE || cres == COMPAT_MOD_UNSAFE || cres == COMPAT_SCHEMA_MISMATCH) ? 1u : 0u;

            (void)d_net_send_handshake_reply(ev.source_peer, &reply);

            if (reply.result == 0u && world) {
                std::vector<unsigned char> blob;
                if (game_save_world_blob(world, blob) && !blob.empty()) {
                    d_net_snapshot snap;
                    std::memset(&snap, 0, sizeof(snap));
                    snap.tick = world->tick_count;
                    snap.data.ptr = &blob[0];
                    snap.data.len = (u32)blob.size();
                    (void)d_net_send_snapshot(ev.source_peer, &snap);
                }
                {
                    d_net_peer *p = d_net_session_get_peer(&m_session, ev.source_peer);
                    if (p) {
                        p->flags |= D_NET_PEER_FLAG_READY;
                    }
                }
            }
        } else if (m_session.role == D_NET_ROLE_CLIENT && ev.type == D_NET_EVENT_HANDSHAKE_REPLY) {
            if (ev.u.handshake_reply.result != 0u) {
                std::printf("Net: handshake rejected (reason=%u)\n",
                            (unsigned)ev.u.handshake_reply.reason_code);
                m_ready = false;
            } else {
                m_local_peer = ev.u.handshake_reply.assigned_peer;
                m_session.id = ev.u.handshake_reply.session_id;
                m_session.tick_rate = ev.u.handshake_reply.tick_rate;
                m_session.tick = ev.u.handshake_reply.tick;
                (void)d_net_session_add_peer(&m_session, m_local_peer);
                m_ready = false;
                std::printf("Net: assigned peer %u (session %u)\n",
                            (unsigned)m_local_peer,
                            (unsigned)m_session.id);
            }
        } else if (m_session.role == D_NET_ROLE_CLIENT && ev.type == D_NET_EVENT_SNAPSHOT) {
            if (world && sim) {
                if (game_load_world_blob(world, ev.u.snapshot.data.ptr, (size_t)ev.u.snapshot.data.len)) {
                    world->tick_count = ev.u.snapshot.tick;
                    sim->tick_index = ev.u.snapshot.tick;
                    m_session.tick = ev.u.snapshot.tick;
                    (void)d_net_cmd_queue_init();
                    m_ready = true;
                    std::printf("Net: snapshot loaded at tick %u\n", (unsigned)ev.u.snapshot.tick);
                } else {
                    std::printf("Net: snapshot load failed\n");
                    m_ready = false;
                }
            }
        }

        d_net_event_free(&ev);
    }

    update_session_tick(world);
}

bool DomGameNet::submit_cmd(d_net_cmd *in_out_cmd) {
    if (!in_out_cmd) {
        return false;
    }
    if (in_out_cmd->schema_id == 0u || in_out_cmd->schema_ver == 0u) {
        return false;
    }
    if (in_out_cmd->tick == 0u) {
        return false;
    }
    in_out_cmd->id = m_cmd_seq++;
    in_out_cmd->source_peer = m_local_peer;

    if (m_session.role == D_NET_ROLE_SINGLE) {
        unsigned char tmp[2048];
        u32 out_size = 0u;
        std::vector<unsigned char> buf;
        int rc;
        rc = d_net_encode_cmd(in_out_cmd, tmp, (u32)sizeof(tmp), &out_size);
        if (rc != 0) {
            buf.resize(16384u);
            rc = d_net_encode_cmd(in_out_cmd, &buf[0], (u32)buf.size(), &out_size);
        } else {
            buf.assign(tmp, tmp + out_size);
        }
        if (rc != 0) {
            return false;
        }
        return d_net_receive_packet(m_session.id, m_local_peer, &buf[0], out_size) == 0;
    }

    if (m_session.role == D_NET_ROLE_HOST) {
        unsigned char tmp[2048];
        u32 out_size = 0u;
        std::vector<unsigned char> buf;
        int rc;
        rc = d_net_encode_cmd(in_out_cmd, tmp, (u32)sizeof(tmp), &out_size);
        if (rc != 0) {
            buf.resize(16384u);
            rc = d_net_encode_cmd(in_out_cmd, &buf[0], (u32)buf.size(), &out_size);
        } else {
            buf.assign(tmp, tmp + out_size);
        }
        if (rc != 0) {
            return false;
        }
        (void)d_net_receive_packet(m_session.id, m_local_peer, &buf[0], out_size);
        (void)dom_net_broadcast_cb(m_impl, &buf[0], out_size);
        return true;
    }

    if (m_session.role == D_NET_ROLE_CLIENT) {
        if (!m_ready || m_local_peer == 0u) {
            return false;
        }
        return d_net_send_cmd(1u, in_out_cmd) == 0;
    }

    return false;
}

} // namespace dom
