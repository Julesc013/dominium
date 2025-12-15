#include <stdlib.h>
#include <string.h>

#include "world/domain/dg_domain_query.h"

#include "world/domain/dg_domain_registry.h"

void dg_domain_query_results_init(dg_domain_query_results *r, dg_domain_query_result *storage, u32 capacity) {
    if (!r) {
        return;
    }
    r->items = storage;
    r->count = 0u;
    r->capacity = capacity;
}

void dg_domain_query_results_clear(dg_domain_query_results *r) {
    if (!r) {
        return;
    }
    r->count = 0u;
}

int dg_domain_query_results_push(dg_domain_query_results *r, const dg_domain_query_result *item) {
    if (!r || !item) {
        return -1;
    }
    if (!r->items || r->capacity == 0u) {
        return -2;
    }
    if (r->count >= r->capacity) {
        return -3;
    }
    r->items[r->count++] = *item;
    return 0;
}

int dg_domain_query_result_cmp(const dg_domain_query_result *a, const dg_domain_query_result *b) {
    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    if (a->result_type_id < b->result_type_id) return -1;
    if (a->result_type_id > b->result_type_id) return 1;
    if (a->domain_id < b->domain_id) return -1;
    if (a->domain_id > b->domain_id) return 1;
    if (a->chunk_id < b->chunk_id) return -1;
    if (a->chunk_id > b->chunk_id) return 1;
    if (a->entity_id < b->entity_id) return -1;
    if (a->entity_id > b->entity_id) return 1;
    if (a->sub_id < b->sub_id) return -1;
    if (a->sub_id > b->sub_id) return 1;
    return 0;
}

static int dg_domain_query_qsort_cmp(const void *pa, const void *pb) {
    const dg_domain_query_result *a = (const dg_domain_query_result *)pa;
    const dg_domain_query_result *b = (const dg_domain_query_result *)pb;
    return dg_domain_query_result_cmp(a, b);
}

void dg_domain_query_results_sort(dg_domain_query_results *r) {
    if (!r || !r->items || r->count < 2u) {
        return;
    }
    qsort(r->items, (size_t)r->count, sizeof(dg_domain_query_result), dg_domain_query_qsort_cmp);
}

int dg_domain_query(
    const dg_domain_registry    *reg,
    const dg_domain_query_desc  *desc,
    const void                  *observer_ctx,
    dg_domain_query_results     *out_results
) {
    u32 i;
    dg_domain_id filter_domain;

    if (!desc || !out_results) {
        return -1;
    }

    filter_domain = desc->domain_id;
    dg_domain_query_results_clear(out_results);

    if (!reg) {
        return 0;
    }

    if (filter_domain != 0u) {
        const dg_domain_registry_entry *e = dg_domain_registry_find(reg, filter_domain);
        if (e && e->domain) {
            (void)dg_domain_query_domain(e->domain, desc, observer_ctx, out_results);
        }
        dg_domain_query_results_sort(out_results);
        return 0;
    }

    for (i = 0u; i < dg_domain_registry_count(reg); ++i) {
        const dg_domain_registry_entry *e = dg_domain_registry_at(reg, i);
        if (!e || !e->domain) {
            continue;
        }
        (void)dg_domain_query_domain(e->domain, desc, observer_ctx, out_results);
    }

    dg_domain_query_results_sort(out_results);
    return 0;
}

