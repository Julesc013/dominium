/*
FILE: source/domino/execution/scheduler/scheduler_single_thread.h
MODULE: Domino
RESPONSIBILITY: Reference single-thread deterministic scheduler (EXEC2).
*/
#ifndef DG_SCHEDULER_SINGLE_THREAD_H
#define DG_SCHEDULER_SINGLE_THREAD_H

#include "domino/execution/scheduler_iface.h"

#ifdef __cplusplus

enum dom_exec_refusal_code {
    DOM_EXEC_REFUSE_INVALID_GRAPH = 1,
    DOM_EXEC_REFUSE_LAW           = 2,
    DOM_EXEC_REFUSE_CONFLICT      = 3,
    DOM_EXEC_REFUSE_REDUCTION     = 4,
    DOM_EXEC_REFUSE_ACCESS_SET    = 5
};

enum dom_exec_audit_event_id {
    DOM_EXEC_AUDIT_TASK_ADMITTED   = 1,
    DOM_EXEC_AUDIT_TASK_REFUSED    = 2,
    DOM_EXEC_AUDIT_TASK_TRANSFORMED = 3,
    DOM_EXEC_AUDIT_TASK_EXECUTED   = 4,
    DOM_EXEC_AUDIT_TASK_COMMITTED  = 5
};

class dom_scheduler_single_thread : public IScheduler {
public:
    virtual void schedule(const dom_task_graph &graph,
                          dom_execution_context &ctx,
                          IScheduleSink &sink);
};

#endif /* __cplusplus */

#endif /* DG_SCHEDULER_SINGLE_THREAD_H */
