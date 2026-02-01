/*
FILE: include/domino/execution/cost_model.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/cost_model
RESPONSIBILITY: Defines the public contract for CostModel (Work IR runtime).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` and EXEC0.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_COST_MODEL_H
#define DOMINO_EXECUTION_COST_MODEL_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Latency sensitivity class. */
typedef enum dom_latency_class {
    DOM_LATENCY_LOW = 0,
    DOM_LATENCY_MEDIUM = 1,
    DOM_LATENCY_HIGH = 2
} dom_latency_class;

/* CostModel runtime structure. */
typedef struct dom_cost_model {
    u64 cost_id;
    u32 cpu_upper_bound;
    u32 memory_upper_bound;
    u32 bandwidth_upper_bound;
    u32 latency_class;         /* dom_latency_class */
    i32 degradation_priority;
} dom_cost_model;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_COST_MODEL_H */
