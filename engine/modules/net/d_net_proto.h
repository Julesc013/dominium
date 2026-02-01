/*
FILE: source/domino/net/d_net_proto.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_proto
RESPONSIBILITY: Defines internal contract for `d_net_proto`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Net packet framing and TLV encode/decode helpers (C89). */
#ifndef D_NET_PROTO_H
#define D_NET_PROTO_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "net/d_net_cmd.h"
#include "net/d_net_session.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum d_net_msg_type_e {
    D_NET_MSG_NONE = 0,
    D_NET_MSG_HANDSHAKE = 1,
    D_NET_MSG_HANDSHAKE_REPLY = 2,
    D_NET_MSG_SNAPSHOT = 3,
    D_NET_MSG_TICK = 4,
    D_NET_MSG_CMD = 5,
    D_NET_MSG_HASH = 6,
    D_NET_MSG_ERROR = 7,
    D_NET_MSG_QOS = 8
} d_net_msg_type;

typedef struct d_net_handshake_s {
    u32 suite_version;
    u32 core_version;
    u32 net_proto_version;
    u32 compat_profile;
    u32 role;
} d_net_handshake;

typedef struct d_net_handshake_reply_s {
    u32 result;          /* 0=ok, nonzero=reject */
    u32 reason_code;     /* product-defined */
    d_peer_id assigned_peer;
    d_session_id session_id;
    u32 tick_rate;
    u32 tick;
} d_net_handshake_reply;

typedef struct d_net_snapshot_s {
    u32 tick;
    d_tlv_blob data;     /* bytes; snapshot/save */
} d_net_snapshot;

typedef struct d_net_tick_s {
    u32 tick;
} d_net_tick;

typedef struct d_net_hash_s {
    u32 tick;
    u64 world_hash;
} d_net_hash;

typedef struct d_net_error_s {
    u32 code;
} d_net_error;

typedef struct d_net_qos_s {
    d_tlv_blob data;     /* bytes; QoS TLV payload */
} d_net_qos;

/* Parse just the frame header and return a payload view. */
int d_net_decode_frame(
    const void     *buf,
    u32             size,
    d_net_msg_type *out_type,
    d_tlv_blob     *out_payload
);

/* Encode/decode command packets. */
int d_net_encode_cmd(const d_net_cmd *cmd, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_cmd(const void *buf, u32 size, d_net_cmd *out_cmd);

int d_net_encode_handshake(const d_net_handshake *hs, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_handshake(const void *buf, u32 size, d_net_handshake *out_hs);

int d_net_encode_handshake_reply(const d_net_handshake_reply *r, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_handshake_reply(const void *buf, u32 size, d_net_handshake_reply *out_r);

int d_net_encode_snapshot(const d_net_snapshot *snap, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_snapshot(const void *buf, u32 size, d_net_snapshot *out_snap);

int d_net_encode_tick(const d_net_tick *t, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_tick(const void *buf, u32 size, d_net_tick *out_t);

int d_net_encode_hash(const d_net_hash *h, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_hash(const void *buf, u32 size, d_net_hash *out_h);

int d_net_encode_error(const d_net_error *e, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_error(const void *buf, u32 size, d_net_error *out_e);

int d_net_encode_qos(const d_net_qos *q, void *buf, u32 buf_size, u32 *out_size);
int d_net_decode_qos(const void *buf, u32 size, d_net_qos *out_q);

/* Free heap-owned buffers returned by decode_snapshot. */
void d_net_snapshot_free(d_net_snapshot *snap);
void d_net_qos_free(d_net_qos *qos);

#ifdef __cplusplus
}
#endif

#endif /* D_NET_PROTO_H */
