/*
LIFE remains, decay, and salvage tests (LIFE4).
*/
#include "dominium/life/remains.h"
#include "dominium/life/remains_decay_scheduler.h"
#include "dominium/life/rights_post_death.h"
#include "dominium/life/salvage.h"

#include "domino/core/dom_ledger.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct life_remains_test_context {
    dom_ledger ledger;

    life_remains remains_storage[16];
    life_remains_aggregate aggregates_storage[8];
    life_post_death_rights rights_storage[8];
    life_salvage_claim claims_storage[8];
    life_salvage_outcome outcomes_storage[8];
    life_estate estate_storage[4];
    dom_account_id_t estate_account_storage[8];
    life_account_owner_entry owner_storage[8];

    dom_time_event decay_event_storage[16];
    dg_due_entry decay_entry_storage[16];
    life_remains_decay_user decay_user_storage[16];

    life_remains_registry remains;
    life_remains_aggregate_registry aggregates;
    life_post_death_rights_registry rights;
    life_salvage_claim_registry claims;
    life_salvage_outcome_registry outcomes;
    life_estate_registry estates;
    life_account_owner_registry owners;
    life_remains_decay_scheduler decay;

    u64 epistemic_ids[8];
    life_remains_epistemic_set epistemic;
} life_remains_test_context;

static void life_remains_test_context_init(life_remains_test_context* t, dom_act_time_t start_tick)
{
    life_remains_decay_rules rules;
    memset(t, 0, sizeof(*t));
    (void)dom_ledger_init(&t->ledger);

    life_remains_registry_init(&t->remains, t->remains_storage, 16u, 1u);
    life_remains_aggregate_registry_init(&t->aggregates, t->aggregates_storage, 8u, 1u);
    life_post_death_rights_registry_init(&t->rights, t->rights_storage, 8u, 1u);
    life_salvage_claim_registry_init(&t->claims, t->claims_storage, 8u, 1u);
    life_salvage_outcome_registry_init(&t->outcomes, t->outcomes_storage, 8u, 1u);
    life_estate_registry_init(&t->estates, t->estate_storage, 4u,
                              t->estate_account_storage, 8u, 1u);
    life_account_owner_registry_init(&t->owners, t->owner_storage, 8u);

    rules.fresh_to_decayed = 5;
    rules.decayed_to_skeletal = 5;
    rules.skeletal_to_unknown = 5;
    (void)life_remains_decay_scheduler_init(&t->decay,
                                            t->decay_event_storage,
                                            16u,
                                            t->decay_entry_storage,
                                            t->decay_user_storage,
                                            16u,
                                            start_tick,
                                            &t->remains,
                                            &rules);

    t->epistemic.known_remains_ids = t->epistemic_ids;
    t->epistemic.count = 0u;
}

static u32 life_count_active_remains(const life_remains_registry* reg)
{
    u32 i;
    u32 count = 0u;
    if (!reg || !reg->remains) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->remains[i].state != LIFE_REMAINS_COLLAPSED) {
            count += 1u;
        }
    }
    return count;
}

static u32 life_count_aggregate_remains(const life_remains_aggregate_registry* reg)
{
    u32 i;
    u32 count = 0u;
    if (!reg || !reg->aggregates) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        count += (u32)reg->aggregates[i].count;
    }
    return count;
}

static int test_remains_creation_determinism(void)
{
    life_remains_registry a;
    life_remains_registry b;
    life_remains a_storage[4];
    life_remains b_storage[4];
    u64 id_a = 0u;
    u64 id_b = 0u;
    life_remains* ra;
    life_remains* rb;

    life_remains_registry_init(&a, a_storage, 4u, 1u);
    life_remains_registry_init(&b, b_storage, 4u, 1u);

    EXPECT(life_remains_create(&a, 10u, 20u, 30u, 40u, 50u, 60u, 0u, &id_a) == 0, "create A");
    EXPECT(life_remains_create(&b, 10u, 20u, 30u, 40u, 50u, 60u, 0u, &id_b) == 0, "create B");
    EXPECT(id_a == id_b, "remains id mismatch");

    ra = life_remains_find(&a, id_a);
    rb = life_remains_find(&b, id_b);
    EXPECT(ra != 0 && rb != 0, "remains lookup");
    EXPECT(ra->person_id == rb->person_id, "person mismatch");
    EXPECT(ra->body_id == rb->body_id, "body mismatch");
    EXPECT(ra->location_ref == rb->location_ref, "location mismatch");
    EXPECT(ra->ownership_rights_ref == rb->ownership_rights_ref, "rights mismatch");
    EXPECT(ra->state == rb->state, "state mismatch");
    return 0;
}

static int test_decay_schedule_invariance(void)
{
    static life_remains_test_context a;
    static life_remains_test_context b;
    u64 id_a = 0u;
    u64 id_b = 0u;
    life_remains* ra;
    life_remains* rb;

    life_remains_test_context_init(&a, 0);
    life_remains_test_context_init(&b, 0);

    EXPECT(life_remains_create(&a.remains, 1u, 2u, 3u, 0, 0u, 0u, 0u, &id_a) == 0, "create A");
    EXPECT(life_remains_create(&b.remains, 1u, 2u, 3u, 0, 0u, 0u, 0u, &id_b) == 0, "create B");
    ra = life_remains_find(&a.remains, id_a);
    rb = life_remains_find(&b.remains, id_b);
    EXPECT(ra != 0 && rb != 0, "remains lookup");

    EXPECT(life_remains_decay_register(&a.decay, ra) == 0, "register A");
    EXPECT(life_remains_decay_register(&b.decay, rb) == 0, "register B");

    EXPECT(life_remains_decay_advance(&a.decay, 5) == 0, "advance A1");
    EXPECT(life_remains_decay_advance(&a.decay, 10) == 0, "advance A2");
    EXPECT(life_remains_decay_advance(&a.decay, 12) == 0, "advance A3");

    EXPECT(life_remains_decay_advance(&b.decay, 12) == 0, "advance B");

    EXPECT(ra->state == rb->state, "state mismatch after advance");
    EXPECT(ra->next_due_tick == rb->next_due_tick, "next due mismatch");
    return 0;
}

static int test_rights_resolution_order(void)
{
    static life_remains_test_context t;
    u64 rights_id = 0u;
    u64 remains_id = 0u;
    u64 claim_id = 0u;
    life_salvage_refusal_code refusal = LIFE_SALVAGE_REFUSAL_NONE;
    life_salvage_context ctx;

    life_remains_test_context_init(&t, 0);
    t.estates.estates[0].estate_id = 1u;
    t.estates.estates[0].has_executor_authority = 0u;
    t.estates.count = 1u;

    EXPECT(life_post_death_rights_create(&t.rights, 1u, 7u, 0u, 1u, 1u, 0u, &rights_id) == 0,
           "create rights");
    EXPECT(life_remains_create(&t.remains, 10u, 11u, 12u, 0, rights_id, 0u, 0u, &remains_id) == 0,
           "create remains");

    t.epistemic_ids[0] = remains_id;
    t.epistemic.count = 1u;

    ctx.claims = &t.claims;
    ctx.outcomes = &t.outcomes;
    ctx.remains = &t.remains;
    ctx.rights = &t.rights;
    ctx.estates = &t.estates;
    ctx.owners = &t.owners;
    ctx.ledger = 0;
    ctx.epistemic = &t.epistemic;

    EXPECT(life_salvage_claim_create(&ctx, 101u, 0u, remains_id,
                                     LIFE_SALVAGE_BASIS_FINDER, 10, &claim_id) == 0,
           "create finder claim");
    EXPECT(life_salvage_resolve_claim(&ctx, claim_id, &refusal, 0) == 1, "resolve finder claim");
    EXPECT(refusal == LIFE_SALVAGE_REFUSAL_JURISDICTION_REFUSES, "finder should be refused");

    EXPECT(life_salvage_claim_create(&ctx, 102u, 0u, remains_id,
                                     LIFE_SALVAGE_BASIS_JURISDICTION, 10, &claim_id) == 0,
           "create jurisdiction claim");
    EXPECT(life_salvage_resolve_claim(&ctx, claim_id, &refusal, 0) == 0, "resolve jurisdiction claim");
    EXPECT(refusal == LIFE_SALVAGE_REFUSAL_NONE, "jurisdiction should be accepted");
    return 0;
}

static int test_salvage_ledger_conservation(void)
{
    static life_remains_test_context t;
    life_salvage_context ctx;
    dom_account_id_t inventory_account = 100u;
    dom_account_id_t claimant_account = 200u;
    dom_account_id_t source_account = 300u;
    dom_ledger_posting postings[2];
    dom_ledger_transaction tx;
    dom_transaction_id_t tx_id;
    dom_amount_t before_inv = 0;
    dom_amount_t before_claim = 0;
    dom_amount_t after_inv = 0;
    dom_amount_t after_claim = 0;
    u64 rights_id = 0u;
    u64 remains_id = 0u;
    u64 claim_id = 0u;
    life_salvage_refusal_code refusal = LIFE_SALVAGE_REFUSAL_NONE;

    life_remains_test_context_init(&t, 0);
    EXPECT(dom_ledger_account_create(&t.ledger, inventory_account, 0u) == DOM_LEDGER_OK, "inventory account");
    EXPECT(dom_ledger_account_create(&t.ledger, claimant_account, 0u) == DOM_LEDGER_OK, "claimant account");
    EXPECT(dom_ledger_account_create(&t.ledger, source_account, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE) == DOM_LEDGER_OK,
           "source account");

    EXPECT(dom_ledger_next_tx_id(&t.ledger, &tx_id) == DOM_LEDGER_OK, "next tx id");
    postings[0].account_id = inventory_account;
    postings[0].asset_id = 1u;
    postings[0].amount = 50;
    postings[0].lot_id = 0u;
    postings[0].provenance_id = 0u;
    postings[1].account_id = source_account;
    postings[1].asset_id = 1u;
    postings[1].amount = -50;
    postings[1].lot_id = 0u;
    postings[1].provenance_id = 0u;
    tx.tx_id = tx_id;
    tx.posting_count = 2u;
    tx.postings = postings;
    EXPECT(dom_ledger_transaction_apply(&t.ledger, &tx, 0) == DOM_LEDGER_OK, "seed inventory");

    EXPECT(dom_ledger_balance_get(&t.ledger, inventory_account, 1u, &before_inv) == DOM_LEDGER_OK, "balance inv");
    EXPECT(dom_ledger_balance_get(&t.ledger, claimant_account, 1u, &before_claim) == DOM_LEDGER_OK, "balance claim");

    EXPECT(life_post_death_rights_create(&t.rights, 0u, 0u, 1u, 0u, 0u, 0u, &rights_id) == 0,
           "create rights");
    EXPECT(life_remains_create(&t.remains, 10u, 11u, 12u, 0, rights_id, 0u, inventory_account, &remains_id) == 0,
           "create remains");
    t.epistemic_ids[0] = remains_id;
    t.epistemic.count = 1u;

    ctx.claims = &t.claims;
    ctx.outcomes = &t.outcomes;
    ctx.remains = &t.remains;
    ctx.rights = &t.rights;
    ctx.estates = &t.estates;
    ctx.owners = &t.owners;
    ctx.ledger = &t.ledger;
    ctx.epistemic = &t.epistemic;

    EXPECT(life_salvage_claim_create(&ctx, 99u, claimant_account, remains_id,
                                     LIFE_SALVAGE_BASIS_CONTRACT, 5, &claim_id) == 0,
           "create contract claim");
    EXPECT(life_salvage_resolve_claim(&ctx, claim_id, &refusal, 0) == 0, "resolve claim");
    EXPECT(refusal == LIFE_SALVAGE_REFUSAL_NONE, "unexpected refusal");

    EXPECT(dom_ledger_balance_get(&t.ledger, inventory_account, 1u, &after_inv) == DOM_LEDGER_OK, "balance inv");
    EXPECT(dom_ledger_balance_get(&t.ledger, claimant_account, 1u, &after_claim) == DOM_LEDGER_OK, "balance claim");
    EXPECT(before_inv + before_claim == after_inv + after_claim, "ledger sum changed");
    return 0;
}

static int test_epistemic_discovery_gating(void)
{
    static life_remains_test_context t;
    life_salvage_context ctx;
    u64 rights_id = 0u;
    u64 remains_id = 0u;
    u64 claim_id = 0u;
    life_salvage_refusal_code refusal = LIFE_SALVAGE_REFUSAL_NONE;

    life_remains_test_context_init(&t, 0);
    EXPECT(life_post_death_rights_create(&t.rights, 0u, 0u, 1u, 0u, 0u, 0u, &rights_id) == 0,
           "create rights");
    EXPECT(life_remains_create(&t.remains, 7u, 8u, 9u, 0, rights_id, 0u, 0u, &remains_id) == 0,
           "create remains");

    ctx.claims = &t.claims;
    ctx.outcomes = &t.outcomes;
    ctx.remains = &t.remains;
    ctx.rights = &t.rights;
    ctx.estates = &t.estates;
    ctx.owners = &t.owners;
    ctx.ledger = 0;
    ctx.epistemic = &t.epistemic;

    EXPECT(life_salvage_claim_create(&ctx, 1u, 0u, remains_id,
                                     LIFE_SALVAGE_BASIS_CONTRACT, 10, &claim_id) == 0,
           "create claim");
    EXPECT(life_salvage_resolve_claim(&ctx, claim_id, &refusal, 0) == 1, "resolve claim");
    EXPECT(refusal == LIFE_SALVAGE_REFUSAL_INSUFFICIENT_EPISTEMIC_KNOWLEDGE,
           "expected epistemic refusal");

    t.epistemic_ids[0] = remains_id;
    t.epistemic.count = 1u;
    EXPECT(life_salvage_claim_create(&ctx, 2u, 0u, remains_id,
                                     LIFE_SALVAGE_BASIS_CONTRACT, 10, &claim_id) == 0,
           "create claim 2");
    EXPECT(life_salvage_resolve_claim(&ctx, claim_id, &refusal, 0) == 0, "resolve claim 2");
    EXPECT(refusal == LIFE_SALVAGE_REFUSAL_NONE, "expected acceptance");
    return 0;
}

static int test_collapse_refine_preserves_counts(void)
{
    static life_remains_test_context t;
    u64 rights_id = 0u;
    u64 remains_id = 0u;
    u64 aggregate_id = 0u;
    u32 total_before = 0u;
    u32 total_after = 0u;
    life_remains_aggregate* agg;

    life_remains_test_context_init(&t, 0);
    EXPECT(life_post_death_rights_create(&t.rights, 0u, 0u, 0u, 1u, 1u, 0u, &rights_id) == 0,
           "create rights");
    EXPECT(life_remains_create(&t.remains, 1u, 2u, 3u, 0, rights_id, 11u, 0u, &remains_id) == 0,
           "create remains");
    EXPECT(life_remains_create(&t.remains, 4u, 5u, 6u, 0, rights_id, 22u, 0u, 0) == 0,
           "create remains 2");

    total_before = life_count_active_remains(&t.remains) + life_count_aggregate_remains(&t.aggregates);
    EXPECT(life_remains_collapse(&t.remains, &t.aggregates, remains_id, &aggregate_id) == 0,
           "collapse remains");
    agg = life_remains_aggregate_find(&t.aggregates, aggregate_id);
    EXPECT(agg != 0, "aggregate lookup");
    EXPECT(agg->count == 1u, "aggregate count");

    total_after = life_count_active_remains(&t.remains) + life_count_aggregate_remains(&t.aggregates);
    EXPECT(total_after == total_before, "total count changed after collapse");

    EXPECT(life_remains_refine(&t.aggregates, &t.remains, aggregate_id, 1u, 5) == 0,
           "refine aggregate");
    EXPECT(agg->count == 0u, "aggregate count after refine");

    total_after = life_count_active_remains(&t.remains) + life_count_aggregate_remains(&t.aggregates);
    EXPECT(total_after == total_before, "total count changed after refine");
    EXPECT(t.remains.remains[t.remains.count - 1u].provenance_ref == agg->provenance_hash,
           "provenance hash mismatch");
    return 0;
}

int main(void)
{
    if (test_remains_creation_determinism() != 0) return 1;
    if (test_decay_schedule_invariance() != 0) return 1;
    if (test_rights_resolution_order() != 0) return 1;
    if (test_salvage_ledger_conservation() != 0) return 1;
    if (test_epistemic_discovery_gating() != 0) return 1;
    if (test_collapse_refine_preserves_counts() != 0) return 1;
    return 0;
}
