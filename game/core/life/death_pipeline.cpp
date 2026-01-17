/*
FILE: game/core/life/death_pipeline.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements deterministic death pipeline and estate creation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pipeline ordering and IDs are deterministic.
*/
#include "dominium/life/death_pipeline.h"

#include <string.h>

void life_body_registry_init(life_body_registry* reg,
                             life_body_record* storage,
                             u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->bodies = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_body_record) * (size_t)capacity);
    }
}

static u32 life_body_find_index(const life_body_registry* reg,
                                u64 body_id,
                                int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->bodies) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->bodies[i].body_id == body_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->bodies[i].body_id > body_id) {
            break;
        }
    }
    return i;
}

int life_body_register(life_body_registry* reg,
                       u64 body_id,
                       u64 person_id,
                       u32 alive_state)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->bodies) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = life_body_find_index(reg, body_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->bodies[i] = reg->bodies[i - 1u];
    }
    reg->bodies[idx].body_id = body_id;
    reg->bodies[idx].person_id = person_id;
    reg->bodies[idx].alive_state = alive_state;
    reg->count += 1u;
    return 0;
}

life_body_record* life_body_find(life_body_registry* reg, u64 body_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->bodies) {
        return 0;
    }
    idx = life_body_find_index(reg, body_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->bodies[idx];
}

void life_person_registry_init(life_person_registry* reg,
                               life_person_record* storage,
                               u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->persons = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_person_record) * (size_t)capacity);
    }
}

int life_person_register(life_person_registry* reg, u64 person_id)
{
    u32 i;
    if (!reg || !reg->persons) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->persons[i].person_id == person_id) {
            return -3;
        }
    }
    reg->persons[reg->count++].person_id = person_id;
    return 0;
}

int life_person_exists(const life_person_registry* reg, u64 person_id)
{
    u32 i;
    if (!reg || !reg->persons) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->persons[i].person_id == person_id) {
            return 1;
        }
    }
    return 0;
}

static void life_audit_append(life_audit_log* log,
                              u32 kind,
                              u64 subject_id,
                              u64 related_id,
                              u32 code,
                              dom_act_time_t act_tick)
{
    life_audit_entry entry;
    if (!log) {
        return;
    }
    entry.audit_id = 0u;
    entry.kind = kind;
    entry.subject_id = subject_id;
    entry.related_id = related_id;
    entry.code = code;
    entry.act_tick = act_tick;
    (void)life_audit_log_append(log, &entry);
}

int life_handle_death(life_death_context* ctx,
                      const life_death_input* input,
                      life_death_refusal_code* out_refusal,
                      u64* out_death_event_id,
                      u64* out_estate_id)
{
    life_body_record* body;
    const dom_account_id_t* accounts = 0;
    u32 account_count = 0u;
    u64 estate_id = 0u;
    u64 death_event_id = 0u;
    life_death_event death_event;
    life_death_refusal_code refusal = LIFE_DEATH_REFUSAL_NONE;

    if (out_refusal) {
        *out_refusal = LIFE_DEATH_REFUSAL_NONE;
    }
    if (!ctx || !input || !ctx->ledger) {
        return -1;
    }
    if (!ctx->bodies || !ctx->persons || !ctx->person_accounts ||
        !ctx->death_events || !ctx->estates || !ctx->scheduler) {
        return -2;
    }

    body = life_body_find(ctx->bodies, input->body_id);
    if (!body || body->alive_state != LIFE_BODY_ALIVE) {
        refusal = LIFE_DEATH_REFUSAL_BODY_NOT_ALIVE;
        goto refusal_out;
    }
    if (!life_person_exists(ctx->persons, body->person_id)) {
        refusal = LIFE_DEATH_REFUSAL_PERSON_MISSING;
        goto refusal_out;
    }
    if (life_estate_find_by_person(ctx->estates, body->person_id)) {
        refusal = LIFE_DEATH_REFUSAL_ESTATE_ALREADY_EXISTS;
        goto refusal_out;
    }
    if (!life_person_account_get(ctx->person_accounts, body->person_id,
                                 &accounts, &account_count)) {
        refusal = LIFE_DEATH_REFUSAL_LEDGER_ACCOUNT_MISSING;
        goto refusal_out;
    }
    if (account_count == 0u) {
        refusal = LIFE_DEATH_REFUSAL_LEDGER_ACCOUNT_MISSING;
        goto refusal_out;
    }

    if (life_estate_create(ctx->estates,
                           ctx->ledger,
                           ctx->account_owners,
                           body->person_id,
                           accounts,
                           account_count,
                           input->act_time,
                           0u,
                           0u,
                           input->policy_id,
                           &estate_id) != 0) {
        refusal = LIFE_DEATH_REFUSAL_LEDGER_ACCOUNT_MISSING;
        goto refusal_out;
    }

    body->alive_state = LIFE_BODY_DEAD;

    memset(&death_event, 0, sizeof(death_event));
    death_event.body_id = body->body_id;
    death_event.person_id = body->person_id;
    death_event.cause_code = input->cause_code;
    death_event.act_time_of_death = input->act_time;
    death_event.location_ref = input->location_ref;
    death_event.provenance_ref = input->provenance_ref;
    death_event.estate_id = estate_id;

    if (life_death_event_append(ctx->death_events, &death_event, &death_event_id) != 0) {
        return -3;
    }

    {
        life_estate* estate = life_estate_find_by_id(ctx->estates, estate_id);
        if (!estate) {
            return -4;
        }
        if (life_inheritance_scheduler_register_estate(ctx->scheduler, estate) != 0) {
            refusal = LIFE_DEATH_REFUSAL_SCHEDULE_INVALID;
            goto refusal_out;
        }
    }

    life_audit_append(ctx->audit_log, LIFE_AUDIT_DEATH, body->body_id, estate_id, input->cause_code, input->act_time);
    life_audit_append(ctx->audit_log, LIFE_AUDIT_ESTATE, estate_id, body->person_id, 0u, input->act_time);

    if (ctx->notice_cb) {
        life_death_notice notice;
        notice.death_event_id = death_event_id;
        notice.body_id = body->body_id;
        notice.person_id = body->person_id;
        notice.cause_code = input->cause_code;
        notice.act_time_of_death = input->act_time;
        notice.location_ref = input->location_ref;
        ctx->notice_cb(ctx->notice_user, &notice);
    }

    if (out_death_event_id) {
        *out_death_event_id = death_event_id;
    }
    if (out_estate_id) {
        *out_estate_id = estate_id;
    }
    if (out_refusal) {
        *out_refusal = LIFE_DEATH_REFUSAL_NONE;
    }
    return 0;

refusal_out:
    if (out_refusal) {
        *out_refusal = refusal;
    }
    life_audit_append(ctx->audit_log, LIFE_AUDIT_REFUSAL, input->body_id, 0u, refusal, input->act_time);
    return 1;
}
