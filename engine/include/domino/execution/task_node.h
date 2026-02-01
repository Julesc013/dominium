/*
FILE: include/domino/execution/task_node.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/task_node
RESPONSIBILITY: Defines the public contract for execution TaskNode (Work IR runtime).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` and EXEC0/EXEC0b/EXEC0c.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_TASK_NODE_H
#define DOMINO_EXECUTION_TASK_NODE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Deterministic task category. */
typedef enum dom_task_category {
    DOM_TASK_AUTHORITATIVE = 0,
    DOM_TASK_DERIVED       = 1,
    DOM_TASK_PRESENTATION  = 2
} dom_task_category;

/* Determinism class for scheduling policy. */
typedef enum dom_determinism_class {
    DOM_DET_STRICT      = 0,
    DOM_DET_ORDERED     = 1,
    DOM_DET_COMMUTATIVE = 2,
    DOM_DET_DERIVED     = 3
} dom_determinism_class;

/* Fidelity tier (lower means cheaper, higher means more detailed). */
typedef enum dom_fidelity_tier {
    DOM_FID_LATENT = 0,
    DOM_FID_MACRO  = 1,
    DOM_FID_MESO   = 2,
    DOM_FID_MICRO  = 3,
    DOM_FID_FOCUS  = 4
} dom_fidelity_tier;

/* Invalid tick sentinel for unscheduled tasks. */
#define DOM_EXEC_TICK_INVALID ((u64)0xFFFFFFFFFFFFFFFFull)

/* Stable commit ordering key: (phase_id, task_id, sub_index). */
typedef struct dom_commit_key {
    u32 phase_id;
    u64 task_id;
    u32 sub_index;
} dom_commit_key;

/* TaskNode runtime structure (immutable after construction by convention). */
typedef struct dom_task_node {
    u64 task_id;           /* stable, deterministic identifier */
    u64 system_id;         /* originating system */
    u32 category;          /* dom_task_category */
    u32 determinism_class; /* dom_determinism_class */
    u32 fidelity_tier;     /* dom_fidelity_tier */
    u64 next_due_tick;     /* ACT tick or DOM_EXEC_TICK_INVALID */
    u64 access_set_id;
    u64 cost_model_id;
    const u32 *law_targets;      /* stable identifiers */
    u32 law_target_count;
    u32 phase_id;                /* explicit phase barrier */
    dom_commit_key commit_key;   /* commit ordering key */
    u64 law_scope_ref;
    u64 actor_ref;
    u64 capability_set_ref;
    const void *policy_params;   /* deterministic parameters */
    u32 policy_params_size;
} dom_task_node;

/* Compare commit keys. Returns <0, 0, >0 like strcmp. */
int dom_commit_key_compare(const dom_commit_key *a, const dom_commit_key *b);

/* Compare TaskNodes by commit key. Returns <0, 0, >0 like strcmp. */
int dom_task_node_compare(const dom_task_node *a, const dom_task_node *b);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_TASK_NODE_H */
