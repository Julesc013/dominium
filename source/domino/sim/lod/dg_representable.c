#include <string.h>

#include "sim/lod/dg_representable.h"

void dg_representable_init(dg_representable *r, const dg_representable_vtbl *vtbl, void *user) {
    if (!r) {
        return;
    }
    memset(r, 0, sizeof(*r));
    r->vtbl = vtbl;
    r->user = user;
}

d_bool dg_representable_is_valid(const dg_representable *r) {
    if (!r || !r->vtbl) {
        return D_FALSE;
    }
    if (!r->vtbl->get_rep_state) {
        return D_FALSE;
    }
    if (!r->vtbl->set_rep_state) {
        return D_FALSE;
    }
    if (!r->vtbl->step_rep) {
        return D_FALSE;
    }
    if (!r->vtbl->serialize_rep_state) {
        return D_FALSE;
    }
    /* rep_invariants_check may be NULL in non-debug builds. */
    return D_TRUE;
}

dg_rep_state dg_representable_get_rep_state(const dg_representable *r) {
    if (!r || !r->vtbl || !r->vtbl->get_rep_state) {
        return DG_REP_R3_DORMANT;
    }
    return r->vtbl->get_rep_state(r);
}

int dg_representable_set_rep_state(dg_representable *r, dg_rep_state new_state) {
    if (!r || !r->vtbl || !r->vtbl->set_rep_state) {
        return -1;
    }
    if (!dg_rep_state_is_valid(new_state)) {
        return -2;
    }
    return r->vtbl->set_rep_state(r, new_state);
}

void dg_representable_step_rep(dg_representable *r, dg_phase phase, u32 *budget_units) {
    if (!r || !r->vtbl || !r->vtbl->step_rep) {
        return;
    }
    r->vtbl->step_rep(r, phase, budget_units);
}

u32 dg_representable_serialize_rep_state(const dg_representable *r, unsigned char *out, u32 out_cap) {
    if (!r || !r->vtbl || !r->vtbl->serialize_rep_state) {
        return 0u;
    }
    return r->vtbl->serialize_rep_state(r, out, out_cap);
}

int dg_representable_rep_invariants_check(const dg_representable *r) {
    if (!r || !r->vtbl || !r->vtbl->rep_invariants_check) {
        return 0;
    }
    return r->vtbl->rep_invariants_check(r);
}

