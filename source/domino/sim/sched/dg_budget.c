#include <stdlib.h>
#include <string.h>

#include "sim/sched/dg_budget.h"

static u32 dg_budget_remaining_limit_used(u32 limit, u32 used) {
    if (limit == DG_BUDGET_UNLIMITED) {
        return DG_BUDGET_UNLIMITED;
    }
    if (used >= limit) {
        return 0u;
    }
    return limit - used;
}

static void dg_budget_saturating_add_u32(u32 *io, u32 add) {
    u32 v;
    if (!io) {
        return;
    }
    v = *io;
    if (v > 0xFFFFFFFFu - add) {
        *io = 0xFFFFFFFFu;
    } else {
        *io = v + add;
    }
}

dg_budget_scope dg_budget_scope_global(void) {
    dg_budget_scope s;
    s.domain_id = 0u;
    s.chunk_id = 0u;
    return s;
}

dg_budget_scope dg_budget_scope_domain(dg_domain_id domain_id) {
    dg_budget_scope s;
    s.domain_id = domain_id;
    s.chunk_id = 0u;
    return s;
}

dg_budget_scope dg_budget_scope_chunk(dg_chunk_id chunk_id) {
    dg_budget_scope s;
    s.domain_id = 0u;
    s.chunk_id = chunk_id;
    return s;
}

dg_budget_scope dg_budget_scope_domain_chunk(dg_domain_id domain_id, dg_chunk_id chunk_id) {
    dg_budget_scope s;
    s.domain_id = domain_id;
    s.chunk_id = chunk_id;
    return s;
}

void dg_budget_init(dg_budget *b) {
    if (!b) {
        return;
    }
    b->tick = 0u;
    b->global_limit = 0u;
    b->global_used = 0u;
    b->domain_default_limit = 0u;
    b->chunk_default_limit = 0u;
    b->domain_entries = (dg_budget_entry *)0;
    b->domain_count = 0u;
    b->domain_capacity = 0u;
    b->chunk_entries = (dg_budget_entry *)0;
    b->chunk_count = 0u;
    b->chunk_capacity = 0u;
    b->probe_domain_overflow = 0u;
    b->probe_chunk_overflow = 0u;
}

void dg_budget_free(dg_budget *b) {
    if (!b) {
        return;
    }
    if (b->domain_entries) {
        free(b->domain_entries);
    }
    if (b->chunk_entries) {
        free(b->chunk_entries);
    }
    dg_budget_init(b);
}

int dg_budget_reserve(dg_budget *b, u32 domain_capacity, u32 chunk_capacity) {
    dg_budget_entry *d;
    dg_budget_entry *c;

    if (!b) {
        return -1;
    }

    if (domain_capacity > 0u) {
        d = (dg_budget_entry *)malloc(sizeof(dg_budget_entry) * (size_t)domain_capacity);
        if (!d) {
            return -2;
        }
        memset(d, 0, sizeof(dg_budget_entry) * (size_t)domain_capacity);
    } else {
        d = (dg_budget_entry *)0;
    }

    if (chunk_capacity > 0u) {
        c = (dg_budget_entry *)malloc(sizeof(dg_budget_entry) * (size_t)chunk_capacity);
        if (!c) {
            if (d) free(d);
            return -3;
        }
        memset(c, 0, sizeof(dg_budget_entry) * (size_t)chunk_capacity);
    } else {
        c = (dg_budget_entry *)0;
    }

    dg_budget_free(b);
    b->domain_entries = d;
    b->domain_capacity = domain_capacity;
    b->domain_count = 0u;
    b->chunk_entries = c;
    b->chunk_capacity = chunk_capacity;
    b->chunk_count = 0u;
    return 0;
}

void dg_budget_begin_tick(dg_budget *b, dg_tick tick) {
    u32 i;
    if (!b) {
        return;
    }
    b->tick = tick;
    b->global_used = 0u;
    for (i = 0u; i < b->domain_count; ++i) {
        b->domain_entries[i].used = 0u;
    }
    for (i = 0u; i < b->chunk_count; ++i) {
        b->chunk_entries[i].used = 0u;
    }
}

void dg_budget_set_limits(dg_budget *b, u32 global_limit, u32 domain_default_limit, u32 chunk_default_limit) {
    if (!b) {
        return;
    }
    b->global_limit = global_limit;
    b->domain_default_limit = domain_default_limit;
    b->chunk_default_limit = chunk_default_limit;
}

static u32 dg_budget_lower_bound(const dg_budget_entry *entries, u32 count, u64 id, int *out_found) {
    u32 lo = 0u;
    u32 hi = count;
    u32 mid;

    if (out_found) {
        *out_found = 0;
    }

    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (entries[mid].id < id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    if (lo < count && entries[lo].id == id) {
        if (out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

static dg_budget_entry *dg_budget_get_or_insert(
    dg_budget_entry *entries,
    u32             *io_count,
    u32              capacity,
    u64              id,
    u32              default_limit,
    u32             *io_probe_overflow
) {
    int found;
    u32 idx;
    u32 count;

    if (!entries || !io_count) {
        return (dg_budget_entry *)0;
    }
    count = *io_count;

    idx = dg_budget_lower_bound(entries, count, id, &found);
    if (found) {
        return &entries[idx];
    }

    if (count >= capacity) {
        if (io_probe_overflow) {
            *io_probe_overflow += 1u;
        }
        return (dg_budget_entry *)0;
    }

    if (idx < count) {
        memmove(&entries[idx + 1u], &entries[idx],
                sizeof(dg_budget_entry) * (size_t)(count - idx));
    }
    entries[idx].id = id;
    entries[idx].limit = default_limit;
    entries[idx].used = 0u;
    *io_count = count + 1u;
    return &entries[idx];
}

static const dg_budget_entry *dg_budget_find_const(const dg_budget_entry *entries, u32 count, u32 capacity, u64 id) {
    int found;
    u32 idx;
    (void)capacity;
    if (!entries || count == 0u) {
        return (const dg_budget_entry *)0;
    }
    idx = dg_budget_lower_bound(entries, count, id, &found);
    if (!found) {
        return (const dg_budget_entry *)0;
    }
    return &entries[idx];
}

int dg_budget_set_domain_limit(dg_budget *b, dg_domain_id domain_id, u32 limit) {
    dg_budget_entry *e;
    if (!b) {
        return -1;
    }
    if (b->domain_capacity == 0u) {
        b->probe_domain_overflow += 1u;
        return -2;
    }
    e = dg_budget_get_or_insert(
        b->domain_entries,
        &b->domain_count,
        b->domain_capacity,
        (u64)domain_id,
        b->domain_default_limit,
        &b->probe_domain_overflow
    );
    if (!e) {
        return -3;
    }
    e->limit = limit;
    return 0;
}

int dg_budget_set_chunk_limit(dg_budget *b, dg_chunk_id chunk_id, u32 limit) {
    dg_budget_entry *e;
    if (!b) {
        return -1;
    }
    if (b->chunk_capacity == 0u) {
        b->probe_chunk_overflow += 1u;
        return -2;
    }
    e = dg_budget_get_or_insert(
        b->chunk_entries,
        &b->chunk_count,
        b->chunk_capacity,
        (u64)chunk_id,
        b->chunk_default_limit,
        &b->probe_chunk_overflow
    );
    if (!e) {
        return -3;
    }
    e->limit = limit;
    return 0;
}

static u32 dg_budget_domain_remaining(const dg_budget *b, dg_domain_id domain_id) {
    const dg_budget_entry *e;
    if (!b) {
        return 0u;
    }
    e = dg_budget_find_const(b->domain_entries, b->domain_count, b->domain_capacity, (u64)domain_id);
    if (!e) {
        if (b->domain_count >= b->domain_capacity) {
            return 0u;
        }
        return b->domain_default_limit;
    }
    return dg_budget_remaining_limit_used(e->limit, e->used);
}

static u32 dg_budget_chunk_remaining(const dg_budget *b, dg_chunk_id chunk_id) {
    const dg_budget_entry *e;
    if (!b) {
        return 0u;
    }
    e = dg_budget_find_const(b->chunk_entries, b->chunk_count, b->chunk_capacity, (u64)chunk_id);
    if (!e) {
        if (b->chunk_count >= b->chunk_capacity) {
            return 0u;
        }
        return b->chunk_default_limit;
    }
    return dg_budget_remaining_limit_used(e->limit, e->used);
}

u32 dg_budget_remaining(const dg_budget *b, const dg_budget_scope *scope) {
    u32 rem;
    if (!b || !scope) {
        return 0u;
    }
    rem = dg_budget_remaining_limit_used(b->global_limit, b->global_used);

    if (scope->domain_id != 0u) {
        u32 drem = dg_budget_domain_remaining(b, scope->domain_id);
        if (rem == DG_BUDGET_UNLIMITED) rem = drem;
        else if (drem != DG_BUDGET_UNLIMITED) rem = D_MIN(rem, drem);
    }

    if (scope->chunk_id != 0u) {
        u32 crem = dg_budget_chunk_remaining(b, scope->chunk_id);
        if (rem == DG_BUDGET_UNLIMITED) rem = crem;
        else if (crem != DG_BUDGET_UNLIMITED) rem = D_MIN(rem, crem);
    }

    return rem;
}

d_bool dg_budget_try_consume(dg_budget *b, const dg_budget_scope *scope, u32 units) {
    u32 rem_global;
    dg_budget_entry *dom = (dg_budget_entry *)0;
    dg_budget_entry *chk = (dg_budget_entry *)0;
    u32 rem_dom = DG_BUDGET_UNLIMITED;
    u32 rem_chk = DG_BUDGET_UNLIMITED;

    if (!b || !scope) {
        return D_FALSE;
    }
    if (units == 0u) {
        return D_TRUE;
    }

    rem_global = dg_budget_remaining_limit_used(b->global_limit, b->global_used);
    if (rem_global != DG_BUDGET_UNLIMITED && rem_global < units) {
        return D_FALSE;
    }

    if (scope->domain_id != 0u) {
        if (!b->domain_entries || b->domain_capacity == 0u) {
            b->probe_domain_overflow += 1u;
            return D_FALSE;
        }
        dom = dg_budget_get_or_insert(
            b->domain_entries,
            &b->domain_count,
            b->domain_capacity,
            (u64)scope->domain_id,
            b->domain_default_limit,
            &b->probe_domain_overflow
        );
        if (!dom) {
            return D_FALSE;
        }
        rem_dom = dg_budget_remaining_limit_used(dom->limit, dom->used);
        if (rem_dom != DG_BUDGET_UNLIMITED && rem_dom < units) {
            return D_FALSE;
        }
    }

    if (scope->chunk_id != 0u) {
        if (!b->chunk_entries || b->chunk_capacity == 0u) {
            b->probe_chunk_overflow += 1u;
            return D_FALSE;
        }
        chk = dg_budget_get_or_insert(
            b->chunk_entries,
            &b->chunk_count,
            b->chunk_capacity,
            (u64)scope->chunk_id,
            b->chunk_default_limit,
            &b->probe_chunk_overflow
        );
        if (!chk) {
            return D_FALSE;
        }
        rem_chk = dg_budget_remaining_limit_used(chk->limit, chk->used);
        if (rem_chk != DG_BUDGET_UNLIMITED && rem_chk < units) {
            return D_FALSE;
        }
    }

    dg_budget_saturating_add_u32(&b->global_used, units);
    if (dom) {
        dg_budget_saturating_add_u32(&dom->used, units);
    }
    if (chk) {
        dg_budget_saturating_add_u32(&chk->used, units);
    }
    return D_TRUE;
}

u32 dg_budget_probe_domain_overflow(const dg_budget *b) {
    return b ? b->probe_domain_overflow : 0u;
}

u32 dg_budget_probe_chunk_overflow(const dg_budget *b) {
    return b ? b->probe_chunk_overflow : 0u;
}
