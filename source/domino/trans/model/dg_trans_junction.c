/* TRANS junctions (topology nodes) (C89). */
#include "trans/model/dg_trans_junction.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"

void dg_trans_junction_init(dg_trans_junction *j) {
    if (!j) return;
    memset(j, 0, sizeof(*j));
}

void dg_trans_junction_free(dg_trans_junction *j) {
    if (!j) return;
    if (j->incidents) {
        free(j->incidents);
    }
    dg_trans_junction_init(j);
}

int dg_trans_junction_reserve_incidents(dg_trans_junction *j, u32 capacity) {
    dg_trans_junction_incident *new_inc;
    u32 new_cap;
    if (!j) return -1;
    if (capacity <= j->incident_capacity) return 0;
    new_cap = j->incident_capacity ? j->incident_capacity : 4u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    new_inc = (dg_trans_junction_incident *)realloc(j->incidents, sizeof(dg_trans_junction_incident) * (size_t)new_cap);
    if (!new_inc) return -2;
    if (new_cap > j->incident_capacity) {
        memset(&new_inc[j->incident_capacity], 0, sizeof(dg_trans_junction_incident) * (size_t)(new_cap - j->incident_capacity));
    }
    j->incidents = new_inc;
    j->incident_capacity = new_cap;
    return 0;
}

int dg_trans_junction_incident_cmp(const dg_trans_junction_incident *a, const dg_trans_junction_incident *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = D_DET_CMP_U64(a->alignment_id, b->alignment_id); if (c) return c;
    c = D_DET_CMP_U32(a->port_index, b->port_index); if (c) return c;
    return 0;
}

static u32 dg_trans_junction_incident_lower_bound(const dg_trans_junction *j, dg_trans_alignment_id aid, u16 port_index) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!j) return 0u;
    hi = j->incident_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        {
            const dg_trans_junction_incident *e = &j->incidents[mid];
            if (e->alignment_id > aid) {
                hi = mid;
            } else if (e->alignment_id < aid) {
                lo = mid + 1u;
            } else {
                if (e->port_index >= port_index) {
                    hi = mid;
                } else {
                    lo = mid + 1u;
                }
            }
        }
    }
    return lo;
}

int dg_trans_junction_set_incident(dg_trans_junction *j, const dg_trans_junction_incident *inc) {
    u32 idx;
    dg_trans_junction_incident tmp;
    if (!j || !inc) return -1;
    if (inc->alignment_id == 0u) return -2;

    idx = dg_trans_junction_incident_lower_bound(j, inc->alignment_id, inc->port_index);
    if (idx < j->incident_count) {
        dg_trans_junction_incident *e = &j->incidents[idx];
        if (e->alignment_id == inc->alignment_id && e->port_index == inc->port_index) {
            *e = *inc;
            return 1;
        }
    }

    if (dg_trans_junction_reserve_incidents(j, j->incident_count + 1u) != 0) return -3;
    if (idx < j->incident_count) {
        memmove(&j->incidents[idx + 1u], &j->incidents[idx],
                sizeof(dg_trans_junction_incident) * (size_t)(j->incident_count - idx));
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp = *inc;
    j->incidents[idx] = tmp;
    j->incident_count += 1u;
    return 0;
}

