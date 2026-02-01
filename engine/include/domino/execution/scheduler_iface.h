/*
FILE: include/domino/execution/scheduler_iface.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/scheduler_iface
RESPONSIBILITY: Defines the scheduler interface for deterministic Work IR ordering.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` and EXEC0/EXEC0b/EXEC0c.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_SCHEDULER_IFACE_H
#define DOMINO_EXECUTION_SCHEDULER_IFACE_H

#include "domino/execution/task_graph.h"
#include "domino/execution/execution_context.h"

#ifdef __cplusplus

class IScheduleSink {
public:
    virtual ~IScheduleSink();
    virtual void on_task(const dom_task_node &node,
                         const dom_law_decision &decision) = 0;
};

class IScheduler {
public:
    virtual ~IScheduler();
    virtual void schedule(const dom_task_graph &graph,
                          dom_execution_context &ctx,
                          IScheduleSink &sink) = 0;
};

#endif /* __cplusplus */

#endif /* DOMINO_EXECUTION_SCHEDULER_IFACE_H */
