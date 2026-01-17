/*
Fidelity projection enforcement tests (SCALE2).
*/
#include "dominium/fidelity.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int test_visibility_continuity(void)
{
    dom_fidelity_context ctx;
    dom_fidelity_object objects[4];
    dom_fidelity_request requests[8];
    dom_fidelity_transition transitions[4];
    dom_fidelity_policy policy;
    dom_interest_set interest;
    u32 transition_cap = 4u;
    const u32 kind = DOM_INTEREST_TARGET_SYSTEM;
    const u64 obj_id = 101u;
    u32 written;

    dom_interest_set_init(&interest);
    dom_fidelity_context_init(&ctx, objects, 4u, requests, 8u);

    EXPECT(dom_fidelity_register_object(&ctx, kind, obj_id, DOM_FIDELITY_MICRO) != NULL,
           "register object failed");
    dom_fidelity_set_provenance_hash(&ctx.objects[0], 0xabcdu);
    dom_fidelity_set_pins(&ctx.objects[0], DOM_FIDELITY_PIN_VISIBLE);

    EXPECT(dom_fidelity_request_collapse(&ctx, kind, obj_id, DOM_FIDELITY_MACRO, 1u) == 0,
           "collapse request failed");

    policy.refine_min_strength = DOM_INTEREST_STRENGTH_LOW;
    policy.collapse_max_strength = 0u;
    policy.min_dwell_ticks = 0;

    written = dom_fidelity_apply_requests(&ctx, &interest, &policy, 10, transitions, &transition_cap);
    EXPECT(ctx.objects[0].state.current_tier == DOM_FIDELITY_MICRO, "visible object collapsed");
    EXPECT(written == 0u, "visible collapse produced transition");

    dom_interest_set_free(&interest);
    return 0;
}

static int test_provenance_preservation(void)
{
    dom_fidelity_context ctx;
    dom_fidelity_object objects[4];
    dom_fidelity_request requests[8];
    dom_fidelity_transition transitions[4];
    dom_fidelity_policy policy;
    dom_interest_set interest_empty;
    dom_interest_set interest_refine;
    u32 transition_cap = 4u;
    const u32 kind = DOM_INTEREST_TARGET_SYSTEM;
    const u64 obj_id = 202u;
    u64 count;
    u64 inventory;
    u64 obligations;

    dom_interest_set_init(&interest_empty);
    dom_interest_set_init(&interest_refine);
    EXPECT(dom_interest_set_reserve(&interest_refine, 4u) == 0, "reserve refine failed");

    dom_fidelity_context_init(&ctx, objects, 4u, requests, 8u);
    EXPECT(dom_fidelity_register_object(&ctx, kind, obj_id, DOM_FIDELITY_MICRO) != NULL,
           "register object failed");
    ctx.objects[0].count = 7u;
    ctx.objects[0].inventory = 11u;
    ctx.objects[0].obligations = 3u;
    dom_fidelity_set_provenance_hash(&ctx.objects[0], 0x1234u);

    policy.refine_min_strength = DOM_INTEREST_STRENGTH_LOW;
    policy.collapse_max_strength = 0u;
    policy.min_dwell_ticks = 0;

    EXPECT(dom_fidelity_request_collapse(&ctx, kind, obj_id, DOM_FIDELITY_MACRO, 1u) == 0,
           "collapse request failed");
    transition_cap = 4u;
    dom_fidelity_apply_requests(&ctx, &interest_empty, &policy, 5, transitions, &transition_cap);
    EXPECT(ctx.objects[0].state.current_tier == DOM_FIDELITY_MACRO, "collapse did not apply");

    EXPECT(dom_interest_set_add(&interest_refine, kind, obj_id, DOM_INTEREST_REASON_PLAYER_FOCUS,
                                DOM_INTEREST_STRENGTH_HIGH, DOM_INTEREST_PERSISTENT) == 0,
           "add refine interest failed");
    dom_interest_set_finalize(&interest_refine);

    count = ctx.objects[0].count;
    inventory = ctx.objects[0].inventory;
    obligations = ctx.objects[0].obligations;

    EXPECT(dom_fidelity_request_refine(&ctx, kind, obj_id, DOM_FIDELITY_MICRO, 2u) == 0,
           "refine request failed");
    transition_cap = 4u;
    dom_fidelity_apply_requests(&ctx, &interest_refine, &policy, 6, transitions, &transition_cap);
    EXPECT(ctx.objects[0].state.current_tier == DOM_FIDELITY_MICRO, "refine did not apply");
    EXPECT(ctx.objects[0].count == count, "count changed on refine");
    EXPECT(ctx.objects[0].inventory == inventory, "inventory changed on refine");
    EXPECT(ctx.objects[0].obligations == obligations, "obligations changed on refine");

    dom_interest_set_free(&interest_refine);
    dom_interest_set_free(&interest_empty);
    return 0;
}

static int test_hysteresis_dwell(void)
{
    dom_fidelity_context ctx;
    dom_fidelity_object objects[2];
    dom_fidelity_request requests[4];
    dom_fidelity_transition transitions[4];
    dom_fidelity_policy policy;
    dom_interest_set interest_empty;
    u32 transition_cap = 4u;
    const u32 kind = DOM_INTEREST_TARGET_SYSTEM;
    const u64 obj_id = 303u;

    dom_interest_set_init(&interest_empty);
    dom_fidelity_context_init(&ctx, objects, 2u, requests, 4u);
    EXPECT(dom_fidelity_register_object(&ctx, kind, obj_id, DOM_FIDELITY_MICRO) != NULL,
           "register object failed");
    dom_fidelity_set_provenance_hash(&ctx.objects[0], 0x55u);

    policy.refine_min_strength = DOM_INTEREST_STRENGTH_LOW;
    policy.collapse_max_strength = 0u;
    policy.min_dwell_ticks = 5;

    EXPECT(dom_fidelity_request_collapse(&ctx, kind, obj_id, DOM_FIDELITY_MACRO, 3u) == 0,
           "collapse request failed");
    transition_cap = 4u;
    dom_fidelity_apply_requests(&ctx, &interest_empty, &policy, 2, transitions, &transition_cap);
    EXPECT(ctx.objects[0].state.current_tier == DOM_FIDELITY_MICRO, "dwell did not hold");

    EXPECT(dom_fidelity_request_collapse(&ctx, kind, obj_id, DOM_FIDELITY_MACRO, 4u) == 0,
           "collapse request retry failed");
    transition_cap = 4u;
    dom_fidelity_apply_requests(&ctx, &interest_empty, &policy, 7, transitions, &transition_cap);
    EXPECT(ctx.objects[0].state.current_tier == DOM_FIDELITY_MACRO, "collapse after dwell failed");

    dom_interest_set_free(&interest_empty);
    return 0;
}

static int test_provenance_refusal(void)
{
    dom_fidelity_context ctx;
    dom_fidelity_object objects[2];
    dom_fidelity_request requests[4];
    dom_fidelity_transition transitions[4];
    dom_interest_set interest_empty;
    dom_fidelity_policy policy;
    u32 transition_cap = 4u;
    const u32 kind = DOM_INTEREST_TARGET_SYSTEM;
    const u64 obj_id = 404u;
    u32 written;

    dom_interest_set_init(&interest_empty);
    dom_fidelity_context_init(&ctx, objects, 2u, requests, 4u);
    EXPECT(dom_fidelity_register_object(&ctx, kind, obj_id, DOM_FIDELITY_MICRO) != NULL,
           "register object failed");

    policy.refine_min_strength = DOM_INTEREST_STRENGTH_LOW;
    policy.collapse_max_strength = 0u;
    policy.min_dwell_ticks = 0;

    EXPECT(dom_fidelity_request_collapse(&ctx, kind, obj_id, DOM_FIDELITY_MACRO, 5u) == 0,
           "collapse request failed");
    transition_cap = 4u;
    written = dom_fidelity_apply_requests(&ctx, &interest_empty, &policy, 10, transitions, &transition_cap);
    EXPECT(ctx.objects[0].state.current_tier == DOM_FIDELITY_MICRO, "collapse bypassed provenance");
    EXPECT(written == 0u, "provenance refusal produced transition");

    dom_interest_set_free(&interest_empty);
    return 0;
}

int main(void)
{
    if (test_visibility_continuity() != 0) {
        return 1;
    }
    if (test_provenance_preservation() != 0) {
        return 1;
    }
    if (test_hysteresis_dwell() != 0) {
        return 1;
    }
    if (test_provenance_refusal() != 0) {
        return 1;
    }
    return 0;
}
