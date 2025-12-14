#include <string.h>

#include "d_net_schema.h"
#include "core/d_tlv_schema.h"
#include "core/d_tlv_kv.h"

static int d_net_schema_require_u32(const d_tlv_blob *in, u32 tag, u32 *out_val) {
    u32 off = 0u;
    u32 t;
    d_tlv_blob payload;
    int rc;
    while ((rc = d_tlv_kv_next(in, &off, &t, &payload)) == 0) {
        if (t == tag) {
            if (out_val) {
                return d_tlv_kv_read_u32(&payload, out_val);
            }
            return 0;
        }
    }
    return -1;
}

static int d_net_schema_validate_handshake(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    u32 tmp = 0u;
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u32(in, D_NET_TLV_HANDSHAKE_SUITE_VERSION, &tmp) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_HANDSHAKE_CORE_VERSION, &tmp) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_HANDSHAKE_NET_PROTO_VER, &tmp) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_handshake_reply(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    u32 tmp = 0u;
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u32(in, D_NET_TLV_HANDSHAKE_REPLY_RESULT, &tmp) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_snapshot(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    u32 tmp = 0u;
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u32(in, D_NET_TLV_SNAPSHOT_TICK, &tmp) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_build(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    u32 kind = 0u;
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u32(in, D_NET_TLV_BUILD_KIND, &kind) != 0) return -1;
    if (kind == 1u) {
        /* structure */
        if (d_net_schema_require_u32(in, D_NET_TLV_BUILD_STRUCTURE_PROTO_ID, (u32 *)0) != 0) return -1;
        if (d_net_schema_require_u32(in, D_NET_TLV_BUILD_OWNER_ORG_ID, (u32 *)0) != 0) return -1;
    } else if (kind == 2u) {
        /* spline */
        if (d_net_schema_require_u32(in, D_NET_TLV_BUILD_SPLINE_PROFILE_ID, (u32 *)0) != 0) return -1;
        if (d_net_schema_require_u32(in, D_NET_TLV_BUILD_OWNER_ORG_ID, (u32 *)0) != 0) return -1;
    } else {
        return -1;
    }
    return 0;
}

static int d_net_schema_validate_research(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u32(in, D_NET_TLV_RESEARCH_ORG_ID, (u32 *)0) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_RESEARCH_ACTIVE_ID, (u32 *)0) != 0) return -1;
    return 0;
}

void d_net_register_schemas(void) {
    static int registered = 0;
    d_tlv_schema_desc desc;
    if (registered) {
        return;
    }

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_HANDSHAKE_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_handshake;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_HANDSHAKE_REPLY_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_handshake_reply;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_SNAPSHOT_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_snapshot;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_BUILD_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_build;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_RESEARCH_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_research;
    (void)d_tlv_schema_register(&desc);

    registered = 1;
}

