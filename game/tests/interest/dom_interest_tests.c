/*
Interest set enforcement tests (SCALE1).
*/
#include "dominium/interest_set.h"
#include "dominium/interest_sources.h"
#include "dominium/interest_macro.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int entries_equal(const dom_interest_entry* a, const dom_interest_entry* b)
{
    if (!a || !b) {
        return 0;
    }
    return a->target_id == b->target_id &&
           a->target_kind == b->target_kind &&
           a->reason == b->reason &&
           a->strength == b->strength &&
           a->expiry_tick == b->expiry_tick;
}

static int test_interest_sources(void)
{
    dom_interest_set set;
    dom_interest_source_list list;
    u64 ids[1];

    dom_interest_set_init(&set);
    EXPECT(dom_interest_set_reserve(&set, 16u) == 0, "reserve failed");

    ids[0] = 42u;
    list.ids = ids;
    list.count = 1u;
    list.target_kind = DOM_INTEREST_TARGET_SYSTEM;
    list.strength = DOM_INTEREST_STRENGTH_HIGH;
    list.ttl_ticks = 5;

    EXPECT(dom_interest_emit_player_focus(&set, &list, 10) == 0, "player focus emit failed");
    EXPECT(dom_interest_emit_command_intent(&set, &list, 10) == 0, "command intent emit failed");
    EXPECT(dom_interest_emit_logistics(&set, &list, 10) == 0, "logistics emit failed");
    EXPECT(dom_interest_emit_sensor_comms(&set, &list, 10) == 0, "sensor comms emit failed");
    EXPECT(dom_interest_emit_hazard_conflict(&set, &list, 10) == 0, "hazard emit failed");
    EXPECT(dom_interest_emit_governance_scope(&set, &list, 10) == 0, "governance emit failed");

    dom_interest_set_finalize(&set);
    EXPECT(set.count == 6u, "expected 6 interest entries");
    dom_interest_set_free(&set);
    return 0;
}

static int test_determinism(void)
{
    dom_interest_set a;
    dom_interest_set b;
    u32 i;

    dom_interest_set_init(&a);
    dom_interest_set_init(&b);
    EXPECT(dom_interest_set_reserve(&a, 8u) == 0, "reserve A failed");
    EXPECT(dom_interest_set_reserve(&b, 8u) == 0, "reserve B failed");

    EXPECT(dom_interest_set_add(&a, DOM_INTEREST_TARGET_SYSTEM, 1u, DOM_INTEREST_REASON_PLAYER_FOCUS,
                                DOM_INTEREST_STRENGTH_HIGH, DOM_INTEREST_PERSISTENT) == 0, "add A1 failed");
    EXPECT(dom_interest_set_add(&a, DOM_INTEREST_TARGET_SYSTEM, 2u, DOM_INTEREST_REASON_LOGISTICS_ROUTE,
                                DOM_INTEREST_STRENGTH_MED, DOM_INTEREST_PERSISTENT) == 0, "add A2 failed");
    EXPECT(dom_interest_set_add(&a, DOM_INTEREST_TARGET_REGION, 3u, DOM_INTEREST_REASON_GOVERNANCE_SCOPE,
                                DOM_INTEREST_STRENGTH_LOW, DOM_INTEREST_PERSISTENT) == 0, "add A3 failed");

    EXPECT(dom_interest_set_add(&b, DOM_INTEREST_TARGET_REGION, 3u, DOM_INTEREST_REASON_GOVERNANCE_SCOPE,
                                DOM_INTEREST_STRENGTH_LOW, DOM_INTEREST_PERSISTENT) == 0, "add B1 failed");
    EXPECT(dom_interest_set_add(&b, DOM_INTEREST_TARGET_SYSTEM, 2u, DOM_INTEREST_REASON_LOGISTICS_ROUTE,
                                DOM_INTEREST_STRENGTH_MED, DOM_INTEREST_PERSISTENT) == 0, "add B2 failed");
    EXPECT(dom_interest_set_add(&b, DOM_INTEREST_TARGET_SYSTEM, 1u, DOM_INTEREST_REASON_PLAYER_FOCUS,
                                DOM_INTEREST_STRENGTH_HIGH, DOM_INTEREST_PERSISTENT) == 0, "add B3 failed");

    dom_interest_set_finalize(&a);
    dom_interest_set_finalize(&b);

    EXPECT(a.count == b.count, "determinism count mismatch");
    for (i = 0u; i < a.count; ++i) {
        EXPECT(entries_equal(&a.entries[i], &b.entries[i]), "determinism entry mismatch");
    }

    dom_interest_set_free(&a);
    dom_interest_set_free(&b);
    return 0;
}

static int test_latent_universe(void)
{
    dom_interest_set set;
    dom_macro_stats stats;

    dom_interest_set_init(&set);
    EXPECT(dom_interest_set_reserve(&set, 4u) == 0, "reserve latent failed");

    EXPECT(dom_interest_set_add(&set, DOM_INTEREST_TARGET_SYSTEM, 1u, DOM_INTEREST_REASON_PLAYER_FOCUS,
                                DOM_INTEREST_STRENGTH_HIGH, DOM_INTEREST_PERSISTENT) == 0, "add system failed");
    dom_interest_set_finalize(&set);

    EXPECT(dom_macro_step(&set, &stats) == 0, "macro step failed");
    EXPECT(stats.processed == 1u, "latent universe processed count mismatch");
    dom_interest_set_free(&set);
    return 0;
}

static int test_interest_transitions(void)
{
    dom_interest_set set;
    dom_interest_state state;
    dom_interest_policy policy;
    dom_interest_transition transitions[4];
    u32 transition_cap;

    dom_interest_set_init(&set);
    EXPECT(dom_interest_set_reserve(&set, 4u) == 0, "reserve transition failed");

    state.target_id = 1u;
    state.target_kind = DOM_INTEREST_TARGET_SYSTEM;
    state.state = DOM_REL_LATENT;
    state.last_change_tick = 0;

    policy.enter_warm = 50u;
    policy.exit_warm = 40u;
    policy.enter_hot = 80u;
    policy.exit_hot = 60u;
    policy.min_dwell_ticks = 2;

    EXPECT(dom_interest_set_add(&set, DOM_INTEREST_TARGET_SYSTEM, 1u, DOM_INTEREST_REASON_PLAYER_FOCUS,
                                90u, 100u) == 0, "add interest failed");
    dom_interest_set_finalize(&set);

    transition_cap = 4u;
    dom_interest_state_apply(&set, &state, 1u, &policy, 10, transitions, &transition_cap);
    EXPECT(state.state == DOM_REL_HOT, "expected HOT on entry");

    dom_interest_set_clear(&set);
    dom_interest_set_finalize(&set);

    transition_cap = 4u;
    dom_interest_state_apply(&set, &state, 1u, &policy, 11, transitions, &transition_cap);
    EXPECT(state.state == DOM_REL_HOT, "dwell should prevent collapse");

    transition_cap = 4u;
    dom_interest_state_apply(&set, &state, 1u, &policy, 13, transitions, &transition_cap);
    EXPECT(state.state == DOM_REL_LATENT, "expected LATENT after dwell");

    dom_interest_set_free(&set);
    return 0;
}

static int test_hysteresis_stability(void)
{
    dom_interest_set set;
    dom_interest_state state;
    dom_interest_policy policy;
    dom_interest_transition transitions[4];
    u32 transition_cap;

    dom_interest_set_init(&set);
    EXPECT(dom_interest_set_reserve(&set, 4u) == 0, "reserve hysteresis failed");

    state.target_id = 2u;
    state.target_kind = DOM_INTEREST_TARGET_SYSTEM;
    state.state = DOM_REL_LATENT;
    state.last_change_tick = 0;

    policy.enter_warm = 70u;
    policy.exit_warm = 50u;
    policy.enter_hot = 90u;
    policy.exit_hot = 75u;
    policy.min_dwell_ticks = 2;

    transition_cap = 4u;
    dom_interest_set_add(&set, DOM_INTEREST_TARGET_SYSTEM, 2u, DOM_INTEREST_REASON_SENSOR_COMMS, 60u, 100u);
    dom_interest_set_finalize(&set);
    dom_interest_state_apply(&set, &state, 1u, &policy, 1, transitions, &transition_cap);
    EXPECT(state.state == DOM_REL_LATENT, "should remain LATENT below enter threshold");

    dom_interest_set_clear(&set);
    dom_interest_set_add(&set, DOM_INTEREST_TARGET_SYSTEM, 2u, DOM_INTEREST_REASON_SENSOR_COMMS, 45u, 100u);
    dom_interest_set_finalize(&set);
    transition_cap = 4u;
    dom_interest_state_apply(&set, &state, 1u, &policy, 2, transitions, &transition_cap);
    EXPECT(state.state == DOM_REL_LATENT, "should remain LATENT on oscillation");

    dom_interest_set_free(&set);
    return 0;
}

int main(void)
{
    if (test_interest_sources() != 0) {
        return 1;
    }
    if (test_determinism() != 0) {
        return 1;
    }
    if (test_latent_universe() != 0) {
        return 1;
    }
    if (test_interest_transitions() != 0) {
        return 1;
    }
    if (test_hysteresis_stability() != 0) {
        return 1;
    }
    return 0;
}
