/*
FILE: include/dominium/rules/knowledge/research_process.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / knowledge
RESPONSIBILITY: Defines research processes and deterministic schedulers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Research ordering and scheduling are deterministic.
*/
#ifndef DOMINIUM_RULES_KNOWLEDGE_RESEARCH_PROCESS_H
#define DOMINIUM_RULES_KNOWLEDGE_RESEARCH_PROCESS_H

#include "domino/core/dom_time_core.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/knowledge/institution_knowledge_binding.h"
#include "dominium/rules/knowledge/knowledge_item.h"
#include "dominium/rules/knowledge/knowledge_refusal_codes.h"

#ifdef __cplusplus
extern "C" {
#endif

#define KNOW_RESEARCH_MAX_PREREQS 8u
#define KNOW_RESEARCH_MAX_OUTPUTS 8u

typedef struct knowledge_requirement {
    u64 knowledge_id;
    u32 min_completeness;
} knowledge_requirement;

typedef enum research_status {
    RESEARCH_PENDING = 0,
    RESEARCH_ACTIVE = 1,
    RESEARCH_COMPLETED = 2,
    RESEARCH_REFUSED = 3
} research_status;

typedef struct research_process {
    u64 process_id;
    u64 institution_id;
    dom_act_time_t start_act;
    dom_act_time_t completion_act;
    knowledge_requirement prerequisites[KNOW_RESEARCH_MAX_PREREQS];
    u32 prerequisite_count;
    u64 output_knowledge_ids[KNOW_RESEARCH_MAX_OUTPUTS];
    u32 output_count;
    dom_act_time_t next_due_tick;
    research_status status;
    knowledge_refusal_code refusal;
} research_process;

typedef struct research_process_registry {
    research_process* processes;
    u32 count;
    u32 capacity;
} research_process_registry;

void research_process_registry_init(research_process_registry* reg,
                                    research_process* storage,
                                    u32 capacity);
int research_process_register(research_process_registry* reg,
                              u64 process_id,
                              u64 institution_id,
                              dom_act_time_t start_act,
                              dom_act_time_t completion_act);
research_process* research_process_find(research_process_registry* reg,
                                        u64 process_id);
int research_process_add_prereq(research_process_registry* reg,
                                u64 process_id,
                                u64 knowledge_id,
                                u32 min_completeness);
int research_process_add_output(research_process_registry* reg,
                                u64 process_id,
                                u64 knowledge_id);

typedef struct research_completion_hook {
    int (*on_complete)(void* user, const research_process* process);
    void* user;
} research_completion_hook;

typedef struct research_due_user {
    struct research_scheduler* scheduler;
    research_process* process;
} research_due_user;

typedef struct research_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    research_due_user* due_users;
    research_process_registry* processes;
    knowledge_registry* knowledge;
    knowledge_institution_registry* institutions;
    research_completion_hook completion_hook;
    u32 processed_last;
    u32 processed_total;
} research_scheduler;

int research_scheduler_init(research_scheduler* sched,
                            dom_time_event* event_storage,
                            u32 event_capacity,
                            dg_due_entry* entry_storage,
                            research_due_user* user_storage,
                            u32 entry_capacity,
                            dom_act_time_t start_tick,
                            research_process_registry* processes,
                            knowledge_registry* knowledge,
                            knowledge_institution_registry* institutions);
void research_scheduler_set_completion_hook(research_scheduler* sched,
                                            const research_completion_hook* hook);
int research_scheduler_register(research_scheduler* sched,
                                research_process* process);
int research_scheduler_advance(research_scheduler* sched,
                               dom_act_time_t target_tick,
                               knowledge_refusal_code* out_refusal);
dom_act_time_t research_scheduler_next_due(const research_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_KNOWLEDGE_RESEARCH_PROCESS_H */
