#include <string.h>

#include "sim/prop/dg_prop_lod.h"

static dg_rep_state dg_prop_lod_get_rep_state(const dg_representable *self) {
    const dg_prop_lod *pl;
    if (!self) return DG_REP_R3_DORMANT;
    pl = (const dg_prop_lod *)self->user;
    if (!pl) return DG_REP_R3_DORMANT;
    return pl->state;
}

static int dg_prop_lod_set_rep_state(dg_representable *self, dg_rep_state new_state) {
    dg_prop_lod *pl;
    if (!self) return -1;
    pl = (dg_prop_lod *)self->user;
    if (!pl) return -2;
    if (!dg_rep_state_is_valid(new_state)) return -3;
    pl->state = new_state;
    return 0;
}

static void dg_prop_lod_step_rep(dg_representable *self, dg_phase phase, u32 *budget_units) {
    (void)self;
    (void)phase;
    (void)budget_units;
}

static u32 dg_prop_lod_serialize_rep_state(const dg_representable *self, unsigned char *out, u32 out_cap) {
    const dg_prop_lod *pl;
    if (!self || !out || out_cap < 1u) return 0u;
    pl = (const dg_prop_lod *)self->user;
    if (!pl) return 0u;
    out[0] = (unsigned char)pl->state;
    return 1u;
}

static int dg_prop_lod_rep_invariants_check(const dg_representable *self) {
    const dg_prop_lod *pl;
    if (!self) return -1;
    pl = (const dg_prop_lod *)self->user;
    if (!pl) return -2;
    if (!dg_rep_state_is_valid(pl->state)) return -3;
    return 0;
}

static const dg_representable_vtbl DG_PROP_LOD_REP_VTBL = {
    dg_prop_lod_get_rep_state,
    dg_prop_lod_set_rep_state,
    dg_prop_lod_step_rep,
    dg_prop_lod_serialize_rep_state,
    dg_prop_lod_rep_invariants_check
};

void dg_prop_lod_init(dg_prop_lod *pl, dg_prop *prop, dg_rep_state initial_state) {
    if (!pl) {
        return;
    }
    memset(pl, 0, sizeof(*pl));
    pl->prop = prop;
    pl->state = dg_rep_state_is_valid(initial_state) ? initial_state : DG_REP_R3_DORMANT;
    dg_representable_init(&pl->rep, &DG_PROP_LOD_REP_VTBL, pl);
}

d_bool dg_prop_lod_is_valid(const dg_prop_lod *pl) {
    if (!pl) return D_FALSE;
    if (!dg_rep_state_is_valid(pl->state)) return D_FALSE;
    if (!dg_representable_is_valid(&pl->rep)) return D_FALSE;
    return D_TRUE;
}

dg_representable *dg_prop_lod_representable(dg_prop_lod *pl) {
    if (!pl) return (dg_representable *)0;
    return &pl->rep;
}

dg_rep_state dg_prop_lod_get_state(const dg_prop_lod *pl) {
    return pl ? pl->state : DG_REP_R3_DORMANT;
}

int dg_prop_lod_set_state(dg_prop_lod *pl, dg_rep_state new_state) {
    if (!pl) return -1;
    if (!dg_rep_state_is_valid(new_state)) return -2;
    pl->state = new_state;
    return 0;
}

dg_lod_obj_key dg_prop_lod_default_key(dg_domain_id domain_id, dg_prop_id prop_id) {
    dg_lod_obj_key k;
    k.domain_id = domain_id;
    k.chunk_id = 0u;
    k.entity_id = 0u;
    k.sub_id = (u64)prop_id;
    return k;
}

