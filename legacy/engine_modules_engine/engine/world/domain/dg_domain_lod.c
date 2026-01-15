/*
FILE: source/domino/world/domain/dg_domain_lod.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain/dg_domain_lod
RESPONSIBILITY: Implements `dg_domain_lod`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "world/domain/dg_domain_lod.h"

static dg_rep_state dg_domain_lod_get_rep_state(const dg_representable *self) {
    const dg_domain_lod *dl;
    if (!self) return DG_REP_R3_DORMANT;
    dl = (const dg_domain_lod *)self->user;
    if (!dl) return DG_REP_R3_DORMANT;
    return dl->state;
}

static int dg_domain_lod_set_rep_state(dg_representable *self, dg_rep_state new_state) {
    dg_domain_lod *dl;
    if (!self) return -1;
    dl = (dg_domain_lod *)self->user;
    if (!dl) return -2;
    if (!dg_rep_state_is_valid(new_state)) return -3;
    dl->state = new_state;
    return 0;
}

static void dg_domain_lod_step_rep(dg_representable *self, dg_phase phase, u32 *budget_units) {
    (void)self;
    (void)phase;
    (void)budget_units;
}

static u32 dg_domain_lod_serialize_rep_state(const dg_representable *self, unsigned char *out, u32 out_cap) {
    const dg_domain_lod *dl;
    if (!self || !out || out_cap < 1u) return 0u;
    dl = (const dg_domain_lod *)self->user;
    if (!dl) return 0u;
    out[0] = (unsigned char)dl->state;
    return 1u;
}

static int dg_domain_lod_rep_invariants_check(const dg_representable *self) {
    const dg_domain_lod *dl;
    if (!self) return -1;
    dl = (const dg_domain_lod *)self->user;
    if (!dl) return -2;
    if (!dg_rep_state_is_valid(dl->state)) return -3;
    return 0;
}

static const dg_representable_vtbl DG_DOMAIN_LOD_REP_VTBL = {
    dg_domain_lod_get_rep_state,
    dg_domain_lod_set_rep_state,
    dg_domain_lod_step_rep,
    dg_domain_lod_serialize_rep_state,
    dg_domain_lod_rep_invariants_check
};

void dg_domain_lod_init(dg_domain_lod *dl, dg_domain *domain, dg_rep_state initial_state) {
    if (!dl) {
        return;
    }
    memset(dl, 0, sizeof(*dl));
    dl->domain = domain;
    dl->state = dg_rep_state_is_valid(initial_state) ? initial_state : DG_REP_R3_DORMANT;
    dg_representable_init(&dl->rep, &DG_DOMAIN_LOD_REP_VTBL, dl);
}

d_bool dg_domain_lod_is_valid(const dg_domain_lod *dl) {
    if (!dl) return D_FALSE;
    if (!dg_rep_state_is_valid(dl->state)) return D_FALSE;
    if (!dg_representable_is_valid(&dl->rep)) return D_FALSE;
    return D_TRUE;
}

dg_representable *dg_domain_lod_representable(dg_domain_lod *dl) {
    if (!dl) return (dg_representable *)0;
    return &dl->rep;
}

dg_rep_state dg_domain_lod_get_state(const dg_domain_lod *dl) {
    return dl ? dl->state : DG_REP_R3_DORMANT;
}

int dg_domain_lod_set_state(dg_domain_lod *dl, dg_rep_state new_state) {
    if (!dl) return -1;
    if (!dg_rep_state_is_valid(new_state)) return -2;
    dl->state = new_state;
    return 0;
}

dg_lod_obj_key dg_domain_lod_default_key(dg_domain_id domain_id) {
    dg_lod_obj_key k;
    k.domain_id = domain_id;
    k.chunk_id = 0u;
    k.entity_id = 0u;
    k.sub_id = 0u;
    return k;
}

