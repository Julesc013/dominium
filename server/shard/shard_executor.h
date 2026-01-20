/*
FILE: server/shard/shard_executor.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Executes shard-local TaskGraphs with deterministic admission.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers, OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_EXECUTOR_H
#define DOMINIUM_SERVER_SHARD_EXECUTOR_H

#include "shard_api.h"
#include "message_bus.h"
#include "domino/execution/task_graph.h"
#include "domino/execution/execution_context.h"
#ifdef __cplusplus
#include "domino/execution/scheduler_iface.h"
#else
typedef struct IScheduler IScheduler;
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shard_executor {
    dom_shard_id shard_id;
    IScheduler* scheduler;
    dom_execution_context* ctx;
    dom_shard_message_bus* bus;
    dom_shard_log* log;
    u64* accepted_tasks;
    u32 accepted_count;
    u32 accepted_capacity;
    u64 next_event_id;
} dom_shard_executor;

void dom_shard_executor_init(dom_shard_executor* executor,
                             dom_shard_id shard_id,
                             IScheduler* scheduler,
                             dom_execution_context* ctx,
                             dom_shard_message_bus* bus,
                             dom_shard_log* log,
                             u64* accepted_storage,
                             u32 accepted_capacity);

int dom_shard_executor_execute(dom_shard_executor* executor,
                               const dom_task_graph* graph,
                               const dom_shard_registry* registry,
                               const dom_shard_message* outbound_messages,
                               u32 outbound_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_EXECUTOR_H */
