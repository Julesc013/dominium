/*
FILE: game/core/law/jurisdiction_resolver.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / law
RESPONSIBILITY: Resolve active jurisdictions from domain containment deterministically.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
DETERMINISM: Ordered resolution with explicit tie-breaks; no wall-clock inputs.
*/
#include "game/core/law/jurisdiction_resolver.h"

#include <string.h>

typedef struct dom_domain_candidate {
    const dom_domain_jurisdiction_entry* entry;
    i64 size_key;
} dom_domain_candidate;

static i64 dom_domain_abs_i64(i64 v)
{
    return (v < 0) ? -v : v;
}

static i64 dom_domain_volume_size_key(const dom_domain_volume* volume)
{
    i64 dx;
    i64 dy;
    i64 dz;
    if (!volume || !volume->source) {
        return (i64)0x7FFFFFFFFFFFFFFFLL;
    }
    dx = (i64)volume->source->bounds.max.x - (i64)volume->source->bounds.min.x;
    dy = (i64)volume->source->bounds.max.y - (i64)volume->source->bounds.min.y;
    dz = (i64)volume->source->bounds.max.z - (i64)volume->source->bounds.min.z;
    return dom_domain_abs_i64(dx) + dom_domain_abs_i64(dy) + dom_domain_abs_i64(dz);
}

void dom_jurisdiction_list_init(dom_jurisdiction_list* list)
{
    if (!list) {
        return;
    }
    memset(list, 0, sizeof(*list));
}

int dom_jurisdiction_list_push_unique(dom_jurisdiction_list* list, dom_jurisdiction_id id)
{
    u32 i;
    if (!list || id == 0u) {
        return -1;
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->ids[i] == id) {
            return 0;
        }
    }
    if (list->count >= DOM_JURISDICTION_MAX) {
        return -1;
    }
    list->ids[list->count++] = id;
    return 0;
}

void dom_jurisdiction_resolution_init(dom_jurisdiction_resolution* res)
{
    if (!res) {
        return;
    }
    dom_jurisdiction_list_init(&res->ordered);
    res->refused = 0u;
    res->uncertain = 0u;
}

static void dom_jurisdiction_append_bindings(dom_jurisdiction_list* out_list,
                                             const dom_domain_jurisdiction_entry* entry)
{
    u32 used[DOM_JURISDICTION_MAX_BINDINGS];
    u32 i;
    u32 count;
    if (!out_list || !entry || !entry->bindings) {
        return;
    }
    count = entry->binding_count;
    if (count > DOM_JURISDICTION_MAX_BINDINGS) {
        count = DOM_JURISDICTION_MAX_BINDINGS;
    }
    for (i = 0u; i < count; ++i) {
        used[i] = 0u;
    }

    for (i = 0u; i < count; ++i) {
        u32 best = 0u;
        d_bool have_best = D_FALSE;
        u32 j;
        for (j = 0u; j < count; ++j) {
            const dom_domain_jurisdiction_binding* b = &entry->bindings[j];
            if (used[j]) {
                continue;
            }
            if (!have_best) {
                best = j;
                have_best = D_TRUE;
            } else {
                const dom_domain_jurisdiction_binding* best_b = &entry->bindings[best];
                if (b->precedence > best_b->precedence ||
                    (b->precedence == best_b->precedence &&
                     b->jurisdiction_id < best_b->jurisdiction_id)) {
                    best = j;
                }
            }
        }
        if (!have_best) {
            break;
        }
        used[best] = 1u;
        dom_jurisdiction_list_push_unique(out_list, entry->bindings[best].jurisdiction_id);
    }
}

static const dom_domain_jurisdiction_entry* dom_jurisdiction_find_domain(
    const dom_domain_jurisdiction_entry* domains,
    u32 domain_count,
    dom_domain_id domain_id)
{
    u32 i;
    if (!domains) {
        return (const dom_domain_jurisdiction_entry*)0;
    }
    for (i = 0u; i < domain_count; ++i) {
        if (domains[i].domain_id == domain_id) {
            return &domains[i];
        }
    }
    return (const dom_domain_jurisdiction_entry*)0;
}

static void dom_jurisdiction_append_parent_chain(dom_jurisdiction_list* out_list,
                                                 const dom_domain_jurisdiction_entry* domains,
                                                 u32 domain_count,
                                                 dom_domain_id start_domain)
{
    dom_domain_id current = start_domain;
    u32 safety = domain_count + 1u;
    while (current != 0u && safety-- > 0u) {
        const dom_domain_jurisdiction_entry* entry = dom_jurisdiction_find_domain(domains, domain_count, current);
        if (!entry) {
            break;
        }
        if (entry->parent_domain_id == 0u) {
            break;
        }
        current = entry->parent_domain_id;
        entry = dom_jurisdiction_find_domain(domains, domain_count, current);
        if (!entry) {
            break;
        }
        dom_jurisdiction_append_bindings(out_list, entry);
    }
}

static void dom_jurisdiction_append_defaults(dom_jurisdiction_list* out_list,
                                             dom_jurisdiction_id world_default,
                                             dom_jurisdiction_id server_default,
                                             dom_jurisdiction_id fallback)
{
    dom_jurisdiction_list_push_unique(out_list, world_default);
    dom_jurisdiction_list_push_unique(out_list, server_default);
    dom_jurisdiction_list_push_unique(out_list, fallback);
}

int dom_jurisdiction_resolve_point(const dom_domain_jurisdiction_entry* domains,
                                   u32 domain_count,
                                   const dom_jurisdiction_list* explicit_context,
                                   const dom_domain_point* point,
                                   dom_domain_budget* budget,
                                   dom_jurisdiction_id world_default,
                                   dom_jurisdiction_id server_default,
                                   dom_jurisdiction_id fallback,
                                   dom_jurisdiction_resolution* out_resolution)
{
    dom_domain_budget local_budget;
    dom_domain_budget* budget_ptr = budget;
    dom_domain_candidate candidates[DOM_JURISDICTION_MAX_DOMAINS];
    u32 candidate_count = 0u;
    u32 i;
    const dom_domain_jurisdiction_entry* smallest = (const dom_domain_jurisdiction_entry*)0;
    i64 smallest_size = 0;

    if (!out_resolution || !point) {
        return -1;
    }
    dom_jurisdiction_resolution_init(out_resolution);

    if (explicit_context) {
        for (i = 0u; i < explicit_context->count; ++i) {
            dom_jurisdiction_list_push_unique(&out_resolution->ordered, explicit_context->ids[i]);
        }
    }

    if (!budget_ptr) {
        dom_domain_budget_init(&local_budget, 0xFFFFFFFFu);
        budget_ptr = &local_budget;
    }

    if (domains) {
        for (i = 0u; i < domain_count && candidate_count < DOM_JURISDICTION_MAX_DOMAINS; ++i) {
            const dom_domain_jurisdiction_entry* entry = &domains[i];
            dom_domain_query_meta meta;
            d_bool inside;
            if (!entry->volume) {
                continue;
            }
            inside = dom_domain_contains(entry->volume, point, budget_ptr, &meta);
            if (meta.status == DOM_DOMAIN_QUERY_REFUSED ||
                meta.confidence == DOM_DOMAIN_CONFIDENCE_UNKNOWN) {
                out_resolution->refused = 1u;
                out_resolution->uncertain = 1u;
                continue;
            }
            if (meta.confidence != DOM_DOMAIN_CONFIDENCE_EXACT) {
                out_resolution->uncertain = 1u;
                continue;
            }
            if (inside) {
                candidates[candidate_count].entry = entry;
                candidates[candidate_count].size_key = dom_domain_volume_size_key(entry->volume);
                candidate_count += 1u;
            }
        }
    }

    if (candidate_count > 0u) {
        smallest = candidates[0].entry;
        smallest_size = candidates[0].size_key;
        for (i = 1u; i < candidate_count; ++i) {
            const dom_domain_jurisdiction_entry* entry = candidates[i].entry;
            i64 size_key = candidates[i].size_key;
            if (size_key < smallest_size ||
                (size_key == smallest_size && entry->domain_id < smallest->domain_id)) {
                smallest = entry;
                smallest_size = size_key;
            }
        }
    }

    if (smallest) {
        dom_jurisdiction_append_bindings(&out_resolution->ordered, smallest);
    }

    if (candidate_count > 1u) {
        u32 used[DOM_JURISDICTION_MAX_DOMAINS];
        u32 used_count = candidate_count;
        for (i = 0u; i < candidate_count; ++i) {
            used[i] = 0u;
            if (candidates[i].entry == smallest) {
                used[i] = 1u;
                used_count -= 1u;
            }
        }
        while (used_count > 0u) {
            u32 best = 0u;
            d_bool have_best = D_FALSE;
            u32 j;
            for (j = 0u; j < candidate_count; ++j) {
                if (used[j]) {
                    continue;
                }
                if (!have_best) {
                    best = j;
                    have_best = D_TRUE;
                } else {
                    const dom_domain_jurisdiction_entry* a = candidates[j].entry;
                    const dom_domain_jurisdiction_entry* b = candidates[best].entry;
                    if (a->domain_precedence > b->domain_precedence ||
                        (a->domain_precedence == b->domain_precedence &&
                         a->domain_id < b->domain_id)) {
                        best = j;
                    }
                }
            }
            if (!have_best) {
                break;
            }
            used[best] = 1u;
            used_count -= 1u;
            dom_jurisdiction_append_bindings(&out_resolution->ordered, candidates[best].entry);
        }
    }

    if (smallest) {
        dom_jurisdiction_append_parent_chain(&out_resolution->ordered, domains, domain_count,
                                             smallest->domain_id);
    }

    dom_jurisdiction_append_defaults(&out_resolution->ordered,
                                     world_default,
                                     server_default,
                                     fallback);

    return 0;
}

static void dom_jurisdiction_merge_resolution(dom_jurisdiction_resolution* out_resolution,
                                              const dom_jurisdiction_resolution* in_resolution)
{
    u32 i;
    if (!out_resolution || !in_resolution) {
        return;
    }
    for (i = 0u; i < in_resolution->ordered.count; ++i) {
        dom_jurisdiction_list_push_unique(&out_resolution->ordered, in_resolution->ordered.ids[i]);
    }
    if (in_resolution->refused) {
        out_resolution->refused = 1u;
    }
    if (in_resolution->uncertain) {
        out_resolution->uncertain = 1u;
    }
}

int dom_jurisdiction_resolve_multi(const dom_domain_jurisdiction_entry* domains,
                                   u32 domain_count,
                                   const dom_jurisdiction_list* explicit_context,
                                   const dom_domain_point* points,
                                   u32 point_count,
                                   dom_domain_budget* budget,
                                   dom_jurisdiction_id world_default,
                                   dom_jurisdiction_id server_default,
                                   dom_jurisdiction_id fallback,
                                   dom_jurisdiction_resolution* out_resolution)
{
    u32 i;
    if (!out_resolution || !points || point_count == 0u) {
        return -1;
    }
    dom_jurisdiction_resolution_init(out_resolution);

    for (i = 0u; i < point_count; ++i) {
        dom_jurisdiction_resolution res;
        dom_jurisdiction_resolution_init(&res);
        dom_jurisdiction_resolve_point(domains, domain_count, explicit_context, &points[i], budget,
                                       world_default, server_default, fallback, &res);
        dom_jurisdiction_merge_resolution(out_resolution, &res);
    }

    return 0;
}
