/*
FILE: source/domino/world/conflict_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/conflict_fields
RESPONSIBILITY: Implements deterministic conflict, engagement, occupation, and morale resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/conflict_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_CONFLICT_RESOLVE_COST_BASE 1u
#define DOM_CONFLICT_RATIO_HALF_Q16 ((q16_16)0x00008000)
#define DOM_CONFLICT_MORALE_LOW_Q16 ((q16_16)0x00004000)
#define DOM_CONFLICT_READINESS_LOW_Q16 ((q16_16)0x00004000)
#define DOM_CONFLICT_LEGITIMACY_LOW_Q16 ((q16_16)0x00004000)

static q16_16 dom_conflict_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_CONFLICT_RATIO_ONE_Q16) {
        return DOM_CONFLICT_RATIO_ONE_Q16;
    }
    return value;
}

static void dom_conflict_record_init(dom_conflict_record* record)
{
    if (!record) {
        return;
    }
    memset(record, 0, sizeof(*record));
    record->status = DOM_CONFLICT_STATUS_UNSET;
}

static void dom_conflict_side_init(dom_conflict_side* side)
{
    if (!side) {
        return;
    }
    memset(side, 0, sizeof(*side));
}

static void dom_conflict_event_init(dom_conflict_event* event)
{
    if (!event) {
        return;
    }
    memset(event, 0, sizeof(*event));
    event->event_type = DOM_CONFLICT_EVENT_UNSET;
}

static void dom_conflict_force_init(dom_security_force* force)
{
    if (!force) {
        return;
    }
    memset(force, 0, sizeof(*force));
    force->force_type = DOM_CONFLICT_FORCE_UNSET;
}

static void dom_conflict_engagement_init(dom_engagement* engagement)
{
    if (!engagement) {
        return;
    }
    memset(engagement, 0, sizeof(*engagement));
}

static void dom_conflict_outcome_init(dom_engagement_outcome* outcome)
{
    if (!outcome) {
        return;
    }
    memset(outcome, 0, sizeof(*outcome));
}

static void dom_conflict_occupation_init(dom_occupation_condition* occupation)
{
    if (!occupation) {
        return;
    }
    memset(occupation, 0, sizeof(*occupation));
    occupation->status = DOM_CONFLICT_OCCUPATION_UNSET;
}

static void dom_conflict_resistance_init(dom_resistance_event* resistance)
{
    if (!resistance) {
        return;
    }
    memset(resistance, 0, sizeof(*resistance));
    resistance->trigger_reason = DOM_CONFLICT_RESIST_UNSET;
}

static void dom_conflict_morale_init(dom_morale_field* morale)
{
    if (!morale) {
        return;
    }
    memset(morale, 0, sizeof(*morale));
}

static void dom_conflict_weapon_init(dom_weapon_spec* weapon)
{
    if (!weapon) {
        return;
    }
    memset(weapon, 0, sizeof(*weapon));
}

static int dom_conflict_find_record_index(const dom_conflict_domain* domain, u32 conflict_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->conflict_count; ++i) {
        if (domain->conflicts[i].conflict_id == conflict_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_side_index(const dom_conflict_domain* domain, u32 side_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->side_count; ++i) {
        if (domain->sides[i].side_id == side_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_event_index(const dom_conflict_domain* domain, u32 event_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->event_count; ++i) {
        if (domain->events[i].event_id == event_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_force_index(const dom_conflict_domain* domain, u32 force_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->force_count; ++i) {
        if (domain->forces[i].force_id == force_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_engagement_index(const dom_conflict_domain* domain, u32 engagement_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->engagement_count; ++i) {
        if (domain->engagements[i].engagement_id == engagement_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_outcome_index(const dom_conflict_domain* domain, u32 outcome_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->outcome_count; ++i) {
        if (domain->outcomes[i].outcome_id == outcome_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_occupation_index(const dom_conflict_domain* domain, u32 occupation_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->occupation_count; ++i) {
        if (domain->occupations[i].occupation_id == occupation_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_resistance_index(const dom_conflict_domain* domain, u32 resistance_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->resistance_count; ++i) {
        if (domain->resistance_events[i].resistance_id == resistance_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_morale_index(const dom_conflict_domain* domain, u32 morale_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->morale_count; ++i) {
        if (domain->morale_fields[i].morale_id == morale_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_conflict_find_weapon_index(const dom_conflict_domain* domain, u32 weapon_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->weapon_count; ++i) {
        if (domain->weapons[i].weapon_id == weapon_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_conflict_domain_is_active(const dom_conflict_domain* domain)
{
    if (!domain) {
        return D_FALSE;
    }
    if (domain->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        domain->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED) {
        return D_FALSE;
    }
    return D_TRUE;
}

static d_bool dom_conflict_region_collapsed(const dom_conflict_domain* domain, u32 region_id)
{
    if (!domain || region_id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static const dom_conflict_macro_capsule* dom_conflict_find_capsule(const dom_conflict_domain* domain,
                                                                   u32 region_id)
{
    if (!domain) {
        return (const dom_conflict_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_conflict_macro_capsule*)0;
}

static void dom_conflict_query_meta_refused(dom_domain_query_meta* meta,
                                            u32 reason,
                                            const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_REFUSED;
    meta->resolution = DOM_DOMAIN_RES_REFUSED;
    meta->confidence = DOM_DOMAIN_CONFIDENCE_UNKNOWN;
    meta->refusal_reason = reason;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static void dom_conflict_query_meta_ok(dom_domain_query_meta* meta,
                                       u32 resolution,
                                       u32 confidence,
                                       u32 cost_units,
                                       const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_OK;
    meta->resolution = resolution;
    meta->confidence = confidence;
    meta->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    meta->cost_units = cost_units;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static u32 dom_conflict_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_CONFLICT_RESOLVE_COST_BASE : cost_units;
}

static d_bool dom_conflict_apply_morale_decay(dom_morale_field* field, u64 tick_delta)
{
    q16_16 decay_per_tick;
    q48_16 decay_total;
    q16_16 decay_q16;
    if (!field || tick_delta == 0u) {
        return D_FALSE;
    }
    if (field->decay_rate <= 0 || field->morale_level <= 0) {
        return D_FALSE;
    }
    decay_per_tick = d_q16_16_mul(field->morale_level, field->decay_rate);
    if (decay_per_tick <= 0) {
        return D_FALSE;
    }
    decay_total = d_q48_16_from_q16_16(decay_per_tick);
    if (tick_delta > 1u) {
        decay_total = d_q48_16_mul(decay_total, d_q48_16_from_int((i64)tick_delta));
    }
    decay_q16 = d_q16_16_from_q48_16(decay_total);
    if (decay_q16 <= 0) {
        return D_FALSE;
    }
    if (decay_q16 >= field->morale_level) {
        field->morale_level = 0;
    } else {
        field->morale_level = d_q16_16_sub(field->morale_level, decay_q16);
    }
    return D_TRUE;
}

static d_bool dom_conflict_apply_event(dom_conflict_domain* domain,
                                       dom_conflict_event* event,
                                       u64 tick,
                                       u32* out_resistance,
                                       u32* out_attrition)
{
    int record_index;
    if (!domain || !event) {
        return D_FALSE;
    }
    if (event->flags & DOM_CONFLICT_EVENT_APPLIED) {
        return D_FALSE;
    }
    if (event->scheduled_tick > tick) {
        return D_FALSE;
    }
    event->flags |= DOM_CONFLICT_EVENT_APPLIED;

    record_index = dom_conflict_find_record_index(domain, event->conflict_id);
    if (record_index >= 0) {
        dom_conflict_record* record = &domain->conflicts[record_index];
        if (event->event_type == DOM_CONFLICT_EVENT_MOBILIZATION ||
            event->event_type == DOM_CONFLICT_EVENT_DEPLOYMENT ||
            event->event_type == DOM_CONFLICT_EVENT_ENGAGEMENT_RESOLUTION ||
            event->event_type == DOM_CONFLICT_EVENT_OCCUPATION) {
            record->status = DOM_CONFLICT_STATUS_ACTIVE;
        }
        if (event->event_type == DOM_CONFLICT_EVENT_DEMOBILIZATION) {
            record->status = DOM_CONFLICT_STATUS_RESOLVED;
        }
    }

    if (event->event_type == DOM_CONFLICT_EVENT_RESISTANCE) {
        if (out_resistance) {
            *out_resistance += 1u;
        }
    }
    if (event->event_type == DOM_CONFLICT_EVENT_ATTRITION ||
        event->event_type == DOM_CONFLICT_EVENT_SABOTAGE) {
        if (out_attrition) {
            *out_attrition += 1u;
        }
    }
    return D_TRUE;
}

static q16_16 dom_conflict_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_conflict_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_conflict_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_CONFLICT_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_CONFLICT_HIST_BINS) {
        scaled = DOM_CONFLICT_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_conflict_surface_desc_init(dom_conflict_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
}

void dom_conflict_domain_init(dom_conflict_domain* domain,
                              const dom_conflict_surface_desc* desc)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    domain->surface = *desc;
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;

    domain->conflict_count = (desc->conflict_count > DOM_CONFLICT_MAX_CONFLICTS)
                               ? DOM_CONFLICT_MAX_CONFLICTS
                               : desc->conflict_count;
    domain->side_count = (desc->side_count > DOM_CONFLICT_MAX_SIDES)
                           ? DOM_CONFLICT_MAX_SIDES
                           : desc->side_count;
    domain->event_count = (desc->event_count > DOM_CONFLICT_MAX_EVENTS)
                            ? DOM_CONFLICT_MAX_EVENTS
                            : desc->event_count;
    domain->force_count = (desc->force_count > DOM_CONFLICT_MAX_FORCES)
                            ? DOM_CONFLICT_MAX_FORCES
                            : desc->force_count;
    domain->engagement_count = (desc->engagement_count > DOM_CONFLICT_MAX_ENGAGEMENTS)
                                 ? DOM_CONFLICT_MAX_ENGAGEMENTS
                                 : desc->engagement_count;
    domain->outcome_count = (desc->outcome_count > DOM_CONFLICT_MAX_OUTCOMES)
                              ? DOM_CONFLICT_MAX_OUTCOMES
                              : desc->outcome_count;
    domain->occupation_count = (desc->occupation_count > DOM_CONFLICT_MAX_OCCUPATIONS)
                                 ? DOM_CONFLICT_MAX_OCCUPATIONS
                                 : desc->occupation_count;
    domain->resistance_count = (desc->resistance_count > DOM_CONFLICT_MAX_RESISTANCE)
                                 ? DOM_CONFLICT_MAX_RESISTANCE
                                 : desc->resistance_count;
    domain->morale_count = (desc->morale_count > DOM_CONFLICT_MAX_MORALE)
                             ? DOM_CONFLICT_MAX_MORALE
                             : desc->morale_count;
    domain->weapon_count = (desc->weapon_count > DOM_CONFLICT_MAX_WEAPONS)
                             ? DOM_CONFLICT_MAX_WEAPONS
                             : desc->weapon_count;

    for (u32 i = 0u; i < domain->conflict_count; ++i) {
        dom_conflict_record_init(&domain->conflicts[i]);
        domain->conflicts[i].conflict_id = desc->conflicts[i].conflict_id;
        domain->conflicts[i].domain_id = desc->conflicts[i].domain_id;
        domain->conflicts[i].side_count = desc->conflicts[i].side_count;
        memcpy(domain->conflicts[i].side_ids, desc->conflicts[i].side_ids,
               sizeof(desc->conflicts[i].side_ids));
        domain->conflicts[i].start_tick = desc->conflicts[i].start_tick;
        domain->conflicts[i].status = desc->conflicts[i].status;
        domain->conflicts[i].next_due_tick = desc->conflicts[i].next_due_tick;
        domain->conflicts[i].event_count = desc->conflicts[i].event_count;
        memcpy(domain->conflicts[i].event_ids, desc->conflicts[i].event_ids,
               sizeof(desc->conflicts[i].event_ids));
        domain->conflicts[i].provenance_id = desc->conflicts[i].provenance_id;
        domain->conflicts[i].epistemic_scope_id = desc->conflicts[i].epistemic_scope_id;
        domain->conflicts[i].region_id = desc->conflicts[i].region_id;
        domain->conflicts[i].order_key = desc->conflicts[i].order_key;
        domain->conflicts[i].flags = DOM_CONFLICT_RECORD_UNRESOLVED;
    }

    for (u32 i = 0u; i < domain->side_count; ++i) {
        dom_conflict_side_init(&domain->sides[i]);
        domain->sides[i].side_id = desc->sides[i].side_id;
        domain->sides[i].conflict_id = desc->sides[i].conflict_id;
        domain->sides[i].authority_id = desc->sides[i].authority_id;
        domain->sides[i].force_count = desc->sides[i].force_count;
        memcpy(domain->sides[i].force_ids, desc->sides[i].force_ids,
               sizeof(desc->sides[i].force_ids));
        domain->sides[i].objectives_ref_id = desc->sides[i].objectives_ref_id;
        domain->sides[i].logistics_dependency_id = desc->sides[i].logistics_dependency_id;
        domain->sides[i].readiness_level = desc->sides[i].readiness_level;
        domain->sides[i].readiness_state = desc->sides[i].readiness_state;
        domain->sides[i].next_due_tick = desc->sides[i].next_due_tick;
        domain->sides[i].provenance_id = desc->sides[i].provenance_id;
        domain->sides[i].region_id = desc->sides[i].region_id;
        domain->sides[i].flags = DOM_CONFLICT_SIDE_UNRESOLVED;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_conflict_event_init(&domain->events[i]);
        domain->events[i].event_id = desc->events[i].event_id;
        domain->events[i].conflict_id = desc->events[i].conflict_id;
        domain->events[i].event_type = desc->events[i].event_type;
        domain->events[i].scheduled_tick = desc->events[i].scheduled_tick;
        domain->events[i].order_key = desc->events[i].order_key;
        domain->events[i].participant_count = desc->events[i].participant_count;
        memcpy(domain->events[i].participant_force_ids,
               desc->events[i].participant_force_ids,
               sizeof(desc->events[i].participant_force_ids));
        domain->events[i].input_ref_count = desc->events[i].input_ref_count;
        memcpy(domain->events[i].input_refs, desc->events[i].input_refs,
               sizeof(desc->events[i].input_refs));
        domain->events[i].output_ref_count = desc->events[i].output_ref_count;
        memcpy(domain->events[i].output_refs, desc->events[i].output_refs,
               sizeof(desc->events[i].output_refs));
        domain->events[i].provenance_id = desc->events[i].provenance_id;
        domain->events[i].epistemic_scope_id = desc->events[i].epistemic_scope_id;
        domain->events[i].region_id = desc->events[i].region_id;
        domain->events[i].flags = desc->events[i].flags;
    }

    for (u32 i = 0u; i < domain->force_count; ++i) {
        dom_conflict_force_init(&domain->forces[i]);
        domain->forces[i].force_id = desc->forces[i].force_id;
        domain->forces[i].authority_id = desc->forces[i].authority_id;
        domain->forces[i].force_type = desc->forces[i].force_type;
        domain->forces[i].capacity = desc->forces[i].capacity;
        domain->forces[i].equipment_count = desc->forces[i].equipment_count;
        memcpy(domain->forces[i].equipment_refs, desc->forces[i].equipment_refs,
               sizeof(desc->forces[i].equipment_refs));
        domain->forces[i].readiness = desc->forces[i].readiness;
        domain->forces[i].morale = desc->forces[i].morale;
        domain->forces[i].logistics_dependency_id = desc->forces[i].logistics_dependency_id;
        domain->forces[i].home_domain_id = desc->forces[i].home_domain_id;
        domain->forces[i].next_due_tick = desc->forces[i].next_due_tick;
        domain->forces[i].provenance_id = desc->forces[i].provenance_id;
        domain->forces[i].region_id = desc->forces[i].region_id;
        domain->forces[i].flags = desc->forces[i].flags;
    }

    for (u32 i = 0u; i < domain->engagement_count; ++i) {
        dom_conflict_engagement_init(&domain->engagements[i]);
        domain->engagements[i].engagement_id = desc->engagements[i].engagement_id;
        domain->engagements[i].conflict_id = desc->engagements[i].conflict_id;
        domain->engagements[i].domain_id = desc->engagements[i].domain_id;
        domain->engagements[i].participant_count = desc->engagements[i].participant_count;
        memcpy(domain->engagements[i].participant_force_ids,
               desc->engagements[i].participant_force_ids,
               sizeof(desc->engagements[i].participant_force_ids));
        domain->engagements[i].start_tick = desc->engagements[i].start_tick;
        domain->engagements[i].resolution_tick = desc->engagements[i].resolution_tick;
        domain->engagements[i].resolution_policy_id = desc->engagements[i].resolution_policy_id;
        domain->engagements[i].order_key = desc->engagements[i].order_key;
        domain->engagements[i].logistics_count = desc->engagements[i].logistics_count;
        memcpy(domain->engagements[i].logistics_inputs,
               desc->engagements[i].logistics_inputs,
               sizeof(desc->engagements[i].logistics_inputs));
        domain->engagements[i].legitimacy_scope_id = desc->engagements[i].legitimacy_scope_id;
        domain->engagements[i].epistemic_scope_id = desc->engagements[i].epistemic_scope_id;
        domain->engagements[i].provenance_id = desc->engagements[i].provenance_id;
        domain->engagements[i].region_id = desc->engagements[i].region_id;
        domain->engagements[i].flags = desc->engagements[i].flags;
    }

    for (u32 i = 0u; i < domain->outcome_count; ++i) {
        dom_conflict_outcome_init(&domain->outcomes[i]);
        domain->outcomes[i].outcome_id = desc->outcomes[i].outcome_id;
        domain->outcomes[i].engagement_id = desc->outcomes[i].engagement_id;
        domain->outcomes[i].casualty_count = desc->outcomes[i].casualty_count;
        memcpy(domain->outcomes[i].casualty_refs, desc->outcomes[i].casualty_refs,
               sizeof(desc->outcomes[i].casualty_refs));
        domain->outcomes[i].resource_delta_count = desc->outcomes[i].resource_delta_count;
        memcpy(domain->outcomes[i].resource_deltas, desc->outcomes[i].resource_deltas,
               sizeof(desc->outcomes[i].resource_deltas));
        domain->outcomes[i].legitimacy_delta_count = desc->outcomes[i].legitimacy_delta_count;
        memcpy(domain->outcomes[i].legitimacy_deltas, desc->outcomes[i].legitimacy_deltas,
               sizeof(desc->outcomes[i].legitimacy_deltas));
        domain->outcomes[i].control_delta_count = desc->outcomes[i].control_delta_count;
        memcpy(domain->outcomes[i].control_deltas, desc->outcomes[i].control_deltas,
               sizeof(desc->outcomes[i].control_deltas));
        domain->outcomes[i].report_count = desc->outcomes[i].report_count;
        memcpy(domain->outcomes[i].report_refs, desc->outcomes[i].report_refs,
               sizeof(desc->outcomes[i].report_refs));
        domain->outcomes[i].provenance_id = desc->outcomes[i].provenance_id;
        domain->outcomes[i].region_id = desc->outcomes[i].region_id;
        domain->outcomes[i].flags = desc->outcomes[i].flags;
    }

    for (u32 i = 0u; i < domain->occupation_count; ++i) {
        dom_conflict_occupation_init(&domain->occupations[i]);
        domain->occupations[i].occupation_id = desc->occupations[i].occupation_id;
        domain->occupations[i].occupier_authority_id = desc->occupations[i].occupier_authority_id;
        domain->occupations[i].occupied_jurisdiction_id = desc->occupations[i].occupied_jurisdiction_id;
        domain->occupations[i].enforcement_capacity = desc->occupations[i].enforcement_capacity;
        domain->occupations[i].legitimacy_support = desc->occupations[i].legitimacy_support;
        domain->occupations[i].logistics_dependency_id = desc->occupations[i].logistics_dependency_id;
        domain->occupations[i].start_tick = desc->occupations[i].start_tick;
        domain->occupations[i].next_due_tick = desc->occupations[i].next_due_tick;
        domain->occupations[i].status = desc->occupations[i].status;
        domain->occupations[i].provenance_id = desc->occupations[i].provenance_id;
        domain->occupations[i].region_id = desc->occupations[i].region_id;
        domain->occupations[i].flags = desc->occupations[i].flags;
    }

    for (u32 i = 0u; i < domain->resistance_count; ++i) {
        dom_conflict_resistance_init(&domain->resistance_events[i]);
        domain->resistance_events[i].resistance_id = desc->resistance_events[i].resistance_id;
        domain->resistance_events[i].occupation_id = desc->resistance_events[i].occupation_id;
        domain->resistance_events[i].trigger_reason = desc->resistance_events[i].trigger_reason;
        domain->resistance_events[i].trigger_tick = desc->resistance_events[i].trigger_tick;
        domain->resistance_events[i].resolution_tick = desc->resistance_events[i].resolution_tick;
        domain->resistance_events[i].order_key = desc->resistance_events[i].order_key;
        domain->resistance_events[i].outcome_count = desc->resistance_events[i].outcome_count;
        memcpy(domain->resistance_events[i].outcome_refs,
               desc->resistance_events[i].outcome_refs,
               sizeof(desc->resistance_events[i].outcome_refs));
        domain->resistance_events[i].provenance_id = desc->resistance_events[i].provenance_id;
        domain->resistance_events[i].region_id = desc->resistance_events[i].region_id;
        domain->resistance_events[i].flags = desc->resistance_events[i].flags;
    }

    for (u32 i = 0u; i < domain->morale_count; ++i) {
        dom_conflict_morale_init(&domain->morale_fields[i]);
        domain->morale_fields[i].morale_id = desc->morale_fields[i].morale_id;
        domain->morale_fields[i].subject_ref_id = desc->morale_fields[i].subject_ref_id;
        domain->morale_fields[i].conflict_id = desc->morale_fields[i].conflict_id;
        domain->morale_fields[i].morale_level = desc->morale_fields[i].morale_level;
        domain->morale_fields[i].decay_rate = desc->morale_fields[i].decay_rate;
        domain->morale_fields[i].influence_count = desc->morale_fields[i].influence_count;
        memcpy(domain->morale_fields[i].influence_refs, desc->morale_fields[i].influence_refs,
               sizeof(desc->morale_fields[i].influence_refs));
        domain->morale_fields[i].provenance_id = desc->morale_fields[i].provenance_id;
        domain->morale_fields[i].region_id = desc->morale_fields[i].region_id;
        domain->morale_fields[i].flags = desc->morale_fields[i].flags;
    }

    for (u32 i = 0u; i < domain->weapon_count; ++i) {
        dom_conflict_weapon_init(&domain->weapons[i]);
        domain->weapons[i].weapon_id = desc->weapons[i].weapon_id;
        domain->weapons[i].assembly_ref_id = desc->weapons[i].assembly_ref_id;
        domain->weapons[i].range = desc->weapons[i].range;
        domain->weapons[i].rate = desc->weapons[i].rate;
        domain->weapons[i].effectiveness = desc->weapons[i].effectiveness;
        domain->weapons[i].reliability = desc->weapons[i].reliability;
        domain->weapons[i].energy_cost = desc->weapons[i].energy_cost;
        domain->weapons[i].material_interaction_ref_id = desc->weapons[i].material_interaction_ref_id;
        domain->weapons[i].provenance_id = desc->weapons[i].provenance_id;
        domain->weapons[i].flags = desc->weapons[i].flags;
    }

    domain->capsule_count = 0u;
}

void dom_conflict_domain_free(dom_conflict_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->conflict_count = 0u;
    domain->side_count = 0u;
    domain->event_count = 0u;
    domain->force_count = 0u;
    domain->engagement_count = 0u;
    domain->outcome_count = 0u;
    domain->occupation_count = 0u;
    domain->resistance_count = 0u;
    domain->morale_count = 0u;
    domain->weapon_count = 0u;
    domain->capsule_count = 0u;
}

void dom_conflict_domain_set_state(dom_conflict_domain* domain,
                                   u32 existence_state,
                                   u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_conflict_domain_set_policy(dom_conflict_domain* domain,
                                    const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_conflict_record_query(const dom_conflict_domain* domain,
                              u32 conflict_id,
                              dom_domain_budget* budget,
                              dom_conflict_record_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_CONFLICT_RECORD_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_record_index(domain, conflict_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->conflicts[index].region_id)) {
        out_sample->conflict_id = domain->conflicts[index].conflict_id;
        out_sample->domain_id = domain->conflicts[index].domain_id;
        out_sample->region_id = domain->conflicts[index].region_id;
        out_sample->flags = DOM_CONFLICT_RECORD_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->conflict_id = domain->conflicts[index].conflict_id;
    out_sample->domain_id = domain->conflicts[index].domain_id;
    out_sample->side_count = domain->conflicts[index].side_count;
    memcpy(out_sample->side_ids, domain->conflicts[index].side_ids,
           sizeof(out_sample->side_ids));
    out_sample->start_tick = domain->conflicts[index].start_tick;
    out_sample->status = domain->conflicts[index].status;
    out_sample->next_due_tick = domain->conflicts[index].next_due_tick;
    out_sample->event_count = domain->conflicts[index].event_count;
    memcpy(out_sample->event_ids, domain->conflicts[index].event_ids,
           sizeof(out_sample->event_ids));
    out_sample->provenance_id = domain->conflicts[index].provenance_id;
    out_sample->epistemic_scope_id = domain->conflicts[index].epistemic_scope_id;
    out_sample->region_id = domain->conflicts[index].region_id;
    out_sample->order_key = domain->conflicts[index].order_key;
    out_sample->flags = domain->conflicts[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_conflict_side_query(const dom_conflict_domain* domain,
                            u32 side_id,
                            dom_domain_budget* budget,
                            dom_conflict_side_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_CONFLICT_SIDE_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_side_index(domain, side_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->sides[index].region_id)) {
        out_sample->side_id = domain->sides[index].side_id;
        out_sample->conflict_id = domain->sides[index].conflict_id;
        out_sample->region_id = domain->sides[index].region_id;
        out_sample->flags = DOM_CONFLICT_SIDE_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->side_id = domain->sides[index].side_id;
    out_sample->conflict_id = domain->sides[index].conflict_id;
    out_sample->authority_id = domain->sides[index].authority_id;
    out_sample->force_count = domain->sides[index].force_count;
    memcpy(out_sample->force_ids, domain->sides[index].force_ids,
           sizeof(out_sample->force_ids));
    out_sample->objectives_ref_id = domain->sides[index].objectives_ref_id;
    out_sample->logistics_dependency_id = domain->sides[index].logistics_dependency_id;
    out_sample->readiness_level = domain->sides[index].readiness_level;
    out_sample->readiness_state = domain->sides[index].readiness_state;
    out_sample->next_due_tick = domain->sides[index].next_due_tick;
    out_sample->provenance_id = domain->sides[index].provenance_id;
    out_sample->region_id = domain->sides[index].region_id;
    out_sample->flags = domain->sides[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_conflict_event_query(const dom_conflict_domain* domain,
                             u32 event_id,
                             dom_domain_budget* budget,
                             dom_conflict_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_CONFLICT_EVENT_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_event_index(domain, event_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->events[index].region_id)) {
        out_sample->event_id = domain->events[index].event_id;
        out_sample->conflict_id = domain->events[index].conflict_id;
        out_sample->region_id = domain->events[index].region_id;
        out_sample->flags = DOM_CONFLICT_EVENT_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->event_id = domain->events[index].event_id;
    out_sample->conflict_id = domain->events[index].conflict_id;
    out_sample->event_type = domain->events[index].event_type;
    out_sample->scheduled_tick = domain->events[index].scheduled_tick;
    out_sample->order_key = domain->events[index].order_key;
    out_sample->participant_count = domain->events[index].participant_count;
    memcpy(out_sample->participant_force_ids, domain->events[index].participant_force_ids,
           sizeof(out_sample->participant_force_ids));
    out_sample->input_ref_count = domain->events[index].input_ref_count;
    memcpy(out_sample->input_refs, domain->events[index].input_refs,
           sizeof(out_sample->input_refs));
    out_sample->output_ref_count = domain->events[index].output_ref_count;
    memcpy(out_sample->output_refs, domain->events[index].output_refs,
           sizeof(out_sample->output_refs));
    out_sample->provenance_id = domain->events[index].provenance_id;
    out_sample->epistemic_scope_id = domain->events[index].epistemic_scope_id;
    out_sample->region_id = domain->events[index].region_id;
    out_sample->flags = domain->events[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_security_force_query(const dom_conflict_domain* domain,
                             u32 force_id,
                             dom_domain_budget* budget,
                             dom_security_force_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_CONFLICT_FORCE_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_force_index(domain, force_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->forces[index].region_id)) {
        out_sample->force_id = domain->forces[index].force_id;
        out_sample->region_id = domain->forces[index].region_id;
        out_sample->flags = DOM_CONFLICT_FORCE_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->force_id = domain->forces[index].force_id;
    out_sample->authority_id = domain->forces[index].authority_id;
    out_sample->force_type = domain->forces[index].force_type;
    out_sample->capacity = domain->forces[index].capacity;
    out_sample->equipment_count = domain->forces[index].equipment_count;
    memcpy(out_sample->equipment_refs, domain->forces[index].equipment_refs,
           sizeof(out_sample->equipment_refs));
    out_sample->readiness = domain->forces[index].readiness;
    out_sample->morale = domain->forces[index].morale;
    out_sample->logistics_dependency_id = domain->forces[index].logistics_dependency_id;
    out_sample->home_domain_id = domain->forces[index].home_domain_id;
    out_sample->next_due_tick = domain->forces[index].next_due_tick;
    out_sample->provenance_id = domain->forces[index].provenance_id;
    out_sample->region_id = domain->forces[index].region_id;
    out_sample->flags = domain->forces[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_engagement_query(const dom_conflict_domain* domain,
                         u32 engagement_id,
                         dom_domain_budget* budget,
                         dom_engagement_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ENGAGEMENT_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_engagement_index(domain, engagement_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->engagements[index].region_id)) {
        out_sample->engagement_id = domain->engagements[index].engagement_id;
        out_sample->region_id = domain->engagements[index].region_id;
        out_sample->flags = DOM_ENGAGEMENT_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->engagement_id = domain->engagements[index].engagement_id;
    out_sample->conflict_id = domain->engagements[index].conflict_id;
    out_sample->domain_id = domain->engagements[index].domain_id;
    out_sample->participant_count = domain->engagements[index].participant_count;
    memcpy(out_sample->participant_force_ids, domain->engagements[index].participant_force_ids,
           sizeof(out_sample->participant_force_ids));
    out_sample->start_tick = domain->engagements[index].start_tick;
    out_sample->resolution_tick = domain->engagements[index].resolution_tick;
    out_sample->resolution_policy_id = domain->engagements[index].resolution_policy_id;
    out_sample->order_key = domain->engagements[index].order_key;
    out_sample->logistics_count = domain->engagements[index].logistics_count;
    memcpy(out_sample->logistics_inputs, domain->engagements[index].logistics_inputs,
           sizeof(out_sample->logistics_inputs));
    out_sample->legitimacy_scope_id = domain->engagements[index].legitimacy_scope_id;
    out_sample->epistemic_scope_id = domain->engagements[index].epistemic_scope_id;
    out_sample->provenance_id = domain->engagements[index].provenance_id;
    out_sample->region_id = domain->engagements[index].region_id;
    out_sample->flags = domain->engagements[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_engagement_outcome_query(const dom_conflict_domain* domain,
                                 u32 outcome_id,
                                 dom_domain_budget* budget,
                                 dom_engagement_outcome_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_OUTCOME_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_outcome_index(domain, outcome_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->outcomes[index].region_id)) {
        out_sample->outcome_id = domain->outcomes[index].outcome_id;
        out_sample->region_id = domain->outcomes[index].region_id;
        out_sample->flags = DOM_OUTCOME_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->outcome_id = domain->outcomes[index].outcome_id;
    out_sample->engagement_id = domain->outcomes[index].engagement_id;
    out_sample->casualty_count = domain->outcomes[index].casualty_count;
    memcpy(out_sample->casualty_refs, domain->outcomes[index].casualty_refs,
           sizeof(out_sample->casualty_refs));
    out_sample->resource_delta_count = domain->outcomes[index].resource_delta_count;
    memcpy(out_sample->resource_deltas, domain->outcomes[index].resource_deltas,
           sizeof(out_sample->resource_deltas));
    out_sample->legitimacy_delta_count = domain->outcomes[index].legitimacy_delta_count;
    memcpy(out_sample->legitimacy_deltas, domain->outcomes[index].legitimacy_deltas,
           sizeof(out_sample->legitimacy_deltas));
    out_sample->control_delta_count = domain->outcomes[index].control_delta_count;
    memcpy(out_sample->control_deltas, domain->outcomes[index].control_deltas,
           sizeof(out_sample->control_deltas));
    out_sample->report_count = domain->outcomes[index].report_count;
    memcpy(out_sample->report_refs, domain->outcomes[index].report_refs,
           sizeof(out_sample->report_refs));
    out_sample->provenance_id = domain->outcomes[index].provenance_id;
    out_sample->region_id = domain->outcomes[index].region_id;
    out_sample->flags = domain->outcomes[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_occupation_condition_query(const dom_conflict_domain* domain,
                                   u32 occupation_id,
                                   dom_domain_budget* budget,
                                   dom_occupation_condition_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_OCCUPATION_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_occupation_index(domain, occupation_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->occupations[index].region_id)) {
        out_sample->occupation_id = domain->occupations[index].occupation_id;
        out_sample->region_id = domain->occupations[index].region_id;
        out_sample->flags = DOM_OCCUPATION_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->occupation_id = domain->occupations[index].occupation_id;
    out_sample->occupier_authority_id = domain->occupations[index].occupier_authority_id;
    out_sample->occupied_jurisdiction_id = domain->occupations[index].occupied_jurisdiction_id;
    out_sample->enforcement_capacity = domain->occupations[index].enforcement_capacity;
    out_sample->legitimacy_support = domain->occupations[index].legitimacy_support;
    out_sample->logistics_dependency_id = domain->occupations[index].logistics_dependency_id;
    out_sample->start_tick = domain->occupations[index].start_tick;
    out_sample->next_due_tick = domain->occupations[index].next_due_tick;
    out_sample->status = domain->occupations[index].status;
    out_sample->provenance_id = domain->occupations[index].provenance_id;
    out_sample->region_id = domain->occupations[index].region_id;
    out_sample->flags = domain->occupations[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_resistance_event_query(const dom_conflict_domain* domain,
                               u32 resistance_id,
                               dom_domain_budget* budget,
                               dom_resistance_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RESISTANCE_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_resistance_index(domain, resistance_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->resistance_events[index].region_id)) {
        out_sample->resistance_id = domain->resistance_events[index].resistance_id;
        out_sample->region_id = domain->resistance_events[index].region_id;
        out_sample->flags = DOM_RESISTANCE_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->resistance_id = domain->resistance_events[index].resistance_id;
    out_sample->occupation_id = domain->resistance_events[index].occupation_id;
    out_sample->trigger_reason = domain->resistance_events[index].trigger_reason;
    out_sample->trigger_tick = domain->resistance_events[index].trigger_tick;
    out_sample->resolution_tick = domain->resistance_events[index].resolution_tick;
    out_sample->order_key = domain->resistance_events[index].order_key;
    out_sample->outcome_count = domain->resistance_events[index].outcome_count;
    memcpy(out_sample->outcome_refs, domain->resistance_events[index].outcome_refs,
           sizeof(out_sample->outcome_refs));
    out_sample->provenance_id = domain->resistance_events[index].provenance_id;
    out_sample->region_id = domain->resistance_events[index].region_id;
    out_sample->flags = domain->resistance_events[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_morale_field_query(const dom_conflict_domain* domain,
                           u32 morale_id,
                           dom_domain_budget* budget,
                           dom_morale_field_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_MORALE_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_morale_index(domain, morale_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_conflict_region_collapsed(domain, domain->morale_fields[index].region_id)) {
        out_sample->morale_id = domain->morale_fields[index].morale_id;
        out_sample->region_id = domain->morale_fields[index].region_id;
        out_sample->flags = DOM_MORALE_COLLAPSED;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->morale_id = domain->morale_fields[index].morale_id;
    out_sample->subject_ref_id = domain->morale_fields[index].subject_ref_id;
    out_sample->conflict_id = domain->morale_fields[index].conflict_id;
    out_sample->morale_level = domain->morale_fields[index].morale_level;
    out_sample->decay_rate = domain->morale_fields[index].decay_rate;
    out_sample->influence_count = domain->morale_fields[index].influence_count;
    memcpy(out_sample->influence_refs, domain->morale_fields[index].influence_refs,
           sizeof(out_sample->influence_refs));
    out_sample->provenance_id = domain->morale_fields[index].provenance_id;
    out_sample->region_id = domain->morale_fields[index].region_id;
    out_sample->flags = domain->morale_fields[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_weapon_spec_query(const dom_conflict_domain* domain,
                          u32 weapon_id,
                          dom_domain_budget* budget,
                          dom_weapon_spec_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_WEAPON_UNRESOLVED;

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_conflict_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_conflict_find_weapon_index(domain, weapon_id);
    if (index < 0) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->weapon_id = domain->weapons[index].weapon_id;
    out_sample->assembly_ref_id = domain->weapons[index].assembly_ref_id;
    out_sample->range = domain->weapons[index].range;
    out_sample->rate = domain->weapons[index].rate;
    out_sample->effectiveness = domain->weapons[index].effectiveness;
    out_sample->reliability = domain->weapons[index].reliability;
    out_sample->energy_cost = domain->weapons[index].energy_cost;
    out_sample->material_interaction_ref_id = domain->weapons[index].material_interaction_ref_id;
    out_sample->provenance_id = domain->weapons[index].provenance_id;
    out_sample->flags = domain->weapons[index].flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_conflict_region_query(const dom_conflict_domain* domain,
                              u32 region_id,
                              dom_domain_budget* budget,
                              dom_conflict_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_full;
    u32 cost_medium;
    u32 cost_coarse;
    q48_16 readiness_total = 0;
    q48_16 morale_total = 0;
    q48_16 force_morale_total = 0;
    q48_16 legitimacy_total = 0;
    u32 readiness_seen = 0u;
    u32 morale_seen = 0u;
    u32 force_morale_seen = 0u;
    u32 legitimacy_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_conflict_domain_is_active(domain)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_conflict_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_conflict_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_conflict_region_collapsed(domain, region_id)) {
        const dom_conflict_macro_capsule* capsule = dom_conflict_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->conflict_count = capsule->conflict_count;
            out_sample->side_count = capsule->side_count;
            out_sample->event_count = capsule->event_count;
            out_sample->force_count = capsule->force_count;
            out_sample->engagement_count = capsule->engagement_count;
            out_sample->outcome_count = capsule->outcome_count;
            out_sample->occupation_count = capsule->occupation_count;
            out_sample->resistance_count = capsule->resistance_count;
            out_sample->morale_count = capsule->morale_count;
            out_sample->readiness_avg = capsule->readiness_avg;
            out_sample->morale_avg = capsule->morale_avg;
            out_sample->legitimacy_avg = capsule->legitimacy_avg;
        }
        out_sample->flags = DOM_CONFLICT_RESOLVE_PARTIAL;
        dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_full = dom_conflict_budget_cost(domain->policy.cost_full);
    cost_medium = dom_conflict_budget_cost(domain->policy.cost_medium);
    cost_coarse = dom_conflict_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->conflict_count; ++i) {
        u32 conflict_region = domain->conflicts[i].region_id;
        if (region_id != 0u && conflict_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, conflict_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_full)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->conflict_count += 1u;
    }

    for (u32 i = 0u; i < domain->side_count; ++i) {
        u32 side_region = domain->sides[i].region_id;
        if (region_id != 0u && side_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, side_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->side_count += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        u32 event_region = domain->events[i].region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, event_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->event_count += 1u;
    }

    for (u32 i = 0u; i < domain->force_count; ++i) {
        u32 force_region = domain->forces[i].region_id;
        if (region_id != 0u && force_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, force_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->force_count += 1u;
        readiness_total = d_q48_16_add(readiness_total, d_q48_16_from_q16_16(domain->forces[i].readiness));
        force_morale_total = d_q48_16_add(force_morale_total, d_q48_16_from_q16_16(domain->forces[i].morale));
        readiness_seen += 1u;
        force_morale_seen += 1u;
    }

    for (u32 i = 0u; i < domain->engagement_count; ++i) {
        u32 engagement_region = domain->engagements[i].region_id;
        if (region_id != 0u && engagement_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, engagement_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->engagement_count += 1u;
    }

    for (u32 i = 0u; i < domain->outcome_count; ++i) {
        u32 outcome_region = domain->outcomes[i].region_id;
        if (region_id != 0u && outcome_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, outcome_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->outcome_count += 1u;
    }

    for (u32 i = 0u; i < domain->occupation_count; ++i) {
        u32 occ_region = domain->occupations[i].region_id;
        if (region_id != 0u && occ_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, occ_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->occupation_count += 1u;
        legitimacy_total = d_q48_16_add(legitimacy_total,
                                        d_q48_16_from_q16_16(domain->occupations[i].legitimacy_support));
        legitimacy_seen += 1u;
    }

    for (u32 i = 0u; i < domain->resistance_count; ++i) {
        u32 res_region = domain->resistance_events[i].region_id;
        if (region_id != 0u && res_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, res_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->resistance_count += 1u;
    }

    for (u32 i = 0u; i < domain->morale_count; ++i) {
        u32 morale_region = domain->morale_fields[i].region_id;
        if (region_id != 0u && morale_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, morale_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->morale_count += 1u;
        morale_total = d_q48_16_add(morale_total, d_q48_16_from_q16_16(domain->morale_fields[i].morale_level));
        morale_seen += 1u;
    }

    for (u32 i = 0u; i < domain->weapon_count; ++i) {
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            break;
        }
        out_sample->weapon_count += 1u;
    }

    out_sample->region_id = region_id;
    if (readiness_seen > 0u) {
        q48_16 div = d_q48_16_div(readiness_total, d_q48_16_from_int((i64)readiness_seen));
        out_sample->readiness_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (morale_seen > 0u) {
        q48_16 div = d_q48_16_div(morale_total, d_q48_16_from_int((i64)morale_seen));
        out_sample->morale_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    } else if (force_morale_seen > 0u) {
        q48_16 div = d_q48_16_div(force_morale_total, d_q48_16_from_int((i64)force_morale_seen));
        out_sample->morale_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (legitimacy_seen > 0u) {
        q48_16 div = d_q48_16_div(legitimacy_total, d_q48_16_from_int((i64)legitimacy_seen));
        out_sample->legitimacy_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    out_sample->flags = flags;
    dom_conflict_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                               cost_base, budget);
    return 0;
}

int dom_conflict_resolve(dom_conflict_domain* domain,
                         u32 region_id,
                         u64 tick,
                         u64 tick_delta,
                         dom_domain_budget* budget,
                         dom_conflict_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_full;
    u32 cost_medium;
    u32 cost_coarse;
    q48_16 readiness_total = 0;
    q48_16 morale_total = 0;
    q48_16 force_morale_total = 0;
    q48_16 legitimacy_total = 0;
    u32 readiness_seen = 0u;
    u32 morale_seen = 0u;
    u32 force_morale_seen = 0u;
    u32 legitimacy_seen = 0u;
    u32 flags = 0u;
    u32 resistance_count_due = 0u;
    u32 attrition_count = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_conflict_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_CONFLICT_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_conflict_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_conflict_region_collapsed(domain, region_id)) {
        const dom_conflict_macro_capsule* capsule = dom_conflict_find_capsule(domain, region_id);
        if (capsule) {
            out_result->conflict_count = capsule->conflict_count;
            out_result->side_count = capsule->side_count;
            out_result->event_count = capsule->event_count;
            out_result->force_count = capsule->force_count;
            out_result->engagement_count = capsule->engagement_count;
            out_result->outcome_count = capsule->outcome_count;
            out_result->occupation_count = capsule->occupation_count;
            out_result->resistance_count = capsule->resistance_count;
            out_result->morale_count = capsule->morale_count;
            out_result->readiness_avg = capsule->readiness_avg;
            out_result->morale_avg = capsule->morale_avg;
            out_result->legitimacy_avg = capsule->legitimacy_avg;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_CONFLICT_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_full = dom_conflict_budget_cost(domain->policy.cost_full);
    cost_medium = dom_conflict_budget_cost(domain->policy.cost_medium);
    cost_coarse = dom_conflict_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->conflict_count; ++i) {
        u32 conflict_region = domain->conflicts[i].region_id;
        if (region_id != 0u && conflict_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, conflict_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_full)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->conflict_count += 1u;
    }

    for (u32 i = 0u; i < domain->side_count; ++i) {
        u32 side_region = domain->sides[i].region_id;
        if (region_id != 0u && side_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, side_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->side_count += 1u;
        if (domain->sides[i].logistics_dependency_id == 0u) {
            flags |= DOM_CONFLICT_RESOLVE_SHORTAGE;
        }
        if (domain->sides[i].readiness_level > 0 &&
            domain->sides[i].readiness_level < DOM_CONFLICT_READINESS_LOW_Q16) {
            flags |= DOM_CONFLICT_RESOLVE_LOW_MORALE;
        }
    }

    {
        u32 due_indices[DOM_CONFLICT_MAX_EVENTS];
        u32 due_count = 0u;
        for (u32 i = 0u; i < domain->event_count; ++i) {
            u32 event_region = domain->events[i].region_id;
            if (region_id != 0u && event_region != region_id) {
                continue;
            }
            if (region_id == 0u && dom_conflict_region_collapsed(domain, event_region)) {
                flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
                continue;
            }
            if (!dom_domain_budget_consume(budget, cost_coarse)) {
                flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
                if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                    out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
                }
                break;
            }
            out_result->event_count += 1u;
            if (domain->events[i].scheduled_tick <= tick &&
                !(domain->events[i].flags & DOM_CONFLICT_EVENT_APPLIED)) {
                if (due_count < DOM_CONFLICT_MAX_EVENTS) {
                    due_indices[due_count++] = i;
                }
            }
        }
        for (u32 i = 1u; i < due_count; ++i) {
            u32 idx = due_indices[i];
            u64 order_key = domain->events[idx].order_key;
            u32 event_id = domain->events[idx].event_id;
            u32 j = i;
            while (j > 0u) {
                u32 prev_idx = due_indices[j - 1u];
                u64 prev_key = domain->events[prev_idx].order_key;
                u32 prev_id = domain->events[prev_idx].event_id;
                if (prev_key < order_key || (prev_key == order_key && prev_id <= event_id)) {
                    break;
                }
                due_indices[j] = prev_idx;
                j -= 1u;
            }
            due_indices[j] = idx;
        }
        for (u32 i = 0u; i < due_count; ++i) {
            dom_conflict_event* event = &domain->events[due_indices[i]];
            if (dom_conflict_apply_event(domain, event, tick,
                                         &resistance_count_due, &attrition_count)) {
                out_result->event_applied_count += 1u;
                flags |= DOM_CONFLICT_RESOLVE_EVENT_APPLIED;
            }
            if (event->event_type == DOM_CONFLICT_EVENT_RESISTANCE) {
                flags |= DOM_CONFLICT_RESOLVE_RESISTANCE;
            }
            if (event->event_type == DOM_CONFLICT_EVENT_ATTRITION ||
                event->event_type == DOM_CONFLICT_EVENT_SABOTAGE) {
                flags |= DOM_CONFLICT_RESOLVE_ATTRITION;
            }
        }
    }

    for (u32 i = 0u; i < domain->force_count; ++i) {
        u32 force_region = domain->forces[i].region_id;
        if (region_id != 0u && force_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, force_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->force_count += 1u;
        readiness_total = d_q48_16_add(readiness_total, d_q48_16_from_q16_16(domain->forces[i].readiness));
        force_morale_total = d_q48_16_add(force_morale_total, d_q48_16_from_q16_16(domain->forces[i].morale));
        readiness_seen += 1u;
        force_morale_seen += 1u;
        if (domain->forces[i].logistics_dependency_id == 0u) {
            flags |= DOM_CONFLICT_RESOLVE_SHORTAGE;
        }
        if (domain->forces[i].morale > 0 &&
            domain->forces[i].morale < DOM_CONFLICT_MORALE_LOW_Q16) {
            flags |= DOM_CONFLICT_RESOLVE_LOW_MORALE;
        }
    }

    for (u32 i = 0u; i < domain->engagement_count; ++i) {
        u32 engagement_region = domain->engagements[i].region_id;
        if (region_id != 0u && engagement_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, engagement_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->engagement_count += 1u;
    }

    for (u32 i = 0u; i < domain->outcome_count; ++i) {
        u32 outcome_region = domain->outcomes[i].region_id;
        if (region_id != 0u && outcome_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, outcome_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->outcome_count += 1u;
        if (!(domain->outcomes[i].flags & DOM_OUTCOME_APPLIED)) {
            int engagement_index = dom_conflict_find_engagement_index(domain,
                                                                      domain->outcomes[i].engagement_id);
            if (engagement_index >= 0 &&
                domain->engagements[engagement_index].resolution_tick <= tick) {
                domain->outcomes[i].flags |= DOM_OUTCOME_APPLIED;
                out_result->outcome_applied_count += 1u;
                flags |= DOM_CONFLICT_RESOLVE_EVENT_APPLIED;
            }
        }
    }

    for (u32 i = 0u; i < domain->occupation_count; ++i) {
        u32 occ_region = domain->occupations[i].region_id;
        if (region_id != 0u && occ_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, occ_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->occupation_count += 1u;
        legitimacy_total = d_q48_16_add(legitimacy_total,
                                        d_q48_16_from_q16_16(domain->occupations[i].legitimacy_support));
        legitimacy_seen += 1u;
        if (domain->occupations[i].logistics_dependency_id == 0u) {
            flags |= DOM_CONFLICT_RESOLVE_SHORTAGE;
        }
        if (domain->occupations[i].legitimacy_support > 0 &&
            domain->occupations[i].legitimacy_support < DOM_CONFLICT_LEGITIMACY_LOW_Q16) {
            flags |= DOM_CONFLICT_RESOLVE_ILLEGITIMATE;
        }
        if (domain->occupations[i].status == DOM_CONFLICT_OCCUPATION_DEGRADING) {
            flags |= DOM_CONFLICT_RESOLVE_RESISTANCE;
        }
    }

    for (u32 i = 0u; i < domain->resistance_count; ++i) {
        u32 res_region = domain->resistance_events[i].region_id;
        if (region_id != 0u && res_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, res_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->resistance_count += 1u;
        if (domain->resistance_events[i].resolution_tick <= tick &&
            !(domain->resistance_events[i].flags & DOM_RESISTANCE_APPLIED)) {
            domain->resistance_events[i].flags |= DOM_RESISTANCE_APPLIED;
            out_result->resistance_applied_count += 1u;
            flags |= DOM_CONFLICT_RESOLVE_EVENT_APPLIED;
        }
    }

    for (u32 i = 0u; i < domain->morale_count; ++i) {
        u32 morale_region = domain->morale_fields[i].region_id;
        if (region_id != 0u && morale_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_conflict_region_collapsed(domain, morale_region)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_medium)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->morale_count += 1u;
        if (dom_conflict_apply_morale_decay(&domain->morale_fields[i], tick_delta)) {
            domain->morale_fields[i].flags |= DOM_MORALE_DECAYING;
            flags |= DOM_CONFLICT_RESOLVE_EVENT_APPLIED;
        }
        morale_total = d_q48_16_add(morale_total,
                                    d_q48_16_from_q16_16(domain->morale_fields[i].morale_level));
        morale_seen += 1u;
        if (domain->morale_fields[i].morale_level > 0 &&
            domain->morale_fields[i].morale_level < DOM_CONFLICT_MORALE_LOW_Q16) {
            flags |= DOM_CONFLICT_RESOLVE_LOW_MORALE;
        }
    }

    for (u32 i = 0u; i < domain->weapon_count; ++i) {
        if (!dom_domain_budget_consume(budget, cost_coarse)) {
            flags |= DOM_CONFLICT_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_CONFLICT_REFUSE_NONE) {
                out_result->refusal_reason = DOM_CONFLICT_REFUSE_BUDGET;
            }
            break;
        }
        out_result->weapon_count += 1u;
    }

    out_result->ok = 1u;
    if (readiness_seen > 0u) {
        q48_16 div = d_q48_16_div(readiness_total, d_q48_16_from_int((i64)readiness_seen));
        out_result->readiness_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (morale_seen > 0u) {
        q48_16 div = d_q48_16_div(morale_total, d_q48_16_from_int((i64)morale_seen));
        out_result->morale_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    } else if (force_morale_seen > 0u) {
        q48_16 div = d_q48_16_div(force_morale_total, d_q48_16_from_int((i64)force_morale_seen));
        out_result->morale_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (legitimacy_seen > 0u) {
        q48_16 div = d_q48_16_div(legitimacy_total, d_q48_16_from_int((i64)legitimacy_seen));
        out_result->legitimacy_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (resistance_count_due > 0u) {
        flags |= DOM_CONFLICT_RESOLVE_RESISTANCE;
    }
    if (attrition_count > 0u) {
        flags |= DOM_CONFLICT_RESOLVE_ATTRITION;
    }
    out_result->flags = flags;
    return 0;
}

int dom_conflict_domain_collapse_region(dom_conflict_domain* domain, u32 region_id)
{
    dom_conflict_macro_capsule capsule;
    u32 readiness_hist_bins[DOM_CONFLICT_HIST_BINS];
    u32 morale_hist_bins[DOM_CONFLICT_HIST_BINS];
    q48_16 readiness_total = 0;
    q48_16 morale_total = 0;
    q48_16 legitimacy_total = 0;
    u32 readiness_seen = 0u;
    u32 morale_seen = 0u;
    u32 legitimacy_seen = 0u;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_conflict_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_CONFLICT_MAX_CAPSULES) {
        return -2;
    }
    memset(readiness_hist_bins, 0, sizeof(readiness_hist_bins));
    memset(morale_hist_bins, 0, sizeof(morale_hist_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;

    for (u32 i = 0u; i < domain->conflict_count; ++i) {
        if (domain->conflicts[i].region_id != region_id) {
            continue;
        }
        capsule.conflict_count += 1u;
    }
    for (u32 i = 0u; i < domain->side_count; ++i) {
        if (domain->sides[i].region_id != region_id) {
            continue;
        }
        capsule.side_count += 1u;
    }
    for (u32 i = 0u; i < domain->event_count; ++i) {
        if (domain->events[i].region_id != region_id) {
            continue;
        }
        capsule.event_count += 1u;
    }
    for (u32 i = 0u; i < domain->force_count; ++i) {
        if (domain->forces[i].region_id != region_id) {
            continue;
        }
        capsule.force_count += 1u;
        readiness_total = d_q48_16_add(readiness_total,
                                       d_q48_16_from_q16_16(domain->forces[i].readiness));
        readiness_hist_bins[dom_conflict_hist_bin(domain->forces[i].readiness)] += 1u;
        readiness_seen += 1u;
    }
    for (u32 i = 0u; i < domain->engagement_count; ++i) {
        if (domain->engagements[i].region_id != region_id) {
            continue;
        }
        capsule.engagement_count += 1u;
    }
    for (u32 i = 0u; i < domain->outcome_count; ++i) {
        if (domain->outcomes[i].region_id != region_id) {
            continue;
        }
        capsule.outcome_count += 1u;
    }
    for (u32 i = 0u; i < domain->occupation_count; ++i) {
        if (domain->occupations[i].region_id != region_id) {
            continue;
        }
        capsule.occupation_count += 1u;
        legitimacy_total = d_q48_16_add(legitimacy_total,
                                        d_q48_16_from_q16_16(domain->occupations[i].legitimacy_support));
        legitimacy_seen += 1u;
    }
    for (u32 i = 0u; i < domain->resistance_count; ++i) {
        if (domain->resistance_events[i].region_id != region_id) {
            continue;
        }
        capsule.resistance_count += 1u;
    }
    for (u32 i = 0u; i < domain->morale_count; ++i) {
        if (domain->morale_fields[i].region_id != region_id) {
            continue;
        }
        capsule.morale_count += 1u;
        morale_total = d_q48_16_add(morale_total,
                                    d_q48_16_from_q16_16(domain->morale_fields[i].morale_level));
        morale_hist_bins[dom_conflict_hist_bin(domain->morale_fields[i].morale_level)] += 1u;
        morale_seen += 1u;
    }

    if (readiness_seen > 0u) {
        q48_16 div = d_q48_16_div(readiness_total, d_q48_16_from_int((i64)readiness_seen));
        capsule.readiness_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (morale_seen > 0u) {
        q48_16 div = d_q48_16_div(morale_total, d_q48_16_from_int((i64)morale_seen));
        capsule.morale_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (legitimacy_seen > 0u) {
        q48_16 div = d_q48_16_div(legitimacy_total, d_q48_16_from_int((i64)legitimacy_seen));
        capsule.legitimacy_avg = dom_conflict_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    for (u32 b = 0u; b < DOM_CONFLICT_HIST_BINS; ++b) {
        capsule.readiness_hist[b] = dom_conflict_hist_bin_ratio(readiness_hist_bins[b],
                                                                readiness_seen);
        capsule.morale_hist[b] = dom_conflict_hist_bin_ratio(morale_hist_bins[b],
                                                             morale_seen);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_conflict_domain_expand_region(dom_conflict_domain* domain, u32 region_id)
{
    if (!domain || region_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            domain->capsules[i] = domain->capsules[domain->capsule_count - 1u];
            domain->capsule_count -= 1u;
            return 0;
        }
    }
    return -2;
}

u32 dom_conflict_domain_capsule_count(const dom_conflict_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_conflict_macro_capsule* dom_conflict_domain_capsule_at(const dom_conflict_domain* domain,
                                                                 u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_conflict_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
