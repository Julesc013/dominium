/* Deterministic net session model (C89). */
#ifndef D_NET_SESSION_H
#define D_NET_SESSION_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_session_id;
typedef u32 d_peer_id;

typedef enum d_net_role_e {
    D_NET_ROLE_SINGLE = 0, /* local-only */
    D_NET_ROLE_HOST,       /* authoritative host */
    D_NET_ROLE_CLIENT      /* remote participant */
} d_net_role;

enum {
    D_NET_PEER_FLAG_NONE      = 0u,
    D_NET_PEER_FLAG_CONNECTED = 1u << 0,
    D_NET_PEER_FLAG_READY     = 1u << 1,
    D_NET_PEER_FLAG_LAGGING   = 1u << 2
};

typedef struct d_net_peer_s {
    d_peer_id id;

    u32       flags;         /* D_NET_PEER_FLAG_* */
    u32       last_ack_tick;
} d_net_peer;

typedef struct d_net_session_s {
    d_session_id id;
    d_net_role   role;

    u32          tick;       /* shared sim tick */
    u32          tick_rate;  /* fixed ticks/sec */

    u16          peer_count;
    u16          peer_capacity;
    d_net_peer  *peers;

    u32          input_delay_ticks; /* fixed delay for local commands */
} d_net_session;

int  d_net_session_init(d_net_session *s, d_net_role role, u32 tick_rate);
void d_net_session_shutdown(d_net_session *s);

int         d_net_session_add_peer(d_net_session *s, d_peer_id peer_id);
d_net_peer *d_net_session_get_peer(d_net_session *s, d_peer_id peer_id);
int         d_net_session_remove_peer(d_net_session *s, d_peer_id peer_id);

#ifdef __cplusplus
}
#endif

#endif /* D_NET_SESSION_H */

