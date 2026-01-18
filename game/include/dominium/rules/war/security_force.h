/*
FILE: include/dominium/rules/war/security_force.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines security force records, refusal codes, and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Force ordering and estimates are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_SECURITY_FORCE_H
#define DOMINIUM_RULES_WAR_SECURITY_FORCE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/epistemic.h"

#ifdef __cplusplus
extern "C" {
#endif

#define SECURITY_FORCE_MAX_EQUIPMENT 8u
#define SECURITY_FORCE_MAX_LOGISTICS 8u

typedef enum war_domain_scope {
    WAR_DOMAIN_LOCAL = 0,
    WAR_DOMAIN_PLANETARY = 1,
    WAR_DOMAIN_ORBITAL = 2,
    WAR_DOMAIN_INTERSTELLAR = 3,
    WAR_DOMAIN_GALACTIC = 4
} war_domain_scope;

typedef enum security_force_status {
    SECURITY_FORCE_INACTIVE = 0,
    SECURITY_FORCE_MOBILIZING = 1,
    SECURITY_FORCE_ACTIVE = 2,
    SECURITY_FORCE_DEMOBILIZED = 3
} security_force_status;

typedef enum war_refusal_code {
    WAR_REFUSAL_NONE = 0,
    WAR_REFUSAL_INSUFFICIENT_POPULATION = 1,
    WAR_REFUSAL_INSUFFICIENT_EQUIPMENT = 2,
    WAR_REFUSAL_INSUFFICIENT_LOGISTICS = 3,
    WAR_REFUSAL_INSUFFICIENT_AUTHORITY = 4,
    WAR_REFUSAL_INSUFFICIENT_LEGITIMACY = 5
} war_refusal_code;

const char* war_refusal_to_string(war_refusal_code code);

typedef struct security_force {
    u64 force_id;
    u64 owning_org_or_jurisdiction;
    u32 domain_scope;
    u64 cohort_ref;
    u64 equipment_refs[SECURITY_FORCE_MAX_EQUIPMENT];
    u32 equipment_qtys[SECURITY_FORCE_MAX_EQUIPMENT];
    u32 equipment_count;
    u64 readiness_state_ref;
    u64 morale_state_ref;
    u64 logistics_dependency_refs[SECURITY_FORCE_MAX_LOGISTICS];
    u32 logistics_dependency_count;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
    u32 status;
} security_force;

typedef struct security_force_registry {
    security_force* forces;
    u32 count;
    u32 capacity;
    u64 next_force_id;
} security_force_registry;

void security_force_registry_init(security_force_registry* reg,
                                  security_force* storage,
                                  u32 capacity,
                                  u64 start_force_id);
security_force* security_force_find(security_force_registry* reg,
                                    u64 force_id);
int security_force_register(security_force_registry* reg,
                            u64 force_id,
                            u64 owning_org_or_jurisdiction,
                            u32 domain_scope,
                            u64 cohort_ref,
                            u64 provenance_ref);
int security_force_add_equipment(security_force_registry* reg,
                                 u64 force_id,
                                 u64 equipment_id,
                                 u32 qty);
int security_force_add_logistics_dependency(security_force_registry* reg,
                                            u64 force_id,
                                            u64 dependency_ref);
int security_force_set_states(security_force_registry* reg,
                              u64 force_id,
                              u64 readiness_state_ref,
                              u64 morale_state_ref);
int security_force_set_status(security_force_registry* reg,
                              u64 force_id,
                              u32 status);

typedef struct security_force_estimate {
    u32 estimated_count;
    u32 estimated_readiness;
    u32 estimated_morale;
    u32 uncertainty_q16;
    int is_exact;
} security_force_estimate;

int security_force_estimate_from_view(const dom_epistemic_view* view,
                                      u32 actual_count,
                                      u32 readiness_level,
                                      u32 morale_level,
                                      security_force_estimate* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_SECURITY_FORCE_H */
