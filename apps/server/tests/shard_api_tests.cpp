/*
Shard API tests (DIST0).
*/
#include "shard/shard_api.h"
#include "shard/shard_router.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static void seed_registry(dom_shard_registry* registry, dom_shard* storage, u32 capacity)
{
    dom_shard shard;
    dom_shard_registry_init(registry, storage, capacity);

    shard.shard_id = 1u;
    shard.scope.kind = DOM_SHARD_SCOPE_ENTITY_RANGE;
    shard.scope.start_id = 0u;
    shard.scope.end_id = 999u;
    shard.scope.domain_tag = 0u;
    shard.determinism_domain = 10u;
    dom_shard_registry_add(registry, &shard);

    shard.shard_id = 2u;
    shard.scope.kind = DOM_SHARD_SCOPE_ENTITY_RANGE;
    shard.scope.start_id = 1000u;
    shard.scope.end_id = 1999u;
    shard.scope.domain_tag = 0u;
    shard.determinism_domain = 10u;
    dom_shard_registry_add(registry, &shard);

    shard.shard_id = 3u;
    shard.scope.kind = DOM_SHARD_SCOPE_ENTITY_RANGE;
    shard.scope.start_id = 2000u;
    shard.scope.end_id = 2999u;
    shard.scope.domain_tag = 0u;
    shard.determinism_domain = 10u;
    dom_shard_registry_add(registry, &shard);
}

static int test_deterministic_placement(void)
{
    dom_shard_registry registry;
    dom_shard shards[3];
    dom_shard_task_key key;
    dom_shard_id placed_a;
    dom_shard_id placed_b;

    seed_registry(&registry, shards, 3u);

    memset(&key, 0, sizeof(key));
    key.task_id = 9001u;
    key.system_id = 4001u;
    key.access_set_id = 7001u;
    key.category = 1u;
    key.determinism_class = 2u;
    key.primary_owner_id = 1500u;

    placed_a = dom_shard_place_task(&registry, &key, 1u);
    placed_b = dom_shard_place_task(&registry, &key, 1u);

    EXPECT(placed_a == 2u, "authoritative owner placement mismatch");
    EXPECT(placed_a == placed_b, "placement must be deterministic");

    key.primary_owner_id = 0u;
    placed_a = dom_shard_place_task(&registry, &key, 1u);
    placed_b = dom_shard_place_task(&registry, &key, 1u);
    EXPECT(placed_a == placed_b, "fallback placement must be deterministic");
    return 0;
}

static int test_message_ordering(void)
{
    dom_shard_message_queue queue;
    dom_shard_message storage[4];
    dom_shard_message msg;
    dom_shard_message out;
    int res;

    dom_shard_message_queue_init(&queue, storage, 4u);

    msg.source_shard = 1u;
    msg.target_shard = 2u;
    msg.task_id = 10u;
    msg.payload = 0;
    msg.payload_size = 0u;

    msg.arrival_tick = 10u;
    msg.message_id = 3u;
    dom_shard_message_queue_push(&queue, &msg);

    msg.arrival_tick = 5u;
    msg.message_id = 9u;
    dom_shard_message_queue_push(&queue, &msg);

    msg.arrival_tick = 5u;
    msg.message_id = 2u;
    dom_shard_message_queue_push(&queue, &msg);

    res = dom_shard_message_queue_pop_ready(&queue, 10u, &out);
    EXPECT(res == 0, "pop ready 1");
    EXPECT(out.arrival_tick == 5u && out.message_id == 2u, "order 1 mismatch");

    res = dom_shard_message_queue_pop_ready(&queue, 10u, &out);
    EXPECT(res == 0, "pop ready 2");
    EXPECT(out.arrival_tick == 5u && out.message_id == 9u, "order 2 mismatch");

    res = dom_shard_message_queue_pop_ready(&queue, 10u, &out);
    EXPECT(res == 0, "pop ready 3");
    EXPECT(out.arrival_tick == 10u && out.message_id == 3u, "order 3 mismatch");

    return 0;
}

static int test_cross_shard_read_refusal(void)
{
    dom_shard_registry registry;
    dom_shard shards[3];
    int res;

    seed_registry(&registry, shards, 3u);

    res = dom_shard_validate_access(&registry, 1u, 1500u, DOM_SHARD_ACCESS_READ);
    EXPECT(res != 0, "cross-shard read should be refused");

    res = dom_shard_validate_access(&registry, 2u, 1500u, DOM_SHARD_ACCESS_READ);
    EXPECT(res == 0, "local read should be allowed");

    res = dom_shard_validate_access(&registry, 3u, 1500u, DOM_SHARD_ACCESS_WRITE);
    EXPECT(res != 0, "cross-shard write should be refused");

    return 0;
}

static int test_replay_reconstruction(void)
{
    dom_shard_log log;
    dom_shard_event_entry events[4];
    dom_shard_message messages[4];
    dom_shard_replay_state replay;
    dom_shard_event_entry ev;
    dom_shard_message msg;
    u8 payload_a[2] = { 1u, 2u };
    u8 payload_b[3] = { 9u, 8u, 7u };
    u64 log_hash;

    dom_shard_log_init(&log, events, 4u, messages, 4u);

    ev.event_id = 1u;
    ev.task_id = 100u;
    ev.tick = 10u;
    dom_shard_log_record_event(&log, &ev);

    ev.event_id = 2u;
    ev.task_id = 101u;
    ev.tick = 12u;
    dom_shard_log_record_event(&log, &ev);

    msg.source_shard = 1u;
    msg.target_shard = 2u;
    msg.message_id = 20u;
    msg.task_id = 100u;
    msg.arrival_tick = 15u;
    msg.payload = payload_a;
    msg.payload_size = 2u;
    dom_shard_log_record_message(&log, &msg);

    msg.source_shard = 2u;
    msg.target_shard = 3u;
    msg.message_id = 21u;
    msg.task_id = 101u;
    msg.arrival_tick = 18u;
    msg.payload = payload_b;
    msg.payload_size = 3u;
    dom_shard_log_record_message(&log, &msg);

    log_hash = dom_shard_log_hash(&log);
    EXPECT(dom_shard_replay_apply(&log, &replay) == 0, "replay apply");
    EXPECT(replay.hash == log_hash, "replay hash mismatch");
    EXPECT(replay.event_count == 2u, "replay event count mismatch");
    EXPECT(replay.message_count == 2u, "replay message count mismatch");
    return 0;
}

int main(void)
{
    if (test_deterministic_placement() != 0) return 1;
    if (test_message_ordering() != 0) return 1;
    if (test_cross_shard_read_refusal() != 0) return 1;
    if (test_replay_reconstruction() != 0) return 1;
    return 0;
}
