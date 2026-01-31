/*
FILE: source/domino/world/knowledge_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/knowledge_fields
RESPONSIBILITY: Implements deterministic knowledge, skill, and education resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/knowledge_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_KNOWLEDGE_RESOLVE_COST_BASE 1u

static q16_16 dom_knowledge_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_KNOWLEDGE_RATIO_ONE_Q16) {
        return DOM_KNOWLEDGE_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_knowledge_add_clamped(q16_16 a, q16_16 b)
{
    q16_16 sum = d_q16_16_add(a, b);
    return dom_knowledge_clamp_ratio(sum);
}

static q16_16 dom_knowledge_sub_clamped(q16_16 a, q16_16 b)
{
    q16_16 diff = d_q16_16_sub(a, b);
    return dom_knowledge_clamp_ratio(diff);
}

static void dom_knowledge_artifact_init(dom_knowledge_artifact* artifact)
{
    if (!artifact) {
        return;
    }
    memset(artifact, 0, sizeof(*artifact));
}

static void dom_skill_profile_init(dom_skill_profile* profile)
{
    if (!profile) {
        return;
    }
    memset(profile, 0, sizeof(*profile));
}

static void dom_education_program_init(dom_education_program* program)
{
    if (!program) {
        return;
    }
    memset(program, 0, sizeof(*program));
}

static void dom_knowledge_event_init(dom_knowledge_event* event)
{
    if (!event) {
        return;
    }
    memset(event, 0, sizeof(*event));
    event->process_type = DOM_KNOWLEDGE_PROCESS_UNSET;
}

static int dom_knowledge_find_artifact_index(const dom_knowledge_domain* domain, u32 artifact_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->artifact_count; ++i) {
        if (domain->artifacts[i].artifact_id == artifact_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_knowledge_find_skill_index(const dom_knowledge_domain* domain, u32 profile_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->skill_count; ++i) {
        if (domain->skills[i].profile_id == profile_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_knowledge_find_program_index(const dom_knowledge_domain* domain, u32 program_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->program_count; ++i) {
        if (domain->programs[i].program_id == program_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_knowledge_find_event_index(const dom_knowledge_domain* domain, u32 event_id)
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

static d_bool dom_knowledge_domain_is_active(const dom_knowledge_domain* domain)
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

static d_bool dom_knowledge_region_collapsed(const dom_knowledge_domain* domain, u32 region_id)
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

static const dom_knowledge_macro_capsule* dom_knowledge_find_capsule(const dom_knowledge_domain* domain,
                                                                     u32 region_id)
{
    if (!domain) {
        return (const dom_knowledge_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_knowledge_macro_capsule*)0;
}

static void dom_knowledge_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_knowledge_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_knowledge_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_KNOWLEDGE_RESOLVE_COST_BASE : cost_units;
}

static d_bool dom_knowledge_apply_artifact_decay(dom_knowledge_artifact* artifact, u64 tick_delta)
{
    q16_16 decay_per_tick;
    q48_16 decay_total;
    q16_16 decay_q16;
    if (!artifact || tick_delta == 0u) {
        return D_FALSE;
    }
    if (artifact->decay_rate <= 0 || artifact->confidence <= 0) {
        return D_FALSE;
    }
    decay_per_tick = d_q16_16_mul(artifact->confidence, artifact->decay_rate);
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
    artifact->confidence = dom_knowledge_sub_clamped(artifact->confidence, decay_q16);
    artifact->uncertainty = dom_knowledge_add_clamped(artifact->uncertainty, decay_q16);
    return D_TRUE;
}

static d_bool dom_knowledge_apply_skill_decay(dom_skill_profile* profile, u64 tick_delta)
{
    q16_16 decay_per_tick;
    q48_16 decay_total;
    q16_16 decay_q16;
    d_bool changed = D_FALSE;
    if (!profile || tick_delta == 0u) {
        return D_FALSE;
    }
    if (profile->decay_rate <= 0) {
        return D_FALSE;
    }
    if (profile->variance_reduction > 0) {
        decay_per_tick = d_q16_16_mul(profile->variance_reduction, profile->decay_rate);
        if (decay_per_tick > 0) {
            decay_total = d_q48_16_from_q16_16(decay_per_tick);
            if (tick_delta > 1u) {
                decay_total = d_q48_16_mul(decay_total, d_q48_16_from_int((i64)tick_delta));
            }
            decay_q16 = d_q16_16_from_q48_16(decay_total);
            if (decay_q16 > 0) {
                profile->variance_reduction = dom_knowledge_sub_clamped(profile->variance_reduction,
                                                                        decay_q16);
                changed = D_TRUE;
            }
        }
    }
    if (profile->failure_bias_reduction > 0) {
        decay_per_tick = d_q16_16_mul(profile->failure_bias_reduction, profile->decay_rate);
        if (decay_per_tick > 0) {
            decay_total = d_q48_16_from_q16_16(decay_per_tick);
            if (tick_delta > 1u) {
                decay_total = d_q48_16_mul(decay_total, d_q48_16_from_int((i64)tick_delta));
            }
            decay_q16 = d_q16_16_from_q48_16(decay_total);
            if (decay_q16 > 0) {
                profile->failure_bias_reduction = dom_knowledge_sub_clamped(
                    profile->failure_bias_reduction, decay_q16);
                changed = D_TRUE;
            }
        }
    }
    return changed;
}

static d_bool dom_knowledge_apply_event(dom_knowledge_domain* domain,
                                        dom_knowledge_event* event,
                                        u64 tick)
{
    d_bool applied = D_FALSE;
    if (!domain || !event) {
        return D_FALSE;
    }
    if (event->flags & DOM_KNOWLEDGE_EVENT_APPLIED) {
        return D_FALSE;
    }
    if (event->event_tick > tick) {
        return D_FALSE;
    }
    if (event->artifact_id != 0u) {
        int artifact_index = dom_knowledge_find_artifact_index(domain, event->artifact_id);
        if (artifact_index >= 0) {
            dom_knowledge_artifact* artifact = &domain->artifacts[artifact_index];
            artifact->confidence = dom_knowledge_add_clamped(artifact->confidence,
                                                             event->delta_confidence);
            artifact->uncertainty = dom_knowledge_add_clamped(artifact->uncertainty,
                                                              event->delta_uncertainty);
            applied = D_TRUE;
        }
    }
    if (event->skill_id != 0u) {
        int skill_index = dom_knowledge_find_skill_index(domain, event->skill_id);
        if (skill_index >= 0) {
            dom_skill_profile* profile = &domain->skills[skill_index];
            profile->variance_reduction = dom_knowledge_add_clamped(profile->variance_reduction,
                                                                    event->delta_variance);
            profile->failure_bias_reduction = dom_knowledge_add_clamped(
                profile->failure_bias_reduction, event->delta_failure_bias);
            applied = D_TRUE;
        }
    }
    if (!applied) {
        return D_FALSE;
    }
    event->flags |= DOM_KNOWLEDGE_EVENT_APPLIED;
    return D_TRUE;
}

static q16_16 dom_knowledge_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_knowledge_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_knowledge_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_KNOWLEDGE_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_KNOWLEDGE_HIST_BINS) {
        scaled = DOM_KNOWLEDGE_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_knowledge_surface_desc_init(dom_knowledge_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->artifact_count = 0u;
    desc->skill_count = 0u;
    desc->program_count = 0u;
    desc->event_count = 0u;
    for (u32 i = 0u; i < DOM_KNOWLEDGE_MAX_ARTIFACTS; ++i) {
        desc->artifacts[i].artifact_id = 0u;
    }
    for (u32 i = 0u; i < DOM_KNOWLEDGE_MAX_SKILLS; ++i) {
        desc->skills[i].profile_id = 0u;
    }
    for (u32 i = 0u; i < DOM_KNOWLEDGE_MAX_PROGRAMS; ++i) {
        desc->programs[i].program_id = 0u;
    }
    for (u32 i = 0u; i < DOM_KNOWLEDGE_MAX_EVENTS; ++i) {
        desc->events[i].event_id = 0u;
    }
}

void dom_knowledge_domain_init(dom_knowledge_domain* domain,
                               const dom_knowledge_surface_desc* desc)
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

    domain->artifact_count = (desc->artifact_count > DOM_KNOWLEDGE_MAX_ARTIFACTS)
                               ? DOM_KNOWLEDGE_MAX_ARTIFACTS
                               : desc->artifact_count;
    domain->skill_count = (desc->skill_count > DOM_KNOWLEDGE_MAX_SKILLS)
                            ? DOM_KNOWLEDGE_MAX_SKILLS
                            : desc->skill_count;
    domain->program_count = (desc->program_count > DOM_KNOWLEDGE_MAX_PROGRAMS)
                              ? DOM_KNOWLEDGE_MAX_PROGRAMS
                              : desc->program_count;
    domain->event_count = (desc->event_count > DOM_KNOWLEDGE_MAX_EVENTS)
                            ? DOM_KNOWLEDGE_MAX_EVENTS
                            : desc->event_count;

    for (u32 i = 0u; i < domain->artifact_count; ++i) {
        dom_knowledge_artifact_init(&domain->artifacts[i]);
        domain->artifacts[i].artifact_id = desc->artifacts[i].artifact_id;
        domain->artifacts[i].subject_domain_id = desc->artifacts[i].subject_domain_id;
        domain->artifacts[i].claim_count = desc->artifacts[i].claim_count;
        domain->artifacts[i].evidence_count = desc->artifacts[i].evidence_count;
        domain->artifacts[i].confidence = desc->artifacts[i].confidence;
        domain->artifacts[i].uncertainty = desc->artifacts[i].uncertainty;
        domain->artifacts[i].decay_rate = desc->artifacts[i].decay_rate;
        domain->artifacts[i].provenance_id = desc->artifacts[i].provenance_id;
        domain->artifacts[i].region_id = desc->artifacts[i].region_id;
    }

    for (u32 i = 0u; i < domain->skill_count; ++i) {
        dom_skill_profile_init(&domain->skills[i]);
        domain->skills[i].profile_id = desc->skills[i].profile_id;
        domain->skills[i].subject_ref_id = desc->skills[i].subject_ref_id;
        domain->skills[i].skill_domain_id = desc->skills[i].skill_domain_id;
        domain->skills[i].variance_reduction = desc->skills[i].variance_reduction;
        domain->skills[i].failure_bias_reduction = desc->skills[i].failure_bias_reduction;
        domain->skills[i].decay_rate = desc->skills[i].decay_rate;
        domain->skills[i].process_ref_count = desc->skills[i].process_ref_count;
        for (u32 p = 0u; p < DOM_KNOWLEDGE_MAX_PROCESS_REFS; ++p) {
            domain->skills[i].process_refs[p] = desc->skills[i].process_refs[p];
        }
        domain->skills[i].provenance_id = desc->skills[i].provenance_id;
        domain->skills[i].region_id = desc->skills[i].region_id;
    }

    for (u32 i = 0u; i < domain->program_count; ++i) {
        dom_education_program_init(&domain->programs[i]);
        domain->programs[i].program_id = desc->programs[i].program_id;
        domain->programs[i].curriculum_id = desc->programs[i].curriculum_id;
        domain->programs[i].duration_ticks = desc->programs[i].duration_ticks;
        domain->programs[i].energy_cost = desc->programs[i].energy_cost;
        domain->programs[i].resource_cost = desc->programs[i].resource_cost;
        domain->programs[i].instructor_count = desc->programs[i].instructor_count;
        for (u32 r = 0u; r < DOM_KNOWLEDGE_MAX_INSTRUCTOR_REFS; ++r) {
            domain->programs[i].instructor_refs[r] = desc->programs[i].instructor_refs[r];
        }
        domain->programs[i].output_skill_id = desc->programs[i].output_skill_id;
        domain->programs[i].accreditation_id = desc->programs[i].accreditation_id;
        domain->programs[i].provenance_id = desc->programs[i].provenance_id;
        domain->programs[i].region_id = desc->programs[i].region_id;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_knowledge_event_init(&domain->events[i]);
        domain->events[i].event_id = desc->events[i].event_id;
        domain->events[i].process_type = desc->events[i].process_type;
        domain->events[i].subject_ref_id = desc->events[i].subject_ref_id;
        domain->events[i].artifact_id = desc->events[i].artifact_id;
        domain->events[i].skill_id = desc->events[i].skill_id;
        domain->events[i].program_id = desc->events[i].program_id;
        domain->events[i].delta_confidence = desc->events[i].delta_confidence;
        domain->events[i].delta_uncertainty = desc->events[i].delta_uncertainty;
        domain->events[i].delta_variance = desc->events[i].delta_variance;
        domain->events[i].delta_failure_bias = desc->events[i].delta_failure_bias;
        domain->events[i].event_tick = desc->events[i].event_tick;
        domain->events[i].region_id = desc->events[i].region_id;
        domain->events[i].provenance_id = desc->events[i].provenance_id;
        domain->events[i].flags = desc->events[i].flags;
    }

    domain->capsule_count = 0u;
}

void dom_knowledge_domain_free(dom_knowledge_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->artifact_count = 0u;
    domain->skill_count = 0u;
    domain->program_count = 0u;
    domain->event_count = 0u;
    domain->capsule_count = 0u;
}

void dom_knowledge_domain_set_state(dom_knowledge_domain* domain,
                                    u32 existence_state,
                                    u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_knowledge_domain_set_policy(dom_knowledge_domain* domain,
                                     const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_knowledge_artifact_query(const dom_knowledge_domain* domain,
                                 u32 artifact_id,
                                 dom_domain_budget* budget,
                                 dom_knowledge_artifact_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_KNOWLEDGE_ARTIFACT_UNRESOLVED;

    if (!dom_knowledge_domain_is_active(domain)) {
        dom_knowledge_query_meta_refused(&out_sample->meta,
                                         DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE,
                                         budget);
        return 0;
    }

    cost = dom_knowledge_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_knowledge_find_artifact_index(domain, artifact_id);
    if (index < 0) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_knowledge_region_collapsed(domain, domain->artifacts[index].region_id)) {
        out_sample->artifact_id = domain->artifacts[index].artifact_id;
        out_sample->region_id = domain->artifacts[index].region_id;
        out_sample->flags = DOM_KNOWLEDGE_ARTIFACT_COLLAPSED;
        dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                    DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->artifact_id = domain->artifacts[index].artifact_id;
    out_sample->subject_domain_id = domain->artifacts[index].subject_domain_id;
    out_sample->claim_count = domain->artifacts[index].claim_count;
    out_sample->evidence_count = domain->artifacts[index].evidence_count;
    out_sample->confidence = domain->artifacts[index].confidence;
    out_sample->uncertainty = domain->artifacts[index].uncertainty;
    out_sample->decay_rate = domain->artifacts[index].decay_rate;
    out_sample->provenance_id = domain->artifacts[index].provenance_id;
    out_sample->region_id = domain->artifacts[index].region_id;
    out_sample->flags = domain->artifacts[index].flags;
    dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_skill_profile_query(const dom_knowledge_domain* domain,
                            u32 profile_id,
                            dom_domain_budget* budget,
                            dom_skill_profile_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_SKILL_PROFILE_UNRESOLVED;

    if (!dom_knowledge_domain_is_active(domain)) {
        dom_knowledge_query_meta_refused(&out_sample->meta,
                                         DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE,
                                         budget);
        return 0;
    }

    cost = dom_knowledge_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_knowledge_find_skill_index(domain, profile_id);
    if (index < 0) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_knowledge_region_collapsed(domain, domain->skills[index].region_id)) {
        out_sample->profile_id = domain->skills[index].profile_id;
        out_sample->region_id = domain->skills[index].region_id;
        out_sample->flags = DOM_SKILL_PROFILE_COLLAPSED;
        dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                    DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->profile_id = domain->skills[index].profile_id;
    out_sample->subject_ref_id = domain->skills[index].subject_ref_id;
    out_sample->skill_domain_id = domain->skills[index].skill_domain_id;
    out_sample->variance_reduction = domain->skills[index].variance_reduction;
    out_sample->failure_bias_reduction = domain->skills[index].failure_bias_reduction;
    out_sample->decay_rate = domain->skills[index].decay_rate;
    out_sample->process_ref_count = domain->skills[index].process_ref_count;
    for (u32 p = 0u; p < DOM_KNOWLEDGE_MAX_PROCESS_REFS; ++p) {
        out_sample->process_refs[p] = domain->skills[index].process_refs[p];
    }
    out_sample->provenance_id = domain->skills[index].provenance_id;
    out_sample->region_id = domain->skills[index].region_id;
    out_sample->flags = domain->skills[index].flags;
    dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_education_program_query(const dom_knowledge_domain* domain,
                                u32 program_id,
                                dom_domain_budget* budget,
                                dom_education_program_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_EDU_PROGRAM_UNRESOLVED;

    if (!dom_knowledge_domain_is_active(domain)) {
        dom_knowledge_query_meta_refused(&out_sample->meta,
                                         DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE,
                                         budget);
        return 0;
    }

    cost = dom_knowledge_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_knowledge_find_program_index(domain, program_id);
    if (index < 0) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_knowledge_region_collapsed(domain, domain->programs[index].region_id)) {
        out_sample->program_id = domain->programs[index].program_id;
        out_sample->region_id = domain->programs[index].region_id;
        out_sample->flags = DOM_EDU_PROGRAM_COLLAPSED;
        dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                    DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->program_id = domain->programs[index].program_id;
    out_sample->curriculum_id = domain->programs[index].curriculum_id;
    out_sample->duration_ticks = domain->programs[index].duration_ticks;
    out_sample->energy_cost = domain->programs[index].energy_cost;
    out_sample->resource_cost = domain->programs[index].resource_cost;
    out_sample->instructor_count = domain->programs[index].instructor_count;
    for (u32 r = 0u; r < DOM_KNOWLEDGE_MAX_INSTRUCTOR_REFS; ++r) {
        out_sample->instructor_refs[r] = domain->programs[index].instructor_refs[r];
    }
    out_sample->output_skill_id = domain->programs[index].output_skill_id;
    out_sample->accreditation_id = domain->programs[index].accreditation_id;
    out_sample->provenance_id = domain->programs[index].provenance_id;
    out_sample->region_id = domain->programs[index].region_id;
    out_sample->flags = domain->programs[index].flags;
    dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_knowledge_event_query(const dom_knowledge_domain* domain,
                              u32 event_id,
                              dom_domain_budget* budget,
                              dom_knowledge_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_KNOWLEDGE_EVENT_UNRESOLVED;

    if (!dom_knowledge_domain_is_active(domain)) {
        dom_knowledge_query_meta_refused(&out_sample->meta,
                                         DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE,
                                         budget);
        return 0;
    }

    cost = dom_knowledge_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_knowledge_find_event_index(domain, event_id);
    if (index < 0) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_knowledge_region_collapsed(domain, domain->events[index].region_id)) {
        out_sample->event_id = domain->events[index].event_id;
        out_sample->region_id = domain->events[index].region_id;
        out_sample->flags = DOM_KNOWLEDGE_EVENT_UNRESOLVED | DOM_KNOWLEDGE_EVENT_APPLIED;
        dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                    DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->event_id = domain->events[index].event_id;
    out_sample->process_type = domain->events[index].process_type;
    out_sample->subject_ref_id = domain->events[index].subject_ref_id;
    out_sample->artifact_id = domain->events[index].artifact_id;
    out_sample->skill_id = domain->events[index].skill_id;
    out_sample->program_id = domain->events[index].program_id;
    out_sample->delta_confidence = domain->events[index].delta_confidence;
    out_sample->delta_uncertainty = domain->events[index].delta_uncertainty;
    out_sample->delta_variance = domain->events[index].delta_variance;
    out_sample->delta_failure_bias = domain->events[index].delta_failure_bias;
    out_sample->event_tick = domain->events[index].event_tick;
    out_sample->region_id = domain->events[index].region_id;
    out_sample->provenance_id = domain->events[index].provenance_id;
    out_sample->flags = domain->events[index].flags;
    dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_knowledge_region_query(const dom_knowledge_domain* domain,
                               u32 region_id,
                               dom_domain_budget* budget,
                               dom_knowledge_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_artifact;
    u32 cost_skill;
    u32 cost_program;
    u32 cost_event;
    q48_16 confidence_total = 0;
    q48_16 uncertainty_total = 0;
    q48_16 variance_total = 0;
    q48_16 bias_total = 0;
    u32 artifacts_seen = 0u;
    u32 skills_seen = 0u;
    u32 programs_seen = 0u;
    u32 events_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_knowledge_domain_is_active(domain)) {
        dom_knowledge_query_meta_refused(&out_sample->meta,
                                         DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE,
                                         budget);
        return 0;
    }

    cost_base = dom_knowledge_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_knowledge_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_knowledge_region_collapsed(domain, region_id)) {
        const dom_knowledge_macro_capsule* capsule = dom_knowledge_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->artifact_count = capsule->artifact_count;
            out_sample->skill_count = capsule->skill_count;
            out_sample->program_count = capsule->program_count;
            out_sample->confidence_avg = capsule->confidence_avg;
            out_sample->variance_reduction_avg = capsule->variance_reduction_avg;
        }
        out_sample->flags = DOM_KNOWLEDGE_RESOLVE_PARTIAL;
        dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                    DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_artifact = dom_knowledge_budget_cost(domain->policy.cost_medium);
    cost_skill = dom_knowledge_budget_cost(domain->policy.cost_medium);
    cost_program = dom_knowledge_budget_cost(domain->policy.cost_coarse);
    cost_event = dom_knowledge_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->artifact_count; ++i) {
        u32 artifact_region = domain->artifacts[i].region_id;
        if (region_id != 0u && artifact_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, artifact_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_artifact)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            break;
        }
        confidence_total = d_q48_16_add(confidence_total,
                                        d_q48_16_from_q16_16(domain->artifacts[i].confidence));
        uncertainty_total = d_q48_16_add(uncertainty_total,
                                         d_q48_16_from_q16_16(domain->artifacts[i].uncertainty));
        artifacts_seen += 1u;
    }

    for (u32 i = 0u; i < domain->skill_count; ++i) {
        u32 skill_region = domain->skills[i].region_id;
        if (region_id != 0u && skill_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, skill_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_skill)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            break;
        }
        variance_total = d_q48_16_add(variance_total,
                                      d_q48_16_from_q16_16(domain->skills[i].variance_reduction));
        bias_total = d_q48_16_add(bias_total,
                                  d_q48_16_from_q16_16(domain->skills[i].failure_bias_reduction));
        skills_seen += 1u;
    }

    for (u32 i = 0u; i < domain->program_count; ++i) {
        u32 program_region = domain->programs[i].region_id;
        if (region_id != 0u && program_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, program_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_program)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            break;
        }
        programs_seen += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        u32 event_region = domain->events[i].region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, event_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            break;
        }
        events_seen += 1u;
    }

    out_sample->region_id = region_id;
    out_sample->artifact_count = artifacts_seen;
    out_sample->skill_count = skills_seen;
    out_sample->program_count = programs_seen;
    out_sample->event_count = events_seen;
    if (artifacts_seen > 0u) {
        q48_16 div = d_q48_16_div(confidence_total,
                                 d_q48_16_from_int((i64)artifacts_seen));
        out_sample->confidence_avg = dom_knowledge_clamp_ratio(d_q16_16_from_q48_16(div));
        div = d_q48_16_div(uncertainty_total,
                          d_q48_16_from_int((i64)artifacts_seen));
        out_sample->uncertainty_avg = dom_knowledge_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (skills_seen > 0u) {
        q48_16 div = d_q48_16_div(variance_total,
                                 d_q48_16_from_int((i64)skills_seen));
        out_sample->variance_reduction_avg = dom_knowledge_clamp_ratio(
            d_q16_16_from_q48_16(div));
        div = d_q48_16_div(bias_total,
                           d_q48_16_from_int((i64)skills_seen));
        out_sample->failure_bias_reduction_avg = dom_knowledge_clamp_ratio(
            d_q16_16_from_q48_16(div));
    }
    out_sample->flags = flags;
    dom_knowledge_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                                cost_base, budget);
    return 0;
}

int dom_knowledge_resolve(dom_knowledge_domain* domain,
                          u32 region_id,
                          u64 tick,
                          u64 tick_delta,
                          dom_domain_budget* budget,
                          dom_knowledge_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_artifact;
    u32 cost_skill;
    u32 cost_program;
    u32 cost_event;
    q48_16 confidence_total = 0;
    q48_16 uncertainty_total = 0;
    q48_16 variance_total = 0;
    q48_16 bias_total = 0;
    u32 artifacts_seen = 0u;
    u32 skills_seen = 0u;
    u32 programs_seen = 0u;
    u32 events_seen = 0u;
    u32 events_applied = 0u;
    u32 flags = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_knowledge_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_KNOWLEDGE_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_knowledge_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_KNOWLEDGE_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_knowledge_region_collapsed(domain, region_id)) {
        const dom_knowledge_macro_capsule* capsule = dom_knowledge_find_capsule(domain, region_id);
        if (capsule) {
            out_result->artifact_count = capsule->artifact_count;
            out_result->skill_count = capsule->skill_count;
            out_result->program_count = capsule->program_count;
            out_result->confidence_avg = capsule->confidence_avg;
            out_result->variance_reduction_avg = capsule->variance_reduction_avg;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_KNOWLEDGE_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_artifact = dom_knowledge_budget_cost(domain->policy.cost_medium);
    cost_skill = dom_knowledge_budget_cost(domain->policy.cost_medium);
    cost_program = dom_knowledge_budget_cost(domain->policy.cost_coarse);
    cost_event = dom_knowledge_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->artifact_count; ++i) {
        u32 artifact_region = domain->artifacts[i].region_id;
        if (region_id != 0u && artifact_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, artifact_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_artifact)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_KNOWLEDGE_REFUSE_NONE) {
                out_result->refusal_reason = DOM_KNOWLEDGE_REFUSE_BUDGET;
            }
            break;
        }
        if (dom_knowledge_apply_artifact_decay(&domain->artifacts[i], tick_delta)) {
            domain->artifacts[i].flags |= DOM_KNOWLEDGE_ARTIFACT_DECAYING;
            flags |= DOM_KNOWLEDGE_RESOLVE_DECAYED;
        }
        confidence_total = d_q48_16_add(confidence_total,
                                        d_q48_16_from_q16_16(domain->artifacts[i].confidence));
        uncertainty_total = d_q48_16_add(uncertainty_total,
                                         d_q48_16_from_q16_16(domain->artifacts[i].uncertainty));
        artifacts_seen += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_knowledge_event* event = &domain->events[i];
        u32 event_region = event->region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, event_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_KNOWLEDGE_REFUSE_NONE) {
                out_result->refusal_reason = DOM_KNOWLEDGE_REFUSE_BUDGET;
            }
            break;
        }
        events_seen += 1u;
        if (dom_knowledge_apply_event(domain, event, tick)) {
            events_applied += 1u;
            flags |= DOM_KNOWLEDGE_RESOLVE_EVENT_APPLIED;
        }
    }

    for (u32 i = 0u; i < domain->skill_count; ++i) {
        u32 skill_region = domain->skills[i].region_id;
        if (region_id != 0u && skill_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, skill_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_skill)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_KNOWLEDGE_REFUSE_NONE) {
                out_result->refusal_reason = DOM_KNOWLEDGE_REFUSE_BUDGET;
            }
            break;
        }
        if (dom_knowledge_apply_skill_decay(&domain->skills[i], tick_delta)) {
            domain->skills[i].flags |= DOM_SKILL_PROFILE_DECAYING;
            flags |= DOM_KNOWLEDGE_RESOLVE_DECAYED;
        }
        variance_total = d_q48_16_add(variance_total,
                                      d_q48_16_from_q16_16(domain->skills[i].variance_reduction));
        bias_total = d_q48_16_add(bias_total,
                                  d_q48_16_from_q16_16(domain->skills[i].failure_bias_reduction));
        skills_seen += 1u;
    }

    for (u32 i = 0u; i < domain->program_count; ++i) {
        u32 program_region = domain->programs[i].region_id;
        if (region_id != 0u && program_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_knowledge_region_collapsed(domain, program_region)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_program)) {
            flags |= DOM_KNOWLEDGE_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_KNOWLEDGE_REFUSE_NONE) {
                out_result->refusal_reason = DOM_KNOWLEDGE_REFUSE_BUDGET;
            }
            break;
        }
        programs_seen += 1u;
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->artifact_count = artifacts_seen;
    out_result->skill_count = skills_seen;
    out_result->program_count = programs_seen;
    out_result->event_count = events_seen;
    out_result->event_applied_count = events_applied;
    if (artifacts_seen > 0u) {
        q48_16 div = d_q48_16_div(confidence_total,
                                 d_q48_16_from_int((i64)artifacts_seen));
        out_result->confidence_avg = dom_knowledge_clamp_ratio(d_q16_16_from_q48_16(div));
        div = d_q48_16_div(uncertainty_total,
                          d_q48_16_from_int((i64)artifacts_seen));
        out_result->uncertainty_avg = dom_knowledge_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (skills_seen > 0u) {
        q48_16 div = d_q48_16_div(variance_total,
                                 d_q48_16_from_int((i64)skills_seen));
        out_result->variance_reduction_avg = dom_knowledge_clamp_ratio(
            d_q16_16_from_q48_16(div));
        div = d_q48_16_div(bias_total,
                           d_q48_16_from_int((i64)skills_seen));
        out_result->failure_bias_reduction_avg = dom_knowledge_clamp_ratio(
            d_q16_16_from_q48_16(div));
    }
    return 0;
}

int dom_knowledge_domain_collapse_region(dom_knowledge_domain* domain, u32 region_id)
{
    dom_knowledge_macro_capsule capsule;
    u32 confidence_bins[DOM_KNOWLEDGE_HIST_BINS];
    u32 variance_bins[DOM_KNOWLEDGE_HIST_BINS];
    q48_16 confidence_total = 0;
    q48_16 variance_total = 0;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_knowledge_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_KNOWLEDGE_MAX_CAPSULES) {
        return -2;
    }
    memset(confidence_bins, 0, sizeof(confidence_bins));
    memset(variance_bins, 0, sizeof(variance_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;
    for (u32 i = 0u; i < domain->artifact_count; ++i) {
        if (domain->artifacts[i].region_id != region_id) {
            continue;
        }
        capsule.artifact_count += 1u;
        confidence_total = d_q48_16_add(confidence_total,
                                        d_q48_16_from_q16_16(domain->artifacts[i].confidence));
        confidence_bins[dom_knowledge_hist_bin(domain->artifacts[i].confidence)] += 1u;
    }
    for (u32 i = 0u; i < domain->skill_count; ++i) {
        if (domain->skills[i].region_id != region_id) {
            continue;
        }
        capsule.skill_count += 1u;
        variance_total = d_q48_16_add(variance_total,
                                      d_q48_16_from_q16_16(domain->skills[i].variance_reduction));
        variance_bins[dom_knowledge_hist_bin(domain->skills[i].variance_reduction)] += 1u;
    }
    for (u32 i = 0u; i < domain->program_count; ++i) {
        if (domain->programs[i].region_id != region_id) {
            continue;
        }
        capsule.program_count += 1u;
    }
    if (capsule.artifact_count > 0u) {
        q48_16 div = d_q48_16_div(confidence_total,
                                 d_q48_16_from_int((i64)capsule.artifact_count));
        capsule.confidence_avg = dom_knowledge_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (capsule.skill_count > 0u) {
        q48_16 div = d_q48_16_div(variance_total,
                                 d_q48_16_from_int((i64)capsule.skill_count));
        capsule.variance_reduction_avg = dom_knowledge_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    for (u32 b = 0u; b < DOM_KNOWLEDGE_HIST_BINS; ++b) {
        capsule.confidence_hist[b] = dom_knowledge_hist_bin_ratio(confidence_bins[b],
                                                                  capsule.artifact_count);
        capsule.variance_hist[b] = dom_knowledge_hist_bin_ratio(variance_bins[b],
                                                                capsule.skill_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_knowledge_domain_expand_region(dom_knowledge_domain* domain, u32 region_id)
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

u32 dom_knowledge_domain_capsule_count(const dom_knowledge_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_knowledge_macro_capsule* dom_knowledge_domain_capsule_at(const dom_knowledge_domain* domain,
                                                                   u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_knowledge_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
