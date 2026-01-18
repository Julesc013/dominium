/*
FILE: include/dominium/rules/technology/tech_prerequisites.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / technology
RESPONSIBILITY: Defines technology prerequisites based on knowledge thresholds.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Prerequisite ordering and checks are deterministic.
*/
#ifndef DOMINIUM_RULES_TECH_PREREQUISITES_H
#define DOMINIUM_RULES_TECH_PREREQUISITES_H

#include "domino/core/types.h"
#include "dominium/rules/knowledge/knowledge_item.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tech_prerequisite {
    u64 tech_id;
    u64 knowledge_id;
    u32 min_completeness;
} tech_prerequisite;

typedef struct tech_prereq_registry {
    tech_prerequisite* prereqs;
    u32 count;
    u32 capacity;
} tech_prereq_registry;

void tech_prereq_registry_init(tech_prereq_registry* reg,
                               tech_prerequisite* storage,
                               u32 capacity);
int tech_prereq_register(tech_prereq_registry* reg,
                         u64 tech_id,
                         u64 knowledge_id,
                         u32 min_completeness);
int tech_prereqs_met(const tech_prereq_registry* reg,
                     const knowledge_registry* knowledge,
                     u64 tech_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_TECH_PREREQUISITES_H */
