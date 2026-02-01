/*
FILE: source/domino/net/d_net_cmd.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_cmd
RESPONSIBILITY: Defines internal contract for `d_net_cmd`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
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
