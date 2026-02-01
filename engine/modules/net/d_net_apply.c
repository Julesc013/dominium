/*
FILE: source/domino/net/d_net_apply.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net_apply
RESPONSIBILITY: Implements `d_net_apply`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "d_net_apply.h"
#include "d_net_cmd.h"
#include "d_net_schema.h"
#include "core/d_tlv_kv.h"

#include "world/d_world.h"
#include "build/d_build.h"
#include "research/d_research_state.h"
#include "domino/core/fixed.h"

enum {
    D_NET_APPLY_MAX_CMDS = D_NET_CMD_MAX_PER_TICK,
    D_NET_APPLY_MAX_SPLINE_NODES = 16u
};

static d_net_tick_cmds_observer_fn g_tick_observer = (d_net_tick_cmds_observer_fn)0;
static void *g_tick_observer_user = (void *)0;

void d_net_set_tick_cmds_observer(d_net_tick_cmds_observer_fn fn, void *user) {
    g_tick_observer = fn;
    g_tick_observer_user = user;
}

static int d_net_tlv_read_i64(const d_tlv_blob *payload, i64 *out) {
    if (!payload || !out || !payload->ptr) {
        return -1;
    }
    if (payload->len != 8u) {
        return -1;
    }
    memcpy(out, payload->ptr, 8u);
    return 0;
}

static int d_net_tlv_read_u64(const d_tlv_blob *payload, u64 *out) {
    if (!payload || !out || !payload->ptr) {
        return -1;
    }
    if (payload->len != 8u) {
        return -1;
    }
    memcpy(out, payload->ptr, 8u);
    return 0;
}

static int d_net_cmd_less(const d_net_cmd *a, const d_net_cmd *b) {
    u32 min_len;
    int cmp;
    if (!a || !b) {
        return 0;
    }
    if (a->source_peer != b->source_peer) return a->source_peer < b->source_peer;
    if (a->id != b->id) return a->id < b->id;
    if (a->schema_id != b->schema_id) return a->schema_id < b->schema_id;
    if (a->schema_ver != b->schema_ver) return a->schema_ver < b->schema_ver;
    if (a->payload.len != b->payload.len) return a->payload.len < b->payload.len;
    min_len = a->payload.len;
    if (min_len > 0u && a->payload.ptr && b->payload.ptr) {
        cmp = memcmp(a->payload.ptr, b->payload.ptr, min_len);
        return cmp < 0;
    }
    return 0;
}

static void d_net_cmd_insertion_sort(d_net_cmd *cmds, u32 count) {
    u32 i;
    if (!cmds || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        d_net_cmd key = cmds[i];
        u32 j = i;
        while (j > 0u && d_net_cmd_less(&key, &cmds[j - 1u])) {
            cmds[j] = cmds[j - 1u];
            j -= 1u;
        }
        cmds[j] = key;
    }
}

static int d_net_apply_build(d_world *w, const d_net_cmd *cmd) {
    d_build_request req;
    u32 off = 0u;
    u32 tag;
    d_tlv_blob payload;
    int rc;

    u32 kind = 0u;
    u32 struct_id = 0u;
    u32 spline_profile_id = 0u;
    u32 owner_org_id = 0u;
    u32 flags = 0u;

    u32 anchor_kind = 0u;
    u64 host_frame = 0u;

    /* Anchor params. */
    u64 id0 = 0u;
    u64 id1 = 0u;
    dg_q q0 = 0;
    dg_q q1 = 0;
    dg_q q2 = 0;
    dg_q q3 = 0;

    if (!w || !cmd) {
        return -1;
    }

    memset(&req, 0, sizeof(req));
    req.offset = dg_pose_identity();

    while ((rc = d_tlv_kv_next(&cmd->payload, &off, &tag, &payload)) == 0) {
        if (tag == D_NET_TLV_BUILD2_KIND) {
            (void)d_tlv_kv_read_u32(&payload, &kind);
        } else if (tag == D_NET_TLV_BUILD2_STRUCTURE_PROTO_ID) {
            (void)d_tlv_kv_read_u32(&payload, &struct_id);
        } else if (tag == D_NET_TLV_BUILD2_SPLINE_PROFILE_ID) {
            (void)d_tlv_kv_read_u32(&payload, &spline_profile_id);
        } else if (tag == D_NET_TLV_BUILD2_OWNER_ORG_ID) {
            (void)d_tlv_kv_read_u32(&payload, &owner_org_id);
        } else if (tag == D_NET_TLV_BUILD2_FLAGS) {
            (void)d_tlv_kv_read_u32(&payload, &flags);
        } else if (tag == D_NET_TLV_BUILD2_ANCHOR_KIND) {
            (void)d_tlv_kv_read_u32(&payload, &anchor_kind);
        } else if (tag == D_NET_TLV_BUILD2_HOST_FRAME) {
            (void)d_net_tlv_read_u64(&payload, &host_frame);
        } else if (tag == D_NET_TLV_BUILD2_TERRAIN_U) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q0 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_TERRAIN_V) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q1 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_TERRAIN_H) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q2 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_CORR_ALIGN_ID) {
            (void)d_net_tlv_read_u64(&payload, &id0);
        } else if (tag == D_NET_TLV_BUILD2_CORR_S) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q0 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_CORR_T) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q1 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_CORR_H) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q2 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_CORR_ROLL) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q3 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_STRUCT_ID) {
            (void)d_net_tlv_read_u64(&payload, &id0);
        } else if (tag == D_NET_TLV_BUILD2_STRUCT_SURFACE_ID) {
            (void)d_net_tlv_read_u64(&payload, &id1);
        } else if (tag == D_NET_TLV_BUILD2_STRUCT_U) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q0 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_STRUCT_V) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q1 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_STRUCT_OFFSET) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q2 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_ROOM_ID) {
            (void)d_net_tlv_read_u64(&payload, &id0);
        } else if (tag == D_NET_TLV_BUILD2_ROOM_SURFACE_ID) {
            (void)d_net_tlv_read_u64(&payload, &id1);
        } else if (tag == D_NET_TLV_BUILD2_ROOM_U) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q0 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_ROOM_V) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q1 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_ROOM_OFFSET) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q2 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_SOCKET_ID) {
            (void)d_net_tlv_read_u64(&payload, &id0);
        } else if (tag == D_NET_TLV_BUILD2_SOCKET_PARAM) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) q0 = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_POS_X) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.pos.x = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_POS_Y) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.pos.y = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_POS_Z) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.pos.z = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_ROT_X) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.rot.x = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_ROT_Y) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.rot.y = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_ROT_Z) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.rot.z = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_ROT_W) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.rot.w = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_INCLINE) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.incline = (dg_q)tmp;
        } else if (tag == D_NET_TLV_BUILD2_OFF_ROLL) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) req.offset.roll = (dg_q)tmp;
        }
    }

    req.request_id = cmd->id;
    req.owner_eid = 0u;
    req.owner_org = (d_org_id)owner_org_id;
    req.kind = (u16)kind;
    req.flags = (u16)flags;
    req.structure_id = (d_structure_proto_id)struct_id;
    req.spline_profile_id = (d_spline_profile_id)spline_profile_id;

    req.anchor.kind = (dg_anchor_kind)anchor_kind;
    req.anchor.host_frame = (dg_frame_id)host_frame;

    /* Fill kind-dependent anchor payload from parsed fields. */
    if (req.anchor.kind == DG_ANCHOR_TERRAIN) {
        req.anchor.u.terrain.u = q0;
        req.anchor.u.terrain.v = q1;
        req.anchor.u.terrain.h = q2;
    } else if (req.anchor.kind == DG_ANCHOR_CORRIDOR_TRANS) {
        req.anchor.u.corridor.alignment_id = id0;
        req.anchor.u.corridor.s = q0;
        req.anchor.u.corridor.t = q1;
        req.anchor.u.corridor.h = q2;
        req.anchor.u.corridor.roll = q3;
    } else if (req.anchor.kind == DG_ANCHOR_STRUCT_SURFACE) {
        req.anchor.u.struct_surface.structure_id = id0;
        req.anchor.u.struct_surface.surface_id = id1;
        req.anchor.u.struct_surface.u = q0;
        req.anchor.u.struct_surface.v = q1;
        req.anchor.u.struct_surface.offset = q2;
    } else if (req.anchor.kind == DG_ANCHOR_ROOM_SURFACE) {
        req.anchor.u.room_surface.room_id = id0;
        req.anchor.u.room_surface.surface_id = id1;
        req.anchor.u.room_surface.u = q0;
        req.anchor.u.room_surface.v = q1;
        req.anchor.u.room_surface.offset = q2;
    } else if (req.anchor.kind == DG_ANCHOR_SOCKET) {
        req.anchor.u.socket.socket_id = id0;
        req.anchor.u.socket.param = q0;
    }

    {
        char err[128];
        memset(err, 0, sizeof(err));
        if (d_build_validate(w, &req, err, (u32)sizeof(err)) != 0) {
            fprintf(stderr, "d_net_apply_build: validate failed: %s\n", err);
            return -2;
        }
        /* No BUILD commit in this prompt. Intents are validated but not applied. */
    }

    return 0;
}

static int d_net_apply_research(d_world *w, const d_net_cmd *cmd) {
    u32 off = 0u;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u32 org_id = 0u;
    u32 active_id = 0u;
    (void)w;

    if (!cmd) {
        return -1;
    }

    while ((rc = d_tlv_kv_next(&cmd->payload, &off, &tag, &payload)) == 0) {
        if (tag == D_NET_TLV_RESEARCH_ORG_ID) {
            (void)d_tlv_kv_read_u32(&payload, &org_id);
        } else if (tag == D_NET_TLV_RESEARCH_ACTIVE_ID) {
            (void)d_tlv_kv_read_u32(&payload, &active_id);
        }
    }

    if (org_id == 0u || active_id == 0u) {
        return -1;
    }
    return d_research_set_active((d_org_id)org_id, (d_research_id)active_id);
}

static int d_net_apply_cmd(d_world *w, const d_net_cmd *cmd) {
    if (!w || !cmd) {
        return -1;
    }
    if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_BUILD_V2) return d_net_apply_build(w, cmd);
    if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_RESEARCH_V1) {
        return d_net_apply_research(w, cmd);
    }
    /* Unknown/unsupported schemas are ignored deterministically. */
    return 0;
}

int d_net_apply_for_tick(struct d_world *w, u32 tick) {
    d_net_cmd cmds[D_NET_APPLY_MAX_CMDS];
    u32 cmd_count = 0u;
    u32 i;
    int rc;

    if (!w) {
        return -1;
    }

    memset(cmds, 0, sizeof(cmds));
    rc = d_net_cmd_dequeue_for_tick(tick, cmds, (u32)D_NET_APPLY_MAX_CMDS, &cmd_count);
    if (rc != 0 || cmd_count == 0u) {
        return rc;
    }

    d_net_cmd_insertion_sort(cmds, cmd_count);

    if (g_tick_observer) {
        g_tick_observer(g_tick_observer_user, w, tick, cmds, cmd_count);
    }

    for (i = 0u; i < cmd_count; ++i) {
        (void)d_net_apply_cmd(w, &cmds[i]);
        d_net_cmd_free(&cmds[i]);
    }

    return 0;
}
