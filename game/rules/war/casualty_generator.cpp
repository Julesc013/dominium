/*
FILE: game/rules/war/casualty_generator.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic casualty generation via LIFE2 pipelines.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Casualty generation order is deterministic.
*/
#include "dominium/rules/war/casualty_generator.h"

#include <string.h>

int casualty_generate(casualty_generator* gen,
                      casualty_source* source,
                      u32 casualty_count,
                      const casualty_request* req,
                      u64* out_death_event_ids,
                      u32 out_capacity,
                      u32* out_count,
                      life_death_refusal_code* out_refusal)
{
    u32 i;
    life_death_input input;
    u32 produced = 0u;
    if (out_refusal) {
        *out_refusal = LIFE_DEATH_REFUSAL_NONE;
    }
    if (out_count) {
        *out_count = 0u;
    }
    if (!gen || !gen->life || !source || !req) {
        return -1;
    }
    if (casualty_count == 0u) {
        return 0;
    }
    if (!source->body_ids || source->count < casualty_count ||
        (source->count - source->cursor) < casualty_count) {
        if (out_refusal) {
            *out_refusal = LIFE_DEATH_REFUSAL_BODY_NOT_ALIVE;
        }
        return -2;
    }
    if (out_capacity < casualty_count) {
        return -3;
    }

    for (i = 0u; i < casualty_count; ++i) {
        u64 body_id = source->body_ids[source->cursor++];
        memset(&input, 0, sizeof(input));
        input.body_id = body_id;
        input.cause_code = req->cause_code;
        input.act_time = req->act_time;
        input.location_ref = req->location_ref;
        input.provenance_ref = req->provenance_ref;
        input.policy_id = req->policy_id;
        input.remains_inventory_account_id = req->remains_inventory_account_id;
        input.jurisdiction_id = req->jurisdiction_id;
        input.has_contract = req->has_contract;
        input.allow_finder = req->allow_finder;
        input.jurisdiction_allows = req->jurisdiction_allows;
        input.estate_locked = req->estate_locked;
        input.collapse_remains = req->collapse_remains;
        if (life_handle_death(gen->life, &input, out_refusal, &out_death_event_ids[produced], 0) != 0) {
            return -4;
        }
        produced += 1u;
    }
    if (out_count) {
        *out_count = produced;
    }
    return 0;
}
