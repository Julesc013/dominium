/*
FILE: include/domino/execution/task_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/task_graph
RESPONSIBILITY: Defines the public contract for TaskGraph (Work IR runtime).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` and EXEC0.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_TASK_GRAPH_H
#define DOMINO_EXECUTION_TASK_GRAPH_H

#include "domino/core/types.h"
#include "domino/execution/task_node.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Task dependency edge. */
typedef struct dom_dependency_edge {
    u64 from_task_id;
    u64 to_task_id;
    u32 reason_id; /* stable token, 0 if unused */
} dom_dependency_edge;

/* Phase barrier declaration. */
typedef struct dom_phase_barrier {
    u32 phase_id;
    const u64 *before_tasks;
    u32 before_count;
    const u64 *after_tasks;
    u32 after_count;
} dom_phase_barrier;

/* TaskGraph runtime structure. */
typedef struct dom_task_graph {
    u64 graph_id;
    u64 epoch_id;
    const dom_task_node *tasks;
    u32 task_count;
    const dom_dependency_edge *dependency_edges;
    u32 dependency_count;
    const dom_phase_barrier *phase_barriers;
    u32 phase_barrier_count;
} dom_task_graph;

/* Stable task sort (by commit key: phase_id, task_id, sub_index). */
void dom_stable_task_sort(dom_task_node *tasks, u32 task_count);

/* Validate sorted ordering. */
d_bool dom_task_graph_is_sorted(const dom_task_node *tasks, u32 task_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_TASK_GRAPH_H */
