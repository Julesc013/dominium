/*
FILE: source/domino/build/d_build.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / build/d_build
RESPONSIBILITY: Defines internal contract for `d_build`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Construction and placement API (C89). */
#ifndef D_BUILD_H
#define D_BUILD_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "core/dg_pose.h"
#include "world/frame/dg_anchor.h"
#include "world/d_world.h"
#include "content/d_content.h"
#include "core/d_org.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    D_BUILD_KIND_NONE      = 0u,
    D_BUILD_KIND_STRUCTURE = 1u,
    D_BUILD_KIND_SPLINE    = 2u
};

enum {
    D_BUILD_FLAG_NONE = 0u
};

typedef struct d_build_request_s {
    u32                  request_id;
    u32                  owner_eid;            /* player or system entity controlling build */
    d_org_id             owner_org;            /* organization/company owning placed assets */
    d_structure_proto_id structure_id;         /* for structures */
    d_spline_profile_id  spline_profile_id;    /* for splines */

    /* Placement contract (authoritative):
     * - anchor: stable reference to authoring primitives
     * - offset: local pose relative to the anchor
     *
     * All fields MUST already be quantized before validation/commit.
     */
    dg_anchor anchor;
    dg_pose   offset;

    u16    kind;                               /* D_BUILD_KIND_* */
    u16    flags;                              /* D_BUILD_FLAG_* */
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
