/*
FILE: tools/conflict/conflict_cli.cpp
MODULE: Dominium
PURPOSE: Conflict fixture CLI for deterministic conflict and war checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/conflict_fields.h"

#define CONFLICT_FIXTURE_HEADER "DOMINIUM_CONFLICT_FIXTURE_V1"

#define CONFLICT_VALIDATE_HEADER "DOMINIUM_CONFLICT_VALIDATE_V1"
#define CONFLICT_INSPECT_HEADER "DOMINIUM_CONFLICT_INSPECT_V1"
#define CONFLICT_RESOLVE_HEADER "DOMINIUM_CONFLICT_RESOLVE_V1"
#define CONFLICT_COLLAPSE_HEADER "DOMINIUM_CONFLICT_COLLAPSE_V1"

#define CONFLICT_PROVIDER_CHAIN \
    "records->sides->events->forces->engagements->outcomes->occupations->resistance->morale->weapons"

#define CONFLICT_LINE_MAX 512u

typedef struct conflict_fixture {
    char fixture_id[96];
    dom_conflict_surface_desc desc;
    dom_domain_policy policy;
    u32 policy_set;
    char record_names[DOM_CONFLICT_MAX_CONFLICTS][64];
    char side_names[DOM_CONFLICT_MAX_SIDES][64];
    char event_names[DOM_CONFLICT_MAX_EVENTS][64];
    char force_names[DOM_CONFLICT_MAX_FORCES][64];
    char engagement_names[DOM_CONFLICT_MAX_ENGAGEMENTS][64];
    char outcome_names[DOM_CONFLICT_MAX_OUTCOMES][64];
    char occupation_names[DOM_CONFLICT_MAX_OCCUPATIONS][64];
    char resistance_names[DOM_CONFLICT_MAX_RESISTANCE][64];
    char morale_names[DOM_CONFLICT_MAX_MORALE][64];
    char weapon_names[DOM_CONFLICT_MAX_WEAPONS][64];
    char region_names[DOM_CONFLICT_MAX_REGIONS][64];
    u32 region_ids[DOM_CONFLICT_MAX_REGIONS];
    u32 region_count;
} conflict_fixture;

static u64 conflict_hash_u64(u64 h, u64 v)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((v >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((v >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((v >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((v >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((v >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((v >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((v >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(v & 0xFFu);
    for (u32 i = 0u; i < 8u; ++i) {
        h ^= (u64)bytes[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 conflict_hash_u32(u64 h, u32 v)
{
    return conflict_hash_u64(h, (u64)v);
}

static u64 conflict_hash_q16(u64 h, q16_16 v)
{
    return conflict_hash_u64(h, (u64)(u32)v);
}

static u64 conflict_hash_q48(u64 h, q48_16 v)
{
    return conflict_hash_u64(h, (u64)v);
}

static char* conflict_trim(char* text)
{
    char* end;
    while (text && *text && isspace((unsigned char)*text)) {
        ++text;
    }
    if (!text || !*text) {
        return text;
    }
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) {
        --end;
    }
    *end = '\0';
    return text;
}

static int conflict_parse_u32(const char* text, u32* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoul(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u32)value;
    return 1;
}

static int conflict_parse_u64(const char* text, u64* out_value)
{
    char* end = 0;
    unsigned long long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoull(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u64)value;
    return 1;
}

static int conflict_parse_q16(const char* text, q16_16* out_value)
{
    char* end = 0;
    double value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtod(text, &end);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = d_q16_16_from_double(value);
    return 1;
}

static int conflict_parse_q48(const char* text, q48_16* out_value)
{
    char* end = 0;
    double value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtod(text, &end);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = d_q48_16_from_double(value);
    return 1;
}

static int conflict_parse_indexed_key(const char* key,
                                      const char* prefix,
                                      u32* out_index,
                                      const char** out_suffix)
{
    size_t len;
    char* end = 0;
    unsigned long idx;
    if (!key || !prefix || !out_index || !out_suffix) {
        return 0;
    }
    len = strlen(prefix);
    if (strncmp(key, prefix, len) != 0) {
        return 0;
    }
    idx = strtoul(key + len, &end, 10);
    if (!end || end == key + len || *end != '_') {
        return 0;
    }
    *out_index = (u32)idx;
    *out_suffix = end + 1;
    return 1;
}

static u32 conflict_parse_ref(const char* text)
{
    u32 value = 0u;
    if (!text) {
        return 0u;
    }
    if (conflict_parse_u32(text, &value)) {
        return value;
    }
    return d_rng_hash_str32(text);
}

static u32 conflict_status_from_text(const char* text)
{
    if (!text) {
        return DOM_CONFLICT_STATUS_UNSET;
    }
    if (strcmp(text, "active") == 0) return DOM_CONFLICT_STATUS_ACTIVE;
    if (strcmp(text, "suspended") == 0) return DOM_CONFLICT_STATUS_SUSPENDED;
    if (strcmp(text, "resolved") == 0) return DOM_CONFLICT_STATUS_RESOLVED;
    return DOM_CONFLICT_STATUS_UNSET;
}

static u32 conflict_status_parse(const char* text)
{
    u32 value = conflict_status_from_text(text);
    if (value != DOM_CONFLICT_STATUS_UNSET) {
        return value;
    }
    if (conflict_parse_u32(text, &value)) {
        return value;
    }
    return DOM_CONFLICT_STATUS_UNSET;
}

static u32 conflict_event_type_from_text(const char* text)
{
    if (!text) {
        return DOM_CONFLICT_EVENT_UNSET;
    }
    if (strcmp(text, "mobilization") == 0) return DOM_CONFLICT_EVENT_MOBILIZATION;
    if (strcmp(text, "deployment") == 0) return DOM_CONFLICT_EVENT_DEPLOYMENT;
    if (strcmp(text, "engagement_resolution") == 0) return DOM_CONFLICT_EVENT_ENGAGEMENT_RESOLUTION;
    if (strcmp(text, "attrition") == 0) return DOM_CONFLICT_EVENT_ATTRITION;
    if (strcmp(text, "demobilization") == 0) return DOM_CONFLICT_EVENT_DEMOBILIZATION;
    if (strcmp(text, "sabotage") == 0) return DOM_CONFLICT_EVENT_SABOTAGE;
    if (strcmp(text, "occupation") == 0) return DOM_CONFLICT_EVENT_OCCUPATION;
    if (strcmp(text, "resistance") == 0) return DOM_CONFLICT_EVENT_RESISTANCE;
    if (strcmp(text, "suppression") == 0) return DOM_CONFLICT_EVENT_SUPPRESSION;
    return DOM_CONFLICT_EVENT_UNSET;
}

static u32 conflict_event_type_parse(const char* text)
{
    u32 value = conflict_event_type_from_text(text);
    if (value != DOM_CONFLICT_EVENT_UNSET) {
        return value;
    }
    if (conflict_parse_u32(text, &value)) {
        return value;
    }
    return DOM_CONFLICT_EVENT_UNSET;
}

static u32 conflict_force_type_from_text(const char* text)
{
    if (!text) {
        return DOM_CONFLICT_FORCE_UNSET;
    }
    if (strcmp(text, "cohort") == 0) return DOM_CONFLICT_FORCE_COHORT;
    if (strcmp(text, "machine") == 0) return DOM_CONFLICT_FORCE_MACHINE;
    if (strcmp(text, "mixed") == 0) return DOM_CONFLICT_FORCE_MIXED;
    return DOM_CONFLICT_FORCE_UNSET;
}

static u32 conflict_force_type_parse(const char* text)
{
    u32 value = conflict_force_type_from_text(text);
    if (value != DOM_CONFLICT_FORCE_UNSET) {
        return value;
    }
    if (conflict_parse_u32(text, &value)) {
        return value;
    }
    return DOM_CONFLICT_FORCE_UNSET;
}

static u32 conflict_occupation_status_from_text(const char* text)
{
    if (!text) {
        return DOM_CONFLICT_OCCUPATION_UNSET;
    }
    if (strcmp(text, "active") == 0) return DOM_CONFLICT_OCCUPATION_ACTIVE;
    if (strcmp(text, "degrading") == 0) return DOM_CONFLICT_OCCUPATION_DEGRADING;
    if (strcmp(text, "ended") == 0) return DOM_CONFLICT_OCCUPATION_ENDED;
    return DOM_CONFLICT_OCCUPATION_UNSET;
}

static u32 conflict_occupation_status_parse(const char* text)
{
    u32 value = conflict_occupation_status_from_text(text);
    if (value != DOM_CONFLICT_OCCUPATION_UNSET) {
        return value;
    }
    if (conflict_parse_u32(text, &value)) {
        return value;
    }
    return DOM_CONFLICT_OCCUPATION_UNSET;
}

static u32 conflict_resistance_reason_from_text(const char* text)
{
    if (!text) {
        return DOM_CONFLICT_RESIST_UNSET;
    }
    if (strcmp(text, "legitimacy") == 0) return DOM_CONFLICT_RESIST_LEGITIMACY;
    if (strcmp(text, "logistics") == 0) return DOM_CONFLICT_RESIST_LOGISTICS;
    if (strcmp(text, "enforcement") == 0) return DOM_CONFLICT_RESIST_ENFORCEMENT;
    return DOM_CONFLICT_RESIST_UNSET;
}

static u32 conflict_resistance_reason_parse(const char* text)
{
    u32 value = conflict_resistance_reason_from_text(text);
    if (value != DOM_CONFLICT_RESIST_UNSET) {
        return value;
    }
    if (conflict_parse_u32(text, &value)) {
        return value;
    }
    return DOM_CONFLICT_RESIST_UNSET;
}

static void conflict_fixture_init(conflict_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_conflict_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "conflict.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void conflict_fixture_register_region(conflict_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_CONFLICT_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int conflict_fixture_apply_record(conflict_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_conflict_record_desc* record;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_CONFLICTS) {
        return 0;
    }
    if (fixture->desc.conflict_count <= index) {
        fixture->desc.conflict_count = index + 1u;
    }
    record = &fixture->desc.conflicts[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->record_names[index], value, sizeof(fixture->record_names[index]) - 1);
        fixture->record_names[index][sizeof(fixture->record_names[index]) - 1] = '\0';
        record->conflict_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "domain") == 0) {
        record->domain_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "side_count") == 0) {
        return conflict_parse_u32(value, &record->side_count);
    }
    if (conflict_parse_indexed_key(suffix, "side", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_SIDE_REFS) {
            return 0;
        }
        if (record->side_count <= sub_index) {
            record->side_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            record->side_ids[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "start_tick") == 0 || strcmp(suffix, "start") == 0) {
        return conflict_parse_u64(value, &record->start_tick);
    }
    if (strcmp(suffix, "status") == 0) {
        record->status = conflict_status_parse(value);
        return 1;
    }
    if (strcmp(suffix, "next_due") == 0 || strcmp(suffix, "next_due_tick") == 0) {
        return conflict_parse_u64(value, &record->next_due_tick);
    }
    if (strcmp(suffix, "event_count") == 0) {
        return conflict_parse_u32(value, &record->event_count);
    }
    if (conflict_parse_indexed_key(suffix, "event", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_EVENT_REFS) {
            return 0;
        }
        if (record->event_count <= sub_index) {
            record->event_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            record->event_ids[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "provenance") == 0) {
        record->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "epistemic_scope") == 0) {
        record->epistemic_scope_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        record->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "order_key") == 0) {
        return conflict_parse_u64(value, &record->order_key);
    }
    return 0;
}

static int conflict_fixture_apply_side(conflict_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_conflict_side_desc* side;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_SIDES) {
        return 0;
    }
    if (fixture->desc.side_count <= index) {
        fixture->desc.side_count = index + 1u;
    }
    side = &fixture->desc.sides[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->side_names[index], value, sizeof(fixture->side_names[index]) - 1);
        fixture->side_names[index][sizeof(fixture->side_names[index]) - 1] = '\0';
        side->side_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "conflict") == 0) {
        side->conflict_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "authority") == 0) {
        side->authority_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "force_count") == 0) {
        return conflict_parse_u32(value, &side->force_count);
    }
    if (conflict_parse_indexed_key(suffix, "force", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_FORCE_REFS) {
            return 0;
        }
        if (side->force_count <= sub_index) {
            side->force_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            side->force_ids[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "objectives") == 0) {
        side->objectives_ref_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "logistics_dependency") == 0) {
        side->logistics_dependency_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "readiness") == 0) {
        return conflict_parse_q16(value, &side->readiness_level);
    }
    if (strcmp(suffix, "readiness_state") == 0) {
        return conflict_parse_u32(value, &side->readiness_state);
    }
    if (strcmp(suffix, "next_due") == 0 || strcmp(suffix, "next_due_tick") == 0) {
        return conflict_parse_u64(value, &side->next_due_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        side->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        side->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int conflict_fixture_apply_event(conflict_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_conflict_event_desc* event;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_EVENTS) {
        return 0;
    }
    if (fixture->desc.event_count <= index) {
        fixture->desc.event_count = index + 1u;
    }
    event = &fixture->desc.events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->event_names[index], value, sizeof(fixture->event_names[index]) - 1);
        fixture->event_names[index][sizeof(fixture->event_names[index]) - 1] = '\0';
        event->event_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "conflict") == 0) {
        event->conflict_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        event->event_type = conflict_event_type_parse(value);
        return 1;
    }
    if (strcmp(suffix, "scheduled") == 0 || strcmp(suffix, "scheduled_tick") == 0) {
        return conflict_parse_u64(value, &event->scheduled_tick);
    }
    if (strcmp(suffix, "order_key") == 0) {
        return conflict_parse_u64(value, &event->order_key);
    }
    if (strcmp(suffix, "participant_count") == 0) {
        return conflict_parse_u32(value, &event->participant_count);
    }
    if (conflict_parse_indexed_key(suffix, "participant", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_FORCE_REFS) {
            return 0;
        }
        if (event->participant_count <= sub_index) {
            event->participant_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            event->participant_force_ids[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "input_count") == 0) {
        return conflict_parse_u32(value, &event->input_ref_count);
    }
    if (conflict_parse_indexed_key(suffix, "input", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_INPUT_REFS) {
            return 0;
        }
        if (event->input_ref_count <= sub_index) {
            event->input_ref_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            event->input_refs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "output_count") == 0) {
        return conflict_parse_u32(value, &event->output_ref_count);
    }
    if (conflict_parse_indexed_key(suffix, "output", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_OUTPUT_REFS) {
            return 0;
        }
        if (event->output_ref_count <= sub_index) {
            event->output_ref_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            event->output_refs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "provenance") == 0) {
        event->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "epistemic_scope") == 0) {
        event->epistemic_scope_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        event->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &event->flags);
    }
    return 0;
}

static int conflict_fixture_apply_force(conflict_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_security_force_desc* force;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_FORCES) {
        return 0;
    }
    if (fixture->desc.force_count <= index) {
        fixture->desc.force_count = index + 1u;
    }
    force = &fixture->desc.forces[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->force_names[index], value, sizeof(fixture->force_names[index]) - 1);
        fixture->force_names[index][sizeof(fixture->force_names[index]) - 1] = '\0';
        force->force_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "authority") == 0) {
        force->authority_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        force->force_type = conflict_force_type_parse(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        return conflict_parse_q48(value, &force->capacity);
    }
    if (strcmp(suffix, "equipment_count") == 0) {
        return conflict_parse_u32(value, &force->equipment_count);
    }
    if (conflict_parse_indexed_key(suffix, "equipment", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_EQUIPMENT_REFS) {
            return 0;
        }
        if (force->equipment_count <= sub_index) {
            force->equipment_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            force->equipment_refs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "readiness") == 0) {
        return conflict_parse_q16(value, &force->readiness);
    }
    if (strcmp(suffix, "morale") == 0) {
        return conflict_parse_q16(value, &force->morale);
    }
    if (strcmp(suffix, "logistics_dependency") == 0) {
        force->logistics_dependency_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "home_domain") == 0) {
        force->home_domain_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "next_due") == 0 || strcmp(suffix, "next_due_tick") == 0) {
        return conflict_parse_u64(value, &force->next_due_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        force->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        force->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &force->flags);
    }
    return 0;
}

static int conflict_fixture_apply_engagement(conflict_fixture* fixture,
                                             u32 index,
                                             const char* suffix,
                                             const char* value)
{
    dom_engagement_desc* engagement;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_ENGAGEMENTS) {
        return 0;
    }
    if (fixture->desc.engagement_count <= index) {
        fixture->desc.engagement_count = index + 1u;
    }
    engagement = &fixture->desc.engagements[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->engagement_names[index], value, sizeof(fixture->engagement_names[index]) - 1);
        fixture->engagement_names[index][sizeof(fixture->engagement_names[index]) - 1] = '\0';
        engagement->engagement_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "conflict") == 0) {
        engagement->conflict_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "domain") == 0) {
        engagement->domain_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "participant_count") == 0) {
        return conflict_parse_u32(value, &engagement->participant_count);
    }
    if (conflict_parse_indexed_key(suffix, "participant", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_FORCE_REFS) {
            return 0;
        }
        if (engagement->participant_count <= sub_index) {
            engagement->participant_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            engagement->participant_force_ids[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "start") == 0 || strcmp(suffix, "start_tick") == 0) {
        return conflict_parse_u64(value, &engagement->start_tick);
    }
    if (strcmp(suffix, "resolution") == 0 || strcmp(suffix, "resolution_tick") == 0) {
        return conflict_parse_u64(value, &engagement->resolution_tick);
    }
    if (strcmp(suffix, "resolution_policy") == 0) {
        engagement->resolution_policy_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "order_key") == 0) {
        return conflict_parse_u64(value, &engagement->order_key);
    }
    if (strcmp(suffix, "logistics_count") == 0) {
        return conflict_parse_u32(value, &engagement->logistics_count);
    }
    if (conflict_parse_indexed_key(suffix, "logistics", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_INPUT_REFS) {
            return 0;
        }
        if (engagement->logistics_count <= sub_index) {
            engagement->logistics_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            engagement->logistics_inputs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "legitimacy_scope") == 0) {
        engagement->legitimacy_scope_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "epistemic_scope") == 0) {
        engagement->epistemic_scope_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        engagement->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        engagement->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &engagement->flags);
    }
    return 0;
}

static int conflict_fixture_apply_outcome(conflict_fixture* fixture,
                                          u32 index,
                                          const char* suffix,
                                          const char* value)
{
    dom_engagement_outcome_desc* outcome;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_OUTCOMES) {
        return 0;
    }
    if (fixture->desc.outcome_count <= index) {
        fixture->desc.outcome_count = index + 1u;
    }
    outcome = &fixture->desc.outcomes[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->outcome_names[index], value, sizeof(fixture->outcome_names[index]) - 1);
        fixture->outcome_names[index][sizeof(fixture->outcome_names[index]) - 1] = '\0';
        outcome->outcome_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "engagement") == 0) {
        outcome->engagement_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "casualty_count") == 0) {
        return conflict_parse_u32(value, &outcome->casualty_count);
    }
    if (conflict_parse_indexed_key(suffix, "casualty", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->casualty_count <= sub_index) {
            outcome->casualty_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            outcome->casualty_refs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "resource_delta_count") == 0) {
        return conflict_parse_u32(value, &outcome->resource_delta_count);
    }
    if (conflict_parse_indexed_key(suffix, "resource_delta", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->resource_delta_count <= sub_index) {
            outcome->resource_delta_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            outcome->resource_deltas[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "legitimacy_delta_count") == 0) {
        return conflict_parse_u32(value, &outcome->legitimacy_delta_count);
    }
    if (conflict_parse_indexed_key(suffix, "legitimacy_delta", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->legitimacy_delta_count <= sub_index) {
            outcome->legitimacy_delta_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            outcome->legitimacy_deltas[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "control_delta_count") == 0) {
        return conflict_parse_u32(value, &outcome->control_delta_count);
    }
    if (conflict_parse_indexed_key(suffix, "control_delta", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->control_delta_count <= sub_index) {
            outcome->control_delta_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            outcome->control_deltas[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "report_count") == 0) {
        return conflict_parse_u32(value, &outcome->report_count);
    }
    if (conflict_parse_indexed_key(suffix, "report", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->report_count <= sub_index) {
            outcome->report_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            outcome->report_refs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "provenance") == 0) {
        outcome->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        outcome->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &outcome->flags);
    }
    return 0;
}

static int conflict_fixture_apply_occupation(conflict_fixture* fixture,
                                             u32 index,
                                             const char* suffix,
                                             const char* value)
{
    dom_occupation_condition_desc* occupation;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_OCCUPATIONS) {
        return 0;
    }
    if (fixture->desc.occupation_count <= index) {
        fixture->desc.occupation_count = index + 1u;
    }
    occupation = &fixture->desc.occupations[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->occupation_names[index], value, sizeof(fixture->occupation_names[index]) - 1);
        fixture->occupation_names[index][sizeof(fixture->occupation_names[index]) - 1] = '\0';
        occupation->occupation_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "occupier") == 0) {
        occupation->occupier_authority_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "occupied") == 0) {
        occupation->occupied_jurisdiction_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "enforcement") == 0) {
        return conflict_parse_q16(value, &occupation->enforcement_capacity);
    }
    if (strcmp(suffix, "legitimacy") == 0) {
        return conflict_parse_q16(value, &occupation->legitimacy_support);
    }
    if (strcmp(suffix, "logistics_dependency") == 0) {
        occupation->logistics_dependency_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "start") == 0 || strcmp(suffix, "start_tick") == 0) {
        return conflict_parse_u64(value, &occupation->start_tick);
    }
    if (strcmp(suffix, "next_due") == 0 || strcmp(suffix, "next_due_tick") == 0) {
        return conflict_parse_u64(value, &occupation->next_due_tick);
    }
    if (strcmp(suffix, "status") == 0) {
        occupation->status = conflict_occupation_status_parse(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        occupation->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        occupation->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &occupation->flags);
    }
    return 0;
}

static int conflict_fixture_apply_resistance(conflict_fixture* fixture,
                                             u32 index,
                                             const char* suffix,
                                             const char* value)
{
    dom_resistance_event_desc* resistance;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_RESISTANCE) {
        return 0;
    }
    if (fixture->desc.resistance_count <= index) {
        fixture->desc.resistance_count = index + 1u;
    }
    resistance = &fixture->desc.resistance_events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->resistance_names[index], value, sizeof(fixture->resistance_names[index]) - 1);
        fixture->resistance_names[index][sizeof(fixture->resistance_names[index]) - 1] = '\0';
        resistance->resistance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "occupation") == 0) {
        resistance->occupation_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "reason") == 0) {
        resistance->trigger_reason = conflict_resistance_reason_parse(value);
        return 1;
    }
    if (strcmp(suffix, "trigger") == 0 || strcmp(suffix, "trigger_tick") == 0) {
        return conflict_parse_u64(value, &resistance->trigger_tick);
    }
    if (strcmp(suffix, "resolution") == 0 || strcmp(suffix, "resolution_tick") == 0) {
        return conflict_parse_u64(value, &resistance->resolution_tick);
    }
    if (strcmp(suffix, "order_key") == 0) {
        return conflict_parse_u64(value, &resistance->order_key);
    }
    if (strcmp(suffix, "outcome_count") == 0) {
        return conflict_parse_u32(value, &resistance->outcome_count);
    }
    if (conflict_parse_indexed_key(suffix, "outcome", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (resistance->outcome_count <= sub_index) {
            resistance->outcome_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            resistance->outcome_refs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "provenance") == 0) {
        resistance->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        resistance->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &resistance->flags);
    }
    return 0;
}

static int conflict_fixture_apply_morale(conflict_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_morale_field_desc* morale;
    u32 sub_index = 0u;
    const char* sub_suffix = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_MORALE) {
        return 0;
    }
    if (fixture->desc.morale_count <= index) {
        fixture->desc.morale_count = index + 1u;
    }
    morale = &fixture->desc.morale_fields[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->morale_names[index], value, sizeof(fixture->morale_names[index]) - 1);
        fixture->morale_names[index][sizeof(fixture->morale_names[index]) - 1] = '\0';
        morale->morale_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        morale->subject_ref_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "conflict") == 0) {
        morale->conflict_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "morale") == 0) {
        return conflict_parse_q16(value, &morale->morale_level);
    }
    if (strcmp(suffix, "decay") == 0) {
        return conflict_parse_q16(value, &morale->decay_rate);
    }
    if (strcmp(suffix, "influence_count") == 0) {
        return conflict_parse_u32(value, &morale->influence_count);
    }
    if (conflict_parse_indexed_key(suffix, "influence", &sub_index, &sub_suffix)) {
        if (sub_index >= DOM_CONFLICT_MAX_INFLUENCE_REFS) {
            return 0;
        }
        if (morale->influence_count <= sub_index) {
            morale->influence_count = sub_index + 1u;
        }
        if (strcmp(sub_suffix, "id") == 0) {
            morale->influence_refs[sub_index] = conflict_parse_ref(value);
            return 1;
        }
        return 0;
    }
    if (strcmp(suffix, "provenance") == 0) {
        morale->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        morale->region_id = region_id;
        conflict_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &morale->flags);
    }
    return 0;
}

static int conflict_fixture_apply_weapon(conflict_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_weapon_spec_desc* weapon;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CONFLICT_MAX_WEAPONS) {
        return 0;
    }
    if (fixture->desc.weapon_count <= index) {
        fixture->desc.weapon_count = index + 1u;
    }
    weapon = &fixture->desc.weapons[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->weapon_names[index], value, sizeof(fixture->weapon_names[index]) - 1);
        fixture->weapon_names[index][sizeof(fixture->weapon_names[index]) - 1] = '\0';
        weapon->weapon_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "assembly") == 0) {
        weapon->assembly_ref_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "range") == 0) {
        return conflict_parse_q16(value, &weapon->range);
    }
    if (strcmp(suffix, "rate") == 0) {
        return conflict_parse_q16(value, &weapon->rate);
    }
    if (strcmp(suffix, "effectiveness") == 0) {
        return conflict_parse_q16(value, &weapon->effectiveness);
    }
    if (strcmp(suffix, "reliability") == 0) {
        return conflict_parse_q16(value, &weapon->reliability);
    }
    if (strcmp(suffix, "energy_cost") == 0) {
        return conflict_parse_q48(value, &weapon->energy_cost);
    }
    if (strcmp(suffix, "material_interaction") == 0) {
        weapon->material_interaction_ref_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        weapon->provenance_id = conflict_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return conflict_parse_u32(value, &weapon->flags);
    }
    return 0;
}

static int conflict_fixture_apply(conflict_fixture* fixture, const char* key, const char* value)
{
    u32 index = 0u;
    const char* suffix = 0;
    if (!fixture || !key || !value) {
        return 0;
    }
    if (strcmp(key, "fixture_id") == 0) {
        strncpy(fixture->fixture_id, value, sizeof(fixture->fixture_id) - 1);
        fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
        return 1;
    }
    if (strcmp(key, "world_seed") == 0) {
        return conflict_parse_u64(value, &fixture->desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return conflict_parse_u64(value, &fixture->desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return conflict_parse_q16(value, &fixture->desc.meters_per_unit);
    }
    if (strcmp(key, "conflict_count") == 0 || strcmp(key, "record_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.conflict_count);
    }
    if (strcmp(key, "side_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.side_count);
    }
    if (strcmp(key, "event_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.event_count);
    }
    if (strcmp(key, "force_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.force_count);
    }
    if (strcmp(key, "engagement_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.engagement_count);
    }
    if (strcmp(key, "outcome_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.outcome_count);
    }
    if (strcmp(key, "occupation_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.occupation_count);
    }
    if (strcmp(key, "resistance_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.resistance_count);
    }
    if (strcmp(key, "morale_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.morale_count);
    }
    if (strcmp(key, "weapon_count") == 0) {
        return conflict_parse_u32(value, &fixture->desc.weapon_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return conflict_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return conflict_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return conflict_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return conflict_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (conflict_parse_indexed_key(key, "record", &index, &suffix)) {
        return conflict_fixture_apply_record(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "side", &index, &suffix)) {
        return conflict_fixture_apply_side(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "event", &index, &suffix)) {
        return conflict_fixture_apply_event(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "force", &index, &suffix)) {
        return conflict_fixture_apply_force(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "engagement", &index, &suffix)) {
        return conflict_fixture_apply_engagement(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "outcome", &index, &suffix)) {
        return conflict_fixture_apply_outcome(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "occupation", &index, &suffix)) {
        return conflict_fixture_apply_occupation(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "resistance", &index, &suffix)) {
        return conflict_fixture_apply_resistance(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "morale", &index, &suffix)) {
        return conflict_fixture_apply_morale(fixture, index, suffix, value);
    }
    if (conflict_parse_indexed_key(key, "weapon", &index, &suffix)) {
        return conflict_fixture_apply_weapon(fixture, index, suffix, value);
    }
    return 0;
}

static int conflict_fixture_load(const char* path, conflict_fixture* out_fixture)
{
    FILE* file;
    char line[CONFLICT_LINE_MAX];
    int header_ok = 0;
    conflict_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    conflict_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = conflict_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, CONFLICT_FIXTURE_HEADER) != 0) {
                fclose(file);
                return 0;
            }
            header_ok = 1;
            continue;
        }
        eq = strchr(text, '=');
        if (!eq) {
            continue;
        }
        *eq++ = '\0';
        conflict_fixture_apply(&fixture, conflict_trim(text), conflict_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* conflict_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 conflict_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = conflict_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && conflict_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 conflict_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = conflict_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && conflict_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 conflict_find_region_id(const conflict_fixture* fixture, const char* name)
{
    if (!name || !*name) {
        return 0u;
    }
    if (!fixture) {
        return d_rng_hash_str32(name);
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (strcmp(fixture->region_names[i], name) == 0) {
            return fixture->region_ids[i];
        }
    }
    return d_rng_hash_str32(name);
}

static const char* conflict_lookup_record_name(const conflict_fixture* fixture, u32 record_id)
{
    if (!fixture || record_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.conflict_count; ++i) {
        if (fixture->desc.conflicts[i].conflict_id == record_id) {
            return fixture->record_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_side_name(const conflict_fixture* fixture, u32 side_id)
{
    if (!fixture || side_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.side_count; ++i) {
        if (fixture->desc.sides[i].side_id == side_id) {
            return fixture->side_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_event_name(const conflict_fixture* fixture, u32 event_id)
{
    if (!fixture || event_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.event_count; ++i) {
        if (fixture->desc.events[i].event_id == event_id) {
            return fixture->event_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_force_name(const conflict_fixture* fixture, u32 force_id)
{
    if (!fixture || force_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.force_count; ++i) {
        if (fixture->desc.forces[i].force_id == force_id) {
            return fixture->force_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_engagement_name(const conflict_fixture* fixture, u32 engagement_id)
{
    if (!fixture || engagement_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.engagement_count; ++i) {
        if (fixture->desc.engagements[i].engagement_id == engagement_id) {
            return fixture->engagement_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_outcome_name(const conflict_fixture* fixture, u32 outcome_id)
{
    if (!fixture || outcome_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.outcome_count; ++i) {
        if (fixture->desc.outcomes[i].outcome_id == outcome_id) {
            return fixture->outcome_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_occupation_name(const conflict_fixture* fixture, u32 occupation_id)
{
    if (!fixture || occupation_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.occupation_count; ++i) {
        if (fixture->desc.occupations[i].occupation_id == occupation_id) {
            return fixture->occupation_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_resistance_name(const conflict_fixture* fixture, u32 resistance_id)
{
    if (!fixture || resistance_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.resistance_count; ++i) {
        if (fixture->desc.resistance_events[i].resistance_id == resistance_id) {
            return fixture->resistance_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_morale_name(const conflict_fixture* fixture, u32 morale_id)
{
    if (!fixture || morale_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.morale_count; ++i) {
        if (fixture->desc.morale_fields[i].morale_id == morale_id) {
            return fixture->morale_names[i];
        }
    }
    return "";
}

static const char* conflict_lookup_weapon_name(const conflict_fixture* fixture, u32 weapon_id)
{
    if (!fixture || weapon_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->desc.weapon_count; ++i) {
        if (fixture->desc.weapons[i].weapon_id == weapon_id) {
            return fixture->weapon_names[i];
        }
    }
    return "";
}

static int conflict_ratio_valid(q16_16 value)
{
    return !(value < 0 || value > DOM_CONFLICT_RATIO_ONE_Q16);
}

static int conflict_validate_fixture(const conflict_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->desc.conflict_count > DOM_CONFLICT_MAX_CONFLICTS) {
        return 0;
    }
    if (fixture->desc.side_count > DOM_CONFLICT_MAX_SIDES) {
        return 0;
    }
    if (fixture->desc.event_count > DOM_CONFLICT_MAX_EVENTS) {
        return 0;
    }
    if (fixture->desc.force_count > DOM_CONFLICT_MAX_FORCES) {
        return 0;
    }
    if (fixture->desc.engagement_count > DOM_CONFLICT_MAX_ENGAGEMENTS) {
        return 0;
    }
    if (fixture->desc.outcome_count > DOM_CONFLICT_MAX_OUTCOMES) {
        return 0;
    }
    if (fixture->desc.occupation_count > DOM_CONFLICT_MAX_OCCUPATIONS) {
        return 0;
    }
    if (fixture->desc.resistance_count > DOM_CONFLICT_MAX_RESISTANCE) {
        return 0;
    }
    if (fixture->desc.morale_count > DOM_CONFLICT_MAX_MORALE) {
        return 0;
    }
    if (fixture->desc.weapon_count > DOM_CONFLICT_MAX_WEAPONS) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->desc.conflict_count; ++i) {
        const dom_conflict_record_desc* record = &fixture->desc.conflicts[i];
        if (record->conflict_id == 0u) {
            return 0;
        }
        if (record->side_count > DOM_CONFLICT_MAX_SIDE_REFS) {
            return 0;
        }
        if (record->event_count > DOM_CONFLICT_MAX_EVENT_REFS) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.side_count; ++i) {
        const dom_conflict_side_desc* side = &fixture->desc.sides[i];
        if (side->side_id == 0u) {
            return 0;
        }
        if (side->force_count > DOM_CONFLICT_MAX_FORCE_REFS) {
            return 0;
        }
        if (!conflict_ratio_valid(side->readiness_level)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.event_count; ++i) {
        const dom_conflict_event_desc* event = &fixture->desc.events[i];
        if (event->event_id == 0u) {
            return 0;
        }
        if (event->event_type == DOM_CONFLICT_EVENT_UNSET) {
            return 0;
        }
        if (event->participant_count > DOM_CONFLICT_MAX_FORCE_REFS) {
            return 0;
        }
        if (event->input_ref_count > DOM_CONFLICT_MAX_INPUT_REFS) {
            return 0;
        }
        if (event->output_ref_count > DOM_CONFLICT_MAX_OUTPUT_REFS) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.force_count; ++i) {
        const dom_security_force_desc* force = &fixture->desc.forces[i];
        if (force->force_id == 0u) {
            return 0;
        }
        if (force->force_type == DOM_CONFLICT_FORCE_UNSET) {
            return 0;
        }
        if (force->equipment_count > DOM_CONFLICT_MAX_EQUIPMENT_REFS) {
            return 0;
        }
        if (!conflict_ratio_valid(force->readiness)) {
            return 0;
        }
        if (!conflict_ratio_valid(force->morale)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.engagement_count; ++i) {
        const dom_engagement_desc* engagement = &fixture->desc.engagements[i];
        if (engagement->engagement_id == 0u) {
            return 0;
        }
        if (engagement->participant_count > DOM_CONFLICT_MAX_FORCE_REFS) {
            return 0;
        }
        if (engagement->logistics_count > DOM_CONFLICT_MAX_INPUT_REFS) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.outcome_count; ++i) {
        const dom_engagement_outcome_desc* outcome = &fixture->desc.outcomes[i];
        if (outcome->outcome_id == 0u) {
            return 0;
        }
        if (outcome->casualty_count > DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->resource_delta_count > DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->legitimacy_delta_count > DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->control_delta_count > DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
        if (outcome->report_count > DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.occupation_count; ++i) {
        const dom_occupation_condition_desc* occupation = &fixture->desc.occupations[i];
        if (occupation->occupation_id == 0u) {
            return 0;
        }
        if (occupation->status == DOM_CONFLICT_OCCUPATION_UNSET) {
            return 0;
        }
        if (!conflict_ratio_valid(occupation->legitimacy_support)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.resistance_count; ++i) {
        const dom_resistance_event_desc* resistance = &fixture->desc.resistance_events[i];
        if (resistance->resistance_id == 0u) {
            return 0;
        }
        if (resistance->trigger_reason == DOM_CONFLICT_RESIST_UNSET) {
            return 0;
        }
        if (resistance->outcome_count > DOM_CONFLICT_MAX_OUTCOME_REFS) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.morale_count; ++i) {
        const dom_morale_field_desc* morale = &fixture->desc.morale_fields[i];
        if (morale->morale_id == 0u) {
            return 0;
        }
        if (!conflict_ratio_valid(morale->morale_level)) {
            return 0;
        }
        if (!conflict_ratio_valid(morale->decay_rate)) {
            return 0;
        }
        if (morale->influence_count > DOM_CONFLICT_MAX_INFLUENCE_REFS) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->desc.weapon_count; ++i) {
        const dom_weapon_spec_desc* weapon = &fixture->desc.weapons[i];
        if (weapon->weapon_id == 0u) {
            return 0;
        }
        if (!conflict_ratio_valid(weapon->effectiveness)) {
            return 0;
        }
        if (!conflict_ratio_valid(weapon->reliability)) {
            return 0;
        }
    }
    return 1;
}

static int conflict_run_validate(const conflict_fixture* fixture)
{
    int ok = conflict_validate_fixture(fixture);
    printf("%s\n", CONFLICT_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("conflict_count=%u\n", (unsigned int)fixture->desc.conflict_count);
    printf("side_count=%u\n", (unsigned int)fixture->desc.side_count);
    printf("event_count=%u\n", (unsigned int)fixture->desc.event_count);
    printf("force_count=%u\n", (unsigned int)fixture->desc.force_count);
    printf("engagement_count=%u\n", (unsigned int)fixture->desc.engagement_count);
    printf("outcome_count=%u\n", (unsigned int)fixture->desc.outcome_count);
    printf("occupation_count=%u\n", (unsigned int)fixture->desc.occupation_count);
    printf("resistance_count=%u\n", (unsigned int)fixture->desc.resistance_count);
    printf("morale_count=%u\n", (unsigned int)fixture->desc.morale_count);
    printf("weapon_count=%u\n", (unsigned int)fixture->desc.weapon_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int conflict_run_inspect_record(const conflict_fixture* fixture,
                                       const char* record_name,
                                       u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_conflict_record_sample sample;
    u32 record_id;
    if (!record_name) {
        return 1;
    }
    record_id = d_rng_hash_str32(record_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_conflict_record_query(&domain, record_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=record\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("conflict_id=%u\n", (unsigned int)sample.conflict_id);
    printf("conflict_id_str=%s\n", conflict_lookup_record_name(fixture, sample.conflict_id));
    printf("domain_id=%u\n", (unsigned int)sample.domain_id);
    printf("side_count=%u\n", (unsigned int)sample.side_count);
    printf("event_count=%u\n", (unsigned int)sample.event_count);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("status=%u\n", (unsigned int)sample.status);
    printf("next_due_tick=%llu\n", (unsigned long long)sample.next_due_tick);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("epistemic_scope_id=%u\n", (unsigned int)sample.epistemic_scope_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("order_key=%llu\n", (unsigned long long)sample.order_key);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_side(const conflict_fixture* fixture,
                                     const char* side_name,
                                     u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_conflict_side_sample sample;
    u32 side_id;
    if (!side_name) {
        return 1;
    }
    side_id = d_rng_hash_str32(side_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_conflict_side_query(&domain, side_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=side\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("side_id=%u\n", (unsigned int)sample.side_id);
    printf("side_id_str=%s\n", conflict_lookup_side_name(fixture, sample.side_id));
    printf("conflict_id=%u\n", (unsigned int)sample.conflict_id);
    printf("authority_id=%u\n", (unsigned int)sample.authority_id);
    printf("force_count=%u\n", (unsigned int)sample.force_count);
    printf("objectives_ref_id=%u\n", (unsigned int)sample.objectives_ref_id);
    printf("logistics_dependency_id=%u\n", (unsigned int)sample.logistics_dependency_id);
    printf("readiness_level_q16=%d\n", (int)sample.readiness_level);
    printf("readiness_state=%u\n", (unsigned int)sample.readiness_state);
    printf("next_due_tick=%llu\n", (unsigned long long)sample.next_due_tick);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_event(const conflict_fixture* fixture,
                                      const char* event_name,
                                      u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_conflict_event_sample sample;
    u32 event_id;
    if (!event_name) {
        return 1;
    }
    event_id = d_rng_hash_str32(event_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_conflict_event_query(&domain, event_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=event\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", conflict_lookup_event_name(fixture, sample.event_id));
    printf("conflict_id=%u\n", (unsigned int)sample.conflict_id);
    printf("event_type=%u\n", (unsigned int)sample.event_type);
    printf("scheduled_tick=%llu\n", (unsigned long long)sample.scheduled_tick);
    printf("order_key=%llu\n", (unsigned long long)sample.order_key);
    printf("participant_count=%u\n", (unsigned int)sample.participant_count);
    printf("input_ref_count=%u\n", (unsigned int)sample.input_ref_count);
    printf("output_ref_count=%u\n", (unsigned int)sample.output_ref_count);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("epistemic_scope_id=%u\n", (unsigned int)sample.epistemic_scope_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_force(const conflict_fixture* fixture,
                                      const char* force_name,
                                      u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_security_force_sample sample;
    u32 force_id;
    if (!force_name) {
        return 1;
    }
    force_id = d_rng_hash_str32(force_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_security_force_query(&domain, force_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=force\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("force_id=%u\n", (unsigned int)sample.force_id);
    printf("force_id_str=%s\n", conflict_lookup_force_name(fixture, sample.force_id));
    printf("authority_id=%u\n", (unsigned int)sample.authority_id);
    printf("force_type=%u\n", (unsigned int)sample.force_type);
    printf("capacity_q48=%lld\n", (long long)sample.capacity);
    printf("equipment_count=%u\n", (unsigned int)sample.equipment_count);
    printf("readiness_q16=%d\n", (int)sample.readiness);
    printf("morale_q16=%d\n", (int)sample.morale);
    printf("logistics_dependency_id=%u\n", (unsigned int)sample.logistics_dependency_id);
    printf("home_domain_id=%u\n", (unsigned int)sample.home_domain_id);
    printf("next_due_tick=%llu\n", (unsigned long long)sample.next_due_tick);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_engagement(const conflict_fixture* fixture,
                                           const char* engagement_name,
                                           u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_engagement_sample sample;
    u32 engagement_id;
    if (!engagement_name) {
        return 1;
    }
    engagement_id = d_rng_hash_str32(engagement_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_engagement_query(&domain, engagement_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=engagement\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("engagement_id=%u\n", (unsigned int)sample.engagement_id);
    printf("engagement_id_str=%s\n", conflict_lookup_engagement_name(fixture, sample.engagement_id));
    printf("conflict_id=%u\n", (unsigned int)sample.conflict_id);
    printf("domain_id=%u\n", (unsigned int)sample.domain_id);
    printf("participant_count=%u\n", (unsigned int)sample.participant_count);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("resolution_tick=%llu\n", (unsigned long long)sample.resolution_tick);
    printf("resolution_policy_id=%u\n", (unsigned int)sample.resolution_policy_id);
    printf("order_key=%llu\n", (unsigned long long)sample.order_key);
    printf("logistics_count=%u\n", (unsigned int)sample.logistics_count);
    printf("legitimacy_scope_id=%u\n", (unsigned int)sample.legitimacy_scope_id);
    printf("epistemic_scope_id=%u\n", (unsigned int)sample.epistemic_scope_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_outcome(const conflict_fixture* fixture,
                                        const char* outcome_name,
                                        u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_engagement_outcome_sample sample;
    u32 outcome_id;
    if (!outcome_name) {
        return 1;
    }
    outcome_id = d_rng_hash_str32(outcome_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_engagement_outcome_query(&domain, outcome_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=outcome\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("outcome_id=%u\n", (unsigned int)sample.outcome_id);
    printf("outcome_id_str=%s\n", conflict_lookup_outcome_name(fixture, sample.outcome_id));
    printf("engagement_id=%u\n", (unsigned int)sample.engagement_id);
    printf("casualty_count=%u\n", (unsigned int)sample.casualty_count);
    printf("resource_delta_count=%u\n", (unsigned int)sample.resource_delta_count);
    printf("legitimacy_delta_count=%u\n", (unsigned int)sample.legitimacy_delta_count);
    printf("control_delta_count=%u\n", (unsigned int)sample.control_delta_count);
    printf("report_count=%u\n", (unsigned int)sample.report_count);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_occupation(const conflict_fixture* fixture,
                                           const char* occupation_name,
                                           u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_occupation_condition_sample sample;
    u32 occupation_id;
    if (!occupation_name) {
        return 1;
    }
    occupation_id = d_rng_hash_str32(occupation_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_occupation_condition_query(&domain, occupation_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=occupation\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("occupation_id=%u\n", (unsigned int)sample.occupation_id);
    printf("occupation_id_str=%s\n", conflict_lookup_occupation_name(fixture, sample.occupation_id));
    printf("occupier_authority_id=%u\n", (unsigned int)sample.occupier_authority_id);
    printf("occupied_jurisdiction_id=%u\n", (unsigned int)sample.occupied_jurisdiction_id);
    printf("enforcement_capacity_q16=%d\n", (int)sample.enforcement_capacity);
    printf("legitimacy_support_q16=%d\n", (int)sample.legitimacy_support);
    printf("logistics_dependency_id=%u\n", (unsigned int)sample.logistics_dependency_id);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("next_due_tick=%llu\n", (unsigned long long)sample.next_due_tick);
    printf("status=%u\n", (unsigned int)sample.status);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_resistance(const conflict_fixture* fixture,
                                           const char* resistance_name,
                                           u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_resistance_event_sample sample;
    u32 resistance_id;
    if (!resistance_name) {
        return 1;
    }
    resistance_id = d_rng_hash_str32(resistance_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_resistance_event_query(&domain, resistance_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=resistance\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("resistance_id=%u\n", (unsigned int)sample.resistance_id);
    printf("resistance_id_str=%s\n", conflict_lookup_resistance_name(fixture, sample.resistance_id));
    printf("occupation_id=%u\n", (unsigned int)sample.occupation_id);
    printf("trigger_reason=%u\n", (unsigned int)sample.trigger_reason);
    printf("trigger_tick=%llu\n", (unsigned long long)sample.trigger_tick);
    printf("resolution_tick=%llu\n", (unsigned long long)sample.resolution_tick);
    printf("order_key=%llu\n", (unsigned long long)sample.order_key);
    printf("outcome_count=%u\n", (unsigned int)sample.outcome_count);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_morale(const conflict_fixture* fixture,
                                       const char* morale_name,
                                       u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_morale_field_sample sample;
    u32 morale_id;
    if (!morale_name) {
        return 1;
    }
    morale_id = d_rng_hash_str32(morale_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_morale_field_query(&domain, morale_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=morale\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("morale_id=%u\n", (unsigned int)sample.morale_id);
    printf("morale_id_str=%s\n", conflict_lookup_morale_name(fixture, sample.morale_id));
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
    printf("conflict_id=%u\n", (unsigned int)sample.conflict_id);
    printf("morale_level_q16=%d\n", (int)sample.morale_level);
    printf("decay_rate_q16=%d\n", (int)sample.decay_rate);
    printf("influence_count=%u\n", (unsigned int)sample.influence_count);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_weapon(const conflict_fixture* fixture,
                                       const char* weapon_name,
                                       u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_weapon_spec_sample sample;
    u32 weapon_id;
    if (!weapon_name) {
        return 1;
    }
    weapon_id = d_rng_hash_str32(weapon_name);
    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_weapon_spec_query(&domain, weapon_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=weapon\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("weapon_id=%u\n", (unsigned int)sample.weapon_id);
    printf("weapon_id_str=%s\n", conflict_lookup_weapon_name(fixture, sample.weapon_id));
    printf("assembly_ref_id=%u\n", (unsigned int)sample.assembly_ref_id);
    printf("range_q16=%d\n", (int)sample.range);
    printf("rate_q16=%d\n", (int)sample.rate);
    printf("effectiveness_q16=%d\n", (int)sample.effectiveness);
    printf("reliability_q16=%d\n", (int)sample.reliability);
    printf("energy_cost_q48=%lld\n", (long long)sample.energy_cost);
    printf("material_interaction_ref_id=%u\n", (unsigned int)sample.material_interaction_ref_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_inspect_region(const conflict_fixture* fixture,
                                       const char* region_name,
                                       u32 budget_max)
{
    dom_conflict_domain domain;
    dom_domain_budget budget;
    dom_conflict_region_sample sample;
    u32 region_id = conflict_find_region_id(fixture, region_name);

    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_conflict_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", CONFLICT_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("conflict_count=%u\n", (unsigned int)sample.conflict_count);
    printf("side_count=%u\n", (unsigned int)sample.side_count);
    printf("event_count=%u\n", (unsigned int)sample.event_count);
    printf("force_count=%u\n", (unsigned int)sample.force_count);
    printf("engagement_count=%u\n", (unsigned int)sample.engagement_count);
    printf("outcome_count=%u\n", (unsigned int)sample.outcome_count);
    printf("occupation_count=%u\n", (unsigned int)sample.occupation_count);
    printf("resistance_count=%u\n", (unsigned int)sample.resistance_count);
    printf("morale_count=%u\n", (unsigned int)sample.morale_count);
    printf("weapon_count=%u\n", (unsigned int)sample.weapon_count);
    printf("readiness_avg_q16=%d\n", (int)sample.readiness_avg);
    printf("morale_avg_q16=%d\n", (int)sample.morale_avg);
    printf("legitimacy_avg_q16=%d\n", (int)sample.legitimacy_avg);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_conflict_domain_free(&domain);
    return 0;
}

static int conflict_run_resolve(const conflict_fixture* fixture,
                                const char* region_name,
                                u64 tick,
                                u64 tick_delta,
                                u32 budget_max,
                                u32 inactive_count)
{
    dom_conflict_domain domain;
    dom_conflict_domain* inactive = 0;
    dom_domain_budget budget;
    dom_conflict_resolve_result result;
    u32 region_id = conflict_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_conflict_domain*)malloc(sizeof(dom_conflict_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                conflict_fixture temp = *fixture;
                temp.desc.domain_id = fixture->desc.domain_id + (u64)(i + 1u);
                dom_conflict_domain_init(&inactive[i], &temp.desc);
                dom_conflict_domain_set_state(&inactive[i],
                                              DOM_DOMAIN_EXISTENCE_DECLARED,
                                              DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_conflict_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.conflict_count; ++i) {
        hash = conflict_hash_u32(hash, domain.conflicts[i].conflict_id);
        hash = conflict_hash_u32(hash, domain.conflicts[i].status);
    }
    for (u32 i = 0u; i < domain.event_count; ++i) {
        hash = conflict_hash_u32(hash, domain.events[i].event_id);
        hash = conflict_hash_u32(hash, domain.events[i].flags);
    }
    for (u32 i = 0u; i < domain.outcome_count; ++i) {
        hash = conflict_hash_u32(hash, domain.outcomes[i].outcome_id);
        hash = conflict_hash_u32(hash, domain.outcomes[i].flags);
    }
    for (u32 i = 0u; i < domain.resistance_count; ++i) {
        hash = conflict_hash_u32(hash, domain.resistance_events[i].resistance_id);
        hash = conflict_hash_u32(hash, domain.resistance_events[i].flags);
    }
    for (u32 i = 0u; i < domain.morale_count; ++i) {
        hash = conflict_hash_u32(hash, domain.morale_fields[i].morale_id);
        hash = conflict_hash_q16(hash, domain.morale_fields[i].morale_level);
        hash = conflict_hash_u32(hash, domain.morale_fields[i].flags);
    }

    printf("%s\n", CONFLICT_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("conflict_count=%u\n", (unsigned int)result.conflict_count);
    printf("side_count=%u\n", (unsigned int)result.side_count);
    printf("event_count=%u\n", (unsigned int)result.event_count);
    printf("event_applied_count=%u\n", (unsigned int)result.event_applied_count);
    printf("force_count=%u\n", (unsigned int)result.force_count);
    printf("engagement_count=%u\n", (unsigned int)result.engagement_count);
    printf("outcome_count=%u\n", (unsigned int)result.outcome_count);
    printf("outcome_applied_count=%u\n", (unsigned int)result.outcome_applied_count);
    printf("occupation_count=%u\n", (unsigned int)result.occupation_count);
    printf("resistance_count=%u\n", (unsigned int)result.resistance_count);
    printf("resistance_applied_count=%u\n", (unsigned int)result.resistance_applied_count);
    printf("morale_count=%u\n", (unsigned int)result.morale_count);
    printf("weapon_count=%u\n", (unsigned int)result.weapon_count);
    printf("readiness_avg_q16=%d\n", (int)result.readiness_avg);
    printf("morale_avg_q16=%d\n", (int)result.morale_avg);
    printf("legitimacy_avg_q16=%d\n", (int)result.legitimacy_avg);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_conflict_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_conflict_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int conflict_run_collapse(const conflict_fixture* fixture, const char* region_name)
{
    dom_conflict_domain domain;
    u32 region_id = conflict_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_conflict_domain_init(&domain, &fixture->desc);
    if (fixture->policy_set) {
        dom_conflict_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_conflict_domain_capsule_count(&domain);
    (void)dom_conflict_domain_collapse_region(&domain, region_id);
    count_after = dom_conflict_domain_capsule_count(&domain);

    printf("%s\n", CONFLICT_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CONFLICT_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_conflict_domain_free(&domain);
    return 0;
}

static void conflict_usage(void)
{
    printf("dom_tool_conflict commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --record <id> [--budget N]\n");
    printf("  inspect --fixture <path> --side <id> [--budget N]\n");
    printf("  inspect --fixture <path> --event <id> [--budget N]\n");
    printf("  inspect --fixture <path> --force <id> [--budget N]\n");
    printf("  inspect --fixture <path> --engagement <id> [--budget N]\n");
    printf("  inspect --fixture <path> --outcome <id> [--budget N]\n");
    printf("  inspect --fixture <path> --occupation <id> [--budget N]\n");
    printf("  inspect --fixture <path> --resistance <id> [--budget N]\n");
    printf("  inspect --fixture <path> --morale <id> [--budget N]\n");
    printf("  inspect --fixture <path> --weapon <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        conflict_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = conflict_find_arg(argc, argv, "--fixture");
        conflict_fixture fixture;
        if (!fixture_path || !conflict_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "conflict: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return conflict_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* record_name = conflict_find_arg(argc, argv, "--record");
            const char* conflict_name = conflict_find_arg(argc, argv, "--conflict");
            const char* side_name = conflict_find_arg(argc, argv, "--side");
            const char* event_name = conflict_find_arg(argc, argv, "--event");
            const char* force_name = conflict_find_arg(argc, argv, "--force");
            const char* engagement_name = conflict_find_arg(argc, argv, "--engagement");
            const char* outcome_name = conflict_find_arg(argc, argv, "--outcome");
            const char* occupation_name = conflict_find_arg(argc, argv, "--occupation");
            const char* resistance_name = conflict_find_arg(argc, argv, "--resistance");
            const char* morale_name = conflict_find_arg(argc, argv, "--morale");
            const char* weapon_name = conflict_find_arg(argc, argv, "--weapon");
            const char* region_name = conflict_find_arg(argc, argv, "--region");
            u32 budget_max = conflict_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (!record_name && conflict_name) {
                record_name = conflict_name;
            }
            if (record_name) {
                return conflict_run_inspect_record(&fixture, record_name, budget_max);
            }
            if (side_name) {
                return conflict_run_inspect_side(&fixture, side_name, budget_max);
            }
            if (event_name) {
                return conflict_run_inspect_event(&fixture, event_name, budget_max);
            }
            if (force_name) {
                return conflict_run_inspect_force(&fixture, force_name, budget_max);
            }
            if (engagement_name) {
                return conflict_run_inspect_engagement(&fixture, engagement_name, budget_max);
            }
            if (outcome_name) {
                return conflict_run_inspect_outcome(&fixture, outcome_name, budget_max);
            }
            if (occupation_name) {
                return conflict_run_inspect_occupation(&fixture, occupation_name, budget_max);
            }
            if (resistance_name) {
                return conflict_run_inspect_resistance(&fixture, resistance_name, budget_max);
            }
            if (morale_name) {
                return conflict_run_inspect_morale(&fixture, morale_name, budget_max);
            }
            if (weapon_name) {
                return conflict_run_inspect_weapon(&fixture, weapon_name, budget_max);
            }
            if (region_name) {
                return conflict_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "conflict: inspect requires an entity selector\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = conflict_find_arg(argc, argv, "--region");
            u64 tick = conflict_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = conflict_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = conflict_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = conflict_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "conflict: resolve requires --region\n");
                return 2;
            }
            return conflict_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = conflict_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "conflict: collapse requires --region\n");
                return 2;
            }
            return conflict_run_collapse(&fixture, region_name);
        }
    }

    conflict_usage();
    return 2;
}
