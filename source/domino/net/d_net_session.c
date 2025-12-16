/*
FILE: source/domino/net/d_net_session.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_session
RESPONSIBILITY: Implements `d_net_session`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "d_net_session.h"

static d_session_id g_next_session_id = 1u;

int d_net_session_init(d_net_session *s, d_net_role role, u32 tick_rate) {
    if (!s || tick_rate == 0u) {
        return -1;
    }
    memset(s, 0, sizeof(*s));
    s->id = g_next_session_id++;
    s->role = role;
    s->tick = 0u;
    s->tick_rate = tick_rate;
    s->peer_count = 0u;
    s->peer_capacity = 0u;
    s->peers = (d_net_peer *)0;
    s->input_delay_ticks = 2u;
    return 0;
}

void d_net_session_shutdown(d_net_session *s) {
    if (!s) {
        return;
    }
    if (s->peers) {
        free(s->peers);
    }
    memset(s, 0, sizeof(*s));
}

static int d_net_session_ensure_capacity(d_net_session *s, u16 needed) {
    u16 new_cap;
    d_net_peer *new_peers;
    u16 i;
    if (!s) {
        return -1;
    }
    if (needed <= s->peer_capacity) {
        return 0;
    }
    new_cap = s->peer_capacity ? (u16)(s->peer_capacity * 2u) : (u16)4u;
    if (new_cap < needed) {
        new_cap = needed;
    }
    new_peers = (d_net_peer *)realloc(s->peers, sizeof(d_net_peer) * new_cap);
    if (!new_peers) {
        return -1;
    }
    for (i = s->peer_capacity; i < new_cap; ++i) {
        new_peers[i].id = 0u;
        new_peers[i].flags = 0u;
        new_peers[i].last_ack_tick = 0u;
    }
    s->peers = new_peers;
    s->peer_capacity = new_cap;
    return 0;
}

d_net_peer *d_net_session_get_peer(d_net_session *s, d_peer_id peer_id) {
    u16 i;
    if (!s || peer_id == 0u) {
        return (d_net_peer *)0;
    }
    for (i = 0u; i < s->peer_count; ++i) {
        if (s->peers[i].id == peer_id) {
            return &s->peers[i];
        }
    }
    return (d_net_peer *)0;
}

int d_net_session_add_peer(d_net_session *s, d_peer_id peer_id) {
    d_net_peer *p;
    if (!s || peer_id == 0u) {
        return -1;
    }
    p = d_net_session_get_peer(s, peer_id);
    if (p) {
        p->flags |= D_NET_PEER_FLAG_CONNECTED;
        return 0;
    }
    if (d_net_session_ensure_capacity(s, (u16)(s->peer_count + 1u)) != 0) {
        return -1;
    }
    s->peers[s->peer_count].id = peer_id;
    s->peers[s->peer_count].flags = D_NET_PEER_FLAG_CONNECTED;
    s->peers[s->peer_count].last_ack_tick = 0u;
    s->peer_count = (u16)(s->peer_count + 1u);
    return 0;
}

int d_net_session_remove_peer(d_net_session *s, d_peer_id peer_id) {
    u16 i;
    if (!s || peer_id == 0u) {
        return -1;
    }
    for (i = 0u; i < s->peer_count; ++i) {
        if (s->peers[i].id == peer_id) {
            s->peers[i] = s->peers[s->peer_count - 1u];
            s->peers[s->peer_count - 1u].id = 0u;
            s->peers[s->peer_count - 1u].flags = 0u;
            s->peers[s->peer_count - 1u].last_ack_tick = 0u;
            s->peer_count = (u16)(s->peer_count - 1u);
            return 0;
        }
    }
    return 1;
}

