/* Construction and placement API (C89). */
#ifndef D_BUILD_H
#define D_BUILD_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "content/d_content.h"
#include "trans/d_trans_spline.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    D_BUILD_KIND_NONE      = 0u,
    D_BUILD_KIND_STRUCTURE = 1u,
    D_BUILD_KIND_SPLINE    = 2u
};

enum {
    D_BUILD_FLAG_NONE          = 0u,
    D_BUILD_FLAG_SNAP_TERRAIN  = 1u << 0,
    D_BUILD_FLAG_REQUIRE_PORTS = 1u << 1
};

typedef struct d_build_request_s {
    u32                  request_id;
    u32                  owner_eid;            /* player or system entity controlling build */
    d_structure_proto_id structure_id;         /* for structures */
    d_spline_profile_id  spline_profile_id;    /* for splines */

    /* Placement coordinates. For structures: anchor; for splines: endpoints. */
    q32_32 pos_x, pos_y, pos_z;
    q16_16 rot_yaw;                            /* turn fraction in Q16.16 (1.0 = full turn) */
    q16_16 slope;                              /* optional hint */

    q32_32 pos2_x, pos2_y, pos2_z;             /* optional second endpoint for splines */
    u16    kind;                               /* D_BUILD_KIND_* */
    u16    flags;                              /* D_BUILD_FLAG_* */

    /* Optional explicit spline polyline nodes (when kind==SPLINE). */
    const d_spline_node *spline_nodes;
    u16                 spline_node_count;
} d_build_request;

/* Validate and commit placement. */
int d_build_validate(
    d_world               *w,
    const d_build_request *req,
    char                  *err_buf,
    u32                    err_buf_size
);

int d_build_commit(
    d_world               *w,
    const d_build_request *req,
    d_spline_id           *out_spline_id,
    u32                   *out_struct_eid
);

/* Optional placement metadata (foundations etc.). */
int d_build_get_foundation_down(
    const d_world *w,
    u32            struct_id,
    q16_16         out_down[4]
);

/* Subsystem registration hook (called once at startup). */
void d_build_register_subsystem(void);

/* Free world-local build state (optional; called by products on shutdown). */
void d_build_shutdown(d_world *w);

/* World-state validator hook. */
int d_build_validate_world(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_BUILD_H */
