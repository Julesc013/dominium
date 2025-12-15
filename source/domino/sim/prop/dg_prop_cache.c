#include <string.h>

#include "sim/prop/dg_prop_cache.h"

void dg_prop_cache_init(dg_prop_cache *c) {
    if (!c) {
        return;
    }
    memset(c, 0, sizeof(*c));
    c->rep_state = DG_REP_R3_DORMANT;
    c->last_built_tick = 0u;
    c->dirty = 1u;
}

void dg_prop_cache_mark_dirty(dg_prop_cache *c) {
    if (!c) {
        return;
    }
    c->dirty = 1u;
}

void dg_prop_cache_mark_built(dg_prop_cache *c, dg_rep_state rep_state, dg_tick tick) {
    if (!c) {
        return;
    }
    c->rep_state = dg_rep_state_is_valid(rep_state) ? rep_state : DG_REP_R3_DORMANT;
    c->last_built_tick = tick;
    c->dirty = 0u;
}

d_bool dg_prop_cache_is_dirty(const dg_prop_cache *c) {
    if (!c) {
        return D_TRUE;
    }
    return (c->dirty != 0u) ? D_TRUE : D_FALSE;
}

