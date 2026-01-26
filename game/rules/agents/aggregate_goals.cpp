/*
FILE: game/agents/aggregate_goals.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic aggregate goal summaries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation is order-independent and deterministic.
*/
#include "dominium/agents/aggregate_goals.h"

#include <string.h>

void aggregate_goals_init(aggregate_goal_summary* summary)
{
    if (!summary) {
        return;
    }
    memset(summary, 0, sizeof(*summary));
}

int aggregate_goals_from_status(const agent_goal_status_entry* statuses,
                                u32 count,
                                aggregate_goal_summary* out_summary)
{
    u32 i;
    if (!out_summary) {
        return -1;
    }
    aggregate_goals_init(out_summary);
    if (!statuses || count == 0u) {
        return 0;
    }
    out_summary->count = count;
    for (i = 0u; i < count; ++i) {
        u32 type = statuses[i].goal_type;
        if (type >= AGENT_GOAL_TYPE_COUNT) {
            continue;
        }
        out_summary->goal_counts[type] += 1u;
        if (statuses[i].is_satisfied) {
            out_summary->satisfied_counts[type] += 1u;
        }
    }
    return 0;
}

int aggregate_goals_from_results(const agent_goal_eval_result* results,
                                 u32 count,
                                 aggregate_goal_summary* out_summary)
{
    u32 i;
    if (!out_summary) {
        return -1;
    }
    aggregate_goals_init(out_summary);
    if (!results || count == 0u) {
        return 0;
    }
    out_summary->count = count;
    for (i = 0u; i < count; ++i) {
        const agent_goal* goal = results[i].goal;
        u32 type;
        if (!goal) {
            continue;
        }
        type = goal->type;
        if (type >= AGENT_GOAL_TYPE_COUNT) {
            continue;
        }
        out_summary->goal_counts[type] += 1u;
    }
    return 0;
}
