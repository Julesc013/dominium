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
#define D_NET_SCHEMA_CMD_BUILD_V1         0x1002u
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
