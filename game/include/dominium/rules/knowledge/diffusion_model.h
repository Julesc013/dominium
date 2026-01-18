/*
FILE: include/dominium/rules/knowledge/diffusion_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / knowledge
RESPONSIBILITY: Defines deterministic knowledge diffusion events and scheduler.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Diffusion ordering and delivery are deterministic.
*/
#ifndef DOMINIUM_RULES_KNOWLEDGE_DIFFUSION_MODEL_H
#define DOMINIUM_RULES_KNOWLEDGE_DIFFUSION_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/knowledge/institution_knowledge_binding.h"
#include "dominium/rules/knowledge/secrecy_controls.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum knowledge_diffusion_status {
    KNOW_DIFFUSION_PENDING = 0,
    KNOW_DIFFUSION_DELIVERED = 1,
    KNOW_DIFFUSION_BLOCKED = 2
} knowledge_diffusion_status;

typedef struct knowledge_diffusion_event {
    u64 diffusion_id;
    u64 knowledge_id;
    u64 src_actor_id;
    u64 dst_actor_id;
    u64 channel_id;
    dom_act_time_t send_act;
    dom_act_time_t receive_act;
    u32 fidelity;
    u32 uncertainty;
    u64 secrecy_policy_id;
    dom_act_time_t next_due_tick;
    knowledge_diffusion_status status;
} knowledge_diffusion_event;

typedef struct knowledge_diffusion_registry {
    knowledge_diffusion_event* events;
    u32 count;
    u32 capacity;
} knowledge_diffusion_registry;

void knowledge_diffusion_registry_init(knowledge_diffusion_registry* reg,
                                       knowledge_diffusion_event* storage,
                                       u32 capacity);
int knowledge_diffusion_register(knowledge_diffusion_registry* reg,
                                 u64 diffusion_id,
                                 u64 knowledge_id,
                                 u64 src_actor_id,
                                 u64 dst_actor_id,
                                 u64 channel_id,
                                 dom_act_time_t send_act,
                                 dom_act_time_t receive_act,
                                 u32 fidelity,
                                 u32 uncertainty,
                                 u64 secrecy_policy_id);
knowledge_diffusion_event* knowledge_diffusion_find(knowledge_diffusion_registry* reg,
                                                    u64 diffusion_id);

typedef struct knowledge_diffusion_hook {
    int (*deliver)(void* user, const knowledge_diffusion_event* event);
    void* user;
} knowledge_diffusion_hook;

typedef struct knowledge_diffusion_due_user {
    struct knowledge_diffusion_scheduler* scheduler;
    knowledge_diffusion_event* event;
} knowledge_diffusion_due_user;

typedef struct knowledge_diffusion_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    knowledge_diffusion_due_user* due_users;
    knowledge_diffusion_registry* registry;
    knowledge_institution_registry* institutions;
    const knowledge_secrecy_registry* secrecy;
    knowledge_diffusion_hook hook;
    u32 processed_last;
    u32 processed_total;
} knowledge_diffusion_scheduler;

int knowledge_diffusion_scheduler_init(knowledge_diffusion_scheduler* sched,
                                       dom_time_event* event_storage,
                                       u32 event_capacity,
                                       dg_due_entry* entry_storage,
                                       knowledge_diffusion_due_user* user_storage,
                                       u32 entry_capacity,
                                       dom_act_time_t start_tick,
                                       knowledge_diffusion_registry* registry,
                                       knowledge_institution_registry* institutions,
                                       const knowledge_secrecy_registry* secrecy);
void knowledge_diffusion_set_hook(knowledge_diffusion_scheduler* sched,
                                  const knowledge_diffusion_hook* hook);
int knowledge_diffusion_scheduler_register(knowledge_diffusion_scheduler* sched,
                                           knowledge_diffusion_event* event);
int knowledge_diffusion_scheduler_advance(knowledge_diffusion_scheduler* sched,
                                          dom_act_time_t target_tick);
dom_act_time_t knowledge_diffusion_scheduler_next_due(const knowledge_diffusion_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_KNOWLEDGE_DIFFUSION_MODEL_H */
