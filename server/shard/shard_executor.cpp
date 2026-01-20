/*
FILE: server/shard/shard_executor.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Executes shard-local TaskGraphs with deterministic admission.
*/
#include "shard_executor.h"

#include "domino/execution/access_set.h"

#include <string.h>

static int dom_shard_executor_record_accept(dom_shard_executor* executor, u64 task_id);

class dom_shard_schedule_sink : public IScheduleSink {
public:
    dom_shard_schedule_sink(dom_shard_executor* executor)
        : executor_(executor) {}

    virtual void on_task(const dom_task_node &node,
                         const dom_law_decision &decision)
    {
        if (!executor_ || !executor_->log) {
            return;
        }
        if (decision.kind != DOM_LAW_REFUSE) {
            dom_shard_event_entry entry;
            entry.event_id = executor_->next_event_id++;
            entry.task_id = node.task_id;
            entry.tick = executor_->ctx ? executor_->ctx->act_now : 0u;
            dom_shard_log_record_event(executor_->log, &entry);
            dom_shard_executor_record_accept(executor_, node.task_id);
        }
    }

private:
    dom_shard_executor* executor_;
};

static int dom_shard_executor_record_accept(dom_shard_executor* executor, u64 task_id)
{
    if (!executor || !executor->accepted_tasks) {
        return -1;
    }
    if (executor->accepted_count >= executor->accepted_capacity) {
        return -2;
    }
    executor->accepted_tasks[executor->accepted_count++] = task_id;
    return 0;
}

static u64 dom_shard_owner_id_from_range(const dom_access_range* range)
{
    if (!range) {
        return 0u;
    }
    switch (range->kind) {
        case DOM_RANGE_INDEX_RANGE:
        case DOM_RANGE_SINGLE:
            return range->start_id;
        case DOM_RANGE_COMPONENT_SET:
        case DOM_RANGE_ENTITY_SET:
        case DOM_RANGE_INTEREST_SET:
        default:
            return range->set_id;
    }
}

static u64 dom_shard_owner_id_from_access(const dom_execution_context* ctx,
                                          const dom_task_node* node)
{
    const dom_access_set* set;
    const dom_access_range* range = 0;
    if (!ctx || !node) {
        return 0u;
    }
    set = dom_execution_context_lookup_access_set(ctx, node->access_set_id);
    if (!set) {
        return 0u;
    }
    if (node->category == DOM_TASK_AUTHORITATIVE && set->write_count > 0u) {
        range = &set->write_ranges[0];
    } else if (set->read_count > 0u) {
        range = &set->read_ranges[0];
    } else if (set->reduce_count > 0u) {
        range = &set->reduce_ranges[0];
    }
    return dom_shard_owner_id_from_range(range);
}

static void dom_shard_sort_u64(u64* values, u32 count)
{
    u32 i;
    if (!values || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        u64 key = values[i];
        u32 j = i;
        while (j > 0u && values[j - 1u] > key) {
            values[j] = values[j - 1u];
            j -= 1u;
        }
        values[j] = key;
    }
}

static int dom_shard_has_task(const dom_shard_executor* executor, u64 task_id)
{
    u32 i;
    if (!executor || !executor->accepted_tasks) {
        return 0;
    }
    for (i = 0u; i < executor->accepted_count; ++i) {
        if (executor->accepted_tasks[i] == task_id) {
            return 1;
        }
    }
    return 0;
}

void dom_shard_executor_init(dom_shard_executor* executor,
                             dom_shard_id shard_id,
                             IScheduler* scheduler,
                             dom_execution_context* ctx,
                             dom_shard_message_bus* bus,
                             dom_shard_log* log,
                             u64* accepted_storage,
                             u32 accepted_capacity)
{
    if (!executor) {
        return;
    }
    executor->shard_id = shard_id;
    executor->scheduler = scheduler;
    executor->ctx = ctx;
    executor->bus = bus;
    executor->log = log;
    executor->accepted_tasks = accepted_storage;
    executor->accepted_capacity = accepted_capacity;
    executor->accepted_count = 0u;
    executor->next_event_id = 1u;
    if (accepted_storage && accepted_capacity > 0u) {
        memset(accepted_storage, 0, sizeof(u64) * (size_t)accepted_capacity);
    }
}

int dom_shard_executor_execute(dom_shard_executor* executor,
                               const dom_task_graph* graph,
                               const dom_shard_registry* registry,
                               const dom_shard_message* outbound_messages,
                               u32 outbound_count)
{
    u32 i;
    dom_shard_schedule_sink sink(executor);
    if (!executor || !graph || !registry) {
        return -1;
    }
    if (!executor->scheduler || !executor->ctx) {
        return -2;
    }
    executor->accepted_count = 0u;

    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        if (node->category != DOM_TASK_AUTHORITATIVE) {
            continue;
        }
        if (dom_shard_validate_access(registry,
                                      executor->shard_id,
                                      dom_shard_owner_id_from_access(executor->ctx, node),
                                      DOM_SHARD_ACCESS_WRITE) != 0) {
            return -3;
        }
    }

    executor->scheduler->schedule(*graph, *executor->ctx, sink);
    if (executor->accepted_tasks && executor->accepted_count > 1u) {
        dom_shard_sort_u64(executor->accepted_tasks, executor->accepted_count);
    }

    if (executor->bus && outbound_messages && outbound_count > 0u) {
        for (i = 0u; i < outbound_count; ++i) {
            const dom_shard_message* msg = &outbound_messages[i];
            if (msg->source_shard != executor->shard_id) {
                continue;
            }
            if (dom_shard_has_task(executor, msg->task_id)) {
                dom_shard_message_bus_enqueue(executor->bus, msg);
            }
        }
    }

    return 0;
}
