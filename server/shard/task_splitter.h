/*
FILE: server/shard/task_splitter.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic TaskGraph partitioning across shards.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers, OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_TASK_SPLITTER_H
#define DOMINIUM_SERVER_SHARD_TASK_SPLITTER_H

#include "shard_api.h"
#include "domino/execution/task_graph.h"
#include "domino/execution/execution_context.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shard_task_graph {
    dom_shard_id shard_id;
    dom_task_graph graph;
    dom_task_node* tasks;
    u32 task_capacity;
    dom_dependency_edge* edges;
    u32 edge_capacity;
    u32 task_count;
    u32 edge_count;
} dom_shard_task_graph;

typedef struct dom_shard_task_mapping {
    u64 task_id;
    dom_shard_id shard_id;
} dom_shard_task_mapping;

typedef struct dom_shard_task_splitter {
    dom_shard_task_graph* shard_graphs;
    u32 shard_graph_count;
    dom_shard_task_mapping* task_map;
    u32 task_map_capacity;
    u32 task_map_count;
    dom_shard_message* messages;
    u32 message_capacity;
    u32 message_count;
} dom_shard_task_splitter;

void dom_shard_task_graph_init(dom_shard_task_graph* graph,
                               dom_shard_id shard_id,
                               dom_task_node* task_storage,
                               u32 task_capacity,
                               dom_dependency_edge* edge_storage,
                               u32 edge_capacity);

void dom_shard_task_splitter_init(dom_shard_task_splitter* splitter,
                                  dom_shard_task_graph* shard_graphs,
                                  u32 shard_graph_count,
                                  dom_shard_task_mapping* map_storage,
                                  u32 map_capacity,
                                  dom_shard_message* message_storage,
                                  u32 message_capacity);
void dom_shard_task_splitter_reset(dom_shard_task_splitter* splitter);

int dom_shard_task_splitter_split(dom_shard_task_splitter* splitter,
                                  const dom_task_graph* graph,
                                  const dom_shard_registry* registry,
                                  const dom_execution_context* ctx,
                                  dom_shard_id fallback_shard);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_TASK_SPLITTER_H */
