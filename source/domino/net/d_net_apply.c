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
#include "trans/d_trans_spline.h"
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
    q32_32 x = 0;
    q32_32 y = 0;
    q32_32 z = 0;
    q32_32 x2 = 0;
    q32_32 y2 = 0;
    q32_32 z2 = 0;
    q16_16 yaw = 0;

    d_spline_node spline_nodes[D_NET_APPLY_MAX_SPLINE_NODES];
    u16 spline_node_count = 0u;

    if (!w || !cmd) {
        return -1;
    }

    memset(&req, 0, sizeof(req));
    memset(spline_nodes, 0, sizeof(spline_nodes));

    while ((rc = d_tlv_kv_next(&cmd->payload, &off, &tag, &payload)) == 0) {
        if (tag == D_NET_TLV_BUILD_KIND) {
            (void)d_tlv_kv_read_u32(&payload, &kind);
        } else if (tag == D_NET_TLV_BUILD_STRUCTURE_PROTO_ID) {
            (void)d_tlv_kv_read_u32(&payload, &struct_id);
        } else if (tag == D_NET_TLV_BUILD_SPLINE_PROFILE_ID) {
            (void)d_tlv_kv_read_u32(&payload, &spline_profile_id);
        } else if (tag == D_NET_TLV_BUILD_OWNER_ORG_ID) {
            (void)d_tlv_kv_read_u32(&payload, &owner_org_id);
        } else if (tag == D_NET_TLV_BUILD_FLAGS) {
            (void)d_tlv_kv_read_u32(&payload, &flags);
        } else if (tag == D_NET_TLV_BUILD_POS_X) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) x = (q32_32)tmp;
        } else if (tag == D_NET_TLV_BUILD_POS_Y) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) y = (q32_32)tmp;
        } else if (tag == D_NET_TLV_BUILD_POS_Z) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) z = (q32_32)tmp;
        } else if (tag == D_NET_TLV_BUILD_POS2_X) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) x2 = (q32_32)tmp;
        } else if (tag == D_NET_TLV_BUILD_POS2_Y) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) y2 = (q32_32)tmp;
        } else if (tag == D_NET_TLV_BUILD_POS2_Z) {
            i64 tmp = 0;
            if (d_net_tlv_read_i64(&payload, &tmp) == 0) z2 = (q32_32)tmp;
        } else if (tag == D_NET_TLV_BUILD_ROT_YAW) {
            (void)d_tlv_kv_read_q16_16(&payload, &yaw);
        } else if (tag == D_NET_TLV_BUILD_SPLINE_NODES) {
            const unsigned char *p = payload.ptr;
            u32 remaining = payload.len;
            u16 count = 0u;
            u16 i;
            if (!p || remaining < 2u) {
                continue;
            }
            memcpy(&count, p, 2u);
            p += 2u;
            remaining -= 2u;
            if (count > D_NET_APPLY_MAX_SPLINE_NODES) {
                count = (u16)D_NET_APPLY_MAX_SPLINE_NODES;
            }
            for (i = 0u; i < count; ++i) {
                i64 nx = 0;
                i64 ny = 0;
                i64 nz = 0;
                if (remaining < 24u) {
                    break;
                }
                memcpy(&nx, p, 8u); p += 8u;
                memcpy(&ny, p, 8u); p += 8u;
                memcpy(&nz, p, 8u); p += 8u;
                remaining -= 24u;
                spline_nodes[i].x = (q32_32)nx;
                spline_nodes[i].y = (q32_32)ny;
                spline_nodes[i].z = (q32_32)nz;
                spline_node_count = (u16)(i + 1u);
            }
        }
    }

    req.request_id = cmd->id;
    req.owner_eid = 0u;
    req.owner_org = (d_org_id)owner_org_id;
    req.kind = (u16)kind;
    req.flags = (u16)flags;
    req.structure_id = (d_structure_proto_id)struct_id;
    req.spline_profile_id = (d_spline_profile_id)spline_profile_id;
    req.pos_x = x;
    req.pos_y = y;
    req.pos_z = z;
    req.pos2_x = x2;
    req.pos2_y = y2;
    req.pos2_z = z2;
    req.rot_yaw = yaw;

    if (req.kind == D_BUILD_KIND_SPLINE) {
        req.spline_nodes = spline_nodes;
        req.spline_node_count = spline_node_count;
    }

    {
        char err[128];
        d_spline_id out_spline = 0u;
        u32 out_struct_eid = 0u;
        memset(err, 0, sizeof(err));
        if (d_build_validate(w, &req, err, (u32)sizeof(err)) != 0) {
            fprintf(stderr, "d_net_apply_build: validate failed: %s\n", err);
            return -2;
        }
        if (d_build_commit(w, &req, &out_spline, &out_struct_eid) != 0) {
            fprintf(stderr, "d_net_apply_build: commit failed\n");
            return -3;
        }
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
    if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_BUILD_V1) {
        return d_net_apply_build(w, cmd);
    }
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
