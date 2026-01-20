/*
FILE: source/domino/execution/scheduler/scheduler_parallel.cpp
MODULE: Domino
RESPONSIBILITY: Deterministic parallel scheduler shim (delegates to EXEC2 reference).
*/
#include "execution/scheduler/scheduler_parallel.h"

#include "execution/scheduler/scheduler_single_thread.h"

void dom_scheduler_parallel::schedule(const dom_task_graph &graph,
                                      dom_execution_context &ctx,
                                      IScheduleSink &sink) {
    dom_scheduler_single_thread ref;
    ref.schedule(graph, ctx, sink);
}
