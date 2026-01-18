/*
FILE: game/rules/knowledge/research_process.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / knowledge
RESPONSIBILITY: Implements research processes and deterministic schedulers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Research ordering and scheduling are deterministic.
*/
#include "dominium/rules/knowledge/research_process.h"

#include <string.h>

void research_process_registry_init(research_process_registry* reg,
                                    research_process* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->processes = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(research_process) * (size_t)capacity);
    }
}

static u32 research_process_find_index(const research_process_registry* reg,
                                       u64 process_id,
                                       int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->processes) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->processes[i].process_id == process_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->processes[i].process_id > process_id) {
            break;
        }
    }
    return i;
}

int research_process_register(research_process_registry* reg,
                              u64 process_id,
                              u64 institution_id,
                              dom_act_time_t start_act,
                              dom_act_time_t completion_act)
{
    int found = 0;
    u32 idx;
    u32 i;
    research_process* entry;
    if (!reg || !reg->processes) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = research_process_find_index(reg, process_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->processes[i] = reg->processes[i - 1u];
    }
    entry = &reg->processes[idx];
    memset(entry, 0, sizeof(*entry));
    entry->process_id = process_id;
    entry->institution_id = institution_id;
    entry->start_act = start_act;
    entry->completion_act = completion_act;
    entry->next_due_tick = start_act;
    entry->status = RESEARCH_PENDING;
    entry->refusal = KNOW_REFUSAL_NONE;
    reg->count += 1u;
    return 0;
}

research_process* research_process_find(research_process_registry* reg,
                                        u64 process_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->processes) {
        return 0;
    }
    idx = research_process_find_index(reg, process_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->processes[idx];
}

static int research_insert_requirement(knowledge_requirement* reqs,
                                       u32* count,
                                       u32 max_count,
                                       u64 knowledge_id,
                                       u32 min_completeness)
{
    u32 i;
    if (!reqs || !count) {
        return -1;
    }
    if (*count >= max_count) {
        return -2;
    }
    for (i = 0u; i < *count; ++i) {
        if (reqs[i].knowledge_id == knowledge_id) {
            reqs[i].min_completeness = min_completeness;
            return 0;
        }
        if (reqs[i].knowledge_id > knowledge_id) {
            break;
        }
    }
    if (i < *count) {
        u32 j;
        for (j = *count; j > i; --j) {
            reqs[j] = reqs[j - 1u];
        }
    }
    reqs[i].knowledge_id = knowledge_id;
    reqs[i].min_completeness = min_completeness;
    *count += 1u;
    return 0;
}

int research_process_add_prereq(research_process_registry* reg,
                                u64 process_id,
                                u64 knowledge_id,
                                u32 min_completeness)
{
    research_process* proc = research_process_find(reg, process_id);
    if (!proc) {
        return -1;
    }
    return research_insert_requirement(proc->prerequisites,
                                       &proc->prerequisite_count,
                                       KNOW_RESEARCH_MAX_PREREQS,
                                       knowledge_id,
                                       min_completeness);
}

static int research_insert_output(u64* outputs,
                                  u32* count,
                                  u32 max_count,
                                  u64 knowledge_id)
{
    u32 i;
    if (!outputs || !count) {
        return -1;
    }
    if (*count >= max_count) {
        return -2;
    }
    for (i = 0u; i < *count; ++i) {
        if (outputs[i] == knowledge_id) {
            return 0;
        }
        if (outputs[i] > knowledge_id) {
            break;
        }
    }
    if (i < *count) {
        u32 j;
        for (j = *count; j > i; --j) {
            outputs[j] = outputs[j - 1u];
        }
    }
    outputs[i] = knowledge_id;
    *count += 1u;
    return 0;
}

int research_process_add_output(research_process_registry* reg,
                                u64 process_id,
                                u64 knowledge_id)
{
    research_process* proc = research_process_find(reg, process_id);
    if (!proc) {
        return -1;
    }
    return research_insert_output(proc->output_knowledge_ids,
                                  &proc->output_count,
                                  KNOW_RESEARCH_MAX_OUTPUTS,
                                  knowledge_id);
}

static int research_prereqs_met(const research_process* proc,
                                const knowledge_registry* knowledge)
{
    u32 i;
    if (!proc) {
        return 0;
    }
    if (!knowledge) {
        return 0;
    }
    for (i = 0u; i < proc->prerequisite_count; ++i) {
        const knowledge_item* item;
        u64 knowledge_id = proc->prerequisites[i].knowledge_id;
        u32 min_comp = proc->prerequisites[i].min_completeness;
        item = knowledge_find((knowledge_registry*)knowledge, knowledge_id);
        if (!item) {
            return 0;
        }
        if (item->completeness < min_comp) {
            return 0;
        }
    }
    return 1;
}

static int research_apply_outputs(const research_process* proc,
                                  knowledge_registry* knowledge)
{
    u32 i;
    if (!proc || !knowledge) {
        return -1;
    }
    for (i = 0u; i < proc->output_count; ++i) {
        u64 knowledge_id = proc->output_knowledge_ids[i];
        knowledge_item* item = knowledge_find(knowledge, knowledge_id);
        if (!item) {
            return -2;
        }
        item->completeness = KNOWLEDGE_COMPLETENESS_MAX;
        item->status = KNOW_STATUS_KNOWN;
    }
    return 0;
}

static dom_act_time_t research_due_next_tick(void* user, dom_act_time_t now_tick)
{
    research_due_user* due = (research_due_user*)user;
    (void)now_tick;
    if (!due || !due->process) {
        return DG_DUE_TICK_NONE;
    }
    if (due->process->status == RESEARCH_COMPLETED ||
        due->process->status == RESEARCH_REFUSED) {
        return DG_DUE_TICK_NONE;
    }
    return due->process->next_due_tick;
}

static int research_due_process_until(void* user, dom_act_time_t target_tick)
{
    research_due_user* due = (research_due_user*)user;
    research_scheduler* sched;
    research_process* proc;
    dom_act_time_t next_tick;

    if (!due || !due->scheduler || !due->process) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    proc = due->process;
    next_tick = proc->next_due_tick;
    if (next_tick == DG_DUE_TICK_NONE || next_tick > target_tick) {
        return DG_DUE_OK;
    }

    while (next_tick != DG_DUE_TICK_NONE && next_tick <= target_tick) {
        sched->processed_last += 1u;
        sched->processed_total += 1u;
        if (proc->status == RESEARCH_PENDING) {
            if (sched->institutions) {
                if (!knowledge_institution_find(sched->institutions, proc->institution_id)) {
                    proc->status = RESEARCH_REFUSED;
                    proc->refusal = KNOW_REFUSAL_INSTITUTION_NOT_AUTHORIZED;
                    proc->next_due_tick = DG_DUE_TICK_NONE;
                    return DG_DUE_OK;
                }
            }
            if (!research_prereqs_met(proc, sched->knowledge)) {
                proc->status = RESEARCH_REFUSED;
                proc->refusal = KNOW_REFUSAL_MISSING_PREREQUISITES;
                proc->next_due_tick = DG_DUE_TICK_NONE;
                return DG_DUE_OK;
            }
            proc->status = RESEARCH_ACTIVE;
            proc->next_due_tick = proc->completion_act;
        } else if (proc->status == RESEARCH_ACTIVE) {
            if (research_apply_outputs(proc, sched->knowledge) != 0) {
                proc->status = RESEARCH_REFUSED;
                proc->refusal = KNOW_REFUSAL_UNKNOWN_KNOWLEDGE;
                proc->next_due_tick = DG_DUE_TICK_NONE;
                return DG_DUE_OK;
            }
            proc->status = RESEARCH_COMPLETED;
            proc->next_due_tick = DG_DUE_TICK_NONE;
            if (sched->completion_hook.on_complete) {
                (void)sched->completion_hook.on_complete(sched->completion_hook.user, proc);
            }
        } else {
            proc->next_due_tick = DG_DUE_TICK_NONE;
        }
        next_tick = proc->next_due_tick;
    }
    return DG_DUE_OK;
}

static dg_due_vtable g_research_due_vtable = {
    research_due_next_tick,
    research_due_process_until
};

int research_scheduler_init(research_scheduler* sched,
                            dom_time_event* event_storage,
                            u32 event_capacity,
                            dg_due_entry* entry_storage,
                            research_due_user* user_storage,
                            u32 entry_capacity,
                            dom_act_time_t start_tick,
                            research_process_registry* processes,
                            knowledge_registry* knowledge,
                            knowledge_institution_registry* institutions)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !processes || !knowledge) {
        return -1;
    }
    rc = dg_due_scheduler_init(&sched->due,
                               event_storage,
                               event_capacity,
                               entry_storage,
                               entry_capacity,
                               start_tick);
    if (rc != DG_DUE_OK) {
        return -2;
    }
    sched->due_events = event_storage;
    sched->due_entries = entry_storage;
    sched->due_users = user_storage;
    sched->processes = processes;
    sched->knowledge = knowledge;
    sched->institutions = institutions;
    sched->completion_hook.on_complete = 0;
    sched->completion_hook.user = 0;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(research_due_user) * (size_t)entry_capacity);
    return 0;
}

void research_scheduler_set_completion_hook(research_scheduler* sched,
                                            const research_completion_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->completion_hook = *hook;
    } else {
        sched->completion_hook.on_complete = 0;
        sched->completion_hook.user = 0;
    }
}

static int research_scheduler_alloc_handle(research_scheduler* sched,
                                           u32* out_handle)
{
    u32 i;
    if (!sched || !sched->due.entries || !out_handle) {
        return -1;
    }
    for (i = 0u; i < sched->due.entry_capacity; ++i) {
        if (!sched->due.entries[i].in_use) {
            *out_handle = i;
            return 0;
        }
    }
    return -2;
}

int research_scheduler_register(research_scheduler* sched,
                                research_process* process)
{
    u32 handle;
    research_due_user* due;
    if (!sched || !process) {
        return -1;
    }
    if (research_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    if (process->next_due_tick == DOM_TIME_ACT_MAX) {
        process->next_due_tick = process->start_act;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->process = process;
    if (dg_due_scheduler_register(&sched->due, &g_research_due_vtable, due,
                                  process->process_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int research_scheduler_advance(research_scheduler* sched,
                               dom_act_time_t target_tick,
                               knowledge_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = KNOW_REFUSAL_NONE;
    }
    if (!sched) {
        return -1;
    }
    sched->processed_last = 0u;
    if (dg_due_scheduler_advance(&sched->due, target_tick) != DG_DUE_OK) {
        if (out_refusal) {
            *out_refusal = KNOW_REFUSAL_MISSING_PREREQUISITES;
        }
        return -2;
    }
    return 0;
}

dom_act_time_t research_scheduler_next_due(const research_scheduler* sched)
{
    dom_time_event ev;
    if (!sched) {
        return DG_DUE_TICK_NONE;
    }
    if (dom_time_event_peek(&sched->due.queue, &ev) != DOM_TIME_OK) {
        return DG_DUE_TICK_NONE;
    }
    return ev.trigger_time;
}
