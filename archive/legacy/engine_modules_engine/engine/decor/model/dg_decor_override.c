/*
FILE: source/domino/decor/model/dg_decor_override.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_override
RESPONSIBILITY: Implements `dg_decor_override`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR overrides (C89). */
#include "decor/model/dg_decor_override.h"

#include <string.h>

#include "core/det_invariants.h"

static dg_q dg_q_min(dg_q a, dg_q b) { return (a < b) ? a : b; }
static dg_q dg_q_max(dg_q a, dg_q b) { return (a > b) ? a : b; }

void dg_decor_override_clear(dg_decor_override *ovr) {
    if (!ovr) return;
    memset(ovr, 0, sizeof(*ovr));
}

int dg_decor_override_cmp_id(const dg_decor_override *a, const dg_decor_override *b) {
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP_U64(a->id, b->id);
}

void dg_decor_suppress_region_canon(dg_decor_suppress_region *r) {
    dg_q lo;
    dg_q hi;
    if (!r) return;

    lo = dg_q_min(r->u0, r->u1);
    hi = dg_q_max(r->u0, r->u1);
    r->u0 = lo; r->u1 = hi;

    lo = dg_q_min(r->v0, r->v1);
    hi = dg_q_max(r->v0, r->v1);
    r->v0 = lo; r->v1 = hi;

    lo = dg_q_min(r->s0, r->s1);
    hi = dg_q_max(r->s0, r->s1);
    r->s0 = lo; r->s1 = hi;

    lo = dg_q_min(r->param0, r->param1);
    hi = dg_q_max(r->param0, r->param1);
    r->param0 = lo; r->param1 = hi;
}

d_bool dg_decor_suppress_region_contains_anchor(const dg_decor_suppress_region *r, const dg_anchor *a) {
    if (!r || !a) return D_FALSE;

    if (a->kind == DG_ANCHOR_TERRAIN) {
        if (a->u.terrain.u < r->u0 || a->u.terrain.u > r->u1) return D_FALSE;
        if (a->u.terrain.v < r->v0 || a->u.terrain.v > r->v1) return D_FALSE;
        return D_TRUE;
    }

    if (a->kind == DG_ANCHOR_CORRIDOR_TRANS) {
        if (a->u.corridor.s < r->s0 || a->u.corridor.s > r->s1) return D_FALSE;
        return D_TRUE;
    }

    if (a->kind == DG_ANCHOR_STRUCT_SURFACE) {
        if (a->u.struct_surface.u < r->u0 || a->u.struct_surface.u > r->u1) return D_FALSE;
        if (a->u.struct_surface.v < r->v0 || a->u.struct_surface.v > r->v1) return D_FALSE;
        return D_TRUE;
    }

    if (a->kind == DG_ANCHOR_ROOM_SURFACE) {
        if (a->u.room_surface.u < r->u0 || a->u.room_surface.u > r->u1) return D_FALSE;
        if (a->u.room_surface.v < r->v0 || a->u.room_surface.v > r->v1) return D_FALSE;
        return D_TRUE;
    }

    if (a->kind == DG_ANCHOR_SOCKET) {
        if (a->u.socket.param < r->param0 || a->u.socket.param > r->param1) return D_FALSE;
        return D_TRUE;
    }

    return D_FALSE;
}
