/*
FILE: include/dominium/rules/knowledge/institution_knowledge_binding.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / knowledge
RESPONSIBILITY: Defines knowledge-holding institutions and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Institution ordering and holdings are deterministic.
*/
#ifndef DOMINIUM_RULES_KNOWLEDGE_INSTITUTION_BINDING_H
#define DOMINIUM_RULES_KNOWLEDGE_INSTITUTION_BINDING_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define KNOWLEDGE_MAX_HOLDINGS 16u

typedef enum knowledge_institution_type {
    KNOW_INST_LAB = 1,
    KNOW_INST_GUILD = 2,
    KNOW_INST_UNIVERSITY = 3,
    KNOW_INST_ARCHIVE = 4
} knowledge_institution_type;

typedef struct knowledge_institution {
    u64 institution_id;
    knowledge_institution_type type;
    u32 capacity;
    u64 secrecy_policy_id;
    u64 holdings[KNOWLEDGE_MAX_HOLDINGS];
    u32 holdings_count;
} knowledge_institution;

typedef struct knowledge_institution_registry {
    knowledge_institution* institutions;
    u32 count;
    u32 capacity;
} knowledge_institution_registry;

void knowledge_institution_registry_init(knowledge_institution_registry* reg,
                                         knowledge_institution* storage,
                                         u32 capacity);
int knowledge_institution_register(knowledge_institution_registry* reg,
                                   u64 institution_id,
                                   knowledge_institution_type type,
                                   u32 capacity,
                                   u64 secrecy_policy_id);
knowledge_institution* knowledge_institution_find(knowledge_institution_registry* reg,
                                                  u64 institution_id);
int knowledge_institution_add_holding(knowledge_institution_registry* reg,
                                      u64 institution_id,
                                      u64 knowledge_id);
int knowledge_institution_knows(const knowledge_institution_registry* reg,
                                u64 institution_id,
                                u64 knowledge_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_KNOWLEDGE_INSTITUTION_BINDING_H */
