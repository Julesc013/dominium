/*
FILE: game/core/life/continuation_policy.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements continuation policy evaluation and selection.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic selection and refusal codes are mandatory.
*/
#include "dominium/life/continuation_policy.h"

static int life_epistemic_knows(const life_epistemic_set* set, u64 person_id)
{
    u32 i;
    if (!set) {
        return 1;
    }
    if (!set->known_person_ids || set->count == 0u) {
        return 0;
    }
    for (i = 0u; i < set->count; ++i) {
        if (set->known_person_ids[i] == person_id) {
            return 1;
        }
    }
    return 0;
}

static int life_candidate_better(const life_candidate* candidate,
                                 const life_candidate* best)
{
    if (!candidate) {
        return 0;
    }
    if (!best) {
        return 1;
    }
    if (candidate->reason < best->reason) {
        return 1;
    }
    if (candidate->reason > best->reason) {
        return 0;
    }
    return candidate->person_id < best->person_id;
}

static void life_decision_refuse(life_continuation_decision* decision,
                                 const life_ability_package* ability,
                                 life_refusal_code refusal)
{
    if (!decision) {
        return;
    }
    decision->refusal = refusal;
    if (ability && ability->spectator_on_refusal == LIFE_BOOL_TRUE) {
        decision->action = LIFE_CONT_ACTION_SPECTATOR;
    }
}

static int life_continuation_select_s1(const life_continuation_context* ctx,
                                       life_continuation_decision* out_decision)
{
    u32 i;
    u32 total = 0u;
    u32 known = 0u;
    u32 authorized = 0u;
    const life_candidate* best = 0;

    if (!ctx || !out_decision) {
        return -1;
    }
    if (ctx->candidate_count > 0u && !ctx->candidates) {
        return -2;
    }

    for (i = 0u; i < ctx->candidate_count; ++i) {
        const life_candidate* cand = &ctx->candidates[i];
        int is_known;
        int has_authority;

        total += 1u;

        if (ctx->allow_blind_delegation) {
            is_known = 1;
        } else {
            is_known = life_epistemic_knows(ctx->epistemic, cand->person_id);
        }
        if (!is_known) {
            continue;
        }
        known += 1u;

        if (ctx->authority) {
            has_authority = life_authority_can_control(ctx->authority,
                                                       ctx->controller_id,
                                                       cand->person_id,
                                                       0);
        } else {
            has_authority = 1;
        }
        if (!has_authority) {
            continue;
        }
        authorized += 1u;

        if (life_candidate_better(cand, best)) {
            best = cand;
        }
    }

    if (best) {
        out_decision->action = LIFE_CONT_ACTION_TRANSFER;
        out_decision->target_person_id = best->person_id;
        out_decision->refusal = LIFE_REFUSAL_NONE;
        return 0;
    }

    if (total == 0u) {
        out_decision->refusal = LIFE_REFUSAL_NO_ELIGIBLE_PERSON;
        return 0;
    }
    if (known == 0u) {
        out_decision->refusal = LIFE_REFUSAL_EPISTEMIC_INSUFFICIENT_KNOWLEDGE;
        return 0;
    }
    if (authorized == 0u) {
        out_decision->refusal = LIFE_REFUSAL_INSUFFICIENT_AUTHORITY;
        return 0;
    }
    out_decision->refusal = LIFE_REFUSAL_NO_ELIGIBLE_PERSON;
    return 0;
}

static int life_continuation_check_prereqs(life_policy_type type,
                                           const life_continuation_prereqs* prereqs,
                                           life_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = LIFE_REFUSAL_NONE;
    }
    if (!prereqs) {
        if (out_refusal) {
            *out_refusal = LIFE_REFUSAL_PREREQ_MISSING_FACILITY;
        }
        return 0;
    }
    if (type == LIFE_POLICY_S2) {
        if (!prereqs->has_facility) {
            if (out_refusal) {
                *out_refusal = LIFE_REFUSAL_PREREQ_MISSING_FACILITY;
            }
            return 0;
        }
        if (!prereqs->has_resources) {
            if (out_refusal) {
                *out_refusal = LIFE_REFUSAL_PREREQ_MISSING_RESOURCES;
            }
            return 0;
        }
        return 1;
    }
    if (type == LIFE_POLICY_S3) {
        if (!prereqs->has_drone) {
            if (out_refusal) {
                *out_refusal = LIFE_REFUSAL_PREREQ_MISSING_FACILITY;
            }
            return 0;
        }
        return 1;
    }
    if (type == LIFE_POLICY_S4) {
        if (!prereqs->has_recording) {
            if (out_refusal) {
                *out_refusal = LIFE_REFUSAL_PREREQ_MISSING_RECORDING;
            }
            return 0;
        }
        if (!prereqs->has_facility) {
            if (out_refusal) {
                *out_refusal = LIFE_REFUSAL_PREREQ_MISSING_FACILITY;
            }
            return 0;
        }
        return 1;
    }
    return 0;
}

int life_continuation_decide(const life_continuation_context* ctx,
                             life_continuation_decision* out_decision)
{
    if (!ctx || !out_decision) {
        return -1;
    }

    out_decision->policy_id = (u32)ctx->policy_type;
    out_decision->target_person_id = 0u;
    out_decision->action = LIFE_CONT_ACTION_NONE;
    out_decision->refusal = LIFE_REFUSAL_NONE;

    if (!ctx->ability) {
        out_decision->refusal = LIFE_REFUSAL_POLICY_NOT_ALLOWED;
        return 0;
    }
    if (!life_ability_package_allows_policy(ctx->ability, ctx->policy_type)) {
        life_decision_refuse(out_decision, ctx->ability, LIFE_REFUSAL_POLICY_NOT_ALLOWED);
        return 0;
    }
    if (ctx->ability->transfer_allowed == LIFE_BOOL_FALSE &&
        ctx->policy_type == LIFE_POLICY_S1) {
        life_decision_refuse(out_decision, ctx->ability, LIFE_REFUSAL_POLICY_NOT_ALLOWED);
        return 0;
    }

    if (ctx->policy_type == LIFE_POLICY_S1) {
        if (life_continuation_select_s1(ctx, out_decision) != 0) {
            return -2;
        }
        if (out_decision->refusal != LIFE_REFUSAL_NONE) {
            life_decision_refuse(out_decision, ctx->ability, out_decision->refusal);
        }
        return 0;
    }

    {
        life_refusal_code refusal = LIFE_REFUSAL_NONE;
        int ok = life_continuation_check_prereqs(ctx->policy_type, &ctx->prereqs, &refusal);
        if (!ok) {
            life_decision_refuse(out_decision, ctx->ability, refusal);
            return 0;
        }
    }

    out_decision->action = LIFE_CONT_ACTION_PENDING;
    out_decision->refusal = LIFE_REFUSAL_NONE;
    return 0;
}
