/*
FILE: source/domino/net/d_net_schema.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_schema
RESPONSIBILITY: Defines internal contract for `d_net_schema`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Net protocol schemas and TLV tags (C89). */
#ifndef D_NET_SCHEMA_H
#define D_NET_SCHEMA_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Network protocol version for packet framing and negotiation. */
#define D_NET_PROTO_VERSION 1u

/* Schema IDs (u16) */
#define D_NET_SCHEMA_HANDSHAKE_V1         0x1101u
#define D_NET_SCHEMA_HANDSHAKE_REPLY_V1   0x1102u
#define D_NET_SCHEMA_SNAPSHOT_V1          0x1201u
#define D_NET_SCHEMA_TICK_V1              0x1202u
#define D_NET_SCHEMA_HASH_V1              0x1203u

#define D_NET_SCHEMA_CMD_INPUT_V1         0x1001u
#define D_NET_SCHEMA_CMD_BUILD_V1         0x1002u /* legacy (raw world-space); deprecated */
#define D_NET_SCHEMA_CMD_BUILD_V2         0x1006u /* anchor+pose contract */
#define D_NET_SCHEMA_CMD_BLUEPRINT_V1     0x1003u
#define D_NET_SCHEMA_CMD_POLICY_V1        0x1004u
#define D_NET_SCHEMA_CMD_RESEARCH_V1      0x1005u

/* Shared handshake tags */
enum {
    D_NET_TLV_HANDSHAKE_SUITE_VERSION    = 0x01u,
    D_NET_TLV_HANDSHAKE_CORE_VERSION     = 0x02u,
    D_NET_TLV_HANDSHAKE_NET_PROTO_VER    = 0x03u,
    D_NET_TLV_HANDSHAKE_COMPAT_PROFILE   = 0x04u,
    D_NET_TLV_HANDSHAKE_ROLE             = 0x05u
};

/* Handshake reply tags */
enum {
    D_NET_TLV_HANDSHAKE_REPLY_RESULT         = 0x01u, /* u32: 0=ok, nonzero=reject */
    D_NET_TLV_HANDSHAKE_REPLY_REASON_CODE    = 0x02u, /* u32: product-defined */
    D_NET_TLV_HANDSHAKE_REPLY_ASSIGNED_PEER  = 0x03u, /* u32 */
    D_NET_TLV_HANDSHAKE_REPLY_SESSION_ID     = 0x04u, /* u32 */
    D_NET_TLV_HANDSHAKE_REPLY_TICK_RATE      = 0x05u, /* u32 */
    D_NET_TLV_HANDSHAKE_REPLY_TICK           = 0x06u  /* u32 */
};

/* Snapshot tags */
enum {
    D_NET_TLV_SNAPSHOT_TICK  = 0x01u, /* u32 */
    D_NET_TLV_SNAPSHOT_DATA  = 0x02u  /* bytes (save blob) */
};

/* Tick tags */
enum {
    D_NET_TLV_TICK_TICK      = 0x01u /* u32 */
};

/* Hash tags */
enum {
    D_NET_TLV_HASH_TICK      = 0x01u, /* u32 */
    D_NET_TLV_HASH_WORLD     = 0x02u  /* u64 */
};

/* Command envelope tags (inside CMD packet payload) */
enum {
    D_NET_TLV_CMD_ID         = 0x01u, /* u32 */
    D_NET_TLV_CMD_SOURCE     = 0x02u, /* u32 */
    D_NET_TLV_CMD_TICK       = 0x03u, /* u32 */
    D_NET_TLV_CMD_SCHEMA_ID  = 0x04u, /* u32 */
    D_NET_TLV_CMD_SCHEMA_VER = 0x05u, /* u16 or u32 */
    D_NET_TLV_CMD_PAYLOAD    = 0x06u  /* bytes (schema-specific TLV) */
};

/* CMD_BUILD_V1 payload tags */
enum {
    D_NET_TLV_BUILD_KIND               = 0x01u, /* u32: matches D_BUILD_KIND_* */
    D_NET_TLV_BUILD_STRUCTURE_PROTO_ID = 0x02u, /* u32 */
    D_NET_TLV_BUILD_SPLINE_PROFILE_ID  = 0x03u, /* u32 */
    D_NET_TLV_BUILD_POS_X              = 0x04u, /* q32_32 (i64) */
    D_NET_TLV_BUILD_POS_Y              = 0x05u, /* q32_32 (i64) */
    D_NET_TLV_BUILD_POS_Z              = 0x06u, /* q32_32 (i64) */
    D_NET_TLV_BUILD_POS2_X             = 0x07u, /* q32_32 (i64) */
    D_NET_TLV_BUILD_POS2_Y             = 0x08u, /* q32_32 (i64) */
    D_NET_TLV_BUILD_POS2_Z             = 0x09u, /* q32_32 (i64) */
    D_NET_TLV_BUILD_ROT_YAW            = 0x0Au, /* q16_16 (i32) */
    D_NET_TLV_BUILD_OWNER_ORG_ID       = 0x0Bu, /* u32 */
    D_NET_TLV_BUILD_FLAGS              = 0x0Cu, /* u32 */
    D_NET_TLV_BUILD_SPLINE_NODES       = 0x0Du  /* bytes: u16 count + nodes */
};

/* CMD_BUILD_V2 payload tags (anchor+pose contract; no raw world-space geometry).
 * All fixed-point scalars are dg_q (Q48.16) encoded as i64.
 */
enum {
    D_NET_TLV_BUILD2_KIND               = 0x01u, /* u32: matches D_BUILD_KIND_* */
    D_NET_TLV_BUILD2_STRUCTURE_PROTO_ID = 0x02u, /* u32 */
    D_NET_TLV_BUILD2_SPLINE_PROFILE_ID  = 0x03u, /* u32 */
    D_NET_TLV_BUILD2_OWNER_ORG_ID       = 0x04u, /* u32 */
    D_NET_TLV_BUILD2_FLAGS              = 0x05u, /* u32 */

    /* Anchor header */
    D_NET_TLV_BUILD2_ANCHOR_KIND        = 0x10u, /* u32: dg_anchor_kind */
    D_NET_TLV_BUILD2_HOST_FRAME         = 0x11u, /* u64: dg_frame_id */

    /* Anchor params (kind-dependent). */
    D_NET_TLV_BUILD2_TERRAIN_U          = 0x20u, /* i64 dg_q */
    D_NET_TLV_BUILD2_TERRAIN_V          = 0x21u, /* i64 dg_q */
    D_NET_TLV_BUILD2_TERRAIN_H          = 0x22u, /* i64 dg_q */

    D_NET_TLV_BUILD2_CORR_ALIGN_ID      = 0x30u, /* u64 */
    D_NET_TLV_BUILD2_CORR_S             = 0x31u, /* i64 dg_q */
    D_NET_TLV_BUILD2_CORR_T             = 0x32u, /* i64 dg_q */
    D_NET_TLV_BUILD2_CORR_H             = 0x33u, /* i64 dg_q */
    D_NET_TLV_BUILD2_CORR_ROLL          = 0x34u, /* i64 dg_q */

    D_NET_TLV_BUILD2_STRUCT_ID          = 0x40u, /* u64 */
    D_NET_TLV_BUILD2_STRUCT_SURFACE_ID  = 0x41u, /* u64 */
    D_NET_TLV_BUILD2_STRUCT_U           = 0x42u, /* i64 dg_q */
    D_NET_TLV_BUILD2_STRUCT_V           = 0x43u, /* i64 dg_q */
    D_NET_TLV_BUILD2_STRUCT_OFFSET      = 0x44u, /* i64 dg_q */

    D_NET_TLV_BUILD2_ROOM_ID            = 0x50u, /* u64 */
    D_NET_TLV_BUILD2_ROOM_SURFACE_ID    = 0x51u, /* u64 */
    D_NET_TLV_BUILD2_ROOM_U             = 0x52u, /* i64 dg_q */
    D_NET_TLV_BUILD2_ROOM_V             = 0x53u, /* i64 dg_q */
    D_NET_TLV_BUILD2_ROOM_OFFSET        = 0x54u, /* i64 dg_q */

    D_NET_TLV_BUILD2_SOCKET_ID          = 0x60u, /* u64 */
    D_NET_TLV_BUILD2_SOCKET_PARAM       = 0x61u, /* i64 dg_q */

    /* Local offset pose relative to anchor. */
    D_NET_TLV_BUILD2_OFF_POS_X          = 0x70u, /* i64 dg_q */
    D_NET_TLV_BUILD2_OFF_POS_Y          = 0x71u, /* i64 dg_q */
    D_NET_TLV_BUILD2_OFF_POS_Z          = 0x72u, /* i64 dg_q */

    D_NET_TLV_BUILD2_OFF_ROT_X          = 0x73u, /* i64 dg_q */
    D_NET_TLV_BUILD2_OFF_ROT_Y          = 0x74u, /* i64 dg_q */
    D_NET_TLV_BUILD2_OFF_ROT_Z          = 0x75u, /* i64 dg_q */
    D_NET_TLV_BUILD2_OFF_ROT_W          = 0x76u, /* i64 dg_q */

    D_NET_TLV_BUILD2_OFF_INCLINE        = 0x77u, /* i64 dg_q */
    D_NET_TLV_BUILD2_OFF_ROLL           = 0x78u  /* i64 dg_q */
};

/* CMD_RESEARCH_V1 payload tags */
enum {
    D_NET_TLV_RESEARCH_ORG_ID     = 0x01u, /* u32 */
    D_NET_TLV_RESEARCH_ACTIVE_ID  = 0x02u  /* u32 */
};

/* Register schema validators with the global TLV schema registry. */
void d_net_register_schemas(void);

#ifdef __cplusplus
}
#endif

#endif /* D_NET_SCHEMA_H */
