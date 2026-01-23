/*
LIFE death pipeline tests (LIFE2).
*/
#include "dominium/life/death_pipeline.h"

#include "domino/core/dom_ledger.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct life_test_context {
    dom_ledger ledger;

    life_body_record bodies_storage[4];
    life_person_record persons_storage[4];
    life_death_event death_storage[4];
    life_estate estate_storage[4];
    dom_account_id_t estate_account_storage[16];
    life_person_account_entry person_account_entries[4];
    dom_account_id_t person_account_storage[16];
    life_account_owner_entry owner_storage[16];
    life_inheritance_action action_storage[8];
    life_audit_entry audit_storage[16];
    dom_time_event due_event_storage[16];
    dg_due_entry due_entry_storage[8];
    life_inheritance_due_user due_user_storage[8];
    life_remains remains_storage[8];
    life_remains_aggregate remains_aggregate_storage[4];
    life_post_death_rights rights_storage[8];
    dom_time_event remains_due_event_storage[8];
    dg_due_entry remains_due_entry_storage[8];
    life_remains_decay_user remains_due_user_storage[8];

    life_body_registry bodies;
    life_person_registry persons;
    life_person_account_registry person_accounts;
    life_account_owner_registry owners;
    life_death_event_list deaths;
    life_estate_registry estates;
    life_inheritance_action_list actions;
    life_inheritance_scheduler scheduler;
    life_audit_log audit_log;
    life_remains_registry remains;
    life_remains_aggregate_registry remains_aggregates;
    life_post_death_rights_registry rights;
    life_remains_decay_scheduler remains_decay;

    life_death_context ctx;
} life_test_context;

static void life_test_context_init(life_test_context* t,
                                   dom_act_time_t start_tick,
                                   dom_act_time_t claim_period)
{
    memset(t, 0, sizeof(*t));
    (void)dom_ledger_init(&t->ledger);

    life_body_registry_init(&t->bodies, t->bodies_storage, 4u);
    life_person_registry_init(&t->persons, t->persons_storage, 4u);
    life_death_event_list_init(&t->deaths, t->death_storage, 4u, 1u);
    life_estate_registry_init(&t->estates, t->estate_storage, 4u,
                              t->estate_account_storage, 16u, 1u);
    life_person_account_registry_init(&t->person_accounts, t->person_account_entries, 4u,
                                      t->person_account_storage, 16u);
    life_account_owner_registry_init(&t->owners, t->owner_storage, 16u);
    life_inheritance_action_list_init(&t->actions, t->action_storage, 8u, 1u);
    life_audit_log_init(&t->audit_log, t->audit_storage, 16u, 1u);
    (void)life_inheritance_scheduler_init(&t->scheduler,
                                          t->due_event_storage,
                                          16u,
                                          t->due_entry_storage,
                                          t->due_user_storage,
                                          8u,
                                          start_tick,
                                          claim_period,
                                          &t->estates,
                                          &t->actions);
    life_remains_registry_init(&t->remains, t->remains_storage, 8u, 1u);
    life_remains_aggregate_registry_init(&t->remains_aggregates,
                                         t->remains_aggregate_storage,
                                         4u,
                                         1u);
    life_post_death_rights_registry_init(&t->rights, t->rights_storage, 8u, 1u);
    {
        life_remains_decay_rules rules;
        rules.fresh_to_decayed = 5;
        rules.decayed_to_skeletal = 5;
        rules.skeletal_to_unknown = 5;
        (void)life_remains_decay_scheduler_init(&t->remains_decay,
                                                t->remains_due_event_storage,
                                                8u,
                                                t->remains_due_entry_storage,
                                                t->remains_due_user_storage,
                                                8u,
                                                start_tick,
                                                &t->remains,
                                                &rules);
    }

    t->ctx.bodies = &t->bodies;
    t->ctx.persons = &t->persons;
    t->ctx.person_accounts = &t->person_accounts;
    t->ctx.account_owners = &t->owners;
    t->ctx.death_events = &t->deaths;
    t->ctx.estates = &t->estates;
    t->ctx.scheduler = &t->scheduler;
    t->ctx.audit_log = &t->audit_log;
    t->ctx.ledger = &t->ledger;
    t->ctx.notice_cb = 0;
    t->ctx.notice_user = 0;
    t->ctx.remains = &t->remains;
    t->ctx.rights = &t->rights;
    t->ctx.remains_decay = &t->remains_decay;
    t->ctx.remains_aggregates = &t->remains_aggregates;
    t->ctx.observation_hooks = 0;
}

static int setup_basic_person(life_test_context* t,
                              u64 person_id,
                              u64 body_id,
                              const dom_account_id_t* accounts,
                              u32 account_count)
{
    u32 i;
    if (!t) {
        return -1;
    }
    if (life_person_register(&t->persons, person_id) != 0) {
        return -2;
    }
    if (life_body_register(&t->bodies, body_id, person_id, LIFE_BODY_ALIVE) != 0) {
        return -3;
    }
    for (i = 0u; i < account_count; ++i) {
        if (dom_ledger_account_create(&t->ledger, accounts[i], 0u) != DOM_LEDGER_OK) {
            return -4;
        }
    }
    if (life_person_account_register(&t->person_accounts, person_id, accounts, account_count) != 0) {
        return -5;
    }
    return 0;
}

static int test_death_estate_determinism(void)
{
    life_test_context a;
    life_test_context b;
    life_death_input input;
    life_death_refusal_code refusal;
    u64 estate_id_a = 0u;
    u64 estate_id_b = 0u;
    const dom_account_id_t* accounts_a;
    const dom_account_id_t* accounts_b;
    u32 count_a = 0u;
    u32 count_b = 0u;
    dom_account_id_t acct_order_a[3] = { 2u, 1u, 3u };
    dom_account_id_t acct_order_b[3] = { 3u, 2u, 1u };

    life_test_context_init(&a, 0, 10);
    life_test_context_init(&b, 0, 10);
    EXPECT(setup_basic_person(&a, 42u, 7u, acct_order_a, 3u) == 0, "setup A failed");
    EXPECT(setup_basic_person(&b, 42u, 7u, acct_order_b, 3u) == 0, "setup B failed");

    memset(&input, 0, sizeof(input));
    input.body_id = 7u;
    input.cause_code = LIFE_DEATH_CAUSE_NATURAL;
    input.act_time = 100;
    input.policy_id = 1u;

    EXPECT(life_handle_death(&a.ctx, &input, &refusal, 0, &estate_id_a) == 0, "death A failed");
    EXPECT(refusal == LIFE_DEATH_REFUSAL_NONE, "death A refusal");
    EXPECT(life_handle_death(&b.ctx, &input, &refusal, 0, &estate_id_b) == 0, "death B failed");
    EXPECT(refusal == LIFE_DEATH_REFUSAL_NONE, "death B refusal");

    accounts_a = life_estate_accounts(&a.estates, life_estate_find_by_id(&a.estates, estate_id_a), &count_a);
    accounts_b = life_estate_accounts(&b.estates, life_estate_find_by_id(&b.estates, estate_id_b), &count_b);
    EXPECT(count_a == count_b, "estate account count mismatch");
    EXPECT(count_a == 3u, "estate account count");
    EXPECT(accounts_a[0] == accounts_b[0] &&
           accounts_a[1] == accounts_b[1] &&
           accounts_a[2] == accounts_b[2], "estate account ordering mismatch");
    return 0;
}

static int test_ledger_conservation(void)
{
    life_test_context t;
    dom_account_id_t accounts[2] = { 1u, 2u };
    dom_ledger_posting postings[2];
    dom_ledger_transaction tx;
    dom_transaction_id_t tx_id;
    dom_amount_t before = 0;
    dom_amount_t after = 0;
    life_death_input input;
    life_death_refusal_code refusal;

    life_test_context_init(&t, 0, 5);
    EXPECT(dom_ledger_account_create(&t.ledger, accounts[0], 0u) == DOM_LEDGER_OK, "ledger account1");
    EXPECT(dom_ledger_account_create(&t.ledger, accounts[1], DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE) == DOM_LEDGER_OK,
           "ledger account2");
    EXPECT(life_person_register(&t.persons, 5u) == 0, "register person");
    EXPECT(life_body_register(&t.bodies, 9u, 5u, LIFE_BODY_ALIVE) == 0, "register body");
    EXPECT(life_person_account_register(&t.person_accounts, 5u, accounts, 1u) == 0, "register accounts");

    EXPECT(dom_ledger_next_tx_id(&t.ledger, &tx_id) == DOM_LEDGER_OK, "next tx id");
    postings[0].account_id = accounts[0];
    postings[0].asset_id = 1u;
    postings[0].amount = 100;
    postings[0].lot_id = 0u;
    postings[0].provenance_id = 0u;
    postings[1].account_id = accounts[1];
    postings[1].asset_id = 1u;
    postings[1].amount = -100;
    postings[1].lot_id = 0u;
    postings[1].provenance_id = 0u;

    tx.tx_id = tx_id;
    tx.posting_count = 2u;
    tx.postings = postings;
    EXPECT(dom_ledger_transaction_apply(&t.ledger, &tx, 0) == DOM_LEDGER_OK, "apply tx");

    EXPECT(dom_ledger_balance_get(&t.ledger, accounts[0], 1u, &before) == DOM_LEDGER_OK, "balance before");

    memset(&input, 0, sizeof(input));
    input.body_id = 9u;
    input.cause_code = LIFE_DEATH_CAUSE_ACCIDENT;
    input.act_time = 50;
    input.policy_id = 1u;
    EXPECT(life_handle_death(&t.ctx, &input, &refusal, 0, 0) == 0, "death pipeline failed");
    EXPECT(refusal == LIFE_DEATH_REFUSAL_NONE, "unexpected refusal");

    EXPECT(dom_ledger_balance_get(&t.ledger, accounts[0], 1u, &after) == DOM_LEDGER_OK, "balance after");
    EXPECT(before == after, "ledger balance changed on death");
    return 0;
}

static int test_inheritance_schedule_equivalence(void)
{
    life_test_context a;
    life_test_context b;
    life_death_input input;
    life_death_refusal_code refusal;
    dom_account_id_t accounts[1] = { 11u };
    dom_act_time_t target_tick = 110;

    life_test_context_init(&a, 0, 10);
    life_test_context_init(&b, 0, 10);
    EXPECT(setup_basic_person(&a, 101u, 201u, accounts, 1u) == 0, "setup A");
    EXPECT(setup_basic_person(&b, 101u, 201u, accounts, 1u) == 0, "setup B");

    memset(&input, 0, sizeof(input));
    input.body_id = 201u;
    input.cause_code = LIFE_DEATH_CAUSE_NATURAL;
    input.act_time = 100;
    input.policy_id = 1u;

    EXPECT(life_handle_death(&a.ctx, &input, &refusal, 0, 0) == 0, "death A");
    EXPECT(life_handle_death(&b.ctx, &input, &refusal, 0, 0) == 0, "death B");

    EXPECT(life_inheritance_scheduler_advance(&a.scheduler, 105) == 0, "advance A1");
    EXPECT(a.actions.count == 0u, "unexpected action A");
    EXPECT(life_inheritance_scheduler_advance(&a.scheduler, target_tick) == 0, "advance A2");

    EXPECT(life_inheritance_scheduler_advance(&b.scheduler, target_tick) == 0, "advance B");
    EXPECT(a.actions.count == b.actions.count, "action count mismatch");
    EXPECT(a.actions.count == 1u, "expected one action");
    EXPECT(a.actions.actions[0].trigger_act == target_tick, "action trigger mismatch");
    EXPECT(b.actions.actions[0].trigger_act == target_tick, "action trigger mismatch B");
    return 0;
}

static int test_executor_authority_enforcement(void)
{
    life_test_context t;
    life_death_input input;
    life_death_refusal_code refusal;
    dom_account_id_t accounts[1] = { 21u };
    const life_estate* estate_ro;
    life_estate* estate;

    life_test_context_init(&t, 0, 5);
    EXPECT(setup_basic_person(&t, 33u, 77u, accounts, 1u) == 0, "setup failed");

    memset(&input, 0, sizeof(input));
    input.body_id = 77u;
    input.cause_code = LIFE_DEATH_CAUSE_VIOLENCE;
    input.act_time = 10;
    input.policy_id = 1u;
    EXPECT(life_handle_death(&t.ctx, &input, &refusal, 0, 0) == 0, "death failed");
    EXPECT(refusal == LIFE_DEATH_REFUSAL_NONE, "unexpected refusal");

    estate_ro = life_estate_find_by_person(&t.estates, 33u);
    EXPECT(estate_ro != 0, "estate missing");
    estate = life_estate_find_by_id(&t.estates, estate_ro->estate_id);
    EXPECT(estate != 0, "estate missing");
    estate->has_executor_authority = 0u;

    EXPECT(life_inheritance_scheduler_advance(&t.scheduler, 20) == 0, "advance failed");
    EXPECT(t.actions.count == 1u, "action count");
    EXPECT(t.actions.actions[0].refusal_code == LIFE_DEATH_REFUSAL_NO_EXECUTOR_AUTHORITY,
           "expected no executor authority refusal");
    return 0;
}

static void notice_counter(void* user, const life_death_notice* notice)
{
    u32* count = (u32*)user;
    (void)notice;
    if (count) {
        *count += 1u;
    }
}

static int test_epistemic_notice_hook(void)
{
    life_test_context t;
    life_death_input input;
    life_death_refusal_code refusal;
    dom_account_id_t accounts[1] = { 31u };
    u32 notice_count = 0u;
    life_death_scene_observation_log obs_log;
    life_death_scene_observation obs_storage[4];
    life_death_scene_observation_hooks obs_hooks;

    life_test_context_init(&t, 0, 5);
    EXPECT(setup_basic_person(&t, 55u, 88u, accounts, 1u) == 0, "setup failed");

    memset(&input, 0, sizeof(input));
    input.body_id = 88u;
    input.cause_code = LIFE_DEATH_CAUSE_UNKNOWN;
    input.act_time = 5;
    input.policy_id = 1u;

    EXPECT(life_handle_death(&t.ctx, &input, &refusal, 0, 0) == 0, "death failed");
    EXPECT(notice_count == 0u, "notice should not fire without callback");

    life_test_context_init(&t, 0, 5);
    EXPECT(setup_basic_person(&t, 55u, 88u, accounts, 1u) == 0, "setup failed");
    t.ctx.notice_cb = notice_counter;
    t.ctx.notice_user = &notice_count;
    life_death_scene_observation_log_init(&obs_log, obs_storage, 4u);
    life_death_scene_observation_hooks_init(&obs_hooks, &obs_log, 0, 0);
    t.ctx.observation_hooks = &obs_hooks;
    notice_count = 0u;
    EXPECT(life_handle_death(&t.ctx, &input, &refusal, 0, 0) == 0, "death failed (cb)");
    EXPECT(notice_count == 1u, "expected one notice");
    EXPECT(obs_log.count == 1u, "expected one observation");
    return 0;
}

static void hash_u64(u64* h, u64 v)
{
    const u64 prime = 1099511628211ULL;
    *h ^= v;
    *h *= prime;
}

static u64 hash_state(const life_death_event_list* deaths,
                      const life_estate_registry* estates)
{
    u64 h = 1469598103934665603ULL;
    u32 i;
    if (deaths) {
        for (i = 0u; i < deaths->count; ++i) {
            const life_death_event* ev = &deaths->events[i];
            hash_u64(&h, ev->death_event_id);
            hash_u64(&h, ev->body_id);
            hash_u64(&h, ev->person_id);
            hash_u64(&h, ev->estate_id);
            hash_u64(&h, (u64)ev->cause_code);
        }
    }
    if (estates) {
        for (i = 0u; i < estates->count; ++i) {
            const life_estate* es = &estates->estates[i];
            u32 count = 0u;
            const dom_account_id_t* accounts = life_estate_accounts(estates, es, &count);
            u32 j;
            hash_u64(&h, es->estate_id);
            hash_u64(&h, es->deceased_person_id);
            for (j = 0u; j < count; ++j) {
                hash_u64(&h, accounts[j]);
            }
        }
    }
    return h;
}

static int test_replay_equivalence(void)
{
    life_test_context a;
    life_test_context b;
    life_death_input input;
    life_death_refusal_code refusal;
    dom_account_id_t accounts[2] = { 41u, 42u };
    u64 hash_a;
    u64 hash_b;

    life_test_context_init(&a, 0, 5);
    life_test_context_init(&b, 0, 5);
    EXPECT(setup_basic_person(&a, 77u, 99u, accounts, 2u) == 0, "setup A");
    EXPECT(setup_basic_person(&b, 77u, 99u, accounts, 2u) == 0, "setup B");

    memset(&input, 0, sizeof(input));
    input.body_id = 99u;
    input.cause_code = LIFE_DEATH_CAUSE_EXECUTION;
    input.act_time = 12;
    input.policy_id = 1u;
    EXPECT(life_handle_death(&a.ctx, &input, &refusal, 0, 0) == 0, "death A");
    EXPECT(life_handle_death(&b.ctx, &input, &refusal, 0, 0) == 0, "death B");

    hash_a = hash_state(&a.deaths, &a.estates);
    hash_b = hash_state(&b.deaths, &b.estates);
    EXPECT(hash_a == hash_b, "replay hash mismatch");
    return 0;
}

int main(void)
{
    if (test_death_estate_determinism() != 0) return 1;
    if (test_ledger_conservation() != 0) return 1;
    if (test_inheritance_schedule_equivalence() != 0) return 1;
    if (test_executor_authority_enforcement() != 0) return 1;
    if (test_epistemic_notice_hook() != 0) return 1;
    if (test_replay_equivalence() != 0) return 1;
    return 0;
}
