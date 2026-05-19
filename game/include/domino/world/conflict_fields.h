/*
FILE: include/domino/world/conflict_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/conflict_fields
RESPONSIBILITY: Deterministic conflict, engagement, occupation, and morale field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by WAR0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_CONFLICT_FIELDS_H
#define DOMINO_WORLD_CONFLICT_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_CONFLICT_MAX_CONFLICTS 64u
#define DOM_CONFLICT_MAX_SIDES 128u
#define DOM_CONFLICT_MAX_EVENTS 256u
#define DOM_CONFLICT_MAX_FORCES 128u
#define DOM_CONFLICT_MAX_ENGAGEMENTS 128u
#define DOM_CONFLICT_MAX_OUTCOMES 128u
#define DOM_CONFLICT_MAX_OCCUPATIONS 64u
#define DOM_CONFLICT_MAX_RESISTANCE 128u
#define DOM_CONFLICT_MAX_MORALE 128u
#define DOM_CONFLICT_MAX_WEAPONS 128u
#define DOM_CONFLICT_MAX_REGIONS 16u
#define DOM_CONFLICT_MAX_CAPSULES 64u
#define DOM_CONFLICT_HIST_BINS 4u

#define DOM_CONFLICT_MAX_SIDE_REFS 4u
#define DOM_CONFLICT_MAX_EVENT_REFS 8u
#define DOM_CONFLICT_MAX_FORCE_REFS 8u
#define DOM_CONFLICT_MAX_INPUT_REFS 8u
#define DOM_CONFLICT_MAX_OUTPUT_REFS 8u
#define DOM_CONFLICT_MAX_EQUIPMENT_REFS 8u
#define DOM_CONFLICT_MAX_OUTCOME_REFS 8u
#define DOM_CONFLICT_MAX_INFLUENCE_REFS 8u

#define DOM_CONFLICT_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_conflict_status {
    DOM_CONFLICT_STATUS_UNSET = 0u,
    DOM_CONFLICT_STATUS_ACTIVE = 1u,
    DOM_CONFLICT_STATUS_SUSPENDED = 2u,
    DOM_CONFLICT_STATUS_RESOLVED = 3u
};

enum dom_conflict_event_type {
    DOM_CONFLICT_EVENT_UNSET = 0u,
    DOM_CONFLICT_EVENT_MOBILIZATION = 1u,
    DOM_CONFLICT_EVENT_DEPLOYMENT = 2u,
    DOM_CONFLICT_EVENT_ENGAGEMENT_RESOLUTION = 3u,
    DOM_CONFLICT_EVENT_ATTRITION = 4u,
    DOM_CONFLICT_EVENT_DEMOBILIZATION = 5u,
    DOM_CONFLICT_EVENT_SABOTAGE = 6u,
    DOM_CONFLICT_EVENT_OCCUPATION = 7u,
    DOM_CONFLICT_EVENT_RESISTANCE = 8u,
    DOM_CONFLICT_EVENT_SUPPRESSION = 9u
};

enum dom_conflict_force_type {
    DOM_CONFLICT_FORCE_UNSET = 0u,
    DOM_CONFLICT_FORCE_COHORT = 1u,
    DOM_CONFLICT_FORCE_MACHINE = 2u,
    DOM_CONFLICT_FORCE_MIXED = 3u
};

enum dom_conflict_occupation_status {
    DOM_CONFLICT_OCCUPATION_UNSET = 0u,
    DOM_CONFLICT_OCCUPATION_ACTIVE = 1u,
    DOM_CONFLICT_OCCUPATION_DEGRADING = 2u,
    DOM_CONFLICT_OCCUPATION_ENDED = 3u
};

enum dom_conflict_resistance_reason {
    DOM_CONFLICT_RESIST_UNSET = 0u,
    DOM_CONFLICT_RESIST_LEGITIMACY = 1u,
    DOM_CONFLICT_RESIST_LOGISTICS = 2u,
    DOM_CONFLICT_RESIST_ENFORCEMENT = 3u
};

enum dom_conflict_record_flags {
    DOM_CONFLICT_RECORD_UNRESOLVED = 1u << 0u,
    DOM_CONFLICT_RECORD_COLLAPSED = 1u << 1u
};

enum dom_conflict_side_flags {
    DOM_CONFLICT_SIDE_UNRESOLVED = 1u << 0u,
    DOM_CONFLICT_SIDE_COLLAPSED = 1u << 1u
};

enum dom_conflict_event_flags {
    DOM_CONFLICT_EVENT_UNRESOLVED = 1u << 0u,
    DOM_CONFLICT_EVENT_APPLIED = 1u << 1u,
    DOM_CONFLICT_EVENT_COLLAPSED = 1u << 2u
};

enum dom_conflict_force_flags {
    DOM_CONFLICT_FORCE_UNRESOLVED = 1u << 0u,
    DOM_CONFLICT_FORCE_COLLAPSED = 1u << 1u,
    DOM_CONFLICT_FORCE_EXHAUSTED = 1u << 2u
};

enum dom_engagement_flags {
    DOM_ENGAGEMENT_UNRESOLVED = 1u << 0u,
    DOM_ENGAGEMENT_COLLAPSED = 1u << 1u
};

enum dom_engagement_outcome_flags {
    DOM_OUTCOME_UNRESOLVED = 1u << 0u,
    DOM_OUTCOME_APPLIED = 1u << 1u,
    DOM_OUTCOME_COLLAPSED = 1u << 2u
};

enum dom_occupation_flags {
    DOM_OCCUPATION_UNRESOLVED = 1u << 0u,
    DOM_OCCUPATION_COLLAPSED = 1u << 1u
};

enum dom_resistance_flags {
    DOM_RESISTANCE_UNRESOLVED = 1u << 0u,
    DOM_RESISTANCE_APPLIED = 1u << 1u,
    DOM_RESISTANCE_COLLAPSED = 1u << 2u
};

enum dom_morale_flags {
    DOM_MORALE_UNRESOLVED = 1u << 0u,
    DOM_MORALE_COLLAPSED = 1u << 1u,
    DOM_MORALE_DECAYING = 1u << 2u
};

enum dom_weapon_flags {
    DOM_WEAPON_UNRESOLVED = 1u << 0u,
    DOM_WEAPON_COLLAPSED = 1u << 1u
};

enum dom_conflict_resolve_flags {
    DOM_CONFLICT_RESOLVE_PARTIAL = 1u << 0u,
    DOM_CONFLICT_RESOLVE_EVENT_APPLIED = 1u << 1u,
    DOM_CONFLICT_RESOLVE_SHORTAGE = 1u << 2u,
    DOM_CONFLICT_RESOLVE_LOW_MORALE = 1u << 3u,
    DOM_CONFLICT_RESOLVE_ILLEGITIMATE = 1u << 4u,
    DOM_CONFLICT_RESOLVE_RESISTANCE = 1u << 5u,
    DOM_CONFLICT_RESOLVE_ATTRITION = 1u << 6u
};

enum dom_conflict_refusal_reason {
    DOM_CONFLICT_REFUSE_NONE = 0u,
    DOM_CONFLICT_REFUSE_BUDGET = 1u,
    DOM_CONFLICT_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_CONFLICT_REFUSE_CONFLICT_MISSING = 3u,
    DOM_CONFLICT_REFUSE_SIDE_MISSING = 4u,
    DOM_CONFLICT_REFUSE_EVENT_MISSING = 5u,
    DOM_CONFLICT_REFUSE_FORCE_MISSING = 6u,
    DOM_CONFLICT_REFUSE_ENGAGEMENT_MISSING = 7u,
    DOM_CONFLICT_REFUSE_OUTCOME_MISSING = 8u,
    DOM_CONFLICT_REFUSE_OCCUPATION_MISSING = 9u,
    DOM_CONFLICT_REFUSE_RESISTANCE_MISSING = 10u,
    DOM_CONFLICT_REFUSE_MORALE_MISSING = 11u,
    DOM_CONFLICT_REFUSE_WEAPON_MISSING = 12u,
    DOM_CONFLICT_REFUSE_POLICY = 13u,
    DOM_CONFLICT_REFUSE_INTERNAL = 14u
};

typedef struct dom_conflict_record_desc {
    u32 conflict_id;
    u32 domain_id;
    u32 side_count;
    u32 side_ids[DOM_CONFLICT_MAX_SIDE_REFS];
    u64 start_tick;
    u32 status;
    u64 next_due_tick;
    u32 event_count;
    u32 event_ids[DOM_CONFLICT_MAX_EVENT_REFS];
    u32 provenance_id;
    u32 epistemic_scope_id;
    u32 region_id;
    u64 order_key;
} dom_conflict_record_desc;

typedef struct dom_conflict_side_desc {
    u32 side_id;
    u32 conflict_id;
    u32 authority_id;
    u32 force_count;
    u32 force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u32 objectives_ref_id;
    u32 logistics_dependency_id;
    q16_16 readiness_level;
    u32 readiness_state;
    u64 next_due_tick;
    u32 provenance_id;
    u32 region_id;
} dom_conflict_side_desc;

typedef struct dom_conflict_event_desc {
    u32 event_id;
    u32 conflict_id;
    u32 event_type;
    u64 scheduled_tick;
    u64 order_key;
    u32 participant_count;
    u32 participant_force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u32 input_ref_count;
    u32 input_refs[DOM_CONFLICT_MAX_INPUT_REFS];
    u32 output_ref_count;
    u32 output_refs[DOM_CONFLICT_MAX_OUTPUT_REFS];
    u32 provenance_id;
    u32 epistemic_scope_id;
    u32 region_id;
    u32 flags;
} dom_conflict_event_desc;

typedef struct dom_security_force_desc {
    u32 force_id;
    u32 authority_id;
    u32 force_type;
    q48_16 capacity;
    u32 equipment_count;
    u32 equipment_refs[DOM_CONFLICT_MAX_EQUIPMENT_REFS];
    q16_16 readiness;
    q16_16 morale;
    u32 logistics_dependency_id;
    u32 home_domain_id;
    u64 next_due_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_security_force_desc;

typedef struct dom_engagement_desc {
    u32 engagement_id;
    u32 conflict_id;
    u32 domain_id;
    u32 participant_count;
    u32 participant_force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u64 start_tick;
    u64 resolution_tick;
    u32 resolution_policy_id;
    u64 order_key;
    u32 logistics_count;
    u32 logistics_inputs[DOM_CONFLICT_MAX_INPUT_REFS];
    u32 legitimacy_scope_id;
    u32 epistemic_scope_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_engagement_desc;

typedef struct dom_engagement_outcome_desc {
    u32 outcome_id;
    u32 engagement_id;
    u32 casualty_count;
    u32 casualty_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 resource_delta_count;
    u32 resource_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 legitimacy_delta_count;
    u32 legitimacy_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 control_delta_count;
    u32 control_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 report_count;
    u32 report_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_engagement_outcome_desc;

typedef struct dom_occupation_condition_desc {
    u32 occupation_id;
    u32 occupier_authority_id;
    u32 occupied_jurisdiction_id;
    q16_16 enforcement_capacity;
    q16_16 legitimacy_support;
    u32 logistics_dependency_id;
    u64 start_tick;
    u64 next_due_tick;
    u32 status;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_occupation_condition_desc;

typedef struct dom_resistance_event_desc {
    u32 resistance_id;
    u32 occupation_id;
    u32 trigger_reason;
    u64 trigger_tick;
    u64 resolution_tick;
    u64 order_key;
    u32 outcome_count;
    u32 outcome_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_resistance_event_desc;

typedef struct dom_morale_field_desc {
    u32 morale_id;
    u32 subject_ref_id;
    u32 conflict_id;
    q16_16 morale_level;
    q16_16 decay_rate;
    u32 influence_count;
    u32 influence_refs[DOM_CONFLICT_MAX_INFLUENCE_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_morale_field_desc;

typedef struct dom_weapon_spec_desc {
    u32 weapon_id;
    u32 assembly_ref_id;
    q16_16 range;
    q16_16 rate;
    q16_16 effectiveness;
    q16_16 reliability;
    q48_16 energy_cost;
    u32 material_interaction_ref_id;
    u32 provenance_id;
    u32 flags;
} dom_weapon_spec_desc;

typedef struct dom_conflict_record {
    u32 conflict_id;
    u32 domain_id;
    u32 side_count;
    u32 side_ids[DOM_CONFLICT_MAX_SIDE_REFS];
    u64 start_tick;
    u32 status;
    u64 next_due_tick;
    u32 event_count;
    u32 event_ids[DOM_CONFLICT_MAX_EVENT_REFS];
    u32 provenance_id;
    u32 epistemic_scope_id;
    u32 region_id;
    u64 order_key;
    u32 flags; /* dom_conflict_record_flags */
} dom_conflict_record;

typedef struct dom_conflict_side {
    u32 side_id;
    u32 conflict_id;
    u32 authority_id;
    u32 force_count;
    u32 force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u32 objectives_ref_id;
    u32 logistics_dependency_id;
    q16_16 readiness_level;
    u32 readiness_state;
    u64 next_due_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_conflict_side_flags */
} dom_conflict_side;

typedef struct dom_conflict_event {
    u32 event_id;
    u32 conflict_id;
    u32 event_type;
    u64 scheduled_tick;
    u64 order_key;
    u32 participant_count;
    u32 participant_force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u32 input_ref_count;
    u32 input_refs[DOM_CONFLICT_MAX_INPUT_REFS];
    u32 output_ref_count;
    u32 output_refs[DOM_CONFLICT_MAX_OUTPUT_REFS];
    u32 provenance_id;
    u32 epistemic_scope_id;
    u32 region_id;
    u32 flags; /* dom_conflict_event_flags */
} dom_conflict_event;

typedef struct dom_security_force {
    u32 force_id;
    u32 authority_id;
    u32 force_type;
    q48_16 capacity;
    u32 equipment_count;
    u32 equipment_refs[DOM_CONFLICT_MAX_EQUIPMENT_REFS];
    q16_16 readiness;
    q16_16 morale;
    u32 logistics_dependency_id;
    u32 home_domain_id;
    u64 next_due_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_conflict_force_flags */
} dom_security_force;

typedef struct dom_engagement {
    u32 engagement_id;
    u32 conflict_id;
    u32 domain_id;
    u32 participant_count;
    u32 participant_force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u64 start_tick;
    u64 resolution_tick;
    u32 resolution_policy_id;
    u64 order_key;
    u32 logistics_count;
    u32 logistics_inputs[DOM_CONFLICT_MAX_INPUT_REFS];
    u32 legitimacy_scope_id;
    u32 epistemic_scope_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_engagement_flags */
} dom_engagement;

typedef struct dom_engagement_outcome {
    u32 outcome_id;
    u32 engagement_id;
    u32 casualty_count;
    u32 casualty_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 resource_delta_count;
    u32 resource_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 legitimacy_delta_count;
    u32 legitimacy_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 control_delta_count;
    u32 control_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 report_count;
    u32 report_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_engagement_outcome_flags */
} dom_engagement_outcome;

typedef struct dom_occupation_condition {
    u32 occupation_id;
    u32 occupier_authority_id;
    u32 occupied_jurisdiction_id;
    q16_16 enforcement_capacity;
    q16_16 legitimacy_support;
    u32 logistics_dependency_id;
    u64 start_tick;
    u64 next_due_tick;
    u32 status;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_occupation_flags */
} dom_occupation_condition;

typedef struct dom_resistance_event {
    u32 resistance_id;
    u32 occupation_id;
    u32 trigger_reason;
    u64 trigger_tick;
    u64 resolution_tick;
    u64 order_key;
    u32 outcome_count;
    u32 outcome_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_resistance_flags */
} dom_resistance_event;

typedef struct dom_morale_field {
    u32 morale_id;
    u32 subject_ref_id;
    u32 conflict_id;
    q16_16 morale_level;
    q16_16 decay_rate;
    u32 influence_count;
    u32 influence_refs[DOM_CONFLICT_MAX_INFLUENCE_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_morale_flags */
} dom_morale_field;

typedef struct dom_weapon_spec {
    u32 weapon_id;
    u32 assembly_ref_id;
    q16_16 range;
    q16_16 rate;
    q16_16 effectiveness;
    q16_16 reliability;
    q48_16 energy_cost;
    u32 material_interaction_ref_id;
    u32 provenance_id;
    u32 flags; /* dom_weapon_flags */
} dom_weapon_spec;

typedef struct dom_conflict_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 conflict_count;
    dom_conflict_record_desc conflicts[DOM_CONFLICT_MAX_CONFLICTS];
    u32 side_count;
    dom_conflict_side_desc sides[DOM_CONFLICT_MAX_SIDES];
    u32 event_count;
    dom_conflict_event_desc events[DOM_CONFLICT_MAX_EVENTS];
    u32 force_count;
    dom_security_force_desc forces[DOM_CONFLICT_MAX_FORCES];
    u32 engagement_count;
    dom_engagement_desc engagements[DOM_CONFLICT_MAX_ENGAGEMENTS];
    u32 outcome_count;
    dom_engagement_outcome_desc outcomes[DOM_CONFLICT_MAX_OUTCOMES];
    u32 occupation_count;
    dom_occupation_condition_desc occupations[DOM_CONFLICT_MAX_OCCUPATIONS];
    u32 resistance_count;
    dom_resistance_event_desc resistance_events[DOM_CONFLICT_MAX_RESISTANCE];
    u32 morale_count;
    dom_morale_field_desc morale_fields[DOM_CONFLICT_MAX_MORALE];
    u32 weapon_count;
    dom_weapon_spec_desc weapons[DOM_CONFLICT_MAX_WEAPONS];
} dom_conflict_surface_desc;

typedef struct dom_conflict_record_sample {
    u32 conflict_id;
    u32 domain_id;
    u32 side_count;
    u32 side_ids[DOM_CONFLICT_MAX_SIDE_REFS];
    u64 start_tick;
    u32 status;
    u64 next_due_tick;
    u32 event_count;
    u32 event_ids[DOM_CONFLICT_MAX_EVENT_REFS];
    u32 provenance_id;
    u32 epistemic_scope_id;
    u32 region_id;
    u64 order_key;
    u32 flags; /* dom_conflict_record_flags */
    dom_domain_query_meta meta;
} dom_conflict_record_sample;

typedef struct dom_conflict_side_sample {
    u32 side_id;
    u32 conflict_id;
    u32 authority_id;
    u32 force_count;
    u32 force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u32 objectives_ref_id;
    u32 logistics_dependency_id;
    q16_16 readiness_level;
    u32 readiness_state;
    u64 next_due_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_conflict_side_flags */
    dom_domain_query_meta meta;
} dom_conflict_side_sample;

typedef struct dom_conflict_event_sample {
    u32 event_id;
    u32 conflict_id;
    u32 event_type;
    u64 scheduled_tick;
    u64 order_key;
    u32 participant_count;
    u32 participant_force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u32 input_ref_count;
    u32 input_refs[DOM_CONFLICT_MAX_INPUT_REFS];
    u32 output_ref_count;
    u32 output_refs[DOM_CONFLICT_MAX_OUTPUT_REFS];
    u32 provenance_id;
    u32 epistemic_scope_id;
    u32 region_id;
    u32 flags; /* dom_conflict_event_flags */
    dom_domain_query_meta meta;
} dom_conflict_event_sample;

typedef struct dom_security_force_sample {
    u32 force_id;
    u32 authority_id;
    u32 force_type;
    q48_16 capacity;
    u32 equipment_count;
    u32 equipment_refs[DOM_CONFLICT_MAX_EQUIPMENT_REFS];
    q16_16 readiness;
    q16_16 morale;
    u32 logistics_dependency_id;
    u32 home_domain_id;
    u64 next_due_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_conflict_force_flags */
    dom_domain_query_meta meta;
} dom_security_force_sample;

typedef struct dom_engagement_sample {
    u32 engagement_id;
    u32 conflict_id;
    u32 domain_id;
    u32 participant_count;
    u32 participant_force_ids[DOM_CONFLICT_MAX_FORCE_REFS];
    u64 start_tick;
    u64 resolution_tick;
    u32 resolution_policy_id;
    u64 order_key;
    u32 logistics_count;
    u32 logistics_inputs[DOM_CONFLICT_MAX_INPUT_REFS];
    u32 legitimacy_scope_id;
    u32 epistemic_scope_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_engagement_flags */
    dom_domain_query_meta meta;
} dom_engagement_sample;

typedef struct dom_engagement_outcome_sample {
    u32 outcome_id;
    u32 engagement_id;
    u32 casualty_count;
    u32 casualty_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 resource_delta_count;
    u32 resource_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 legitimacy_delta_count;
    u32 legitimacy_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 control_delta_count;
    u32 control_deltas[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 report_count;
    u32 report_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_engagement_outcome_flags */
    dom_domain_query_meta meta;
} dom_engagement_outcome_sample;

typedef struct dom_occupation_condition_sample {
    u32 occupation_id;
    u32 occupier_authority_id;
    u32 occupied_jurisdiction_id;
    q16_16 enforcement_capacity;
    q16_16 legitimacy_support;
    u32 logistics_dependency_id;
    u64 start_tick;
    u64 next_due_tick;
    u32 status;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_occupation_flags */
    dom_domain_query_meta meta;
} dom_occupation_condition_sample;

typedef struct dom_resistance_event_sample {
    u32 resistance_id;
    u32 occupation_id;
    u32 trigger_reason;
    u64 trigger_tick;
    u64 resolution_tick;
    u64 order_key;
    u32 outcome_count;
    u32 outcome_refs[DOM_CONFLICT_MAX_OUTCOME_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_resistance_flags */
    dom_domain_query_meta meta;
} dom_resistance_event_sample;

typedef struct dom_morale_field_sample {
    u32 morale_id;
    u32 subject_ref_id;
    u32 conflict_id;
    q16_16 morale_level;
    q16_16 decay_rate;
    u32 influence_count;
    u32 influence_refs[DOM_CONFLICT_MAX_INFLUENCE_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_morale_flags */
    dom_domain_query_meta meta;
} dom_morale_field_sample;

typedef struct dom_weapon_spec_sample {
    u32 weapon_id;
    u32 assembly_ref_id;
    q16_16 range;
    q16_16 rate;
    q16_16 effectiveness;
    q16_16 reliability;
    q48_16 energy_cost;
    u32 material_interaction_ref_id;
    u32 provenance_id;
    u32 flags; /* dom_weapon_flags */
    dom_domain_query_meta meta;
} dom_weapon_spec_sample;

typedef struct dom_conflict_region_sample {
    u32 region_id;
    u32 conflict_count;
    u32 side_count;
    u32 event_count;
    u32 force_count;
    u32 engagement_count;
    u32 outcome_count;
    u32 occupation_count;
    u32 resistance_count;
    u32 morale_count;
    u32 weapon_count;
    q16_16 readiness_avg;
    q16_16 morale_avg;
    q16_16 legitimacy_avg;
    u32 flags; /* dom_conflict_resolve_flags */
    dom_domain_query_meta meta;
} dom_conflict_region_sample;

typedef struct dom_conflict_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_conflict_refusal_reason */
    u32 flags; /* dom_conflict_resolve_flags */
    u32 conflict_count;
    u32 side_count;
    u32 event_count;
    u32 event_applied_count;
    u32 force_count;
    u32 engagement_count;
    u32 outcome_count;
    u32 outcome_applied_count;
    u32 occupation_count;
    u32 resistance_count;
    u32 resistance_applied_count;
    u32 morale_count;
    u32 weapon_count;
    q16_16 readiness_avg;
    q16_16 morale_avg;
    q16_16 legitimacy_avg;
} dom_conflict_resolve_result;

typedef struct dom_conflict_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 conflict_count;
    u32 side_count;
    u32 event_count;
    u32 force_count;
    u32 engagement_count;
    u32 outcome_count;
    u32 occupation_count;
    u32 resistance_count;
    u32 morale_count;
    q16_16 readiness_avg;
    q16_16 morale_avg;
    q16_16 legitimacy_avg;
    q16_16 readiness_hist[DOM_CONFLICT_HIST_BINS];
    q16_16 morale_hist[DOM_CONFLICT_HIST_BINS];
    u32 rng_cursor[DOM_CONFLICT_HIST_BINS];
} dom_conflict_macro_capsule;

typedef struct dom_conflict_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_conflict_surface_desc surface;
    dom_conflict_record conflicts[DOM_CONFLICT_MAX_CONFLICTS];
    u32 conflict_count;
    dom_conflict_side sides[DOM_CONFLICT_MAX_SIDES];
    u32 side_count;
    dom_conflict_event events[DOM_CONFLICT_MAX_EVENTS];
    u32 event_count;
    dom_security_force forces[DOM_CONFLICT_MAX_FORCES];
    u32 force_count;
    dom_engagement engagements[DOM_CONFLICT_MAX_ENGAGEMENTS];
    u32 engagement_count;
    dom_engagement_outcome outcomes[DOM_CONFLICT_MAX_OUTCOMES];
    u32 outcome_count;
    dom_occupation_condition occupations[DOM_CONFLICT_MAX_OCCUPATIONS];
    u32 occupation_count;
    dom_resistance_event resistance_events[DOM_CONFLICT_MAX_RESISTANCE];
    u32 resistance_count;
    dom_morale_field morale_fields[DOM_CONFLICT_MAX_MORALE];
    u32 morale_count;
    dom_weapon_spec weapons[DOM_CONFLICT_MAX_WEAPONS];
    u32 weapon_count;
    dom_conflict_macro_capsule capsules[DOM_CONFLICT_MAX_CAPSULES];
    u32 capsule_count;
} dom_conflict_domain;

void dom_conflict_surface_desc_init(dom_conflict_surface_desc* desc);

void dom_conflict_domain_init(dom_conflict_domain* domain,
                              const dom_conflict_surface_desc* desc);
void dom_conflict_domain_free(dom_conflict_domain* domain);
void dom_conflict_domain_set_state(dom_conflict_domain* domain,
                                   u32 existence_state,
                                   u32 archival_state);
void dom_conflict_domain_set_policy(dom_conflict_domain* domain,
                                    const dom_domain_policy* policy);

int dom_conflict_record_query(const dom_conflict_domain* domain,
                              u32 conflict_id,
                              dom_domain_budget* budget,
                              dom_conflict_record_sample* out_sample);

int dom_conflict_side_query(const dom_conflict_domain* domain,
                            u32 side_id,
                            dom_domain_budget* budget,
                            dom_conflict_side_sample* out_sample);

int dom_conflict_event_query(const dom_conflict_domain* domain,
                             u32 event_id,
                             dom_domain_budget* budget,
                             dom_conflict_event_sample* out_sample);

int dom_security_force_query(const dom_conflict_domain* domain,
                             u32 force_id,
                             dom_domain_budget* budget,
                             dom_security_force_sample* out_sample);

int dom_engagement_query(const dom_conflict_domain* domain,
                         u32 engagement_id,
                         dom_domain_budget* budget,
                         dom_engagement_sample* out_sample);

int dom_engagement_outcome_query(const dom_conflict_domain* domain,
                                 u32 outcome_id,
                                 dom_domain_budget* budget,
                                 dom_engagement_outcome_sample* out_sample);

int dom_occupation_condition_query(const dom_conflict_domain* domain,
                                   u32 occupation_id,
                                   dom_domain_budget* budget,
                                   dom_occupation_condition_sample* out_sample);

int dom_resistance_event_query(const dom_conflict_domain* domain,
                               u32 resistance_id,
                               dom_domain_budget* budget,
                               dom_resistance_event_sample* out_sample);

int dom_morale_field_query(const dom_conflict_domain* domain,
                           u32 morale_id,
                           dom_domain_budget* budget,
                           dom_morale_field_sample* out_sample);

int dom_weapon_spec_query(const dom_conflict_domain* domain,
                          u32 weapon_id,
                          dom_domain_budget* budget,
                          dom_weapon_spec_sample* out_sample);

int dom_conflict_region_query(const dom_conflict_domain* domain,
                              u32 region_id,
                              dom_domain_budget* budget,
                              dom_conflict_region_sample* out_sample);

int dom_conflict_resolve(dom_conflict_domain* domain,
                         u32 region_id,
                         u64 tick,
                         u64 tick_delta,
                         dom_domain_budget* budget,
                         dom_conflict_resolve_result* out_result);

int dom_conflict_domain_collapse_region(dom_conflict_domain* domain, u32 region_id);
int dom_conflict_domain_expand_region(dom_conflict_domain* domain, u32 region_id);

u32 dom_conflict_domain_capsule_count(const dom_conflict_domain* domain);
const dom_conflict_macro_capsule* dom_conflict_domain_capsule_at(const dom_conflict_domain* domain,
                                                                 u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_CONFLICT_FIELDS_H */
