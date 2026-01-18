/*
FILE: include/dominium/rules/scale/scale_domains.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / scale
RESPONSIBILITY: Defines scale domains and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Domain ordering and lookups are deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_DOMAINS_H
#define DOMINIUM_RULES_SCALE_DOMAINS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum scale_domain_type {
    SCALE_DOMAIN_LOCAL = 1,
    SCALE_DOMAIN_PLANETARY = 2,
    SCALE_DOMAIN_ORBITAL = 3,
    SCALE_DOMAIN_SYSTEM = 4,
    SCALE_DOMAIN_INTERSTELLAR = 5,
    SCALE_DOMAIN_GALACTIC = 6,
    SCALE_DOMAIN_UNIVERSAL = 7
} scale_domain_type;

typedef enum scale_fidelity_limit {
    SCALE_FIDELITY_MACRO = 1,
    SCALE_FIDELITY_MESO = 2,
    SCALE_FIDELITY_MICRO = 3
} scale_fidelity_limit;

typedef struct scale_domain_record {
    u64 domain_id;
    scale_domain_type type;
    u32 min_warp;
    u32 max_warp;
    u32 default_step_act;
    scale_fidelity_limit fidelity_limit;
} scale_domain_record;

typedef struct scale_domain_registry {
    scale_domain_record* records;
    u32 count;
    u32 capacity;
} scale_domain_registry;

void scale_domain_registry_init(scale_domain_registry* reg,
                                scale_domain_record* storage,
                                u32 capacity);
int scale_domain_register(scale_domain_registry* reg,
                          u64 domain_id,
                          scale_domain_type type,
                          u32 min_warp,
                          u32 max_warp,
                          u32 default_step_act,
                          scale_fidelity_limit fidelity_limit);
scale_domain_record* scale_domain_find(scale_domain_registry* reg,
                                       u64 domain_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_DOMAINS_H */
