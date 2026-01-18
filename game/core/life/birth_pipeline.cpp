/*
FILE: game/core/life/birth_pipeline.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements deterministic birth pipeline and scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pipeline ordering and IDs are deterministic.
*/
#include "dominium/life/birth_pipeline.h"

#include <string.h>

void life_id_gen_init(life_id_gen* gen, u64 start_id)
{
    if (!gen) {
        return;
    }
    gen->next_id = start_id ? start_id : 1u;
}

int life_id_next(life_id_gen* gen, u64* out_id)
{
    if (!gen || !out_id) {
        return -1;
    }
    if (gen->next_id == 0u) {
        return -2;
    }
    *out_id = gen->next_id++;
    if (gen->next_id == 0u) {
        return -3;
    }
    return 0;
}

static void life_sort_parents(u64* parent_ids,
                              u32* certainties,
                              u32 count)
{
    u32 i;
    if (!parent_ids || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        u64 key_id = parent_ids[i];
        u32 key_cert = certainties ? certainties[i] : 0u;
        u32 j = i;
        while (j > 0u) {
            u64 prev = parent_ids[j - 1u];
            u64 prev_cmp = (prev == 0u) ? 0xFFFFFFFFFFFFFFFFULL : prev;
            u64 key_cmp = (key_id == 0u) ? 0xFFFFFFFFFFFFFFFFULL : key_id;
            if (prev_cmp <= key_cmp) {
                break;
            }
            parent_ids[j] = parent_ids[j - 1u];
            if (certainties) {
                certainties[j] = certainties[j - 1u];
            }
            --j;
        }
        parent_ids[j] = key_id;
        if (certainties) {
            certainties[j] = key_cert;
        }
    }
}

static dom_act_time_t life_gestation_next_due(void* user, dom_act_time_t now_tick)
{
    life_birth_due_user* due = (life_birth_due_user*)user;
    (void)now_tick;
    if (!due || !due->gestation) {
        return DG_DUE_TICK_NONE;
    }
    if (due->gestation->status != LIFE_GESTATION_ACTIVE) {
        return DG_DUE_TICK_NONE;
    }
    return due->gestation->expected_end_act;
}

static void life_birth_notice_emit(life_birth_scheduler* sched,
                                   u64 birth_event_id,
                                   const life_birth_event* birth)
{
    life_birth_notice notice;
    if (!sched || !sched->notice_cb || !birth) {
        return;
    }
    notice.birth_event_id = birth_event_id;
    notice.child_person_id = birth->child_person_id;
    notice.parent_count = birth->parent_count;
    notice.parent_ids[0] = birth->parent_ids[0];
    notice.parent_ids[1] = birth->parent_ids[1];
    notice.act_time_of_birth = birth->act_time_of_birth;
    notice.location_ref = birth->location_ref;
    sched->notice_cb(sched->notice_user, &notice);
}

static int life_birth_complete(life_birth_scheduler* sched,
                               life_gestation_state* gestation)
{
    u64 child_person_id = 0u;
    u64 birth_event_id = 0u;
    life_birth_event birth_event;

    if (!sched || !gestation) {
        return DG_DUE_ERR;
    }
    if (life_id_next(sched->person_ids, &child_person_id) != 0) {
        return DG_DUE_ERR;
    }
    if (life_person_register(sched->persons, child_person_id) != 0) {
        return DG_DUE_ERR;
    }

    if (gestation->micro_active && sched->bodies && sched->body_ids) {
        u64 body_id = 0u;
        if (life_id_next(sched->body_ids, &body_id) != 0) {
            return DG_DUE_ERR;
        }
        if (life_body_register(sched->bodies, body_id, child_person_id, LIFE_BODY_ALIVE) != 0) {
            return DG_DUE_ERR;
        }
    }

    if (!gestation->micro_active && sched->cohorts && gestation->cohort_id != 0u) {
        (void)life_cohort_add_birth(sched->cohorts, gestation->cohort_id, 1u);
    }

    memset(&birth_event, 0, sizeof(birth_event));
    birth_event.child_person_id = child_person_id;
    birth_event.parent_count = gestation->parent_count;
    birth_event.parent_ids[0] = gestation->parent_ids[0];
    birth_event.parent_ids[1] = gestation->parent_ids[1];
    birth_event.act_time_of_birth = gestation->expected_end_act;
    birth_event.location_ref = gestation->location_ref;
    birth_event.provenance_ref = gestation->provenance_ref;
    if (life_birth_event_append(sched->births, &birth_event, &birth_event_id) != 0) {
        return DG_DUE_ERR;
    }

    if (sched->audit_log) {
        life_audit_entry entry;
        entry.audit_id = 0u;
        entry.kind = LIFE_AUDIT_BIRTH;
        entry.subject_id = child_person_id;
        entry.related_id = gestation->gestation_id;
        entry.code = 0u;
        entry.act_tick = gestation->expected_end_act;
        (void)life_audit_log_append(sched->audit_log, &entry);
    }

    life_birth_notice_emit(sched, birth_event_id, &birth_event);

    gestation->status = LIFE_GESTATION_COMPLETED;
    return DG_DUE_OK;
}

static int life_gestation_process_until(void* user, dom_act_time_t target_tick)
{
    life_birth_due_user* due = (life_birth_due_user*)user;
    life_gestation_state* gestation;

    if (!due || !due->scheduler || !due->gestation) {
        return DG_DUE_ERR;
    }
    gestation = due->gestation;
    if (gestation->status != LIFE_GESTATION_ACTIVE) {
        return DG_DUE_OK;
    }
    if (gestation->expected_end_act > target_tick) {
        return DG_DUE_OK;
    }
    return life_birth_complete(due->scheduler, gestation);
}

static dg_due_vtable g_life_gestation_vtable = {
    life_gestation_next_due,
    life_gestation_process_until
};

int life_birth_scheduler_init(life_birth_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              life_birth_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              life_gestation_registry* gestations,
                              life_birth_event_list* births,
                              life_cohort_registry* cohorts,
                              life_person_registry* persons,
                              life_body_registry* bodies,
                              life_id_gen* person_ids,
                              life_id_gen* body_ids,
                              life_audit_log* audit_log,
                              life_birth_notice_cb notice_cb,
                              void* notice_user)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage) {
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
    sched->gestations = gestations;
    sched->births = births;
    sched->cohorts = cohorts;
    sched->persons = persons;
    sched->bodies = bodies;
    sched->person_ids = person_ids;
    sched->body_ids = body_ids;
    sched->audit_log = audit_log;
    sched->notice_cb = notice_cb;
    sched->notice_user = notice_user;
    memset(user_storage, 0, sizeof(life_birth_due_user) * (size_t)entry_capacity);
    return 0;
}

int life_birth_scheduler_register(life_birth_scheduler* sched,
                                  life_gestation_state* gestation)
{
    u32 handle = 0u;
    life_birth_due_user* due;
    if (!sched || !gestation) {
        return -1;
    }
    if (gestation->expected_end_act < gestation->start_act) {
        return -2;
    }
    if (sched->due.entry_count >= sched->due.entry_capacity) {
        return -3;
    }
    due = &sched->due_users[sched->due.entry_count];
    due->scheduler = sched;
    due->gestation = gestation;
    if (dg_due_scheduler_register(&sched->due, &g_life_gestation_vtable, due,
                                  gestation->gestation_id, &handle) != DG_DUE_OK) {
        return -4;
    }
    return 0;
}

int life_birth_scheduler_advance(life_birth_scheduler* sched,
                                 dom_act_time_t target_tick)
{
    if (!sched) {
        return -1;
    }
    if (dg_due_scheduler_advance(&sched->due, target_tick) != DG_DUE_OK) {
        return -2;
    }
    return 0;
}

static int life_check_authority(const life_birth_context* ctx,
                                u64 controller_id,
                                const u64* parent_ids,
                                u32 parent_count)
{
    u32 i;
    if (!ctx || !ctx->authority || controller_id == 0u) {
        return 1;
    }
    for (i = 0u; i < parent_count; ++i) {
        if (parent_ids[i] == 0u) {
            continue;
        }
        if (!life_authority_can_control(ctx->authority, controller_id, parent_ids[i], 0)) {
            return 0;
        }
    }
    return 1;
}

int life_request_birth(life_birth_context* ctx,
                       const life_birth_request* request,
                       life_birth_refusal_code* out_refusal,
                       u64* out_gestation_id)
{
    life_gestation_state gestation;
    u64 parents[2] = { 0u, 0u };
    u32 certainties[2] = { LIFE_LINEAGE_UNKNOWN, LIFE_LINEAGE_UNKNOWN };
    life_birth_refusal_code refusal = LIFE_BIRTH_REFUSAL_NONE;
    u64 gestation_id = 0u;
    u32 parent_count;

    if (out_refusal) {
        *out_refusal = LIFE_BIRTH_REFUSAL_NONE;
    }
    if (!ctx || !request || !ctx->gestations || !ctx->scheduler) {
        return -1;
    }
    if (!ctx->reproduction_rules) {
        refusal = LIFE_BIRTH_REFUSAL_POLICY_DISALLOWS_BIRTH;
        goto refusal_out;
    }

    parent_count = request->parent_count;
    if (parent_count > 2u) {
        refusal = LIFE_BIRTH_REFUSAL_INELIGIBLE_PARENTS;
        goto refusal_out;
    }
    if (parent_count > 0u) {
        parents[0] = request->parent_ids[0];
        certainties[0] = request->parent_certainty[0];
    }
    if (parent_count > 1u) {
        parents[1] = request->parent_ids[1];
        certainties[1] = request->parent_certainty[1];
    }
    life_sort_parents(parents, certainties, parent_count);

    if (!life_reproduction_rules_validate(ctx->reproduction_rules, parents, parent_count)) {
        refusal = LIFE_BIRTH_REFUSAL_INELIGIBLE_PARENTS;
        goto refusal_out;
    }
    if (!life_needs_constraints_ok(&request->needs)) {
        refusal = LIFE_BIRTH_REFUSAL_INSUFFICIENT_RESOURCES;
        goto refusal_out;
    }
    if (!life_check_authority(ctx, request->controller_id, parents, parent_count)) {
        refusal = LIFE_BIRTH_REFUSAL_INSUFFICIENT_AUTHORITY;
        goto refusal_out;
    }
    if (life_gestation_find_active(ctx->gestations, parents, parent_count)) {
        refusal = LIFE_BIRTH_REFUSAL_GESTATION_ALREADY_ACTIVE;
        goto refusal_out;
    }

    memset(&gestation, 0, sizeof(gestation));
    gestation.parent_ids[0] = parents[0];
    gestation.parent_ids[1] = parents[1];
    gestation.parent_count = parent_count;
    gestation.parent_certainty[0] = certainties[0];
    gestation.parent_certainty[1] = certainties[1];
    gestation.start_act = request->act_time;
    gestation.expected_end_act = request->act_time + ctx->reproduction_rules->gestation_ticks;
    if (gestation.expected_end_act < gestation.start_act) {
        refusal = LIFE_BIRTH_REFUSAL_POLICY_DISALLOWS_BIRTH;
        goto refusal_out;
    }
    gestation.resource_contract_count = 0u;
    gestation.status = LIFE_GESTATION_ACTIVE;
    gestation.cohort_id = request->cohort_id;
    gestation.location_ref = request->location_ref;
    gestation.provenance_ref = request->provenance_ref;
    gestation.micro_active = request->micro_active;

    if (life_gestation_append(ctx->gestations, &gestation, &gestation_id) != 0) {
        return -2;
    }

    {
        life_gestation_state* state = life_gestation_find_by_id(ctx->gestations, gestation_id);
        if (!state) {
            return -3;
        }
        if (life_birth_scheduler_register(ctx->scheduler, state) != 0) {
            refusal = LIFE_BIRTH_REFUSAL_POLICY_DISALLOWS_BIRTH;
            goto refusal_out;
        }
    }

    if (out_gestation_id) {
        *out_gestation_id = gestation_id;
    }
    if (out_refusal) {
        *out_refusal = LIFE_BIRTH_REFUSAL_NONE;
    }
    return 0;

refusal_out:
    if (out_refusal) {
        *out_refusal = refusal;
    }
    if (ctx->audit_log) {
        life_audit_entry entry;
        entry.audit_id = 0u;
        entry.kind = LIFE_AUDIT_REFUSAL;
        entry.subject_id = 0u;
        entry.related_id = 0u;
        entry.code = refusal;
        entry.act_tick = request ? request->act_time : 0;
        (void)life_audit_log_append(ctx->audit_log, &entry);
    }
    return 1;
}
