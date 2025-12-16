/*
FILE: source/domino/trans/d_trans_spline.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/d_trans_spline
RESPONSIBILITY: Defines internal contract for `d_trans_spline`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Generic spline-based transport runtime (C89). */
#ifndef D_TRANS_SPLINE_H
#define D_TRANS_SPLINE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "core/d_org.h"
#include "world/d_world.h"
#include "content/d_content.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_spline_id;
typedef u16 d_spline_flags;

/* Spline node in world coordinates (anchor point). */
typedef struct d_spline_node_s {
    q32_32 x;
    q32_32 y;
    q32_32 z;
    q16_16 nx;
    q16_16 ny;
    q16_16 nz;
} d_spline_node;

/* Runtime spline instance (one logical segment/line). */
typedef struct d_spline_instance_s {
    d_spline_id         id;
    d_spline_profile_id profile_id;
    d_org_id            owner_org;
    d_spline_flags      flags;

    /* Node indices into spline node pool. Minimal: start + end; midpoints optional. */
    u16                 node_start_index;
    u16                 node_count;

    /* Optional endpoint attachments (generic ports on world entities). */
    u32                 endpoint_a_eid;
    u16                 endpoint_a_port_kind;
    u16                 endpoint_a_port_index;
    u32                 endpoint_b_eid;
    u16                 endpoint_b_port_kind;
    u16                 endpoint_b_port_index;

    /* Cached length for simulation. */
    q16_16              length;
} d_spline_instance;

/* Generic transport profile classification. */
enum {
    D_SPLINE_TYPE_ITEM    = 1u,
    D_SPLINE_TYPE_VEHICLE = 2u,
    D_SPLINE_TYPE_FLUID   = 3u
};

/* Resolved spline profile (loaded from content). */
typedef struct d_spline_profile_runtime_s {
    d_spline_profile_id id;
    u16                 type;      /* D_SPLINE_TYPE_* */
    u16                 flags;     /* bidirectional, grade limits, etc. */
    q16_16              base_speed;
    q16_16              max_grade; /* tan(theta) */
    q16_16              capacity;
    d_content_tag        tags;
    d_tlv_blob           params;   /* model-specific params */
} d_spline_profile_runtime;

/* Initialize/free world-local transport state. */
int  d_trans_init(d_world *w);
void d_trans_shutdown(d_world *w);

/* Spline instance management (placed by construction). */
d_spline_id d_trans_spline_create(
    d_world                 *w,
    const d_spline_node     *nodes,
    u16                      node_count,
    d_spline_profile_id      profile_id,
    d_spline_flags           flags,
    d_org_id                 owner_org
);
int d_trans_spline_destroy(d_world *w, d_spline_id id);

int d_trans_spline_get(const d_world *w, d_spline_id id, d_spline_instance *out);

/* Attach endpoints to entity ports (0 clears). */
int d_trans_spline_set_endpoints(
    d_world     *w,
    d_spline_id  spline_id,
    u32          endpoint_a_eid,
    u16          endpoint_a_port_kind,
    u16          endpoint_a_port_index,
    u32          endpoint_b_eid,
    u16          endpoint_b_port_kind,
    u16          endpoint_b_port_index
);

/* Iteration helpers for UI/debug. */
u32 d_trans_spline_count(const d_world *w);
int d_trans_spline_get_by_index(const d_world *w, u32 index, d_spline_instance *out);

/* Copy spline nodes by pool range (node_start_index/node_count). */
int d_trans_spline_copy_nodes(
    const d_world     *w,
    u16                node_start_index,
    u16                node_count,
    d_spline_node     *out_nodes,
    u16                out_capacity,
    u16               *out_count
);

/* Resolve a profile from content into a runtime description. */
int d_trans_profile_resolve(
    const d_world             *w,
    d_spline_profile_id        profile_id,
    d_spline_profile_runtime  *out
);

/* Sample a point along a spline polyline at param in [0,1]. */
int d_trans_spline_sample_pos(
    const d_world *w,
    d_spline_id    spline_id,
    q16_16         param,
    q32_32        *out_x,
    q32_32        *out_y,
    q32_32        *out_z
);

/* Tick transport simulation. */
void d_trans_tick(d_world *w, u32 ticks);

#ifdef __cplusplus
}
#endif

#endif /* D_TRANS_SPLINE_H */
