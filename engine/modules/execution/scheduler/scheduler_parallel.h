/*
FILE: source/domino/execution/scheduler/scheduler_parallel.h
MODULE: Domino
RESPONSIBILITY: Deterministic parallel scheduler shim (delegates to EXEC2 reference).
*/
#ifndef DG_SCHEDULER_PARALLEL_H
#define DG_SCHEDULER_PARALLEL_H

#include "domino/execution/scheduler_iface.h"

#ifdef __cplusplus

class dom_scheduler_parallel : public IScheduler {
public:
    virtual void schedule(const dom_task_graph &graph,
                          dom_execution_context &ctx,
                          IScheduleSink &sink);
};

#endif /* __cplusplus */

#endif /* DG_SCHEDULER_PARALLEL_H */
