/*
FILE: source/domino/net/d_net_transport.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_transport
RESPONSIBILITY: Implements `d_net_transport`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "d_net_transport.h"
#include "net/d_net_cmd.h"

enum {
    D_NET_EVENT_QUEUE_CAP = 64u,
    D_NET_SEND_TMP_STACK = 2048u
};

static d_net_transport g_transport;
static int g_transport_set = 0;

static d_net_event g_events[D_NET_EVENT_QUEUE_CAP];
static u32 g_ev_head = 0u;
static u32 g_ev_tail = 0u;

static int d_net_events_is_empty(void) {
    return g_ev_head == g_ev_tail;
}

static int d_net_events_is_full(void) {
    return ((g_ev_tail + 1u) % D_NET_EVENT_QUEUE_CAP) == g_ev_head;
}

static int d_net_push_event(const d_net_event *ev) {
    if (!ev) {
        return -1;
    }
    if (d_net_events_is_full()) {
        return -2;
    }
    g_events[g_ev_tail] = *ev;
    g_ev_tail = (g_ev_tail + 1u) % D_NET_EVENT_QUEUE_CAP;
    return 0;
}

int d_net_poll_event(d_net_event *out_ev) {
    if (!out_ev) {
        return -1;
    }
    if (d_net_events_is_empty()) {
        return 1;
    }
    *out_ev = g_events[g_ev_head];
    memset(&g_events[g_ev_head], 0, sizeof(g_events[g_ev_head]));
    g_ev_head = (g_ev_head + 1u) % D_NET_EVENT_QUEUE_CAP;
    return 0;
}

void d_net_event_free(d_net_event *ev) {
    if (!ev) {
        return;
    }
    if (ev->type == D_NET_EVENT_SNAPSHOT) {
        d_net_snapshot_free(&ev->u.snapshot);
    }
    memset(ev, 0, sizeof(*ev));
}

int d_net_set_transport(const d_net_transport *t) {
    if (!t || !t->send_to_peer || !t->broadcast) {
        memset(&g_transport, 0, sizeof(g_transport));
        g_transport_set = 0;
        return -1;
    }
    g_transport = *t;
    g_transport_set = 1;
    return 0;
}

const d_net_transport *d_net_get_transport(void) {
    if (!g_transport_set) {
        return (const d_net_transport *)0;
    }
    return &g_transport;
}

static int d_net_send_raw_to_peer(d_peer_id peer, const void *data, u32 size) {
    if (!g_transport_set || !g_transport.send_to_peer) {
        return -1;
    }
    return g_transport.send_to_peer(g_transport.user_ctx, peer, data, size);
}

static int d_net_broadcast_raw(const void *data, u32 size) {
    if (!g_transport_set || !g_transport.broadcast) {
        return -1;
    }
    return g_transport.broadcast(g_transport.user_ctx, data, size);
}

int d_net_receive_packet(
    d_session_id session,
    d_peer_id    source,
    const void  *data,
    u32          size
) {
    d_net_msg_type type;
    d_tlv_blob payload;
    int rc;
    if (!data || size == 0u) {
        return -1;
    }

    rc = d_net_decode_frame(data, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }

    if (type == D_NET_MSG_CMD) {
        d_net_cmd cmd;
        memset(&cmd, 0, sizeof(cmd));
        rc = d_net_decode_cmd(data, size, &cmd);
        if (rc != 0) {
            return rc;
        }
        /* Trust the source_peer embedded in cmd; transport source is advisory. */
        (void)source;
        rc = d_net_cmd_enqueue(&cmd);
        d_net_cmd_free(&cmd);
        return rc;
    }

    /* Control/event messages: decode and push onto event queue. */
    {
        d_net_event ev;
        memset(&ev, 0, sizeof(ev));
        ev.session = session;
        ev.source_peer = source;

        if (type == D_NET_MSG_HANDSHAKE) {
            ev.type = D_NET_EVENT_HANDSHAKE;
            (void)d_net_decode_handshake(data, size, &ev.u.handshake);
        } else if (type == D_NET_MSG_HANDSHAKE_REPLY) {
            ev.type = D_NET_EVENT_HANDSHAKE_REPLY;
            (void)d_net_decode_handshake_reply(data, size, &ev.u.handshake_reply);
        } else if (type == D_NET_MSG_SNAPSHOT) {
            ev.type = D_NET_EVENT_SNAPSHOT;
            if (d_net_decode_snapshot(data, size, &ev.u.snapshot) != 0) {
                d_net_event_free(&ev);
                return -1;
            }
        } else if (type == D_NET_MSG_TICK) {
            ev.type = D_NET_EVENT_TICK;
            (void)d_net_decode_tick(data, size, &ev.u.tick);
        } else if (type == D_NET_MSG_HASH) {
            ev.type = D_NET_EVENT_HASH;
            (void)d_net_decode_hash(data, size, &ev.u.hash);
        } else if (type == D_NET_MSG_ERROR) {
            ev.type = D_NET_EVENT_ERROR;
            (void)d_net_decode_error(data, size, &ev.u.error);
        } else {
            return 0;
        }

        rc = d_net_push_event(&ev);
        if (rc != 0) {
            d_net_event_free(&ev);
        }
        return rc;
    }
}

static int d_net_send_with_encoder(
    d_peer_id peer,
    int (*encode_fn)(const void *, void *, u32, u32 *),
    const void *obj
) {
    unsigned char stack_buf[D_NET_SEND_TMP_STACK];
    unsigned char *dyn_buf;
    u32 out_size = 0u;
    int rc;
    size_t cap;
    u32 attempt;

    if (!encode_fn) {
        return -1;
    }

    dyn_buf = (unsigned char *)0;
    rc = encode_fn(obj, stack_buf, (u32)sizeof(stack_buf), &out_size);
    if (rc == 0) {
        return d_net_send_raw_to_peer(peer, stack_buf, out_size);
    }
    if (rc != -2) {
        return rc;
    }

    /* Too small; retry with an expanding heap buffer. */
    cap = (size_t)(sizeof(stack_buf) * 8u);
    for (attempt = 0u; attempt < 8u; ++attempt) {
        dyn_buf = (unsigned char *)malloc(cap);
        if (!dyn_buf) {
            return -1;
        }
        rc = encode_fn(obj, dyn_buf, (u32)cap, &out_size);
        if (rc == 0) {
            rc = d_net_send_raw_to_peer(peer, dyn_buf, out_size);
            free(dyn_buf);
            return rc;
        }
        free(dyn_buf);
        dyn_buf = (unsigned char *)0;
        if (rc != -2) {
            return rc;
        }
        cap *= 2u;
        if (cap > (size_t)(16u * 1024u * 1024u)) {
            break;
        }
    }
    return -2;
}

static int d_net_broadcast_with_encoder(
    int (*encode_fn)(const void *, void *, u32, u32 *),
    const void *obj
) {
    unsigned char stack_buf[D_NET_SEND_TMP_STACK];
    unsigned char *dyn_buf;
    u32 out_size = 0u;
    int rc;
    size_t cap;
    u32 attempt;

    if (!encode_fn) {
        return -1;
    }

    dyn_buf = (unsigned char *)0;
    rc = encode_fn(obj, stack_buf, (u32)sizeof(stack_buf), &out_size);
    if (rc == 0) {
        return d_net_broadcast_raw(stack_buf, out_size);
    }
    if (rc != -2) {
        return rc;
    }

    cap = (size_t)(sizeof(stack_buf) * 8u);
    for (attempt = 0u; attempt < 8u; ++attempt) {
        dyn_buf = (unsigned char *)malloc(cap);
        if (!dyn_buf) {
            return -1;
        }
        rc = encode_fn(obj, dyn_buf, (u32)cap, &out_size);
        if (rc == 0) {
            rc = d_net_broadcast_raw(dyn_buf, out_size);
            free(dyn_buf);
            return rc;
        }
        free(dyn_buf);
        dyn_buf = (unsigned char *)0;
        if (rc != -2) {
            return rc;
        }
        cap *= 2u;
        if (cap > (size_t)(16u * 1024u * 1024u)) {
            break;
        }
    }
    return -2;
}

static int d_net_encode_handshake_adapter(const void *obj, void *buf, u32 buf_size, u32 *out_size) {
    return d_net_encode_handshake((const d_net_handshake *)obj, buf, buf_size, out_size);
}

static int d_net_encode_handshake_reply_adapter(const void *obj, void *buf, u32 buf_size, u32 *out_size) {
    return d_net_encode_handshake_reply((const d_net_handshake_reply *)obj, buf, buf_size, out_size);
}

static int d_net_encode_snapshot_adapter(const void *obj, void *buf, u32 buf_size, u32 *out_size) {
    return d_net_encode_snapshot((const d_net_snapshot *)obj, buf, buf_size, out_size);
}

static int d_net_encode_tick_adapter(const void *obj, void *buf, u32 buf_size, u32 *out_size) {
    return d_net_encode_tick((const d_net_tick *)obj, buf, buf_size, out_size);
}

static int d_net_encode_cmd_adapter(const void *obj, void *buf, u32 buf_size, u32 *out_size) {
    return d_net_encode_cmd((const d_net_cmd *)obj, buf, buf_size, out_size);
}

static int d_net_encode_hash_adapter(const void *obj, void *buf, u32 buf_size, u32 *out_size) {
    return d_net_encode_hash((const d_net_hash *)obj, buf, buf_size, out_size);
}

static int d_net_encode_error_adapter(const void *obj, void *buf, u32 buf_size, u32 *out_size) {
    return d_net_encode_error((const d_net_error *)obj, buf, buf_size, out_size);
}

int d_net_send_handshake(d_peer_id peer, const d_net_handshake *hs) {
    return d_net_send_with_encoder(peer, d_net_encode_handshake_adapter, hs);
}

int d_net_send_handshake_reply(d_peer_id peer, const d_net_handshake_reply *r) {
    return d_net_send_with_encoder(peer, d_net_encode_handshake_reply_adapter, r);
}

int d_net_send_snapshot(d_peer_id peer, const d_net_snapshot *snap) {
    return d_net_send_with_encoder(peer, d_net_encode_snapshot_adapter, snap);
}

int d_net_send_tick(d_peer_id peer, const d_net_tick *t) {
    return d_net_send_with_encoder(peer, d_net_encode_tick_adapter, t);
}

int d_net_send_cmd(d_peer_id peer, const d_net_cmd *cmd) {
    return d_net_send_with_encoder(peer, d_net_encode_cmd_adapter, cmd);
}

int d_net_broadcast_cmd(const d_net_cmd *cmd) {
    return d_net_broadcast_with_encoder(d_net_encode_cmd_adapter, cmd);
}

int d_net_send_hash(d_peer_id peer, const d_net_hash *h) {
    return d_net_send_with_encoder(peer, d_net_encode_hash_adapter, h);
}

int d_net_send_error(d_peer_id peer, const d_net_error *e) {
    return d_net_send_with_encoder(peer, d_net_encode_error_adapter, e);
}
