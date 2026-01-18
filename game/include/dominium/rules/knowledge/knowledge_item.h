/*
FILE: include/dominium/rules/knowledge/knowledge_item.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / knowledge
RESPONSIBILITY: Defines knowledge items and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Knowledge ordering and updates are deterministic.
*/
#ifndef DOMINIUM_RULES_KNOWLEDGE_ITEM_H
#define DOMINIUM_RULES_KNOWLEDGE_ITEM_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define KNOWLEDGE_COMPLETENESS_MAX 1000u

typedef enum knowledge_type {
    KNOW_TYPE_THEORY = 1,
    KNOW_TYPE_METHOD = 2,
    KNOW_TYPE_DESIGN = 3,
    KNOW_TYPE_DOCTRINE = 4
} knowledge_type;

typedef enum knowledge_epistemic_status {
    KNOW_STATUS_UNKNOWN = 0,
    KNOW_STATUS_RUMORED = 1,
    KNOW_STATUS_KNOWN = 2
} knowledge_epistemic_status;

typedef struct knowledge_item {
    u64 knowledge_id;
    knowledge_type type;
    u32 domain_tags;
    u32 completeness;
    u64 provenance_ref;
    knowledge_epistemic_status status;
} knowledge_item;

typedef struct knowledge_registry {
    knowledge_item* items;
    u32 count;
    u32 capacity;
} knowledge_registry;

void knowledge_registry_init(knowledge_registry* reg,
                             knowledge_item* storage,
                             u32 capacity);
int knowledge_register(knowledge_registry* reg,
                       u64 knowledge_id,
                       knowledge_type type,
                       u32 domain_tags);
knowledge_item* knowledge_find(knowledge_registry* reg, u64 knowledge_id);
int knowledge_set_completeness(knowledge_registry* reg,
                               u64 knowledge_id,
                               u32 completeness);
int knowledge_add_completeness(knowledge_registry* reg,
                               u64 knowledge_id,
                               u32 delta);
int knowledge_set_status(knowledge_registry* reg,
                         u64 knowledge_id,
                         knowledge_epistemic_status status);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_KNOWLEDGE_ITEM_H */
