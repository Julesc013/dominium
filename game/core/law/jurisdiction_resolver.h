/*
FILE: game/core/law/jurisdiction_resolver.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / law
RESPONSIBILITY: Resolve active jurisdictions from domain containment deterministically.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
DETERMINISM: Ordered resolution with explicit tie-breaks; no wall-clock inputs.
*/
#ifndef DOMINIUM_LAW_JURISDICTION_RESOLVER_H
#define DOMINIUM_LAW_JURISDICTION_RESOLVER_H

#include "domino/world/domain_query.h"
#include "dominium/law/law_kernel.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_JURISDICTION_MAX 16u
#define DOM_JURISDICTION_MAX_DOMAINS 32u
#define DOM_JURISDICTION_MAX_BINDINGS 16u

typedef u64 dom_jurisdiction_id;

typedef struct dom_jurisdiction_list {
    dom_jurisdiction_id ids[DOM_JURISDICTION_MAX];
    u32 count;
} dom_jurisdiction_list;

typedef struct dom_domain_jurisdiction_binding {
    dom_jurisdiction_id jurisdiction_id;
    u32 precedence;
} dom_domain_jurisdiction_binding;

typedef struct dom_domain_jurisdiction_entry {
    dom_domain_id domain_id;
    dom_domain_id parent_domain_id;
    u32 domain_precedence;
    const dom_domain_volume *volume;
    const dom_domain_jurisdiction_binding *bindings;
    u32 binding_count;
} dom_domain_jurisdiction_entry;

typedef struct dom_jurisdiction_resolution {
    dom_jurisdiction_list ordered;
    u32 refused;
    u32 uncertain;
} dom_jurisdiction_resolution;

void dom_jurisdiction_list_init(dom_jurisdiction_list* list);
int dom_jurisdiction_list_push_unique(dom_jurisdiction_list* list, dom_jurisdiction_id id);

void dom_jurisdiction_resolution_init(dom_jurisdiction_resolution* res);

int dom_jurisdiction_resolve_point(const dom_domain_jurisdiction_entry* domains,
                                   u32 domain_count,
                                   const dom_jurisdiction_list* explicit_context,
                                   const dom_domain_point* point,
                                   dom_domain_budget* budget,
                                   dom_jurisdiction_id world_default,
                                   dom_jurisdiction_id server_default,
                                   dom_jurisdiction_id fallback,
                                   dom_jurisdiction_resolution* out_resolution);

int dom_jurisdiction_resolve_multi(const dom_domain_jurisdiction_entry* domains,
                                   u32 domain_count,
                                   const dom_jurisdiction_list* explicit_context,
                                   const dom_domain_point* points,
                                   u32 point_count,
                                   dom_domain_budget* budget,
                                   dom_jurisdiction_id world_default,
                                   dom_jurisdiction_id server_default,
                                   dom_jurisdiction_id fallback,
                                   dom_jurisdiction_resolution* out_resolution);

void dom_law_context_build(dom_law_context* ctx,
                           u64 authority_id,
                           u32 authority_kind,
                           const dom_jurisdiction_resolution* res);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LAW_JURISDICTION_RESOLVER_H */
