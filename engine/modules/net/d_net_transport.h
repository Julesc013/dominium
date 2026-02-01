/*
FILE: source/domino/net/d_net_transport.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_transport
RESPONSIBILITY: Defines internal contract for `d_net_transport`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Engine-facing transport hooks for deterministic netcode (C89). */
#ifndef D_NET_TRANSPORT_H
#define D_NET_TRANSPORT_H

#include "domino/core/types.h"
#include "net/d_net_session.h"
#include "net/d_net_proto.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef int (*d_net_send_fn)(
    void       *user,
    d_peer_id   peer,
    const void *data,
    u32         size
);

typedef int (*d_net_broadcast_fn)(
    void       *user,
    const void *data,
    u32         size
);

typedef struct d_net_transport_s {
    void               *user_ctx;
    d_net_send_fn       send_to_peer;
    d_net_broadcast_fn  broadcast;
} d_net_transport;

int d_net_set_transport(const d_net_transport *t);
const d_net_transport *d_net_get_transport(void);

/* Queue-driven event model for non-command messages. */
typedef enum d_net_event_type_e {
    D_NET_EVENT_NONE = 0,
    D_NET_EVENT_HANDSHAKE,
    D_NET_EVENT_HANDSHAKE_REPLY,
    D_NET_EVENT_SNAPSHOT,
    D_NET_EVENT_TICK,
    D_NET_EVENT_HASH,
    D_NET_EVENT_ERROR,
    D_NET_EVENT_QOS
} d_net_event_type;

typedef struct d_net_event_s {
    d_net_event_type type;
    d_session_id     session;
    d_peer_id        source_peer;
    union {
        d_net_handshake        handshake;
        d_net_handshake_reply  handshake_reply;
        d_net_snapshot         snapshot;
        d_net_tick             tick;
        d_net_hash             hash;
        d_net_error            error;
        d_net_qos              qos;
    } u;
} d_net_event;

/* Receive a raw packet from transport and feed it into the protocol decoder. */
int d_net_receive_packet(
    d_session_id session,
    d_peer_id    source,
    const void  *data,
    u32          size
);

/* Poll decoded control events (handshake/snapshot/etc). Returns 0 if event, 1 if none. */
int d_net_poll_event(d_net_event *out_ev);
void d_net_event_free(d_net_event *ev);

/* Convenience: encode+send helpers that invoke the registered transport. */
int d_net_send_handshake(d_peer_id peer, const d_net_handshake *hs);
int d_net_send_handshake_reply(d_peer_id peer, const d_net_handshake_reply *r);
int d_net_send_snapshot(d_peer_id peer, const d_net_snapshot *snap);
int d_net_send_tick(d_peer_id peer, const d_net_tick *t);
int d_net_send_cmd(d_peer_id peer, const d_net_cmd *cmd);
int d_net_broadcast_cmd(const d_net_cmd *cmd);
int d_net_send_hash(d_peer_id peer, const d_net_hash *h);
int d_net_send_error(d_peer_id peer, const d_net_error *e);
int d_net_send_qos(d_peer_id peer, const d_net_qos *q);

#ifdef __cplusplus
}
#endif

#endif /* D_NET_TRANSPORT_H */
