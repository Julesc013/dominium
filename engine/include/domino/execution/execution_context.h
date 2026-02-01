/*
FILE: include/domino/execution/execution_context.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/execution_context
RESPONSIBILITY: Defines the public contract for ExecutionContext and law hooks.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` and EXEC0c.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_CONTEXT_H
#define DOMINO_EXECUTION_CONTEXT_H

#include "domino/core/types.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"
#include "domino/execution/access_set.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Determinism mode for scheduling and audit. */
typedef enum dom_determinism_mode {
    DOM_DET_MODE_STRICT = 0,
    DOM_DET_MODE_AUDIT  = 1,
    DOM_DET_MODE_TEST   = 2
} dom_determinism_mode;

/* Scope chain reference (deterministic ordering assumed). */
typedef struct dom_scope_chain {
    const u64 *scope_ids;
    u32 scope_count;
} dom_scope_chain;

/* Capability set reference list. */
typedef struct dom_capability_set_list {
    const u64 *capability_set_ids;
    u32 capability_set_count;
} dom_capability_set_list;

/* Budget snapshot (abstract units). */
typedef struct dom_budget_snapshot {
    u32 cpu_budget;
    u32 memory_budget;
    u32 bandwidth_budget;
} dom_budget_snapshot;

/* Law decision outcome kinds. */
typedef enum dom_law_decision_kind {
    DOM_LAW_ACCEPT = 0,
    DOM_LAW_REFUSE = 1,
    DOM_LAW_TRANSFORM = 2,
    DOM_LAW_CONSTRAIN = 3
} dom_law_decision_kind;

/* Law decision payload (minimal runtime representation). */
typedef struct dom_law_decision {
    u32 kind; /* dom_law_decision_kind */
    u32 refusal_code;
    u32 transformed_fidelity_tier; /* dom_fidelity_tier, 0 if unchanged */
    u64 transformed_next_due_tick; /* DOM_EXEC_TICK_INVALID if unchanged */
} dom_law_decision;

/* Audit event (minimal runtime representation). */
typedef struct dom_audit_event {
    u32 event_id;
    u64 task_id;
    u32 decision_kind; /* dom_law_decision_kind */
    u32 refusal_code;
} dom_audit_event;

struct dom_execution_context;

typedef dom_law_decision (*dom_law_eval_fn)(const struct dom_execution_context *ctx,
                                            const dom_task_node *node,
                                            void *user_data);
typedef void (*dom_audit_fn)(const struct dom_execution_context *ctx,
                             const dom_audit_event *event,
                             void *user_data);
typedef const dom_access_set *(*dom_access_set_lookup_fn)(const struct dom_execution_context *ctx,
                                                          u64 access_set_id,
                                                          void *user_data);

/* Execution context for schedulers and law evaluation. */
typedef struct dom_execution_context {
    u64 act_now;
    const dom_scope_chain *scope_chain;
    const dom_capability_set_list *capability_sets;
    const dom_budget_snapshot *budget_snapshot;
    u32 determinism_mode; /* dom_determinism_mode */

    dom_law_eval_fn evaluate_law;
    dom_audit_fn record_audit;
    dom_access_set_lookup_fn lookup_access_set;
    void *user_data;
} dom_execution_context;

/* Law evaluation helper (calls callback or returns ACCEPT). */
dom_law_decision dom_execution_context_evaluate_law(const dom_execution_context *ctx,
                                                    const dom_task_node *node);

/* Audit helper (calls callback if present). */
void dom_execution_context_record_audit(const dom_execution_context *ctx,
                                        const dom_audit_event *event);

/* AccessSet lookup helper (returns NULL if unavailable). */
const dom_access_set *dom_execution_context_lookup_access_set(const dom_execution_context *ctx,
                                                              u64 access_set_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_CONTEXT_H */
