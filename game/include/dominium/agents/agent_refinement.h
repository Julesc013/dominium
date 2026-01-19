/*
FILE: include/dominium/agents/agent_refinement.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines deterministic refinement selection and events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Selection order is stable by (role_rank desc, agent_id asc).
*/
#ifndef DOMINIUM_AGENTS_AGENT_REFINEMENT_H
#define DOMINIUM_AGENTS_AGENT_REFINEMENT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/agents/aggregate_beliefs.h"
#include "dominium/agents/agent_aggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct agent_refine_candidate {
    u64 agent_id;
    u32 role_rank;
} agent_refine_candidate;

typedef enum agent_refinement_event_type {
    AGENT_REFINE_EVENT_REFINE = 0,
    AGENT_REFINE_EVENT_COLLAPSE = 1
} agent_refinement_event_type;

typedef struct agent_refinement_event {
    u64 event_id;
    u64 aggregate_agent_id;
    dom_act_time_t trigger_act;
    agent_refinement_event_type type;
    u32 desired_count;
    u64 provenance_ref;
} agent_refinement_event;

int agent_refinement_select(const agent_refine_candidate* candidates,
                            u32 candidate_count,
                            u32 max_select,
                            u64* out_ids,
                            u32* in_out_count);
int agent_refinement_apply(const aggregate_belief_summary* summary,
                           const agent_refine_candidate* candidates,
                           u32 candidate_count,
                           u32 desired_count,
                           agent_belief_state* out_states,
                           u64* out_ids,
                           u32* in_out_count,
                           dom_act_time_t now_act,
                           agent_refusal_code* out_refusal);
int agent_refinement_apply_to_aggregate(aggregate_agent* agg,
                                        u32 desired_count,
                                        agent_refusal_code* out_refusal);
int agent_refinement_process_events(agent_aggregate_registry* aggregates,
                                    agent_refinement_event* events,
                                    u32 event_count,
                                    dom_act_time_t target_tick,
                                    agent_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_REFINEMENT_H */
