/*
FILE: source/domino/execution/scheduler/scheduler_parallel.h
MODULE: Domino
RESPONSIBILITY: Parallel deterministic scheduler backend (EXEC3).
*/
#ifndef DG_SCHEDULER_PARALLEL_H
#define DG_SCHEDULER_PARALLEL_H

#include "domino/execution/scheduler_iface.h"

#ifdef __cplusplus

class dom_scheduler_parallel : public IScheduler {
public:
    dom_scheduler_parallel(u32 worker_count, u32 queue_capacity);
    ~dom_scheduler_parallel();

    virtual void schedule(const dom_task_graph &graph,
                          dom_execution_context &ctx,
                          IScheduleSink &sink);

private:
    struct dom_thread_pool *pool;
    u32 worker_count;
    u32 queue_capacity;
};

#endif /* __cplusplus */

#endif /* DG_SCHEDULER_PARALLEL_H */
