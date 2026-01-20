/*
Integrity checkpoint tests (DIST2).
*/
#include "persistence/integrity_checkpoints.h"
#include "persistence/dispute_bundle.h"
#include "shard/shard_hashing.h"
#include "shard/shard_api.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static void seed_log(dom_shard_log* log,
                     dom_shard_event_entry* events,
                     u32 event_capacity,
                     dom_shard_message* messages,
                     u32 message_capacity)
{
    dom_shard_event_entry ev;
    dom_shard_message msg;
    static u8 payload_a[2] = { 1u, 2u };
    static u8 payload_b[3] = { 9u, 8u, 7u };

    dom_shard_log_init(log, events, event_capacity, messages, message_capacity);

    ev.event_id = 1u;
    ev.task_id = 100u;
    ev.tick = 5u;
    dom_shard_log_record_event(log, &ev);

    ev.event_id = 2u;
    ev.task_id = 101u;
    ev.tick = 8u;
    dom_shard_log_record_event(log, &ev);

    msg.source_shard = 1u;
    msg.target_shard = 2u;
    msg.message_id = 10u;
    msg.task_id = 100u;
    msg.arrival_tick = 7u;
    msg.payload = payload_a;
    msg.payload_size = 2u;
    dom_shard_log_record_message(log, &msg);

    msg.source_shard = 2u;
    msg.target_shard = 1u;
    msg.message_id = 11u;
    msg.task_id = 101u;
    msg.arrival_tick = 9u;
    msg.payload = payload_b;
    msg.payload_size = 3u;
    dom_shard_log_record_message(log, &msg);
}

static int test_deterministic_hash(void)
{
    dom_shard_log log;
    dom_shard_event_entry events[4];
    dom_shard_message messages[4];
    u32 partitions[2] = { 1u, 2u };
    u64 hashes_a[2];
    u64 hashes_b[2];

    seed_log(&log, events, 4u, messages, 4u);
    EXPECT(dom_shard_compute_partition_hashes(&log, partitions, 2u, hashes_a) == 0, "hash a");
    EXPECT(dom_shard_compute_partition_hashes(&log, partitions, 2u, hashes_b) == 0, "hash b");
    EXPECT(hashes_a[0] == hashes_b[0], "partition hash mismatch");
    EXPECT(hashes_a[1] == hashes_b[1], "partition hash mismatch");
    return 0;
}

static int test_checkpoint_schedule(void)
{
    dom_integrity_schedule sched_a;
    dom_integrity_schedule sched_b;
    dom_act_time_t next_a;
    dom_act_time_t next_b;

    sched_a.interval = 10u;
    sched_a.next_due = 0u;
    sched_b.interval = 10u;
    sched_b.next_due = 0u;

    next_a = dom_integrity_schedule_next(&sched_a, 5u);
    next_b = dom_integrity_schedule_next(&sched_b, 5u);
    EXPECT(next_a == 15u, "schedule next incorrect");
    EXPECT(next_a == next_b, "schedule determinism mismatch");

    next_a = dom_integrity_schedule_next(&sched_a, 7u);
    next_b = dom_integrity_schedule_next(&sched_b, 7u);
    EXPECT(next_a == 15u, "schedule should remain");
    EXPECT(next_a == next_b, "schedule determinism mismatch");
    return 0;
}

static int test_dispute_bundle_replay(void)
{
    dom_shard_log log;
    dom_shard_event_entry events[4];
    dom_shard_message messages[4];
    dom_integrity_checkpoint checkpoint;
    dom_integrity_checkpoint checkpoints[1];
    dom_dispute_bundle bundle;
    dom_dispute_report report;
    u32 partitions[1] = { 1u };
    u64 schema_versions[1] = { 77u };
    u64 replay_hashes[1];

    seed_log(&log, events, 4u, messages, 4u);
    EXPECT(dom_integrity_checkpoint_build(&checkpoint, &log, 1u, 10u,
                                          partitions, 1u,
                                          schema_versions, 1u,
                                          900u, 111u, 222u) == 0,
           "checkpoint build");
    checkpoints[0] = checkpoint;
    dom_dispute_bundle_init(&bundle, 500u, 700u, 701u, 999u,
                            77u, 900u, 111u, 222u,
                            checkpoints, 1u);
    replay_hashes[0] = dom_integrity_checkpoint_hash(&checkpoint);

    EXPECT(dom_dispute_bundle_verify(&bundle, replay_hashes, 1u, &report) == 0, "bundle verify");
    EXPECT(report.ok == 1u, "bundle verify ok");

    replay_hashes[0] ^= 1u;
    EXPECT(dom_dispute_bundle_verify(&bundle, replay_hashes, 1u, &report) != 0, "bundle mismatch");
    EXPECT(report.ok == 0u, "bundle mismatch ok");
    EXPECT(report.mismatch_index == 0u, "bundle mismatch index");
    return 0;
}

static int test_corruption_detection(void)
{
    dom_shard_log log_clean;
    dom_shard_log log_corrupt;
    dom_shard_event_entry events_clean[4];
    dom_shard_event_entry events_corrupt[4];
    dom_shard_message messages_clean[4];
    dom_shard_message messages_corrupt[4];
    dom_integrity_checkpoint checkpoint;
    u32 partitions[1] = { 3u };
    u32 mismatch_partition = 0u;

    seed_log(&log_clean, events_clean, 4u, messages_clean, 4u);
    seed_log(&log_corrupt, events_corrupt, 4u, messages_corrupt, 4u);
    events_corrupt[0].task_id = 999u;

    EXPECT(dom_integrity_checkpoint_build(&checkpoint, &log_clean, 1u, 20u,
                                          partitions, 1u,
                                          0, 0u,
                                          0u, 0u, 0u) == 0,
           "checkpoint build");
    EXPECT(dom_integrity_witness_verify(&checkpoint, &log_corrupt, &mismatch_partition) != 0,
           "corruption should be detected");
    EXPECT(mismatch_partition == partitions[0], "mismatch partition");
    return 0;
}

int main(void)
{
    if (test_deterministic_hash() != 0) return 1;
    if (test_checkpoint_schedule() != 0) return 1;
    if (test_dispute_bundle_replay() != 0) return 1;
    if (test_corruption_detection() != 0) return 1;
    return 0;
}
