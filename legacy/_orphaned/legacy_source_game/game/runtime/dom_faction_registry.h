/*
FILE: source/dominium/game/runtime/dom_faction_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/faction_registry
RESPONSIBILITY: Deterministic faction registry + resource storage.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_FACTION_REGISTRY_H
#define DOM_FACTION_REGISTRY_H

#include "domino/core/types.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_station_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_FACTION_OK = 0,
    DOM_FACTION_ERR = -1,
    DOM_FACTION_INVALID_ARGUMENT = -2,
    DOM_FACTION_DUPLICATE_ID = -3,
    DOM_FACTION_NOT_FOUND = -4,
    DOM_FACTION_INVALID_DATA = -5,
    DOM_FACTION_INSUFFICIENT = -6,
    DOM_FACTION_OVERFLOW = -7
};

enum dom_faction_policy_kind {
    DOM_FACTION_POLICY_BALANCED = 0u,
    DOM_FACTION_POLICY_EXPANSION = 1u,
    DOM_FACTION_POLICY_CONSERVE = 2u
};

enum dom_faction_policy_flags {
    DOM_FACTION_POLICY_ALLOW_STATION = 1u << 0,
    DOM_FACTION_POLICY_ALLOW_ROUTE = 1u << 1,
    DOM_FACTION_POLICY_ALLOW_EVENTS = 1u << 2
};

typedef u64 dom_faction_id;

typedef struct dom_faction_resource_entry {
    dom_resource_id resource_id;
    i64 quantity;
} dom_faction_resource_entry;

typedef struct dom_faction_resource_delta {
    dom_resource_id resource_id;
    i64 delta;
} dom_faction_resource_delta;

typedef struct dom_faction_desc {
    dom_faction_id faction_id;
    u32 home_scope_kind;
    u64 home_scope_id;
    u32 policy_kind;
    u32 policy_flags;
    u64 ai_seed;
    const u64 *known_nodes;
    u32 known_node_count;
} dom_faction_desc;

typedef struct dom_faction_info {
    dom_faction_id faction_id;
    u32 home_scope_kind;
    u64 home_scope_id;
    u32 policy_kind;
    u32 policy_flags;
    u64 ai_seed;
    u32 known_node_count;
} dom_faction_info;

typedef void (*dom_faction_iter_fn)(const dom_faction_info *info, void *user);

typedef struct dom_faction_registry dom_faction_registry;

dom_faction_registry *dom_faction_registry_create(void);
void dom_faction_registry_destroy(dom_faction_registry *registry);
int dom_faction_registry_init(dom_faction_registry *registry);

int dom_faction_register(dom_faction_registry *registry,
                         const dom_faction_desc *desc);
int dom_faction_get(const dom_faction_registry *registry,
                    dom_faction_id faction_id,
                    dom_faction_info *out_info);
int dom_faction_iterate(const dom_faction_registry *registry,
                        dom_faction_iter_fn fn,
                        void *user);
u32 dom_faction_count(const dom_faction_registry *registry);

int dom_faction_list_known_nodes(const dom_faction_registry *registry,
                                 dom_faction_id faction_id,
                                 u64 *out_nodes,
                                 u32 max_nodes,
                                 u32 *out_count);

int dom_faction_resource_get(const dom_faction_registry *registry,
                             dom_faction_id faction_id,
                             dom_resource_id resource_id,
                             i64 *out_quantity);
int dom_faction_resource_list(const dom_faction_registry *registry,
                              dom_faction_id faction_id,
                              dom_faction_resource_entry *out_entries,
                              u32 max_entries,
                              u32 *out_count);
int dom_faction_update_resources(dom_faction_registry *registry,
                                 dom_faction_id faction_id,
                                 const dom_faction_resource_delta *deltas,
                                 u32 delta_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_FACTION_REGISTRY_H */
