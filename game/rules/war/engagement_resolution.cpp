/*
FILE: game/rules/war/engagement_resolution.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic engagement resolution and casualty generation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resolution outcomes are deterministic.
*/
#include "dominium/rules/war/engagement_resolution.h"

#include <string.h>

typedef struct engagement_participant_state {
    engagement_participant participant;
    security_force* force;
    military_cohort* cohort;
    readiness_state* readiness;
    morale_state* morale;
    u32 cohort_count;
    u32 equipment_total;
    u32 readiness_level;
    u32 morale_level;
    u64 supply_store_ref;
    int supply_shortage;
    u32 legitimacy_value;
    int has_legitimacy;
    u64 strength;
} engagement_participant_state;

static u64 engagement_hash_mix(u64 h, u64 v)
{
    h ^= v + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    return h;
}

static u32 engagement_environment_factor(const engagement* eng)
{
    u64 h = 0xC0FFEEu;
    u32 i;
    if (!eng) {
        return 1000u;
    }
    h = engagement_hash_mix(h, (u64)eng->domain_scope);
    for (i = 0u; i < eng->environment_modifier_count; ++i) {
        h = engagement_hash_mix(h, eng->environment_modifiers[i]);
    }
    return 900u + (u32)(h % 201u);
}

static u32 engagement_objective_factor(u32 objective, u32 role)
{
    switch (objective) {
        case ENGAGEMENT_OBJECTIVE_ATTACK:
            return (role == ENGAGEMENT_ROLE_ATTACKER) ? 900u : 1100u;
        case ENGAGEMENT_OBJECTIVE_DEFEND:
            return (role == ENGAGEMENT_ROLE_ATTACKER) ? 900u : 1100u;
        case ENGAGEMENT_OBJECTIVE_RAID:
            return (role == ENGAGEMENT_ROLE_ATTACKER) ? 950u : 1000u;
        case ENGAGEMENT_OBJECTIVE_BLOCKADE:
            return 1000u;
        default:
            return 1000u;
    }
}

static engagement_casualty_source* engagement_find_casualty_source(engagement_resolution_context* ctx,
                                                                   u64 force_id)
{
    u32 i;
    if (!ctx || !ctx->casualty_sources) {
        return 0;
    }
    for (i = 0u; i < ctx->casualty_source_count; ++i) {
        if (ctx->casualty_sources[i].force_id == force_id) {
            return &ctx->casualty_sources[i];
        }
    }
    return 0;
}

static u32 engagement_bucket_u32(u32 value, u32 bucket)
{
    if (bucket == 0u) {
        return value;
    }
    return (value / bucket) * bucket;
}

static u64 engagement_select_force_id_by_role(const engagement_participant_state* states,
                                              u32 count,
                                              u32 role)
{
    u32 i;
    u64 selected = 0u;
    for (i = 0u; i < count; ++i) {
        if (states[i].participant.role != role ||
            states[i].participant.force_id == 0u) {
            continue;
        }
        if (selected == 0u || states[i].participant.force_id < selected) {
            selected = states[i].participant.force_id;
        }
    }
    return selected;
}

static int engagement_strength_compute(const engagement* eng,
                                       engagement_participant_state* state,
                                       u32 env_factor)
{
    u64 strength;
    u32 objective_factor;
    u32 legitimacy_factor = 1000u;
    u32 readiness_level = state->readiness_level;
    u32 morale_level = state->morale_level;
    if (state->supply_shortage) {
        if (readiness_level > 100u) {
            readiness_level -= 100u;
        } else {
            readiness_level = 0u;
        }
    }
    if (state->has_legitimacy) {
        legitimacy_factor = 900u + (state->legitimacy_value / 10u);
        if (legitimacy_factor > 1000u) {
            legitimacy_factor = 1000u;
        }
    }
    objective_factor = engagement_objective_factor(eng->objective, state->participant.role);
    strength = (u64)state->cohort_count * 1000u;
    strength += (u64)state->equipment_total * 500u;
    strength = (strength * (u64)readiness_level) / READINESS_SCALE;
    strength = (strength * (u64)morale_level) / MORALE_SCALE;
    strength = (strength * (u64)legitimacy_factor) / 1000u;
    strength = (strength * (u64)env_factor) / 1000u;
    strength = (strength * (u64)objective_factor) / 1000u;
    state->strength = strength;
    return 0;
}

static int engagement_collect_participants(const engagement* eng,
                                           engagement_resolution_context* ctx,
                                           engagement_participant_state* out_states,
                                           u32* out_count,
                                           engagement_refusal_code* out_refusal)
{
    u32 i;
    u32 count = 0u;
    if (out_refusal) {
        *out_refusal = ENGAGEMENT_REFUSAL_NONE;
    }
    if (!eng || !ctx || !out_states || !out_count) {
        return -1;
    }
    for (i = 0u; i < eng->participant_count; ++i) {
        engagement_participant_state* state = &out_states[count++];
        u32 eq_total = 0u;
        u32 j;
        u64 supply_store_ref;

        memset(state, 0, sizeof(*state));
        state->participant = eng->participants[i];
        if (state->participant.role > ENGAGEMENT_ROLE_DEFENDER) {
            if (out_refusal) {
                *out_refusal = ENGAGEMENT_REFUSAL_OBJECTIVE_INVALID;
            }
            return -2;
        }
        state->force = security_force_find(ctx->forces, state->participant.force_id);
        if (!state->force) {
            if (out_refusal) {
                *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
            }
            return -2;
        }
        if (state->force->domain_scope != eng->domain_scope) {
            if (out_refusal) {
                *out_refusal = ENGAGEMENT_REFUSAL_OUT_OF_DOMAIN;
            }
            return -3;
        }
        state->cohort = military_cohort_find(ctx->military, state->force->cohort_ref);
        if (!state->cohort || state->cohort->count == 0u) {
            if (out_refusal) {
                *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
            }
            return -4;
        }
        state->readiness = readiness_find(ctx->readiness, state->force->readiness_state_ref);
        state->morale = morale_find(ctx->morale, state->force->morale_state_ref);
        if (!state->readiness || !state->morale) {
            if (out_refusal) {
                *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
            }
            return -5;
        }
        state->cohort_count = state->cohort->count;
        for (j = 0u; j < state->force->equipment_count; ++j) {
            eq_total += state->force->equipment_qtys[j];
        }
        state->equipment_total = eq_total;
        state->readiness_level = state->readiness->readiness_level;
        state->morale_level = state->morale->morale_level;
        if (state->readiness_level == 0u || state->morale_level == 0u) {
            if (out_refusal) {
                *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
            }
            return -6;
        }
        if (ctx->legitimacy && state->participant.legitimacy_id != 0u) {
            legitimacy_state* legit = legitimacy_find(ctx->legitimacy, state->participant.legitimacy_id);
            if (legit) {
                state->legitimacy_value = legit->value;
                state->has_legitimacy = 1;
            }
        }
        supply_store_ref = state->participant.supply_store_ref;
        if (supply_store_ref == 0u && state->force->logistics_dependency_count > 0u) {
            supply_store_ref = state->force->logistics_dependency_refs[0];
        }
        state->supply_store_ref = supply_store_ref;
        state->supply_shortage = 0;
        if (eng->supply_asset_id != 0u && eng->supply_qty > 0u && supply_store_ref != 0u) {
            u32 available = 0u;
            if (infra_store_get_qty(ctx->stores, supply_store_ref, eng->supply_asset_id, &available) != 0 ||
                available < eng->supply_qty) {
                state->supply_shortage = 1;
            }
        }
    }
    *out_count = count;
    return 0;
}

static u32 engagement_compute_casualties(u32 cohort_count, u64 own_strength, u64 opp_strength, u32 role)
{
    u64 total = own_strength + opp_strength;
    u64 loss_scale;
    u64 casualties;
    if (cohort_count == 0u) {
        return 0u;
    }
    if (total == 0u) {
        return 0u;
    }
    loss_scale = (opp_strength * 1000u) / total;
    casualties = ((u64)cohort_count * loss_scale) / 2000u;
    if (role == ENGAGEMENT_ROLE_ATTACKER) {
        casualties = (casualties * 1100u) / 1000u;
    } else {
        casualties = (casualties * 900u) / 1000u;
    }
    if (casualties > cohort_count) {
        casualties = cohort_count;
    }
    return (u32)casualties;
}

static void engagement_apply_equipment_losses(engagement_outcome* out,
                                              const security_force* force,
                                              u32 casualty_count,
                                              u32 cohort_count)
{
    u32 i;
    if (!out || !force || cohort_count == 0u) {
        return;
    }
    for (i = 0u; i < force->equipment_count; ++i) {
        u64 equipment_id = force->equipment_refs[i];
        u32 qty = force->equipment_qtys[i];
        u32 loss_qty;
        if (equipment_id == 0u || qty == 0u) {
            continue;
        }
        loss_qty = (u32)(((u64)qty * (u64)casualty_count) / (u64)cohort_count);
        if (loss_qty == 0u) {
            continue;
        }
        if (out->equipment_loss_count >= ENGAGEMENT_MAX_EQUIPMENT_LOSSES) {
            continue;
        }
        out->equipment_losses[out->equipment_loss_count].equipment_id = equipment_id;
        out->equipment_losses[out->equipment_loss_count].qty = loss_qty;
        out->equipment_loss_count += 1u;
    }
}

int engagement_resolve(const engagement* eng,
                       engagement_resolution_context* ctx,
                       engagement_outcome* out_outcome,
                       engagement_refusal_code* out_refusal)
{
    engagement_participant_state states[ENGAGEMENT_MAX_PARTICIPANTS];
    u32 count = 0u;
    u32 env_factor;
    u32 i;
    u64 attacker_strength = 0u;
    u64 defender_strength = 0u;
    u32 attacker_cohort = 0u;
    u32 defender_cohort = 0u;
    u64 winner_force_id = 0u;
    u64 loser_force_id = 0u;
    engagement_outcome outcome;
    u32 total_casualties = 0u;
    i32 winner_morale_delta = 0;
    i32 loser_morale_delta = 0;
    i32 winner_legitimacy_delta = 0;
    i32 loser_legitimacy_delta = 0;

    if (out_refusal) {
        *out_refusal = ENGAGEMENT_REFUSAL_NONE;
    }
    if (!eng || !ctx || !out_outcome) {
        return -1;
    }
    if (!ctx->casualty_gen || !ctx->forces || !ctx->military ||
        !ctx->readiness || !ctx->morale) {
        return -1;
    }
    if (eng->status == ENGAGEMENT_STATUS_RESOLVED) {
        if (out_refusal) {
            *out_refusal = ENGAGEMENT_REFUSAL_ALREADY_RESOLVED;
        }
        return -2;
    }
    if (eng->participant_count < 2u || eng->participant_count > ENGAGEMENT_MAX_PARTICIPANTS) {
        if (out_refusal) {
            *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
        }
        return -3;
    }
    if (eng->environment_modifier_count > ENGAGEMENT_MAX_ENV_MODIFIERS) {
        if (out_refusal) {
            *out_refusal = ENGAGEMENT_REFUSAL_OBJECTIVE_INVALID;
        }
        return -3;
    }
    if (eng->objective > ENGAGEMENT_OBJECTIVE_BLOCKADE) {
        if (out_refusal) {
            *out_refusal = ENGAGEMENT_REFUSAL_OBJECTIVE_INVALID;
        }
        return -4;
    }
    if (eng->resolution_act < eng->start_act) {
        if (out_refusal) {
            *out_refusal = ENGAGEMENT_REFUSAL_OBJECTIVE_INVALID;
        }
        return -5;
    }
    if (engagement_collect_participants(eng, ctx, states, &count, out_refusal) != 0) {
        return -6;
    }
    env_factor = engagement_environment_factor(eng);
    for (i = 0u; i < count; ++i) {
        (void)engagement_strength_compute(eng, &states[i], env_factor);
        if (states[i].participant.role == ENGAGEMENT_ROLE_ATTACKER) {
            attacker_strength += states[i].strength;
            attacker_cohort += states[i].cohort_count;
        } else {
            defender_strength += states[i].strength;
            defender_cohort += states[i].cohort_count;
        }
    }

    if (attacker_strength == 0u || defender_strength == 0u ||
        attacker_cohort == 0u || defender_cohort == 0u) {
        if (out_refusal) {
            *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
        }
        return -7;
    }

    if (attacker_strength > defender_strength) {
        u64 diff = attacker_strength - defender_strength;
        if ((diff * 100u) / attacker_strength >= 5u) {
            winner_force_id = engagement_select_force_id_by_role(states, count, ENGAGEMENT_ROLE_ATTACKER);
            loser_force_id = engagement_select_force_id_by_role(states, count, ENGAGEMENT_ROLE_DEFENDER);
        }
    } else if (defender_strength > attacker_strength) {
        u64 diff = defender_strength - attacker_strength;
        if ((diff * 100u) / defender_strength >= 5u) {
            winner_force_id = engagement_select_force_id_by_role(states, count, ENGAGEMENT_ROLE_DEFENDER);
            loser_force_id = engagement_select_force_id_by_role(states, count, ENGAGEMENT_ROLE_ATTACKER);
        }
    }

    memset(&outcome, 0, sizeof(outcome));
    outcome.engagement_id = eng->engagement_id;
    outcome.winner_force_id = winner_force_id;
    outcome.loser_force_id = loser_force_id;
    if (winner_force_id != 0u && loser_force_id != 0u) {
        winner_morale_delta = 50;
        loser_morale_delta = -50;
        winner_legitimacy_delta = 10;
        loser_legitimacy_delta = -10;
        outcome.morale_delta = winner_morale_delta;
        outcome.legitimacy_delta = winner_legitimacy_delta;
    }

    for (i = 0u; i < count; ++i) {
        engagement_participant_state* state = &states[i];
        u64 own_strength = (state->participant.role == ENGAGEMENT_ROLE_ATTACKER) ? attacker_strength : defender_strength;
        u64 opp_strength = (state->participant.role == ENGAGEMENT_ROLE_ATTACKER) ? defender_strength : attacker_strength;
        u32 casualties = engagement_compute_casualties(state->cohort_count, own_strength, opp_strength,
                                                       state->participant.role);
        if (state->supply_shortage) {
            u32 penalty = state->readiness ? state->readiness->degradation_rate : 50u;
            u32 extra = (casualties + penalty) / 20u;
            if (extra > 0u) {
                if (casualties + extra > state->cohort_count) {
                    casualties = state->cohort_count;
                } else {
                    casualties += extra;
                }
            }
        }
        if (casualties > 0u) {
            engagement_casualty_source* source = engagement_find_casualty_source(ctx, state->participant.force_id);
            casualty_request req;
            life_death_refusal_code death_refusal;
            u32 produced = 0u;
            if (!source) {
                if (out_refusal) {
                    *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
                }
                return -8;
            }
            req = ctx->casualty_config;
            req.act_time = eng->resolution_act;
            if (req.cause_code == 0u) {
                req.cause_code = LIFE_DEATH_CAUSE_VIOLENCE;
            }
            req.provenance_ref = eng->provenance_ref ? eng->provenance_ref : eng->engagement_id;
            if (casualty_generate(ctx->casualty_gen,
                                  &source->source,
                                  casualties,
                                  &req,
                                  &outcome.casualty_event_ids[total_casualties],
                                  ENGAGEMENT_MAX_CASUALTIES - total_casualties,
                                  &produced,
                                  &death_refusal) != 0) {
                if (out_refusal) {
                    *out_refusal = ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY;
                }
                return -9;
            }
            total_casualties += produced;
            outcome.casualty_count = total_casualties;
            (void)military_cohort_adjust_count(ctx->military, state->cohort->cohort_id,
                                               -(i32)produced, 0);
            engagement_apply_equipment_losses(&outcome, state->force, casualties, state->cohort_count);
            {
                engagement_equipment_loss local_losses[ENGAGEMENT_MAX_EQUIPMENT_LOSSES];
                u32 loss_count = 0u;
                u32 j;
                memset(local_losses, 0, sizeof(local_losses));
                for (j = 0u; j < state->force->equipment_count; ++j) {
                    u64 equipment_id = state->force->equipment_refs[j];
                    u32 qty = state->force->equipment_qtys[j];
                    u32 loss_qty;
                    if (equipment_id == 0u || qty == 0u) {
                        continue;
                    }
                    loss_qty = (u32)(((u64)qty * (u64)casualties) / (u64)state->cohort_count);
                    if (loss_qty == 0u) {
                        continue;
                    }
                    if (loss_count < ENGAGEMENT_MAX_EQUIPMENT_LOSSES) {
                        local_losses[loss_count].equipment_id = equipment_id;
                        local_losses[loss_count].qty = loss_qty;
                        loss_count += 1u;
                    }
                }
                (void)loss_accounting_apply_equipment_losses(state->force, local_losses, loss_count);
            }
        }
    }

    for (i = 0u; i < count; ++i) {
        engagement_participant_state* state = &states[i];
        i32 morale_delta = 0;
        i32 legitimacy_delta = 0;
        if (winner_force_id != 0u && loser_force_id != 0u) {
            if ((winner_force_id == engagement_select_force_id_by_role(states, count, state->participant.role))) {
                morale_delta = winner_morale_delta;
                legitimacy_delta = winner_legitimacy_delta;
            } else {
                morale_delta = loser_morale_delta;
                legitimacy_delta = loser_legitimacy_delta;
            }
        }
        if (state->supply_shortage) {
            morale_delta -= 25;
            (void)loss_accounting_apply_readiness(ctx->readiness,
                                                  state->readiness->readiness_id,
                                                  -(i32)state->readiness->degradation_rate,
                                                  eng->resolution_act);
        }
        if (state->has_legitimacy) {
            u32 threshold = LEGITIMACY_SCALE / 2u;
            if (state->legitimacy_value < threshold) {
                u32 shortfall = threshold - state->legitimacy_value;
                i32 penalty = (i32)(shortfall / 10u);
                if (penalty > 50) {
                    penalty = 50;
                }
                morale_delta -= penalty;
            }
        }
        (void)loss_accounting_apply_morale(ctx->morale, state->morale->morale_id, morale_delta);
        if (state->participant.legitimacy_id != 0u) {
            (void)loss_accounting_apply_legitimacy(ctx->legitimacy,
                                                   state->participant.legitimacy_id,
                                                   legitimacy_delta);
        }
    }

    if (eng->supply_asset_id != 0u && eng->supply_qty > 0u) {
        for (i = 0u; i < count; ++i) {
            engagement_participant_state* state = &states[i];
            if (state->supply_store_ref == 0u) {
                continue;
            }
            if (infra_store_consume(ctx->stores,
                                    state->supply_store_ref,
                                    eng->supply_asset_id,
                                    eng->supply_qty) == 0) {
                outcome.logistics_consumed += eng->supply_qty;
            }
        }
    }

    outcome.provenance_summary = engagement_hash_mix(eng->engagement_id,
                                                     (u64)outcome.casualty_count);
    *out_outcome = outcome;
    if (ctx->outcomes) {
        (void)engagement_outcome_append(ctx->outcomes, &outcome, 0);
    }
    return 0;
}

int engagement_outcome_estimate_from_view(const dom_epistemic_view* view,
                                          const engagement_outcome* outcome,
                                          engagement_outcome_summary* out_summary)
{
    int is_known = 0;
    i32 morale_shift;
    i32 legitimacy_shift;
    if (!outcome || !out_summary) {
        return -1;
    }
    if (view && view->state == DOM_EPI_KNOWN && !view->is_uncertain) {
        is_known = 1;
    }
    if (is_known) {
        out_summary->casualty_count = outcome->casualty_count;
        out_summary->equipment_loss_count = outcome->equipment_loss_count;
        out_summary->morale_delta = outcome->morale_delta;
        out_summary->legitimacy_delta = outcome->legitimacy_delta;
        out_summary->uncertainty_q16 = view ? view->uncertainty_q16 : 0u;
        out_summary->is_exact = 1;
        return 0;
    }
    out_summary->casualty_count = engagement_bucket_u32(outcome->casualty_count, 5u);
    out_summary->equipment_loss_count = engagement_bucket_u32(outcome->equipment_loss_count, 2u);
    morale_shift = outcome->morale_delta + 100;
    if (morale_shift < 0) {
        morale_shift = 0;
    }
    if (morale_shift > 200) {
        morale_shift = 200;
    }
    legitimacy_shift = outcome->legitimacy_delta + 100;
    if (legitimacy_shift < 0) {
        legitimacy_shift = 0;
    }
    if (legitimacy_shift > 200) {
        legitimacy_shift = 200;
    }
    out_summary->morale_delta = (i32)engagement_bucket_u32((u32)morale_shift, 10u) - 100;
    out_summary->legitimacy_delta = (i32)engagement_bucket_u32((u32)legitimacy_shift, 10u) - 100;
    out_summary->uncertainty_q16 = view ? view->uncertainty_q16 : 0xFFFFu;
    out_summary->is_exact = 0;
    return 0;
}
