/*
Player embodiment tests (PLAYER-2/TestX).
*/
#include "dominium/player.h"
#include "dominium/agents/agent_goal.h"
#include "dominium/agents/agent_planner.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static u64 fnv1a_init(void)
{
    return 1469598103934665603ULL;
}

static u64 fnv1a_u64(u64 h, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 hash_events(const dom_player_event_log* log)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!log || !log->entries) {
        return h;
    }
    h = fnv1a_u64(h, (u64)log->count);
    for (i = 0u; i < log->count; ++i) {
        const dom_player_event* e = &log->entries[i];
        h = fnv1a_u64(h, e->event_id);
        h = fnv1a_u64(h, e->player_id);
        h = fnv1a_u64(h, e->agent_id);
        h = fnv1a_u64(h, e->kind);
        h = fnv1a_u64(h, e->intent_id);
        h = fnv1a_u64(h, e->refusal);
        h = fnv1a_u64(h, (u64)e->act_time);
    }
    return h;
}

static int test_player_authority_block(void)
{
    dom_player_intent_queue queue;
    dom_player_intent intents[4];
    dom_player_event_log events;
    dom_player_event event_storage[4];
    dom_agent_capability caps[1];
    dom_agent_belief beliefs[1];
    dom_player_intent_context ctx;
    dom_player_intent intent;

    dom_player_intent_queue_init(&queue, intents, 4u, 1u);
    dom_player_event_log_init(&events, event_storage, 4u, 1u);

    memset(caps, 0, sizeof(caps));
    caps[0].agent_id = 100u;
    caps[0].capability_mask = DOM_PHYS_CAP_TERRAIN;
    caps[0].authority_mask = 0u;

    memset(beliefs, 0, sizeof(beliefs));
    beliefs[0].agent_id = 100u;
    beliefs[0].knowledge_mask = 0u;

    memset(&ctx, 0, sizeof(ctx));
    ctx.caps = caps;
    ctx.cap_count = 1u;
    ctx.beliefs = beliefs;
    ctx.belief_count = 1u;
    ctx.now_act = 10u;
    ctx.events = &events;

    memset(&intent, 0, sizeof(intent));
    intent.player_id = 1u;
    intent.agent_id = 100u;
    intent.kind = DOM_PLAYER_INTENT_PROCESS_REQUEST;
    intent.payload.process_request.required_capability_mask = DOM_PHYS_CAP_TERRAIN;
    intent.payload.process_request.required_authority_mask = DOM_PHYS_AUTH_TERRAIN;

    EXPECT(dom_player_submit_intent(&queue, &intent, &ctx) != 0,
           "authority blocks intent");
    EXPECT(queue.entries[0].refusal == DOM_PLAYER_REFUSAL_NO_AUTHORITY,
           "refusal code");
    EXPECT(events.count == 1u && events.entries[0].kind == DOM_PLAYER_EVENT_INTENT_REFUSED,
           "event recorded");
    return 0;
}

static int test_player_subjective_snapshot(void)
{
    dom_agent_belief beliefs[2];
    dom_player_subjective_snapshot snap_a;
    dom_player_subjective_snapshot snap_b;

    memset(beliefs, 0, sizeof(beliefs));
    beliefs[0].agent_id = 200u;
    beliefs[0].knowledge_mask = AGENT_KNOW_RESOURCE;
    beliefs[1].agent_id = 201u;
    beliefs[1].knowledge_mask = AGENT_KNOW_THREAT;

    EXPECT(dom_player_build_snapshot(beliefs, 2u, 200u, &snap_a) == 0, "snapshot a");
    EXPECT(dom_player_build_snapshot(beliefs, 2u, 201u, &snap_b) == 0, "snapshot b");
    EXPECT(snap_a.knowledge_mask == AGENT_KNOW_RESOURCE, "subjective knowledge a");
    EXPECT(snap_b.knowledge_mask == AGENT_KNOW_THREAT, "subjective knowledge b");
    return 0;
}

static int test_player_intent_refusal_and_history(void)
{
    dom_player_intent_queue queue;
    dom_player_intent intents[2];
    dom_player_event_log events;
    dom_player_event event_storage[2];
    dom_agent_capability caps[1];
    dom_agent_belief beliefs[1];
    dom_player_intent_context ctx;
    dom_player_intent intent;

    dom_player_intent_queue_init(&queue, intents, 2u, 1u);
    dom_player_event_log_init(&events, event_storage, 2u, 1u);

    memset(caps, 0, sizeof(caps));
    caps[0].agent_id = 300u;
    caps[0].capability_mask = AGENT_CAP_MOVE;
    caps[0].authority_mask = AGENT_AUTH_BASIC;

    memset(beliefs, 0, sizeof(beliefs));
    beliefs[0].agent_id = 300u;
    beliefs[0].knowledge_mask = 0u;

    memset(&ctx, 0, sizeof(ctx));
    ctx.caps = caps;
    ctx.cap_count = 1u;
    ctx.beliefs = beliefs;
    ctx.belief_count = 1u;
    ctx.now_act = 20u;
    ctx.events = &events;

    memset(&intent, 0, sizeof(intent));
    intent.player_id = 2u;
    intent.agent_id = 300u;
    intent.kind = DOM_PLAYER_INTENT_PROCESS_REQUEST;
    intent.payload.process_request.required_capability_mask = AGENT_CAP_MOVE;
    intent.payload.process_request.required_authority_mask = AGENT_AUTH_BASIC;
    intent.payload.process_request.required_knowledge_mask = AGENT_KNOW_RESOURCE;

    EXPECT(dom_player_submit_intent(&queue, &intent, &ctx) != 0, "intent refused");
    EXPECT(queue.entries[0].refusal == DOM_PLAYER_REFUSAL_NO_KNOWLEDGE, "knowledge refusal");
    EXPECT(events.count == 1u && events.entries[0].kind == DOM_PLAYER_EVENT_INTENT_REFUSED,
           "history recorded");
    return 0;
}

static int test_multiplayer_determinism(void)
{
    dom_player_intent_queue queue_a;
    dom_player_intent_queue queue_b;
    dom_player_intent intents_a[2];
    dom_player_intent intents_b[2];
    dom_player_event_log events_a;
    dom_player_event_log events_b;
    dom_player_event event_storage_a[2];
    dom_player_event event_storage_b[2];
    dom_agent_capability caps[2];
    dom_agent_belief beliefs[2];
    dom_player_intent_context ctx_a;
    dom_player_intent_context ctx_b;
    dom_player_intent intent;
    u64 hash_a;
    u64 hash_b;

    dom_player_intent_queue_init(&queue_a, intents_a, 2u, 1u);
    dom_player_intent_queue_init(&queue_b, intents_b, 2u, 1u);
    dom_player_event_log_init(&events_a, event_storage_a, 2u, 1u);
    dom_player_event_log_init(&events_b, event_storage_b, 2u, 1u);

    memset(caps, 0, sizeof(caps));
    caps[0].agent_id = 400u;
    caps[0].capability_mask = DOM_PHYS_CAP_TERRAIN;
    caps[0].authority_mask = DOM_PHYS_AUTH_TERRAIN;
    caps[1].agent_id = 401u;
    caps[1].capability_mask = DOM_PHYS_CAP_TERRAIN;
    caps[1].authority_mask = DOM_PHYS_AUTH_TERRAIN;

    memset(beliefs, 0, sizeof(beliefs));
    beliefs[0].agent_id = 400u;
    beliefs[0].knowledge_mask = AGENT_KNOW_RESOURCE;
    beliefs[1].agent_id = 401u;
    beliefs[1].knowledge_mask = AGENT_KNOW_RESOURCE;

    memset(&ctx_a, 0, sizeof(ctx_a));
    ctx_a.caps = caps;
    ctx_a.cap_count = 2u;
    ctx_a.beliefs = beliefs;
    ctx_a.belief_count = 2u;
    ctx_a.now_act = 30u;
    ctx_a.events = &events_a;

    ctx_b = ctx_a;
    ctx_b.events = &events_b;

    memset(&intent, 0, sizeof(intent));
    intent.player_id = 10u;
    intent.agent_id = 400u;
    intent.kind = DOM_PLAYER_INTENT_PROCESS_REQUEST;
    intent.payload.process_request.required_capability_mask = DOM_PHYS_CAP_TERRAIN;
    intent.payload.process_request.required_authority_mask = DOM_PHYS_AUTH_TERRAIN;
    (void)dom_player_submit_intent(&queue_a, &intent, &ctx_a);
    (void)dom_player_submit_intent(&queue_b, &intent, &ctx_b);

    hash_a = hash_events(&events_a);
    hash_b = hash_events(&events_b);
    EXPECT(hash_a == hash_b, "multiplayer determinism");
    return 0;
}

static int test_headless_safe(void)
{
    dom_player_intent_queue queue;
    dom_player_intent intents[1];
    dom_player_intent_context ctx;
    dom_player_intent intent;

    dom_player_intent_queue_init(&queue, intents, 1u, 1u);
    memset(&ctx, 0, sizeof(ctx));

    memset(&intent, 0, sizeof(intent));
    intent.player_id = 50u;
    intent.agent_id = 500u;
    intent.kind = DOM_PLAYER_INTENT_PLAN_CONFIRM;
    intent.payload.plan_id = 0u;

    /* No UI/render dependencies; intent should be refused cleanly without side effects. */
    EXPECT(dom_player_submit_intent(&queue, &intent, &ctx) != 0, "headless refusal");
    EXPECT(queue.count == 1u, "headless queue");
    return 0;
}

int main(void)
{
    if (test_player_authority_block() != 0) return 1;
    if (test_player_subjective_snapshot() != 0) return 1;
    if (test_player_intent_refusal_and_history() != 0) return 1;
    if (test_multiplayer_determinism() != 0) return 1;
    if (test_headless_safe() != 0) return 1;
    return 0;
}
