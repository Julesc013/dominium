/* Deterministic net command queue (C89). */
#ifndef D_NET_CMD_H
#define D_NET_CMD_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "net/d_net_session.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_cmd_id;

enum {
    D_NET_CMD_MAX_PER_TICK = 256u
};

typedef struct d_net_cmd_s {
    d_cmd_id  id;          /* per-peer monotonic id (sequence) */
    d_peer_id source_peer;
    u32       tick;        /* sim tick to apply at */

    u32       schema_id;   /* D_NET_SCHEMA_* */
    u16       schema_ver;  /* schema version */
    u16       _pad0;

    d_tlv_blob payload;    /* schema-specific TLV payload */
} d_net_cmd;

int  d_net_cmd_queue_init(void);
void d_net_cmd_queue_shutdown(void);

int d_net_cmd_enqueue(const d_net_cmd *cmd);
int d_net_cmd_dequeue_for_tick(
    u32       tick,
    d_net_cmd *out_cmd,
    u32       max_cmds,
    u32      *out_count
);

void d_net_cmd_free(d_net_cmd *cmd);

#ifdef __cplusplus
}
#endif

#endif /* D_NET_CMD_H */
