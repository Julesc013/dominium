/*
FILE: source/domino/net/d_net_schema.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_schema
RESPONSIBILITY: Implements `d_net_schema`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

static int d_net_schema_require_u64_bytes(const d_tlv_blob *in, u32 tag) {
    u32 off = 0u;
    u32 t;
    d_tlv_blob payload;
    int rc;
    if (!in) return -1;
    while ((rc = d_tlv_kv_next(in, &off, &t, &payload)) == 0) {
        if (t == tag) {
            return (payload.len == 8u) ? 0 : -1;
        }
    }
    return -1;
}

static int d_net_schema_require_bytes(const d_tlv_blob *in,
                                      u32 tag,
                                      const unsigned char **out_ptr,
                                      u32 *out_len) {
    u32 off = 0u;
    u32 t;
    d_tlv_blob payload;
    int rc;
    if (!in || !out_ptr || !out_len) return -1;
    while ((rc = d_tlv_kv_next(in, &off, &t, &payload)) == 0) {
        if (t == tag) {
            *out_ptr = payload.ptr;
            *out_len = payload.len;
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

static int d_net_schema_validate_build_v2(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    u32 kind = 0u;
    u32 anchor_kind = 0u;
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u32(in, D_NET_TLV_BUILD2_KIND, &kind) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_BUILD2_ANCHOR_KIND, &anchor_kind) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_BUILD2_OWNER_ORG_ID, (u32 *)0) != 0) return -1;

    /* host frame is required (0 is allowed for world). */
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_BUILD2_HOST_FRAME) != 0) return -1;

    if (kind == 1u) {
        if (d_net_schema_require_u32(in, D_NET_TLV_BUILD2_STRUCTURE_PROTO_ID, (u32 *)0) != 0) return -1;
    } else if (kind == 2u) {
        if (d_net_schema_require_u32(in, D_NET_TLV_BUILD2_SPLINE_PROFILE_ID, (u32 *)0) != 0) return -1;
    } else {
        return -1;
    }

    if (anchor_kind == 0u) {
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

static int d_net_schema_validate_warp(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    u32 factor = 0u;
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u32(in, D_NET_TLV_WARP_FACTOR, &factor) != 0) return -1;
    if (factor == 0u) return -1;
    return 0;
}

static int d_net_schema_validate_maneuver(
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
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_MANEUVER_FRAME_ID) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_MANEUVER_DV_X) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_MANEUVER_DV_Y) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_MANEUVER_DV_Z) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_construction_place(
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
    if (d_net_schema_require_u32(in, D_NET_TLV_CONSTRUCTION_TYPE_ID, &tmp) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_CONSTRUCTION_BODY_ID) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_CONSTRUCTION_LAT_TURNS, &tmp) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_CONSTRUCTION_LON_TURNS, &tmp) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_CONSTRUCTION_ORIENT, &tmp) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_construction_remove(
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
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_CONSTRUCTION_INSTANCE_ID) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_station_create(
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
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_STATION_ID) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_STATION_BODY_ID) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_STATION_FRAME_ID) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_route_create(
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
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_ROUTE_ID) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_ROUTE_SRC_STATION_ID) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_ROUTE_DST_STATION_ID) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_ROUTE_DURATION_TICKS) != 0) return -1;
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_ROUTE_CAPACITY_UNITS) != 0) return -1;
    return 0;
}

static int d_net_schema_validate_transfer_schedule(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    u32 count = 0u;
    const unsigned char *items = 0;
    u32 items_len = 0u;
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (d_net_schema_require_u64_bytes(in, D_NET_TLV_TRANSFER_ROUTE_ID) != 0) return -1;
    if (d_net_schema_require_u32(in, D_NET_TLV_TRANSFER_ITEM_COUNT, &count) != 0) return -1;
    if (d_net_schema_require_bytes(in, D_NET_TLV_TRANSFER_ITEMS, &items, &items_len) != 0) return -1;
    if (!items || count == 0u) return -1;
    if (items_len != (count * 16u)) return -1;
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
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_BUILD_V2;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_build_v2;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_RESEARCH_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_research;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_WARP_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_warp;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_ORBIT_MANEUVER_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_maneuver;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_CONSTRUCTION_PLACE_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_construction_place;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_CONSTRUCTION_REMOVE_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_construction_remove;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_STATION_CREATE_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_station_create;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_ROUTE_CREATE_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_route_create;
    (void)d_tlv_schema_register(&desc);

    memset(&desc, 0, sizeof(desc));
    desc.schema_id = (d_tlv_schema_id)D_NET_SCHEMA_CMD_TRANSFER_SCHEDULE_V1;
    desc.version = 1u;
    desc.validate_fn = d_net_schema_validate_transfer_schedule;
    (void)d_tlv_schema_register(&desc);

    registered = 1;
}
