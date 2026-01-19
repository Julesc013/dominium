/*
FILE: game/agents/aggregate_beliefs.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic aggregate belief summaries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation is order-independent and deterministic.
*/
#include "dominium/agents/aggregate_beliefs.h"

#include <string.h>

int aggregate_beliefs_from_states(const agent_belief_state* states,
                                  u32 count,
                                  aggregate_belief_summary* out_summary)
{
    u32 i;
    u64 hunger_sum = 0u;
    u64 threat_sum = 0u;
    if (!out_summary) {
        return -1;
    }
    memset(out_summary, 0, sizeof(*out_summary));
    if (!states || count == 0u) {
        return 0;
    }
    out_summary->count = count;
    out_summary->knowledge_mask = states[0].knowledge_mask;
    out_summary->knowledge_any_mask = states[0].knowledge_mask;
    out_summary->hunger_min = states[0].hunger_level;
    out_summary->hunger_max = states[0].hunger_level;
    out_summary->threat_min = states[0].threat_level;
    out_summary->threat_max = states[0].threat_level;
    hunger_sum = states[0].hunger_level;
    threat_sum = states[0].threat_level;
    for (i = 1u; i < count; ++i) {
        u32 hunger = states[i].hunger_level;
        u32 threat = states[i].threat_level;
        out_summary->knowledge_mask &= states[i].knowledge_mask;
        out_summary->knowledge_any_mask |= states[i].knowledge_mask;
        if (hunger < out_summary->hunger_min) {
            out_summary->hunger_min = hunger;
        }
        if (hunger > out_summary->hunger_max) {
            out_summary->hunger_max = hunger;
        }
        if (threat < out_summary->threat_min) {
            out_summary->threat_min = threat;
        }
        if (threat > out_summary->threat_max) {
            out_summary->threat_max = threat;
        }
        hunger_sum += hunger;
        threat_sum += threat;
    }
    out_summary->hunger_avg = (u32)(hunger_sum / (u64)count);
    out_summary->threat_avg = (u32)(threat_sum / (u64)count);
    return 0;
}
